#-*- coding: utf8 -*-

import csv
import pandas
import click

from get_annotations import get_annotations_df
from helpers import write_to_csv, get_tag, get_task_id, get_transcription


def get_cac_annotations():
    """Return the Convert-a-Card annotations."""
    url_base = 'https://annotations.libcrowds.com'
    container_id = 'convert-a-card-results'
    url = '{0}/annotations/{1}/'.format(url_base, container_id)
    df = get_annotations_df(url)
    return df


def add_columns(df):
    """Add required columns to the dataframe."""
    df['tag'] = df['body'].apply(get_tag)
    df['task_id'] = df['generator'].apply(get_task_id)
    df['transcription'] = df['body'].apply(get_transcription)
    return df


def create_reference_lookup_df(df):
    """Return a dataframe indexed by task_id for looking up the reference."""
    df = df[df['tag'] == 'reference']
    df.set_index('task_id', verify_integrity=True, inplace=True)
    return df


def lookup_reference(task_id, reference_df):
    """Lookup the reference for a task ID."""
    series = reference_df.loc[task_id]
    return series.transcription


def get_cac_index_df():
    """Return the Convert-a-Card OCLC to shelfmark index as a dataframe."""
    df = get_cac_annotations()
    df = add_columns(df)
    df = df[df['motivation'] == 'describing']
    reference_df = create_reference_lookup_df(df)

    df = df[df['tag'] == 'control_number']
    df = df.rename(columns={'transcription': 'control_number'})

    df['reference'] = df['task_id'].apply(lookup_reference,
                                          args=(reference_df,))

    return df[['control_number', 'reference']]


@click.command()
def main():
    df = get_cac_index_df()
    write_to_csv(df, 'cac_index.csv')


if __name__ == "__main__":
    main()
