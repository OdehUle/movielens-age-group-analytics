# MovieLens 1M — Age Group Analytics (Power BI Dashboard)

An interactive five-page Power BI dashboard built on top of the notebook
analysis in this repo — same dataset, same findings, translated into a
report someone can click through instead of scroll through.

![Logo](logo/movielens_marquee_logo.png)

## Pages

| Page | What it shows |
|---|---|
| **Overview** | Headline KPIs, user base share by age group, engagement (ratings per user) by age group |
| **Genre** | Avg rating by genre × age group (matrix), most polarizing genres by rating std dev |
| **Timing** | Monthly rating activity per group with a signup-burst-excluded slicer, weekday vs weekend split |
| **Stats** | The two significance-tested findings from the notebook (Child gender split, Older vs Child generosity), Horror vs Action rating distribution |
| **Recommender** | Item-based CF model output — RMSE vs. a naive baseline, and a user-selectable top-rated vs. recommended comparison |

## Design

Background art: `../images/` and the standalone deck at the repo root
(`movielens_dashboard_backgrounds.pptx`) — a "Cinema Marquee" theme (deep
midnight navy, antique gold accent) with a page-specific watermark motif
(donut, film reel, clock, flask, star) on each of the five pages. Full
design writeup and the PNG exports used as Power BI page backgrounds are
in that deck and its accompanying `pbi_backgrounds_png/` export.

## Data model

Star schema, built in Power Query from the raw `.dat` files (see
`../data/README.md`):

- `users` (dimension) — includes an `age_group` custom column and an
  `age_group_sort` helper column so Child → Youth → Adult → Older sorts
  correctly everywhere instead of alphabetically
- `ratings` (fact) — includes derived `Month`, `Hour`, `DayOfWeek`,
  `IsWeekend`/`DayType`, and `IsFirstDay` (signup-burst flag, computed by
  comparing each rating's date to that user's earliest rating date)
- `movies` (dimension) — includes a derived `year` column parsed from the
  title
- `movie_genre_bridge` — `movies` with `genres` split into rows (one row
  per movie-genre pair), so a movie with 3 genres doesn't triple-count in
  genre-level aggregates. Relationship to `movies` is set to **Both**
  cross-filter direction so a genre selection filters back up to ratings.

Two small static reference tables (Python-computed, loaded via Enter Data
/ CSV, since Power BI's DAX has no p-value or cosine-similarity function):
- `significance_results` — t-statistics, p-values, Cohen's d for the two
  tested gaps (Stats page)
- `model_metrics` + `recommender_showcase` — CF model RMSE vs. baseline,
  and example top-rated/recommended lists per user, exported by
  `../scripts/export_powerbi_data.py`

## Opening the dashboard

The `.pbix` isn't committed to this repo (see note below) — to rebuild it:

1. Follow `../data/README.md` to get the three MovieLens `.dat` files
2. Open Power BI Desktop, import them, and follow the data model steps
   above (or recreate the transformations from the notebook's Section
   11/12 logic, which they mirror)
3. Run `python scripts/export_powerbi_data.py` (from the repo root) to
   generate `recommender_showcase.csv` for the Recommender page
4. Apply the page backgrounds from `pbi_backgrounds_png/` via **Format
   page → Canvas background → Add image** on each page

## Author

Moses — built as the capstone piece for the notebook analysis in this
repo, translating the EDA and CF recommender into an interactive report.
