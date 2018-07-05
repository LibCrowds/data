# -*- coding: utf8 -*-
"""
Helper functions.
"""
import re
import os
import errno
import pandas
from diskcache import FanoutCache


CACHE = FanoutCache('../cache')


def mkdirs(path):
    """Make directories if they do not exist."""
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise


def write_to_csv(df, *path_parts):
    """Save a dataframe to CSV."""
    here = os.path.abspath(os.path.dirname(__file__))
    _dir = os.path.join(os.path.dirname(here), *path_parts[:-1])
    fn = path_parts[-1]
    mkdirs(_dir)
    out_path = os.path.join(_dir, fn)
    df.to_csv(out_path, encoding='utf8', index=False)
    print('CSV file saved to {}'.format(out_path))


def get_tag(body):
  """Get the annotation tag from the body."""
  if not isinstance(body, list):
      body = [body]
  try:
      return [b['value'] for b in body if b['purpose'] == 'tagging'][0]
  except IndexError:
      return None


def get_transcription(body):
  """Get the annotation transcription from the body."""
  if not isinstance(body, list):
      body = [body]
  try:
      return [b['value'] for b in body if b['purpose'] == 'describing'][0]
  except IndexError:
      return None


def get_source(target):
    """Get the annotation source (i.e. the canvas URI)."""
    if isinstance(target, dict):
        return target['source']
    return target


def get_task_id(generator):
    """Get the PYBOSSA task ID from the annotation generator."""
    for g in generator:
        if 'api/task' in g['id']:
            return g['id'].split('/')[-1]


def get_volumes_df():
    """Return a dataframe containing metadata for each volume."""
    here = os.path.abspath(os.path.dirname(__file__))
    in_path = os.path.join(os.path.dirname(here), 'metadata',
                           'its_volumes.csv')
    df = pandas.read_csv(in_path)
    df.set_index('manifest_uri', inplace=True, verify_integrity=True)
    return df


def normalise_shelfmark(sm):
    """Normalize shelfmarks."""
    sm = "".join(sm.split())
    sm = re.sub(r',|\.|;|:', r'', sm)
    sm = re.sub(r'\[|\{', r'\(', sm)
    sm = re.sub(r'\]|\}', r'\)', sm)
    sm = sm.replace('_', '-')
    sm = sm.replace('&', ' & ')
    sm = re.sub(r'(\d+)', lambda m: m.group(1).rjust(7, ' '), sm)
    return sm.upper()
