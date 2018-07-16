# -*- coding: utf-8 -*-
"""
Produce a CSV file containing aggregated data for each performance.
"""
import click
import pandas as pd

from get_annotations import get_annotations_df
from get_pybossa_objects import get_pybossa_df
from helpers import write_to_csv, get_tag, get_transcription, get_source
from helpers import get_task_id, get_volumes_df, CACHE


def fragment_from_task(task_id, task_df):
    """Get fragment selector from a PYBOSSA task."""
    try:
        task = task_df.loc[int(task_id)]
    except KeyError:
        return None
    return task['info']['target']['selector']['value']


def get_df_from_tag(input_df, tag):
    """Return a dataframe containing transcriptions of a given tag."""
    df = input_df[input_df['tag'] == tag]
    df = df.rename(columns={'transcription': tag})
    df = df.drop('tag', axis=1)
    return df


def add_fields(df):
    """Add fields to the dataframe."""
    df['tag'] = df['body'].apply(get_tag)
    df['transcription'] = df['body'].apply(get_transcription)
    df['source'] = df['target'].apply(get_source)
    df['task_id'] = df['generator'].apply(get_task_id)
    return df


def add_volume_metadata(df):
    """Add volume metadata to the dataframe."""
    volume_md_df = get_volumes_df()
    df = df.merge(volume_md_df[['theatre', 'city']], left_on='partOf',
                  right_on='manifest_uri', how='left')
    return df


def merge_genres_df(df, genres_df):
    """Merge genres by matching fragment selectors of related tasks."""
    tasks_df = get_pybossa_df('task')
    genres_df['fragment'] = genres_df['task_id'].apply(fragment_from_task,
                                                       args=(tasks_df,))
    df['fragment'] = df['task_id_title'].apply(fragment_from_task,
                                               args=(tasks_df,))
    df = df.merge(genres_df[['genre', 'source', 'fragment']],
                  on=['source', 'fragment'], how='left')
    return df


def merge_dates_df(df, dates_df):
    """Merge the dates by matching on source."""
    df = df.merge(dates_df[['date', 'source', 'task_id']], on='source',
                  how='left', suffixes=('_title', '_date'))
    return df


def get_task_link(task_id, task_df):
    """Get the link from the PYBOSSA task."""
    try:
        task = task_df.loc[int(task_id)]
    except KeyError:
        return None
    return task['info']['link']


def add_link(df):
    """Add the link from one of the related tasks."""
    tasks_df = get_pybossa_df('task')
    df['link'] = df['task_id_title'].apply(get_task_link, args=(tasks_df,))
    return df


@CACHE.memoize(typed=True, expire=3600, tag='its_performances')
def get_performances_df():
    """Return a dataframe of performances."""
    url = 'https://annotations.libcrowds.com/annotations/playbills-results/'
    df = get_annotations_df(url)
    df = add_fields(df)
    df = df[df['motivation'] == 'describing']

    titles_df = get_df_from_tag(df, 'title')
    dates_df = get_df_from_tag(df, 'date')
    genres_df = get_df_from_tag(df, 'genre')

    df = titles_df
    df = merge_dates_df(df, dates_df)
    df = merge_genres_df(df, genres_df)
    df = add_volume_metadata(df)
    df = add_link(df)
    df = df[['title', 'date', 'genre', 'link', 'theatre', 'city', 'source']]
    df.drop_duplicates(inplace=True)
    return df


@click.command()
def main():
    df = get_performances_df()
    write_to_csv(df, 'data', 'its', 'performances.csv')


if __name__ == "__main__":
    main()
