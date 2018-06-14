# -*- coding: utf8 -*-
"""
Produce a CSV file used to enhance structural metadata in the IIIF manifests.
"""
import tqdm
import pandas

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


def run():
    df = get_annotations_df()

    # Add some fields
    df['tag'] = df['body'].apply(get_tag)
    df['transcription'] = df['body'].apply(get_transcription)
    df['lark'] = df['partOf'].apply(get_lark)
    df['source'] = df['target'].apply(get_source)
    df['selector'] = df['target'].apply(get_fragment_selector)

    # Filter title transcriptions
    df = df[df['motivation'] == 'describing']
    df = df[df['tag'] == 'title']

    df['x'], df['y'], df['w'], df['h'] = df['selector'].str.split(pat=',').str

    groups = df.groupby('source', as_index=False)

    out = []
    for source, group_df in tqdm.tqdm(groups, desc='Processing',
                                      unit='annotation'):

        sorted_df = group_df.sort_values(by=['x', 'y'])

        titles = sorted_df['transcription'].tolist()
        lark = sorted_df.iloc[0]['lark']
        title = titles[0]
        if len(titles) > 0:
            title += ', et al'
        out.append({
            'l-ark': lark.split('/iiif/')[-1],
            'canvas-ark': source,
            'title-summary': title
        })

    out_df = pandas.DataFrame(out)
    out_df.to_csv('out.csv', index=False, encoding='utf-8')

if __name__ == "__main__":
    run()
