# -*- coding: utf8 -*-
"""
Output all current results data to a CSV template for MARC ingest.
"""
import click
import pandas
import dateutil
from dateutil import parser
from datetime import datetime
from collections import OrderedDict

from get_tasks import get_tasks_df
from get_annotations import get_annotations_df
from helpers import write_to_csv, get_tag, get_transcription, get_source
from helpers import get_volumes_df, CACHE


def get_static_fields():
    """Return the static data."""
    return {
        'Aleph system number (001)': '',  # Will become a lookup after initial ingest
        'Country (008/15-17)': 'enk',
        'Form of item (008/23)': 's',
        'Language (008/35-37)': 'eng',
        'Place of manufacture (264 $a)': '[London]',
        'Manufacturer (264 $b)': '[British Library]',
        'Date of manufacture (264 $c)': '[{}]'.format(datetime.now().year),
        'Extent (300 $a)': '1 online resource',
        'Content type term (336 $a)': 'text',
        'Source (336 $2)': 'rdacontent',
        'Media type term (337 $a)': 'computer',
        'Source (337 $2)': 'rdamedia',
        'Carrier type term (338 $a)': 'online resource',
        'Source (338 $2)': 'rdacarrier',
        'Corporate name or jurisdiction name as entry element (710 $a)': 'British Library Playbills Project',
        'Relator term (710 $e)': 'manufacturer',
        'Link text (856 $y)': 'digitised sheet'
    }


def get_transcriptions_by_tag(group_df, tag):
    """Return transcriptions for a given tag."""
    transcriptions_df = group_df[group_df['motivation'] == 'describing']
    transcriptions_df = transcriptions_df[transcriptions_df['tag'] == tag]
    return transcriptions_df['transcription'].tolist()


def get_performance_timestamp(group_df):
    """Return the timestamp of the performance."""
    transcriptions = get_transcriptions_by_tag(group_df, 'date')
    if not transcriptions:
        return None

    # We should only have one date for each sheet
    elif len(transcriptions) > 1:
        raise ValueError('Multiple dates found')

    # Skip until we determine how to handle partial dates
    elif len(transcriptions[0]) < 10:
        return None

    ts = dateutil.parser.parse(transcriptions[0], yearfirst=True)
    return ts


def get_title_fields(group_df, volume_metadata):
    """Return the title data."""
    theatre = volume_metadata['theatre']
    transcriptions = get_transcriptions_by_tag(group_df, 'title')
    if not transcriptions:
        return {}

    joined_titles = u'; '.join(transcriptions)
    out = {
        'Devised title (245 $a)': u'[{0} playbill for {1}]'.format(theatre, joined_titles),
        'Title statement of original (534 $t)': u'[Playbill for {0}]'.format(joined_titles)
    }

    for i, value in enumerate(transcriptions):
        out['Other title - {} (246 $a)'.format(i + 1)] = value

    return out


def get_date_fields(group_df):
    """Return the date data."""
    ts = get_performance_timestamp(group_df)
    if not ts:
        return {}

    return {
        'Date/Time of an Event (033 $a)': ts.year + ts.month + ts.day
    }


def get_genre_fields(group_df, volume_md):
    """Return the genre data."""
    country = volume_md['country']
    city = volume_md['city']
    transcriptions = get_transcriptions_by_tag(group_df, 'genre')
    if not transcriptions:
        return {}

    ts = get_performance_timestamp(group_df)
    out = {}
    for i, value in enumerate(transcriptions):
        out.update({
            'Topical term or geographic name entry element - {} (650 $a)'.format(i + 1): value,
            'Geographic subdivision - {} (650 $z)'.format(i + 1): country,
            'Geographic subdivision - {} (650 $z)'.format(i + 1): city
        })

        if ts:
            out['Chronological subdivision - {} (650 $y)'.format(i + 1)] = ts.year
    return out


def add_fields(df):
    """Add fields to the dataframe."""
    df['tag'] = df['body'].apply(get_tag)
    df['transcription'] = df['body'].apply(get_transcription)
    df['source'] = df['target'].apply(get_source)
    return df


@CACHE.memoize(typed=True, expire=3600, tag='its_marc')
def get_marc_df():
    """Return the MARC template dataframe."""
    url = 'https://annotations.libcrowds.com/annotations/playbills-results/'
    df = get_annotations_df(url)
    df = add_fields(df)

    df = df[df['motivation'] == 'describing']
    grouped = df.groupby('source', as_index=False)
    volume_md_df = get_volumes_df()

    out_data = []
    for source, group_df in grouped:

        # Get volume metadata
        manifest_uri = group_df['partOf'].tolist()[0]
        volume_md = volume_md_df.loc[manifest_uri].to_dict()

        date_fields = get_date_fields(group_df)
        title_fields = get_title_fields(group_df, volume_md)
        genre_fields = get_genre_fields(group_df, volume_md)

        # Skip rows without titles or dates for now
        if not all(bool(d) for d in [title_fields, date_fields]):
            continue

        row = get_static_fields()
        row.update(title_fields)
        row.update(date_fields)
        row.update(genre_fields)
        out_data.append(row)

    out_df = pandas.DataFrame(out_data)
    return out_df


@click.command()
def main():
    df = get_marc_df()
    write_to_csv(df, 'its_marc.csv')


if __name__ == "__main__":
    main()
