"""
Helper functions.
"""
import os
import pandas


def write_to_csv(df, fn):
    """Save a dataframe to CSV."""
    here = os.path.abspath(os.path.dirname(__file__))
    out_path = os.path.join(os.path.dirname(here), 'data', fn)
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
