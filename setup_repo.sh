#!/usr/bin/env bash
# Commit the movielens-age-group-analysis project into an empty GitHub repo.
#
# Prerequisites:
#   1. You've unzipped movielens-age-group-analysis.zip somewhere locally.
#   2. You've created a new, EMPTY repository on GitHub (no README/license/
#      .gitignore added there -- those are already included in this project).
#   3. You have git installed and are authenticated with GitHub
#      (SSH key set up, or a PAT if using HTTPS).
#
# Usage:
#   ./setup_repo.sh git@github.com:<your-username>/<your-repo-name>.git
#
# or with HTTPS:
#   ./setup_repo.sh https://github.com/<your-username>/<your-repo-name>.git

set -euo pipefail

REMOTE_URL="${1:-}"

if [ -z "$REMOTE_URL" ]; then
  echo "Usage: $0 <git-remote-url>"
  echo "Example: $0 git@github.com:yourname/movielens-age-group-analysis.git"
  exit 1
fi

# Run this from inside the project folder (the one containing README.md,
# src/, notebooks/, etc.)
if [ ! -f "README.md" ] || [ ! -d "notebooks" ]; then
  echo "Error: run this script from inside the movielens-age-group-analysis folder"
  echo "(the one containing README.md, notebooks/, src/, tests/, data/, images/)."
  exit 1
fi

git init -b main
git add .
git commit -m "Initial commit: MovieLens 1M age-group EDA + significance testing + item-based CF recommender"
git remote add origin "$REMOTE_URL"
git push -u origin main

echo ""
echo "Done. Pushed to $REMOTE_URL"
