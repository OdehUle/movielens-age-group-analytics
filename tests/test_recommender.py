"""
Tests for src.recommender.ItemBasedRecommender, using a small synthetic
ratings table rather than the full MovieLens data set (fast, no data
download required, and it lets us construct a case where the "right"
answer is known ahead of time).

Run with: pytest tests/
"""

import sys
import os
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.recommender import ItemBasedRecommender, evaluate_rmse


def make_synthetic_ratings() -> pd.DataFrame:
    """Two clusters of taste: users 1-3 like movies 1-2 (action-ish),
    users 4-6 like movies 3-4 (romance-ish). Movie 5 is a niche title only
    ever co-rated by one user with movie 6, to exercise the popularity
    floor. Movie 1 is unrated by user 3, and should be the top
    recommendation for user 3 given users 1 and 2's overlap with them."""
    rows = [
        (1, 1, 5), (1, 2, 4), (1, 3, 1),
        (2, 1, 5), (2, 2, 5), (2, 3, 1),
        (3, 2, 4), (3, 3, 1),  # movie 1 withheld for user 3
        (4, 3, 5), (4, 4, 4),
        (5, 3, 4), (5, 4, 5),
        (6, 3, 5), (6, 4, 5),
        (1, 5, 5), (1, 6, 5),  # low-popularity pair -> should be filtered out
    ]
    return pd.DataFrame(rows, columns=["user_id", "movie_id", "rating"])


def test_fit_builds_expected_matrix_shape():
    ratings = make_synthetic_ratings()
    model = ItemBasedRecommender(min_movie_popularity=1).fit(ratings)
    assert model.R.shape == (ratings["user_id"].nunique(), ratings["movie_id"].nunique())
    assert model.item_sim.shape[0] == model.item_sim.shape[1] == ratings["movie_id"].nunique()


def test_recommend_excludes_already_rated_movies():
    ratings = make_synthetic_ratings()
    model = ItemBasedRecommender(min_movie_popularity=1).fit(ratings)
    recs = model.recommend(user_id=1, n=10)
    rated_by_user_1 = set(ratings.loc[ratings["user_id"] == 1, "movie_id"])
    assert rated_by_user_1.isdisjoint(set(recs["movie_id"]))


def test_recommend_surfaces_similar_taste_cluster():
    ratings = make_synthetic_ratings()
    model = ItemBasedRecommender(min_movie_popularity=1).fit(ratings)
    # User 3 has rated movies 2 and 3 like users 1/2 (movie 2) but is
    # missing movie 1, which users 1 and 2 both rated highly -- it should
    # be the top (or near-top) recommendation.
    recs = model.recommend(user_id=3, n=1)
    assert recs.iloc[0]["movie_id"] == 1


def test_popularity_floor_filters_low_popularity_movies():
    ratings = make_synthetic_ratings()
    # movies 5 and 6 are each only rated once -> excluded at floor=2
    model = ItemBasedRecommender(min_movie_popularity=2).fit(ratings)
    recs = model.recommend(user_id=4, n=10)
    assert 5 not in set(recs["movie_id"])
    assert 6 not in set(recs["movie_id"])


def test_predict_rating_is_bounded_by_rated_values():
    ratings = make_synthetic_ratings()
    model = ItemBasedRecommender(min_movie_popularity=1).fit(ratings)
    pred = model.predict_rating(user_id=3, movie_id=1)
    assert 1.0 <= pred <= 5.0


def test_evaluate_rmse_beats_or_matches_naive_baseline_on_easy_synthetic_case():
    ratings = make_synthetic_ratings()
    model = ItemBasedRecommender(min_movie_popularity=1).fit(ratings)
    global_mean = ratings["rating"].mean()
    # Evaluate on the same data it was fit on (fine for a synthetic smoke
    # test -- this checks evaluate_rmse() runs and returns sane values, it
    # is not a held-out generalization test).
    result = evaluate_rmse(model, ratings, global_mean)
    assert result["rmse"] >= 0
    assert result["baseline_rmse"] >= 0
    assert result["rmse"] <= result["baseline_rmse"]
