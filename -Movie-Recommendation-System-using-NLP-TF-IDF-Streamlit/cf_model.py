"""
cf_model.py
-----------
Collaborative Filtering evaluation pipeline for the MovieLens 100K dataset.

Steps:
  1. Download & cache the dataset
  2. Binarize ratings (>=4 → 1, else ignored)
  3. Leave-One-Out split with latest interaction as test item
  4. Evaluate SVD Matrix Factorization vs. Popularity Baseline
  5. Report Hit Rate@K and NDCG@K, save CSVs to results/
"""

import os
import math
import zipfile
import requests
import numpy as np
import pandas as pd
from io import BytesIO
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import svds

# ─────────────────────────────────────────────
# 1.  DATA DOWNLOAD
# ─────────────────────────────────────────────

DATA_DIR    = "data"
RESULTS_DIR = "results"
ML_URL      = "https://files.grouplens.org/datasets/movielens/ml-100k.zip"


def download_movielens() -> tuple[str, str]:
    """Download the MovieLens 100K zip and extract u.data / u.item."""
    os.makedirs(DATA_DIR, exist_ok=True)
    data_file = os.path.join(DATA_DIR, "u.data")
    item_file = os.path.join(DATA_DIR, "u.item")

    if not os.path.exists(data_file) or not os.path.exists(item_file):
        print("Downloading MovieLens 100K …")
        resp = requests.get(ML_URL, timeout=60)
        resp.raise_for_status()
        with zipfile.ZipFile(BytesIO(resp.content)) as z:
            for name in ("ml-100k/u.data", "ml-100k/u.item"):
                z.extract(name, DATA_DIR)
        # Flatten the nested ml-100k/ folder
        sub = os.path.join(DATA_DIR, "ml-100k")
        os.rename(os.path.join(sub, "u.data"), data_file)
        os.rename(os.path.join(sub, "u.item"), item_file)
        os.rmdir(sub)
        print("Download complete.")
    else:
        print("Dataset already present.")

    return data_file, item_file


# ─────────────────────────────────────────────
# 2.  LOAD & BINARIZE
# ─────────────────────────────────────────────

def load_and_binarize(data_file: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load ratings, binarize (rating >= 4 → 1), keep only positives.
    Returns:
        df_all      – full frame with binarised 'rating' column (0 / 1)
        df_positive – only the rows where rating == 1
    """
    df = pd.read_csv(
        data_file, sep="\t",
        names=["user_id", "item_id", "rating", "timestamp"]
    )
    df["rating"] = (df["rating"] >= 4).astype(int)
    df_pos = df[df["rating"] == 1].copy()
    print(f"Total positive interactions (rating >= 4): {len(df_pos):,}")
    return df, df_pos


# ─────────────────────────────────────────────
# 3.  LEAVE-ONE-OUT SPLIT
# ─────────────────────────────────────────────

def leave_one_out_split(df_pos: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    For each user, hold out the *most recent* positive interaction as the test item.
    Users with only 1 interaction are dropped (no training signal).
    """
    df_pos = df_pos.copy()
    df_pos["rank"] = df_pos.groupby("user_id")["timestamp"].rank(
        method="first", ascending=False
    )
    test_df  = df_pos[df_pos["rank"] == 1].drop(columns="rank")
    train_df = df_pos[df_pos["rank"] >  1].drop(columns="rank")

    # Keep only users that appear in both splits
    valid_users = set(train_df["user_id"]) & set(test_df["user_id"])
    train_df = train_df[train_df["user_id"].isin(valid_users)]
    test_df  = test_df[test_df["user_id"].isin(valid_users)]

    print(f"Train: {len(train_df):,} | Test: {len(test_df):,} | Users: {len(valid_users):,}")
    return train_df, test_df


# ─────────────────────────────────────────────
# 4.  NEGATIVE SAMPLING
# ─────────────────────────────────────────────

def sample_negatives(df_all: pd.DataFrame,
                     test_df: pd.DataFrame,
                     n_neg: int = 99,
                     seed: int = 42) -> dict[int, list[int]]:
    """
    For each test user, sample n_neg items the user has never interacted with.
    Returns { user_id: [neg_item_id, …] }
    """
    rng       = np.random.default_rng(seed)
    all_items = set(df_all["item_id"].unique())
    seen      = df_all.groupby("user_id")["item_id"].apply(set).to_dict()

    negatives: dict[int, list[int]] = {}
    for user_id in test_df["user_id"]:
        pool = list(all_items - seen.get(user_id, set()))
        n    = min(n_neg, len(pool))
        negatives[user_id] = rng.choice(pool, size=n, replace=False).tolist()

    return negatives


# ─────────────────────────────────────────────
# 5.  METRIC HELPERS
# ─────────────────────────────────────────────

def hit_and_ndcg(ranked: list, k: int) -> tuple[float, float]:
    """
    Given a ranked list where the test item is marked as the string 'TEST',
    return (HitRate@k, NDCG@k).
    """
    for rank, item in enumerate(ranked[:k]):
        if item == "TEST":
            return 1.0, math.log(2) / math.log(rank + 2)
    return 0.0, 0.0


# ─────────────────────────────────────────────
# 6.  SVD MODEL
# ─────────────────────────────────────────────

def train_svd(train_df: pd.DataFrame,
              n_factors: int = 50) -> tuple[np.ndarray, np.ndarray, dict, dict]:
    """
    Build a user-item matrix from binary implicit feedback and apply
    Truncated SVD to obtain latent user and item factor matrices.
    Returns user_factors, item_factors, user_map, item_map.
    """
    users = sorted(train_df["user_id"].unique())
    items = sorted(train_df["item_id"].unique())
    user_map = {u: i for i, u in enumerate(users)}
    item_map = {v: j for j, v in enumerate(items)}

    row  = train_df["user_id"].map(user_map).values
    col  = train_df["item_id"].map(item_map).values
    data = np.ones(len(train_df), dtype=np.float32)

    mat = coo_matrix((data, (row, col)), shape=(len(users), len(items))).tocsr()

    k = min(n_factors, min(mat.shape) - 1)
    U, s, Vt = svds(mat, k=k)

    user_factors = U  * s          # shape (n_users, k)
    item_factors = Vt.T            # shape (n_items, k)

    print(f"SVD trained: {len(users)} users × {len(items)} items, {k} factors.")
    return user_factors, item_factors, user_map, item_map


def evaluate_svd(test_df: pd.DataFrame,
                 negatives: dict,
                 user_factors: np.ndarray,
                 item_factors: np.ndarray,
                 user_map: dict,
                 item_map: dict,
                 top_k_list: list[int] = [5, 10, 20]) -> pd.DataFrame:
    """Evaluate SVD model with Hit Rate@K and NDCG@K."""
    results = {k: {"hits": [], "ndcgs": []} for k in top_k_list}

    for _, row in test_df.iterrows():
        user, test_item = row["user_id"], row["item_id"]
        if user not in user_map or test_item not in item_map:
            continue

        u_vec  = user_factors[user_map[user]]
        candidates = [test_item] + negatives.get(user, [])

        # Score every candidate
        scores: dict[object, float] = {}
        for item in candidates:
            key = "TEST" if item == test_item else item
            scores[key] = float(np.dot(u_vec, item_factors[item_map[item]]) if item in item_map else 0.0)

        ranked = sorted(scores, key=scores.__getitem__, reverse=True)

        for k in top_k_list:
            h, n = hit_and_ndcg(ranked, k)
            results[k]["hits"].append(h)
            results[k]["ndcgs"].append(n)

    rows = []
    for k in top_k_list:
        hr   = round(float(np.mean(results[k]["hits"])), 4)
        ndcg = round(float(np.mean(results[k]["ndcgs"])), 4)
        rows.append({"Model": "SVD Matrix Factorization", "Top-K": f"@{k}",
                     "Hit Rate": hr, "NDCG": ndcg})
        print(f"  SVD  @{k:2d}  HR={hr:.4f}  NDCG={ndcg:.4f}")
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 7.  POPULARITY BASELINE
# ─────────────────────────────────────────────

def evaluate_popularity(train_df: pd.DataFrame,
                        test_df: pd.DataFrame,
                        negatives: dict,
                        top_k_list: list[int] = [5, 10, 20]) -> pd.DataFrame:
    """Evaluate a simple Item Popularity baseline."""
    pop = train_df["item_id"].value_counts().to_dict()
    results = {k: {"hits": [], "ndcgs": []} for k in top_k_list}

    for _, row in test_df.iterrows():
        user, test_item = row["user_id"], row["item_id"]
        candidates = [test_item] + negatives.get(user, [])

        scores = {("TEST" if it == test_item else it): pop.get(it, 0) for it in candidates}
        ranked = sorted(scores, key=scores.__getitem__, reverse=True)

        for k in top_k_list:
            h, n = hit_and_ndcg(ranked, k)
            results[k]["hits"].append(h)
            results[k]["ndcgs"].append(n)

    rows = []
    for k in top_k_list:
        hr   = round(float(np.mean(results[k]["hits"])), 4)
        ndcg = round(float(np.mean(results[k]["ndcgs"])), 4)
        rows.append({"Model": "Popularity Baseline", "Top-K": f"@{k}",
                     "Hit Rate": hr, "NDCG": ndcg})
        print(f"  POP  @{k:2d}  HR={hr:.4f}  NDCG={ndcg:.4f}")
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# 8.  MAIN PIPELINE
# ─────────────────────────────────────────────

def run_pipeline():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # --- Data ---
    data_file, _ = download_movielens()
    df_all, df_pos = load_and_binarize(data_file)
    train_df, test_df = leave_one_out_split(df_pos)
    negatives = sample_negatives(df_all, test_df)

    # --- SVD ---
    print("\n[SVD Matrix Factorization]")
    user_factors, item_factors, user_map, item_map = train_svd(train_df)
    svd_metrics = evaluate_svd(test_df, negatives, user_factors, item_factors,
                               user_map, item_map)

    # --- Popularity ---
    print("\n[Popularity Baseline]")
    pop_metrics = evaluate_popularity(train_df, test_df, negatives)

    # --- Save ---
    svd_metrics.to_csv(os.path.join(RESULTS_DIR, "svd_metrics.csv"), index=False)
    pop_metrics.to_csv(os.path.join(RESULTS_DIR, "popularity_metrics.csv"), index=False)

    # Combined table
    combined = pd.concat([svd_metrics, pop_metrics], ignore_index=True)
    combined.to_csv(os.path.join(RESULTS_DIR, "all_metrics.csv"), index=False)

    print(f"\nAll results saved to '{RESULTS_DIR}/'")
    print("\n=== Final Results ===")
    print(combined.to_string(index=False))
    return svd_metrics, pop_metrics


if __name__ == "__main__":
    run_pipeline()
