"""
Helper functions.
"""
import os


def write_to_csv(df, fn):
    """Save a dataframe to CSV."""
    here = os.path.abspath(os.path.dirname(__file__))
    out_path = os.path.join(os.path.dirname(here), 'data', fn)
    df.to_csv(out_path, encoding='utf8', index=False)
    print('CSV file saved to {}'.format(out_path))
