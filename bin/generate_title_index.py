# -*- coding: utf8 -*-
"""
Produce a JSON file used to enhance structural metadata in the IIIF manifests.
"""
import json
import tqdm
import pandas as pd

from get_annotations import get_annotations_df


def get_tag(body):
  if not isinstance(body, list):
      body = [body]
  try:
      return [b['value'] for b in body if b['purpose'] == 'tagging'][0]
  except IndexError:
      return None


def get_transcription(body):
  if not isinstance(body, list):
      body = [body]
  try:
      return [b['value'] for b in body if b['purpose'] == 'describing'][0]
  except IndexError:
      return None


def get_source(target):
    if isinstance(target, dict):
        return target['source']
    return target


def get_fragment_selector(target):
  if isinstance(target, dict):
      return target['selector']['value'].lstrip('?xywh=')
  return None


def get_lark(part_of):
    tmp = part_of.rstrip('/manifest.json')
    return tmp.split('/iiif/')[1]


def add_fields(df):
    df['tag'] = df['body'].apply(get_tag)
    df['transcription'] = df['body'].apply(get_transcription)
    df['lark'] = df['partOf'].apply(get_lark)
    df['source'] = df['target'].apply(get_source)
    df['selector'] = df['target'].apply(get_fragment_selector)
    return df


def filter_title_transcriptions(df):
    df = df[df['motivation'] == 'describing']
    df = df[df['tag'] == 'title']
    return df


def add_fragment_selectors_to_cols(df):
    df['x'], df['y'], df['w'], df['h'] = df['selector'].str.split(pat=',').str
    df[['x', 'y', 'w', 'h']] = df[['x', 'y', 'w', 'h']].apply(pd.to_numeric)
    return df


def run():
    df = get_annotations_df()
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
    out_df.to_csv('data/title_index.csv', encoding='utf8', index=False)

if __name__ == "__main__":
    run()
