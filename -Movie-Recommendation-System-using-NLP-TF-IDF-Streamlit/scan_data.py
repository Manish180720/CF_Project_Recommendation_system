import pandas as pd, numpy as np

cols = ['item_id','title','release_date','video_release_date','imdb_url',
        'unknown','Action','Adventure','Animation','Childrens','Comedy','Crime',
        'Documentary','Drama','Fantasy','FilmNoir','Horror','Musical','Mystery',
        'Romance','SciFi','Thriller','War','Western']
movies = pd.read_csv('data/u.item', sep='|', encoding='latin-1', header=None, names=cols)
ratings = pd.read_csv('data/u.data', sep='\t', names=['user_id','item_id','rating','timestamp'])

genre_cols = cols[5:]
movies['genres_list'] = movies[genre_cols].apply(lambda r: [g for g in genre_cols if r[g]==1], axis=1)
movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').fillna('Unknown')

print("=== MOVIES ===")
print(f"Total: {len(movies)}")
print(f"Year range: {movies['year'].min()} - {movies['year'].max()}")
print()

print("=== RATINGS ===")
print(f"Total: {len(ratings)}, Users: {ratings['user_id'].nunique()}, Items: {ratings['item_id'].nunique()}")
print("Rating counts:")
print(ratings['rating'].value_counts().sort_index())
binary = (ratings['rating']>=4).sum()
print(f"Positive (>=4): {binary} ({binary/len(ratings)*100:.1f}%)")

mr = ratings.groupby('item_id').agg(count=('rating','count'), avg=('rating','mean')).reset_index()
mr = mr.merge(movies[['item_id','title']], on='item_id')
print("\nTop 10 most rated:")
print(mr.nlargest(10,'count')[['title','count','avg']].to_string())
print("\nTop 10 highest avg (min 50 ratings):")
print(mr[mr['count']>=50].nlargest(10,'avg')[['title','count','avg']].to_string())

print("\nGenre distribution:")
for g in genre_cols:
    print(f"  {g}: {movies[g].sum()}")
