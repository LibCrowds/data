#-*- coding: utf8 -*-
"""
Generate Convert-a-Card index of OCLC numbers against shelfmarks.
"""
import re
import csv
import pandas
import click

from get_pybossa_objects import get_pybossa_df
from get_annotations import get_annotations_df
from generate_cac_summary import get_cac_summary_df
from helpers import write_to_csv, get_tag, get_task_id, get_transcription
from helpers import CACHE, normalise_shelfmark


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


def fix_unclosed_brackets(value):
    """Fix unclosed brackets at the end of shelfmarks."""
    s = value
    if re.search(r'\([^\)]*$', s):
        s = '{})'.format(s)
    if re.search(r'\[[^\]]*$', s):
        s = '{}]'.format(s)
    return s


def capitalise_chi(value):
    """CHI at the start of shelfmarks should always be capitalised."""
    return re.sub(r'(?i)^chi\.', 'CHI.', value)


def add_shelfmark_column(df):
    """Add shelfmark column."""
    reference_df = create_reference_lookup_df(df)
    df['shelfmark'] = df['task_id'].apply(lookup_reference,
                                          args=(reference_df,))
    df['shelfmark'] = df['shelfmark'].apply(fix_unclosed_brackets)
    df['shelfmark'] = df['shelfmark'].apply(capitalise_chi)
    return df


def add_created_column(df):
    """Add column to identify if a record has been created for a shelfmark."""
    summary_df = get_cac_summary_df()
    normalised_shelfmarks = summary_df['normalised_shelfmark'].tolist()
    df['norm'] = df['shelfmark'].apply(normalise_shelfmark)
    df['created'] = df['norm'].apply(lambda s: s in normalised_shelfmarks)
    return df


def get_project_name(task_id, tasks_df, projects_df):
    """Return the project name from the task ID."""
    task = tasks_df.loc[int(task_id)]
    project = projects_df.loc[int(task.project_id)]
    return project['name']


def add_project_column(df):
    """Add column for the project title."""
    tasks_df = get_pybossa_df('task')
    projects_df = get_pybossa_df('project')
    df['project'] = df['task_id'].apply(get_project_name,
                                        args=(tasks_df, projects_df))
    return df


# @CACHE.memoize(typed=True, expire=3600, tag='cac_index')
def get_cac_index_df():
    """Return the Convert-a-Card OCLC to shelfmark index as a dataframe."""
    df = get_cac_annotations()
    df = add_columns(df)
    df = df[df['motivation'] == 'describing']
    df = add_shelfmark_column(df)
    df = add_created_column(df)
    df = add_project_column(df)
    df = df[df['tag'] == 'control_number']
    df = df.rename(columns={'transcription': 'control_number'})
    df.drop_duplicates(subset=['shelfmark'], inplace=True)
    df.set_index('task_id', verify_integrity=True, inplace=True)
    df.sort_values('project', inplace=True)
    return df[[
      'control_number',
      'shelfmark',
      'created',
      'project'
    ]]


@click.command()
def main():
    df = get_cac_index_df()
    write_to_csv(df, 'cac_index.csv')


if __name__ == "__main__":
    main()
