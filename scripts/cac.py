#-*- coding: utf8 -*-
"""
Generate Convert-a-Card index of OCLC numbers against shelfmarks.
"""
import os
import re
import csv
import pandas
import click
from pymarc import MARCReader

from get_pybossa_objects import get_pybossa_df
from get_annotations import get_annotations_df
from helpers import write_to_csv, get_tag, get_task_id, get_transcription
from helpers import normalise_shelfmark


def get_marc_file_paths():
    """Return a list of paths to MARC metadata files."""
    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(os.path.dirname(here), 'metadata', 'convert-a-card')
    return [os.path.join(path, fn) for fn in os.listdir(path)]


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


def filter_new_items(df):
    """Return rows where a record has not already been created."""
    ingested_df = get_ingested_df()
    norm_sm = ingested_df['normalised_shelfmark'].tolist()
    df['ingested'] = df['shelfmark'].apply(lambda s: normalise_shelfmark(s) in norm_sm)
    df = df[~df.ingested]
    return df


def get_project_name(task_id, tasks_df, projects_df):
    """Return the project name from the task ID."""
    task = tasks_df.loc[int(task_id)]
    project = projects_df.loc[int(task.project_id)]
    return project['name']


def get_link(task_id, tasks_df):
    """Return the task link from the task ID."""
    task = tasks_df.loc[int(task_id)]
    return task['info']['link']


def add_project_column(df):
    """Add column for the project title."""
    tasks_df = get_pybossa_df('task')
    projects_df = get_pybossa_df('project')
    df['project'] = df['task_id'].apply(get_project_name,
                                        args=(tasks_df, projects_df,))
    return df


def add_link_column(df):
    """Add column for the image link."""
    tasks_df = get_pybossa_df('task')
    df['link'] = df['task_id'].apply(get_link, args=(tasks_df,))
    return df


def get_new_df():
    """Return the Convert-a-Card OCLC to shelfmark index as a dataframe."""
    df = get_cac_annotations()
    df = add_columns(df)
    df = df[df['motivation'] == 'describing']
    df = add_shelfmark_column(df)
    df = filter_new_items(df)
    df = add_project_column(df)
    df = add_link_column(df)
    df = df[df['tag'] == 'control_number']
    df = df.rename(columns={'transcription': 'control_number'})
    df.drop_duplicates(subset=['shelfmark'], inplace=True)
    df.set_index('task_id', verify_integrity=True, inplace=True)
    df.sort_values('project', inplace=True)
    return df[[
      'control_number',
      'shelfmark',
      'project',
      'link'
    ]]


def get_ingested_df():
    """Return a summary of records already created from Convert-a-Card."""
    paths = get_marc_file_paths()
    out = []
    for path in paths:
        with open(path, 'rb') as f:
            reader = MARCReader(f)
            for record in reader:
                out.append({
                    'language': record['008'].data[35:38],
                    'shelfmark': record['852']['j']
                })
    df = pandas.DataFrame(out)
    df['normalised_shelfmark'] = df['shelfmark'].apply(normalise_shelfmark)
    return df


@click.command()
def main():
    new_df = get_new_df()
    write_to_csv(new_df, 'data', 'cac', 'new.csv')

    ingested_df = get_ingested_df()
    write_to_csv(ingested_df, 'data', 'cac', 'ingested.csv')


if __name__ == "__main__":
    main()
