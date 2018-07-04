# -*- coding: utf8 -*-
"""
Download all PYBOSSA tasks and load into a dataframe.

If run from as a standalone script the dataframe is saved as a CSV.
"""
import tqdm
import time
import click
import pandas
import requests
import datetime

from helpers import write_to_csv, CACHE


BASE_URL = 'https://backend.libcrowds.com'


def get_objects(obj, offset=0):
    """Get a set of domain objects."""
    r = requests.get(BASE_URL + '/api/{}'.format(obj), params={
        'offset': offset,
        'limit': 100,
        'all': 1
    })
    r.raise_for_status()
    return r


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


@CACHE.memoize(typed=True, expire=3600, tag='pybossa')
def get_pybossa_df(obj):
    """Load all of the chosen domain objects into a dataframe and return."""
    progress = tqdm.tqdm(desc='Downloading', unit=obj)
    r = get_objects(obj)
    last_fetched = r.json()
    data = last_fetched
    progress.update(len(last_fetched))
    respect_rate_limits(r, progress)
    while _not_exhausted(last_fetched):
        r = get_objects(obj, len(data))
        last_fetched = r.json()
        data += last_fetched
        progress.update(len(last_fetched))
        respect_rate_limits(r, progress)
    progress.close()
    df = pandas.DataFrame(data)
    df.set_index('id', inplace=True, verify_integrity=True)
    return df


@click.command()
@click.argument('obj')
def main(obj):
    df = get_pybossa_df(obj)
    write_to_csv(df, '{}.csv'.format(obj))


if __name__ == '__main__':
    main()
