"""
data_loader.py  — loads, enriches and caches all MovieLens 100K data
"""
import os, zipfile, requests
import numpy as np, pandas as pd
from io import BytesIO
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import svds
import streamlit as st

DDIR  = "data"
DFILE = os.path.join(DDIR, "u.data")
IFILE = os.path.join(DDIR, "u.item")
RDIR  = "results"
ML    = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"

GENRE_COLS = ['unknown','Action','Adventure','Animation','Childrens','Comedy','Crime',
              'Documentary','Drama','Fantasy','FilmNoir','Horror','Musical','Mystery',
              'Romance','SciFi','Thriller','War','Western']

GENRE_EMOJI = {
    'Action':'💥','Adventure':'🗺️','Animation':'🎨','Childrens':'🧸',
    'Comedy':'😂','Crime':'🔫','Documentary':'📽️','Drama':'🎭',
    'Fantasy':'🧙','FilmNoir':'🕵️','Horror':'👻','Musical':'🎵',
    'Mystery':'🔍','Romance':'❤️','SciFi':'🚀','Thriller':'😱',
    'War':'⚔️','Western':'🤠','unknown':'🎬'
}

GRADIENT_PALETTES = [
    "linear-gradient(135deg,#1a1a2e,#16213e)",
    "linear-gradient(135deg,#2d1b69,#11998e)",
    "linear-gradient(135deg,#641c34,#111)",
    "linear-gradient(135deg,#0f2027,#2c5364)",
    "linear-gradient(135deg,#373b44,#4286f4)",
    "linear-gradient(135deg,#3a1c71,#d76d77)",
    "linear-gradient(135deg,#000428,#004e92)",
    "linear-gradient(135deg,#1f4037,#99f2c8,#1f4037)",
    "linear-gradient(135deg,#4b134f,#c94b4b)",
    "linear-gradient(135deg,#12c2e9,#c471ed,#f64f59)",
]

def _ensure_data():
    os.makedirs(DDIR, exist_ok=True)
    if not os.path.exists(DFILE):
        r = requests.get(ML, timeout=60); r.raise_for_status()
        with zipfile.ZipFile(BytesIO(r.content)) as z:
            z.extract("ml-100k/u.data", DDIR); z.extract("ml-100k/u.item", DDIR)
        sub = os.path.join(DDIR, "ml-100k")
        os.rename(os.path.join(sub,"u.data"), DFILE)
        os.rename(os.path.join(sub,"u.item"), IFILE)
        os.rmdir(sub)

@st.cache_resource(show_spinner="🧠 Loading model & data…")
def load_all():
    _ensure_data()

    # ── Movies ──
    item_cols = ['item_id','title','release_date','video_release_date','imdb_url'] + GENRE_COLS
    movies = pd.read_csv(IFILE, sep="|", encoding="latin-1", header=None, names=item_cols)
    movies['genres'] = movies[GENRE_COLS].apply(
        lambda r: [g for g in GENRE_COLS if r[g]==1], axis=1)
    movies['year']   = movies['title'].str.extract(r'\((\d{4})\)').fillna('?')
    movies['clean_title'] = movies['title'].str.replace(r'\s*\(\d{4}\)','',regex=True).str.strip()
    movies['imdb_url'] = movies['imdb_url'].fillna('')

    # ── Ratings ──
    ratings = pd.read_csv(DFILE, sep="\t", names=["user_id","item_id","rating","timestamp"])
    ratings['binary'] = (ratings['rating'] >= 4).astype(int)
    df_pos = ratings[ratings['binary']==1].copy()

    # ── Per-movie stats ──
    stats = ratings.groupby('item_id').agg(
        num_ratings=('rating','count'),
        avg_rating=('rating','mean'),
        num_positive=('binary','sum')
    ).reset_index()
    movies = movies.merge(stats, on='item_id', how='left').fillna({'num_ratings':0,'avg_rating':0,'num_positive':0})
    movies['popularity_pct'] = (movies['num_ratings'] / movies['num_ratings'].max() * 100).round(1)

    # ── SVD Model ──
    users = sorted(df_pos["user_id"].unique())
    items = sorted(df_pos["item_id"].unique())
    um  = {u:i for i,u in enumerate(users)}
    im  = {v:j for j,v in enumerate(items)}
    rim = {j:v for v,j in im.items()}

    row  = df_pos["user_id"].map(um).values
    col  = df_pos["item_id"].map(im).values
    data = np.ones(len(df_pos), dtype=np.float32)
    mat  = coo_matrix((data,(row,col)), shape=(len(users),len(items))).tocsr()
    k    = min(100, min(mat.shape)-1)
    _,_,Vt = svds(mat.asfptype(), k=k)
    item_factors = Vt.T   # (n_items, k)

    return movies, ratings, df_pos, item_factors, im, rim
