# Collaborative Filtering Movie Recommendation System

**Student Name:** Manish Vardhan 
**Roll No:** MT24052
**Dataset:** MovieLens 100K  
**Algorithm:** SVD Matrix Factorization (Collaborative Filtering)  
**Binarization:** Ratings ≥ 4 → 1 (Positive), rest discarded  
**Evaluation Protocol:** Leave-One-Out with 99 Negative Samples  

---

## a. Tables of Hit Rate

**Hit Rate@K** measures how often the true held-out item appears in the top-K recommendations (out of 100 candidates: 1 positive + 99 random negatives).

| Top-K | SVD Matrix Factorization | Popularity Baseline |
|:-----:|:------------------------:|:-------------------:|
| @5    | **0.4413**               | 0.3174              |
| @10   | **0.6071**               | 0.4735              |
| @20   | **0.7535**               | 0.6709              |

> The SVD model achieves a **Hit Rate of 60.71% at K=10**, meaning for 60.71% of users, the true held-out movie appears in the top 10 recommendations out of 100 candidates. At K=20, this rises to **75.35%**, exceeding the 70% threshold.

---

## b. Tables of NDCG

**NDCG@K** (Normalized Discounted Cumulative Gain) measures not just whether the true item is found, but how high it is ranked within the top-K list. Higher = better.

| Top-K | SVD Matrix Factorization | Popularity Baseline |
|:-----:|:------------------------:|:-------------------:|
| @5    | **0.3194**               | 0.2204              |
| @10   | **0.3732**               | 0.2705              |
| @20   | **0.4100**               | 0.3201              |

> The SVD model consistently outperforms the Popularity Baseline across all K values in both Hit Rate and NDCG, demonstrating that learning latent user-item interaction patterns produces genuinely better recommendations than simply recommending popular items.

---

## Model Summary

| Parameter | Value |
|-----------|-------|
| Dataset | MovieLens 100K |
| Total Ratings | 100,000 |
| Users | 943 |
| Movies | 1,682 |
| Genres | 19 |
| Binarization Threshold | Rating ≥ 4 → 1 |
| Positive Interactions | 55,375 (55.4%) |
| Algorithm | SVD Matrix Factorization |
| Latent Factors | 100 |
| Evaluation | Leave-One-Out |
| Negative Samples | 99 per user |

---

## c. Link to Demo Video : - https://youtu.be/s4Ts6X9-RYY

**YouTube Demo Link:**

> The demo video shows:
> - User registration with OTP email verification
> - Login authentication (only registered users can access)
> - Movie search and AI-powered recommendations with match percentage
> - Browse movies by all 19 genres (Action, Drama, Comedy, etc.)
> - Dataset statistics with charts
> - Evaluation metrics tab showing Hit Rate and NDCG tables

## demo link : https://movierecommendationsystem-xqga6cdxfsbdsunrhuc6u6.streamlit.app/

