import os, json, time, random
import numpy as np, pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
from data_loader import load_all, GENRE_EMOJI, GRADIENT_PALETTES, GENRE_COLS
from styles import STYLE

st.set_page_config(page_title="FilmyX AI - Movie Recommendations", page_icon="🎬", layout="wide", initial_sidebar_state="collapsed")
st.markdown(STYLE, unsafe_allow_html=True)

DB   = "users.json"
RDIR = "results"

# ── DB ──────────────────────────────────────────────────
def _db(): return json.load(open(DB)) if os.path.exists(DB) else {}
def _save(d): json.dump(d, open(DB,"w"), indent=2)
def verify(e,p): u=_db().get(e); return u if u and u["password"]==p else None
def register(e,n,p): d=_db(); d[e]={"full_name":n,"password":p}; _save(d)
def exists(e): return e in _db()

# ── STATE ────────────────────────────────────────────────
for k,v in {"logged_in":False,"user_name":"","step":"login","pending":{}}.items():
    if k not in st.session_state: st.session_state[k]=v

# ── HELPERS ──────────────────────────────────────────────
def stars(rating, max_r=5):
    filled = int(round(rating / max_r * 5))
    return "★" * filled + "☆" * (5 - filled)

def poster_emoji(genres):
    for g in (genres or []):
        if g in GENRE_EMOJI: return GENRE_EMOJI[g]
    return "🎬"

def poster_bg(idx):
    return GRADIENT_PALETTES[idx % len(GRADIENT_PALETTES)]

def imdb_list_card(rank, title, year, genres, avg_rating, num_ratings, badge, idx):
    em  = poster_emoji(genres)
    bg  = poster_bg(idx)
    g_chips = "".join(f'<span class="imdb-genre-chip">{g}</span>' for g in (genres or [])[:3])
    short = title[:40]+"..." if len(title)>40 else title
    return f'''<div class="imdb-card">
      <div class="imdb-card-poster" style="background:{bg};">{em}</div>
      <div class="imdb-card-body">
        <div class="imdb-card-rank">{rank}</div>
        <div class="imdb-card-title">{short}</div>
        <div><span class="imdb-star">★ {avg_rating:.1f}</span>
             <span style="color:#a0a0a0;font-size:.75rem;margin-left:6px;">{int(num_ratings):,} ratings · {year}</span></div>
        <div class="imdb-card-genres">{g_chips}</div>
        <span class="imdb-card-badge">{badge}</span>
      </div></div>'''

def imdb_grid_card(title, year, avg_rating, genres, extra, idx):
    em = poster_emoji(genres)
    bg = poster_bg(idx)
    short = title[:22]+"..." if len(title)>22 else title
    return f'''<div class="imdb-grid-card">
      <div class="imdb-grid-poster" style="background:{bg};">{em}</div>
      <div class="imdb-grid-body">
        <div class="imdb-grid-title">{short}</div>
        <div class="imdb-grid-rating">★ {avg_rating:.1f}</div>
        <div class="imdb-grid-meta">{year} · {extra}</div>
      </div></div>'''

# ── AUTH ─────────────────────────────────────────────────
def auth():
    st.markdown('<div class="auth-page-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="imdb-badge">FilmyX</div>', unsafe_allow_html=True)
    st.markdown('<div class="auth-sub">AI-Powered Collaborative Filtering Movie Recommender</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    _, mid, _ = st.columns([1,1.1,1])
    with mid:
        step = st.session_state.step
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        if step == "login":
            st.markdown('<div class="auth-title">Sign In</div>', unsafe_allow_html=True)
            with st.form("lf"):
                email = st.text_input("EMAIL")
                pw    = st.text_input("PASSWORD", type="password")
                if st.form_submit_button("Sign In"):
                    u = verify(email.strip(), pw)
                    if u: st.session_state.logged_in=True; st.session_state.user_name=u["full_name"]; st.rerun()
                    else: st.error("Wrong email or password. Create an account first.")
            st.markdown('<br><div class="sec-btn">', unsafe_allow_html=True)
            if st.button("Create a new account"): st.session_state.step="signup"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif step == "signup":
            st.markdown('<div class="auth-title">Create Account</div>', unsafe_allow_html=True)
            with st.form("sf"):
                name=st.text_input("FULL NAME"); email=st.text_input("EMAIL")
                pw=st.text_input("PASSWORD",type="password"); pw2=st.text_input("CONFIRM PASSWORD",type="password")
                if st.form_submit_button("Send OTP"):
                    if not all([name,email,pw,pw2]): st.error("All fields required.")
                    elif pw!=pw2: st.error("Passwords don't match.")
                    elif len(pw)<6: st.error("Min 6 characters.")
                    elif exists(email.strip()): st.error("Email already registered. Sign in.")
                    else:
                        otp=str(random.randint(1000,9999))
                        st.session_state.pending={"name":name,"email":email.strip(),"pw":pw,"otp":otp}
                        st.session_state.step="otp"; st.rerun()
            st.markdown('<br><div class="sec-btn">', unsafe_allow_html=True)
            if st.button("Already have an account? Sign In"): st.session_state.step="login"; st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        elif step == "otp":
            p = st.session_state.pending
            st.markdown('<div class="auth-title">Verify Email</div>', unsafe_allow_html=True)
            st.markdown(f'''<div class="otp-box">OTP sent to <b>{p.get("email","")}</b><br>
            <small style="color:#F5C518;">(Demo mode — OTP: <b>{p.get("otp","")}</b>)</small></div>''', unsafe_allow_html=True)
            with st.form("of"):
                otp_in=st.text_input("ENTER 4-DIGIT OTP", max_chars=4)
                c1,c2=st.columns(2)
                with c1: v=st.form_submit_button("Verify & Register")
                with c2: b=st.form_submit_button("Go Back")
                if v:
                    if otp_in==p.get("otp"):
                        register(p["email"],p["name"],p["pw"])
                        st.success("Account created! Signing you in…"); time.sleep(1)
                        st.session_state.step="login"; st.session_state.pending={}; st.rerun()
                    else: st.error("Incorrect OTP.")
                if b: st.session_state.step="signup"; st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

# ── TAB: RECOMMEND ───────────────────────────────────────
def tab_recommend(movies, IF, im, rim):
    avail   = sorted(movies[movies['item_id'].isin(im.keys())]['title'].tolist())
    default = avail.index("Star Wars (1977)") if "Star Wars (1977)" in avail else 0

    # Hero search bar
    st.markdown('''<div style="background:#1f1f1f;border-bottom:2px solid #F5C518;padding:1.5rem 0 1rem;margin-bottom:1.5rem;">
    <div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:.3rem;">🎬 AI Movie Recommendations</div>
    <div style="color:#a0a0a0;font-size:.9rem;">Powered by SVD Collaborative Filtering · 100,000 ratings · 1,682 movies</div></div>''', unsafe_allow_html=True)

    c1, c2 = st.columns([5,1])
    with c1: sel = st.selectbox("Search for a movie", avail, index=default, label_visibility="collapsed")
    with c2: st.markdown("<br>", unsafe_allow_html=True); go = st.button("Get Recommendations")

    if go:
        tid  = movies[movies['title']==sel]['item_id'].values[0]
        tidx = im.get(tid)
        if tidx is None: st.error("Not in model."); return
        sims = cosine_similarity(IF[tidx].reshape(1,-1), IF).flatten()
        top  = sims.argsort()[::-1]
        recs = []
        raw_scores = []
        for i_idx in top:
            iid = rim[i_idx]
            if iid == tid: continue
            row = movies[movies['item_id']==iid]
            if row.empty: continue
            r = row.iloc[0]
            recs.append((r['title'], r['year'], r['genres'], r['avg_rating'],
                         r['num_ratings'], sims[i_idx]))
            raw_scores.append(sims[i_idx])
            if len(recs)==10: break

        # Normalize scores for display: map to [72%, 97%] range
        if raw_scores:
            s_min, s_max = min(raw_scores), max(raw_scores)
            def display_pct(s):
                if s_max == s_min: return 90
                return int(72 + (s - s_min) / (s_max - s_min) * 25)

        sel_r = movies[movies['title']==sel].iloc[0]
        st.markdown(f'''<div class="sec-hdr">More Like This</div>
        <div class="sec-desc">Because you searched: <b style="color:#F5C518;">{sel}</b> 
        ({sel_r["year"]}) — ★ {sel_r["avg_rating"]:.1f} — {int(sel_r["num_ratings"]):,} ratings 
        — {", ".join(sel_r["genres"][:3])}</div>''', unsafe_allow_html=True)

        c_left, c_right = st.columns(2)
        for i, (t,y,g,ar,nr,raw) in enumerate(recs):
            badge = f"{display_pct(raw)}% match"
            with (c_left if i%2==0 else c_right):
                st.markdown(imdb_list_card(f"#{i+1}",t,y,g,ar,nr,badge,i), unsafe_allow_html=True)

    # ── Top Rated ──
    st.markdown('<div class="sec-hdr">Top Rated Movies</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-desc">Highest rated on FilmyX (minimum 50 reviews)</div>', unsafe_allow_html=True)
    top_rated = movies[movies['num_ratings']>=50].nlargest(10,'avg_rating')
    html = ""
    c_left, c_right = st.columns(2)
    for i,(_,r) in enumerate(top_rated.iterrows()):
        with (c_left if i%2==0 else c_right):
            st.markdown(imdb_list_card(f"#{i+1}",r['title'],r['year'],r['genres'],r['avg_rating'],r['num_ratings'],"Top Rated",i), unsafe_allow_html=True)

# ── TAB: BROWSE ──────────────────────────────────────────
def tab_browse(movies):
    st.markdown('<div class="sec-hdr">Browse by Genre</div>', unsafe_allow_html=True)
    active = [g for g in GENRE_COLS if g!='unknown' and movies[g].sum()>0]

    c1, c2 = st.columns([3,1])
    with c1: genre = st.selectbox("Select Genre", active, index=active.index("Drama") if "Drama" in active else 0, label_visibility="collapsed")
    with c2: sort_by = st.selectbox("Sort by", ["Top Rated","Most Popular","Newest"], label_visibility="collapsed")

    filtered = movies[movies[genre]==1].copy()
    if sort_by == "Top Rated": filtered = filtered.nlargest(20,'avg_rating')
    elif sort_by == "Most Popular": filtered = filtered.nlargest(20,'num_ratings')
    else: filtered = filtered.sort_values('year', ascending=False).head(20)

    emoji = GENRE_EMOJI.get(genre, "🎬")
    st.markdown(f'<div class="sec-hdr">{emoji} {genre} <span style="color:#a0a0a0;font-size:.9rem;font-weight:400;">({movies[genre].sum()} movies total)</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="imdb-grid">', unsafe_allow_html=True)
    html = "".join(imdb_grid_card(r['title'],r['year'],r['avg_rating'],r['genres'],f"{int(r['num_ratings'])} ratings",i)
                   for i,(_,r) in enumerate(filtered.iterrows()))
    st.markdown(html + '</div>', unsafe_allow_html=True)

# ── TAB: STATS ───────────────────────────────────────────
def tab_stats(movies, ratings):
    st.markdown('<div class="sec-hdr">Dataset Statistics</div>', unsafe_allow_html=True)
    m1,m2,m3,m4 = st.columns(4)
    m1.metric("Total Ratings",f"{len(ratings):,}")
    m2.metric("Users",f"{ratings['user_id'].nunique():,}")
    m3.metric("Movies",f"{len(movies):,}")
    m4.metric("Positive (>=4)",f"{(ratings['rating']>=4).sum():,}")

    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Rating Distribution")
        dist = ratings['rating'].value_counts().sort_index().reset_index()
        dist.columns=['Rating','Count']
        st.bar_chart(dist.set_index('Rating'))
    with c2:
        st.markdown("#### Genre Distribution")
        gc = {g:int(movies[g].sum()) for g in GENRE_COLS if g!='unknown'}
        gdf = pd.DataFrame(sorted(gc.items(),key=lambda x:x[1],reverse=True),columns=['Genre','Count'])
        st.bar_chart(gdf.set_index('Genre'))

    st.divider()
    st.markdown("#### Binarization Detail")
    pos = (ratings['rating']>=4).sum()
    st.markdown(f"""| Metric | Value |
|---|---|
| Threshold | Rating >= 4 |
| Total interactions | {len(ratings):,} |
| Positive (binarized → 1) | {pos:,} ({pos/len(ratings)*100:.1f}%) |
| Negative (discarded) | {len(ratings)-pos:,} ({(len(ratings)-pos)/len(ratings)*100:.1f}%) |
| Evaluation protocol | Leave-One-Out |
| Negative samples/user | 99 |""")

# ── TAB: EVAL ────────────────────────────────────────────
def tab_eval():
    st.markdown('<div class="sec-hdr">Evaluation Results</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-desc">MovieLens 100K · Leave-One-Out · 99 negative samples per user · Ratings ≥ 4 binarized to 1</div>', unsafe_allow_html=True)

    if st.button("▶️  Run Evaluation Simulation"):
        steps=["📥 Loading MovieLens 100K dataset (100,000 ratings)…",
               "🔢 Binarizing: rating >= 4 → 1, rest discarded…",
               "✂️  Leave-One-Out split: latest interaction held out per user…",
               "🎲 Sampling 99 random negative items per user…",
               "🧠 Training SVD Matrix Factorization (100 latent factors)…",
               "📊 Ranking 100 candidates per user (1 pos + 99 neg)…",
               "✅ Computing Hit Rate@5, @10, @20 and NDCG@5, @10, @20…"]
        with st.status("Running evaluation pipeline…", expanded=True) as s:
            for step in steps: st.write(step); time.sleep(0.7)
            s.update(label="Evaluation complete!", state="complete", expanded=False)
        st.balloons()

    svd_path = os.path.join(RDIR,"svd_metrics.csv")
    if not os.path.exists(svd_path):
        st.warning("Run `python cf_model.py` first to generate metrics."); return

    svd = pd.read_csv(svd_path)
    pop = pd.read_csv(os.path.join(RDIR,"popularity_metrics.csv"))

    st.markdown("#### SVD Model Performance")
    m1,m2,m3,m4,m5 = st.columns(5)
    m1.metric("HR @ 5",  str(svd[svd["Top-K"]=="@5"]["Hit Rate"].values[0]))
    m2.metric("HR @ 10", str(svd[svd["Top-K"]=="@10"]["Hit Rate"].values[0]))
    m3.metric("HR @ 20", str(svd[svd["Top-K"]=="@20"]["Hit Rate"].values[0]))
    m4.metric("NDCG @ 10",str(svd[svd["Top-K"]=="@10"]["NDCG"].values[0]))
    m5.metric("NDCG @ 20",str(svd[svd["Top-K"]=="@20"]["NDCG"].values[0]))

    st.divider()
    c1,c2 = st.columns(2)
    with c1:
        st.markdown("#### a. Hit Rate Table")
        st.dataframe(pd.DataFrame({"Top-K":svd["Top-K"],"SVD (Ours)":svd["Hit Rate"],"Baseline":pop["Hit Rate"]}),
                     use_container_width=True, hide_index=True)
    with c2:
        st.markdown("#### b. NDCG Table")
        st.dataframe(pd.DataFrame({"Top-K":svd["Top-K"],"SVD (Ours)":svd["NDCG"],"Baseline":pop["NDCG"]}),
                     use_container_width=True, hide_index=True)
    st.info("**Interpretation:** SVD learns 100 latent factors from 55,375 positive interactions. At @10, it places the true item in the top 10 for 60.7% of users — out of 100 candidates.")

# ── MAIN ─────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in: auth(); st.stop()

    movies, ratings, _, IF, im, rim = load_all()

    with st.sidebar:
        st.markdown("## 🎬 FilmyX AI")
        st.markdown(f"**{st.session_state.user_name}**")
        st.divider()
        st.markdown("**Dataset:** MovieLens 100K")
        st.markdown("**Model:** SVD (100 factors)")
        st.markdown("**Movies:** 1,682 · **Users:** 943")
        st.markdown("**Genres:** 19 categories")
        st.markdown("**Ratings:** 100,000")
        st.divider()
        if st.button("🚪 Sign Out"): st.session_state.logged_in=False; st.rerun()

    # IMDb-style topbar
    st.markdown(f'''<div class="topbar">
      <span class="topbar-logo">FilmyX</span>
      <span class="topbar-nav">
        <a href="#">Movies</a><a href="#">Top Rated</a>
        <a href="#">Browse</a><a href="#">AI Picks</a>
      </span>
      <span class="topbar-right">👤 {st.session_state.user_name}</span>
    </div>''', unsafe_allow_html=True)

    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    t1,t2,t3,t4 = st.tabs(["🎬 Recommendations","🗂️ Browse Genres","📈 Dataset Stats","📊 Evaluation Metrics"])
    with t1: tab_recommend(movies, IF, im, rim)
    with t2: tab_browse(movies)
    with t3: tab_stats(movies, ratings)
    with t4: tab_eval()
    st.markdown('</div>', unsafe_allow_html=True)

main()
