# Data

This project uses the **MovieLens 1M** dataset from GroupLens Research:
1 million ratings from 6,040 users on 3,706 movies, collected 2000.

The raw data files are **not committed to this repository** (standard
practice for this dataset -- see citation/license note below), so you'll
need to download them yourself:

1. Download the dataset: https://grouplens.org/datasets/movielens/1m/
   (direct zip: https://files.grouplens.org/datasets/movielens/ml-1m.zip)
2. Unzip it, and copy the three files into this `data/` folder:
   - `users.dat`
   - `ratings.dat`
   - `movies.dat`
3. Run the notebook in `notebooks/` -- it reads these files with relative
   paths (`../data/users.dat`, etc.), so no path edits should be needed if
   you keep this folder structure.

## Citation

If you use this dataset, GroupLens asks that you cite:

> F. Maxwell Harper and Joseph A. Konstan. 2015. The MovieLens Datasets:
> History and Context. ACM Transactions on Interactive Intelligent
> Systems (TiiS) 5, 4: 19:1-19:19. https://doi.org/10.1145/2827872

## License note

The MovieLens dataset is provided by GroupLens Research for research
purposes under its own usage license (see the `README` bundled inside the
dataset zip file for the current terms) -- it is separate from, and not
covered by, this repository's MIT license, which applies only to the code.
