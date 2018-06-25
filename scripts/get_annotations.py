# -*- coding: utf8 -*-
"""
Download all annotations for a collection and load into a dataframe.

If run from as a standalone script the dataframe is saved as a CSV.
"""
import sys
import tqdm
import time
import click
import pandas
import requests
import datetime

from helpers import write_to_csv, CACHE


def get_n_annotations(url):
    """Get the number of playbills results annotations on the server."""
    r = requests.get(url)
    r.raise_for_status()
    n_annotations = r.json()['total']
    return n_annotations


def get_annotations(url, page=0):
    """Get a page of annotations."""
    r = requests.get(url, params={
        'page': page
    })
    if r.status_code == 404:
        return None
    else:
        r.raise_for_status()
    return r


@CACHE.memoize(typed=True, expire=3600, tag='annotations')
def get_annotations_df(url):
    """Load all annotations into a dataframe and return."""
    n_anno = get_n_annotations(url)
    progress = tqdm.tqdm(desc='Downloading', total=n_anno, unit='annotation')
    page = 0
    r = get_annotations(url, page)
    last_fetched = r.json()['items']
    data = last_fetched
    progress.update(len(last_fetched))
    respect_rate_limits(r, progress)
    while _not_exhausted(last_fetched):
        page += 1
        r = get_annotations(url, page)
        if not r:  # 404
            break
        last_fetched = r.json()['items']
        data += last_fetched
        progress.update(len(last_fetched))
        respect_rate_limits(r, progress)
    progress.close()
    df = pandas.DataFrame(data)
    return df


def _not_exhausted(last_fetched):
    """Check if the last fetched tasks were the last available."""
    return len(last_fetched) != 0


def respect_rate_limits(response, progress):
    """If we have exceeded the rate limit sleep until it is refreshed."""
    reset = response.headers.get('x-ratelimit-reset')
    remaining = response.headers.get('x-ratelimit-remaining')
    if not reset or not remaining:
        # Rate limiting not implemented at the time of writing
        return

    reset_dt = datetime.datetime.fromtimestamp(float(reset))
    if remaining == 0:
        progress.write('Sleeping until rate limit refreshed, please wait...')
        while reset_dt > datetime.datetime.now():
            time.sleep(1)


@click.command()
@click.argument('url')
def main(url):
    df = get_annotations_df(url)
    write_to_csv(df, 'annotations.csv')


if __name__ == '__main__':
    main()
