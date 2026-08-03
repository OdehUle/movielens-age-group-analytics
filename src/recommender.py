"""
Item-based collaborative filtering recommender.

A deliberately simple similarity-based recommender (cosine similarity on a
user-item ratings matrix) -- not a claim of production-grade ML, just a
demonstration of going from EDA to a basic working recommender. Extracted
from notebooks/movielens_age_group_analysis.ipynb, section 12, so it can be
imported, tested, and reused independently of the notebook.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity


class ItemBasedRecommender:
    """Item-based CF recommender using cosine similarity.

    Parameters
    ----------
    min_movie_popularity : int
        Minimum number of ratings a movie must have before it's eligible to
        be recommended. Raw cosine similarity on a very sparse matrix can
        give two obscure titles a similarity of 1.0 just because one person
        happened to rate both -- this floor keeps that from dominating
        recommendations. It does not otherwise regularize the similarity
        weights themselves.

    Attributes
    ----------
    user_ids, movie_ids : np.ndarray
        Sorted arrays mapping matrix row/column position back to real IDs.
    R : scipy.sparse.csr_matrix
        The fitted user-item ratings matrix (users x movies).
    item_sim : scipy.sparse.csr_matrix
        Item-item cosine similarity matrix (movies x movies).
    """

    def __init__(self, min_movie_popularity: int = 50):
        self.min_movie_popularity = min_movie_popularity
        self.user_ids = None
        self.movie_ids = None
        self.user_idx = None
        self.movie_idx = None
        self.R = None
        self.item_sim = None
        self.popular_movie_mask = None

    def fit(self, ratings: pd.DataFrame,
            user_col: str = "user_id", item_col: str = "movie_id", rating_col: str = "rating"):
        """Build the ratings matrix and item-item similarity matrix.

        Parameters
        ----------
        ratings : pd.DataFrame
            Long-format ratings table with one row per (user, item, rating).
        """
        self.user_ids = np.sort(ratings[user_col].unique())
        self.movie_ids = np.sort(ratings[item_col].unique())
        self.user_idx = {u: i for i, u in enumerate(self.user_ids)}
        self.movie_idx = {m: i for i, m in enumerate(self.movie_ids)}

        rows = ratings[user_col].map(self.user_idx).values
        cols = ratings[item_col].map(self.movie_idx).values
        vals = ratings[rating_col].values.astype(float)

        self.R = csr_matrix((vals, (rows, cols)),
                             shape=(len(self.user_ids), len(self.movie_ids)))
        self.item_sim = cosine_similarity(self.R.T, dense_output=False)

        movie_rating_counts = np.asarray((self.R > 0).sum(axis=0)).ravel()
        self.popular_movie_mask = movie_rating_counts >= self.min_movie_popularity
        return self

    def _check_fitted(self):
        if self.R is None:
            raise RuntimeError("Call .fit(ratings) before requesting recommendations.")

    def predict_all(self, user_id) -> np.ndarray:
        """Return a predicted-rating score for every movie for this user
        (unrated + rated). Rated and unpopular movies are set to -inf so
        they never surface via recommend(); use this directly if you want
        raw scores instead."""
        self._check_fitted()
        if user_id not in self.user_idx:
            raise KeyError(f"Unknown user_id: {user_id!r}")

        uidx = self.user_idx[user_id]
        user_row = self.R[uidx].toarray().ravel()
        rated_mask = user_row > 0
        rated_idx = np.where(rated_mask)[0]

        scores = np.zeros(self.R.shape[1])
        sim_sums = np.zeros(self.R.shape[1])
        for m in rated_idx:
            sims = self.item_sim[m].toarray().ravel()
            scores += sims * user_row[m]
            sim_sums += np.abs(sims)

        with np.errstate(divide="ignore", invalid="ignore"):
            pred = np.where(sim_sums > 0, scores / sim_sums, 0)

        pred[rated_mask] = -np.inf
        pred[~self.popular_movie_mask] = -np.inf
        return pred

    def recommend(self, user_id, n: int = 5) -> pd.DataFrame:
        """Top-n recommended movie_ids and predicted ratings for a user.
        Movies the user already rated, or that fall below the popularity
        floor, are excluded entirely rather than returned with a -inf
        score -- so the result may have fewer than n rows if there aren't
        n eligible candidates."""
        pred = self.predict_all(user_id)
        eligible = np.where(np.isfinite(pred))[0]
        eligible = eligible[np.argsort(pred[eligible])[::-1]][:n]
        return pd.DataFrame({
            "movie_id": self.movie_ids[eligible],
            "predicted_rating": pred[eligible],
        })

    def predict_rating(self, user_id, movie_id) -> float:
        """Predicted rating for a single (user, movie) pair. Falls back to
        0.0 if the user has no rated movies overlapping with any similarity
        signal -- callers doing evaluation typically want to fall back to
        a global mean instead; see evaluate_rmse() below for that pattern."""
        self._check_fitted()
        uidx = self.user_idx[user_id]
        midx = self.movie_idx[movie_id]
        user_row = self.R[uidx].toarray().ravel()
        rated_mask = user_row > 0
        if not rated_mask.any():
            return 0.0
        sims = self.item_sim[midx].toarray().ravel()
        sims_rated = sims[rated_mask]
        ratings_rated = user_row[rated_mask]
        denom = np.abs(sims_rated).sum()
        if denom == 0:
            return 0.0
        return float((sims_rated * ratings_rated).sum() / denom)


def evaluate_rmse(model: ItemBasedRecommender, test_df: pd.DataFrame,
                   global_mean: float,
                   user_col: str = "user_id", item_col: str = "movie_id",
                   rating_col: str = "rating") -> dict:
    """Compare a fitted model's held-out RMSE/MAE against a naive
    global-mean baseline. Returns a dict of {rmse, mae, baseline_rmse}."""
    preds, actuals = [], []
    for _, row in test_df.iterrows():
        uid, mid, actual = row[user_col], row[item_col], row[rating_col]
        if uid not in model.user_idx or mid not in model.movie_idx:
            preds.append(global_mean)
        else:
            pred = model.predict_rating(uid, mid)
            preds.append(pred if pred != 0.0 else global_mean)
        actuals.append(actual)

    preds = np.array(preds)
    actuals = np.array(actuals)
    rmse = float(np.sqrt(np.mean((preds - actuals) ** 2)))
    mae = float(np.mean(np.abs(preds - actuals)))
    baseline_rmse = float(np.sqrt(np.mean((global_mean - actuals) ** 2)))
    return {"rmse": rmse, "mae": mae, "baseline_rmse": baseline_rmse}
