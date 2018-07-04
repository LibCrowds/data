#-*- coding: utf8 -*-
"""
Generate Convert-a-Card ingest summary.
"""
import os
import re
import csv
import pandas
import click
from pymarc import MARCReader

from helpers import write_to_csv, normalise_shelfmark


def get_marc_file_paths():
    """Return a list of paths to MARC metadata files."""
    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(os.path.dirname(here), 'metadata', 'convert-a-card')
    return [os.path.join(path, fn) for fn in os.listdir(path)]


def get_cac_summary_df():
    """Return a summary of records already created from Convert-a-Card."""
    paths = get_marc_file_paths()
    out = []
    for path in paths:
        with open(path, 'rb') as f:
            reader = MARCReader(f)
            for record in reader:
                out.append({
                    'title': record.title(),
                    'language': record['008'].data[35:38],
                    'shelfmark': record['852']['j']
                })
    df = pandas.DataFrame(out)
    df['normalised_shelfmark'] = df['shelfmark'].apply(normalise_shelfmark)
    return df


@click.command()
def main():
    df = get_cac_summary_df()
    write_to_csv(df, 'cac_summary.csv')


if __name__ == "__main__":
    main()
