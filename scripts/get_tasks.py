# -*- coding: utf8 -*-
"""
Download all PYBOSSA tasks and load into a dataframe.

If run from as a standalone script the dataframe is saved as a CSV.
"""
import tqdm
import time
import pandas
import requests
import datetime
from diskcache import FanoutCache

from helpers import write_to_csv


CACHE = FanoutCache('../cache')
BASE_URL = 'https://backend.libcrowds.com'


def get_n_tasks():
    """Get the number of tasks on the server."""
    r = requests.get(BASE_URL + '/stats/', headers={
      'content-type': 'application/json'
    })
    r.raise_for_status()
    n_tasks = r.json()['stats']['n_tasks']
    return n_tasks


def get_tasks(offset=0):
    """Get a set of domain objects."""
    r = requests.get(BASE_URL + '/api/task', params={
        'offset': offset,
        'limit': 100,
        'all': 1
    })
    r.raise_for_status()
    return r


@CACHE.memoize(typed=True, expire=3600, tag='tasks')
def get_tasks_df():
    """Load all of the chosen domain objects into a dataframe and return."""
    n_tasks = get_n_tasks()
    progress = tqdm.tqdm(desc='Downloading', total=n_tasks, unit='tasks')
    r = get_tasks()
    last_fetched = r.json()
    data = last_fetched
    progress.update(len(last_fetched))
    respect_rate_limits(r, progress)
    while _not_exhausted(last_fetched):
        r = get_tasks(len(data))
        last_fetched = r.json()
        data += last_fetched
        progress.update(len(last_fetched))
        respect_rate_limits(r, progress)
    progress.close()
    df = pandas.DataFrame(data)
    return df


def _not_exhausted(last_fetched):
    """Check if the last fetched tasks were the last available."""
    return len(last_fetched) == 100


def respect_rate_limits(response, progress):
    """If we have exceeded the rate limit sleep until it is refreshed."""
    reset = response.headers['x-ratelimit-reset']
    reset_dt = datetime.datetime.fromtimestamp(float(reset))
    remaining = response.headers['x-ratelimit-remaining']
    if remaining == 0:
        progress.write('Sleeping until rate limit refreshed, please wait...')
        while reset_dt > datetime.datetime.now():
            time.sleep(1)


if __name__ == '__main__':
    df = get_tasks_df()
    write_to_csv(df, 'tasks.csv')
