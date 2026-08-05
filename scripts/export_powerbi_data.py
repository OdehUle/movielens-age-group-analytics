"""
One-off export script: generates the small CSV/table data consumed by the
Power BI dashboard's Stats and Recommender pages (DAX has no p-value or
cosine-similarity function, so these are computed here and loaded as
static reference tables in Power BI -- see dashboard/README.md).

Not part of the reusable recommender library itself -- run manually
whenever the underlying data or model changes and the dashboard needs
refreshing.

Run from the repo root:
    python scripts/export_powerbi_data.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from src.recommender import ItemBasedRecommender

ratings = pd.read_table("data/ratings.dat", sep="::", header=None,
                         names=["user_id", "movie_id", "rating", "timestamp"],
                         engine="python")
movies = pd.read_table("data/movies.dat", sep="::", header=None,
                        names=["movie_id", "title", "genres"],
                        engine="python", encoding="latin-1")

model = ItemBasedRecommender(min_movie_popularity=50).fit(ratings)

example_users = [("Older group, user 6", 6), ("Adult group, user 30", 30)]

rows = []
for label, uid in example_users:
    top_rated = (ratings[ratings["user_id"] == uid]
                 .merge(movies, on="movie_id")
                 .sort_values("rating", ascending=False)
                 .head(5))
    for _, r in top_rated.iterrows():
        rows.append({"user_label": label, "list_type": "Top rated",
                     "title": r["title"], "value": r["rating"]})

    recs = model.recommend(uid, n=5).merge(movies, on="movie_id")
    for _, r in recs.iterrows():
        rows.append({"user_label": label, "list_type": "Recommended",
                     "title": r["title"], "value": round(r["predicted_rating"], 2)})

pd.DataFrame(rows).to_csv("recommender_showcase.csv", index=False)
print("Wrote recommender_showcase.csv")
