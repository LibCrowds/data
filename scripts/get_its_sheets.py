# -*- coding: utf8 -*-
"""
Output results as a row per playbill.
"""
import tqdm
import click
import pandas
import flatten_json

from get_annotations import get_annotations_df
from helpers import write_to_csv, get_tag, get_transcription, get_source
from helpers import get_volumes_df


def add_fields(df):
    """Add fields to the dataframe."""
    df['tag'] = df['body'].apply(get_tag)
    df['transcription'] = df['body'].apply(get_transcription)
    df['source'] = df['target'].apply(get_source)
    return df


def get_sheets_df():
    """Return the all data for each sheet."""
    url = 'https://annotations.libcrowds.com/annotations/playbills-results/'
    df = get_annotations_df(url)
    df = add_fields(df)
    df = df[df['motivation'] == 'describing']
    groups = df.groupby('source', as_index=False)
    vol_md_df = get_volumes_df()
    out_data = []
    for source, group_df in tqdm.tqdm(groups, desc='Processing', unit='item'):
        manifest_uri = group_df['partOf'].tolist()[0]
        group_df = group_df.pivot(columns='tag', values='transcription')
        row = {c: list(set([v for v in group_df[c].tolist()
                            if v and not pandas.isnull(v)]))
               for c in group_df.columns}
        row['id'] = source
        row['sys_no'] = vol_md_df.loc[manifest_uri].to_dict()['system_number']
        flat_row = flatten_json.flatten(row)
        out_data.append(flat_row)
    out_df = pandas.DataFrame(out_data)
    return out_df


@click.command()
def main():
    df = get_sheets_df()
    write_to_csv(df, 'data', 'its', 'sheets.csv')


if __name__ == "__main__":
    main()
