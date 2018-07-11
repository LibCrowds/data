# -*- coding: utf8 -*-
"""
Download PYBOSSA domain objects and load them into a pandas dataframe. This
functionality is used as part of the input for various other scripts in this
repository. If run as a standalone script, using the command below, the task
data will be output to a CSV file. The `<domain_object>` argument appended to
the end of the script should be any valid PYBOSSA domain object, such as
project, task, taskrun or result.

```
python scripts/get_pybossa_objects.py <domain_object>
```

The CSV file will be saved to `data/{domain_object}.csv`.
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
    write_to_csv(df, 'data', '{}.csv'.format(obj))


if __name__ == '__main__':
    main()
