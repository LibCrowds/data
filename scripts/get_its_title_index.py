# -*- coding: utf8 -*-
"""
Produce a JSON file used to enhance structural metadata in the IIIF manifests.
"""
import json
import tqdm
import click
import pandas as pd

from get_annotations import get_annotations_df
from helpers import write_to_csv, get_tag, get_transcription, get_source
from helpers import CACHE


def get_fragment_selector(target):
  """Return the fragmenet selector coordinates."""
  if isinstance(target, dict):
      return target['selector']['value'].lstrip('?xywh=')
  return None


def get_lark(part_of):
    """Return the logical ARK."""
    tmp = part_of.rstrip('/manifest.json')
    return tmp.split('/iiif/')[1]


def add_fields(df):
    """Add fields to the dataframe."""
    df['tag'] = df['body'].apply(get_tag)
    df['transcription'] = df['body'].apply(get_transcription)
    df['lark'] = df['partOf'].apply(get_lark)
    df['source'] = df['target'].apply(get_source)
    df['selector'] = df['target'].apply(get_fragment_selector)
    return df


def filter_title_transcriptions(df):
    """Filter the title transcriptions."""
    df = df[df['motivation'] == 'describing']
    df = df[df['tag'] == 'title']
    return df


def add_fragment_selectors_to_cols(df):
    """Add fragement selector coordinates to columns of the dataframe."""
    df['x'], df['y'], df['w'], df['h'] = df['selector'].str.split(pat=',').str
    df[['x', 'y', 'w', 'h']] = df[['x', 'y', 'w', 'h']].apply(pd.to_numeric)
    return df


@CACHE.memoize(typed=True, expire=3600, tag='its_title_index')
def get_title_index_df():
    """Return title index as a dataframe."""
    url = 'https://annotations.libcrowds.com/annotations/playbills-results/'
    df = get_annotations_df(url)
    df = add_fields(df)
    df = filter_title_transcriptions(df)
    df = add_fragment_selectors_to_cols(df)

    groups = df.groupby('source', as_index=False)

    out = []
    for source, group_df in tqdm.tqdm(groups, desc='Processing',
                                      unit='annotation'):

        sorted_df = group_df.sort_values(by=['y', 'x'], ascending=True)
        titles = sorted_df['transcription'].tolist()
        lark = sorted_df.iloc[0]['lark']
        title = titles[0]
        if len(titles) > 0:
            title += ', etc.'

        row = {
            'l-ark': lark,
            'canvas-ark': source.split('/iiif/')[-1],
            'title-summary': json.dumps(title).strip('"')  # JSON-escape
        }
        out.append(row)

    out_df = pd.DataFrame(out)
    return out_df


@click.command()
def main():
    df = get_title_index_df()
    write_to_csv(df, 'data', 'its', 'title-index.csv')


if __name__ == "__main__":
    main()
