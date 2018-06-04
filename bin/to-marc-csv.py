# -*- coding: utf8 -*-

import re
import os
import json
import pandas
import requests
import dateutil
from dateutil import parser
from datetime import datetime
from collections import OrderedDict


BASE_IRI = 'https://annotations.libcrowds.com'
CONTAINER_ID = 'playbills-results'


def get_tag(annotation):
    return [body['value'] for body in annotation['body']
            if body['purpose'] == 'tagging'][0]


def get_value(annotation):
    return [body['value'] for body in annotation['body']
            if body['purpose'] == 'describing'][0]


def get_target(annotation):
    if isinstance(annotation['target'], dict):
        return annotation['target']['source']
    return annotation['target']


def get_static_fields():
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


def get_timestamp(dates):
    if len(dates) > 1:
        raise ValueError('Multiple dates found')

    # Skip until we determine how to handle partial dates
    if len(dates[0]) < 10:
        return None

    return dateutil.parser.parse(dates[0], yearfirst=True)


def get_date_fields(ts):
    return {
        'Date/Time of an Event (033 $a)': ts.year + ts.month + ts.day
    }


def get_genre_fields(genres, country, city, ts):
    out = {}
    if not genres:
        return out

    for i, value in enumerate(genres):
        out.update({
            'Topical term or geographic name entry element - {} (650 $a)'.format(i + 1): value,
            'Geographic subdivision - {} (650 $z)'.format(i + 1): country,
            'Geographic subdivision - {} (650 $z)'.format(i + 1): city,
            'Chronological subdivision - {} (650 $y)'.format(i + 1): ts.year
        })
    return out


def get_title_fields(titles, theatre):
    out = {}
    joined = '; '.join(titles)
    out.update({
        'Devised title (245 $a)': '[{0} playbill for {1}]'.format(theatre, joined),
        'Title statement of original (534 $t)': '[Playbill for {0}]'.format(joined)
    })
    for i, value in enumerate(titles):
        out['Other title - {} (246 $a)'.format(i + 1)] = value
    return out


def get_row_out(row_in):
    theatre = 'REPLACE WITH REAL LOCATION'
    country = 'REPLACE WITH REAL PLACE'
    city = 'REPLACE WITH REAL CITY'

    # Only create records where we have this minimum set of info, for now
    if not all(key in row_in for key in ['date', 'title', 'genre']):
        return None

    ts = get_timestamp(row_in['date'])
    if not ts:
        return None

    base = get_static_fields()
    dates = get_date_fields(ts)
    titles = get_title_fields(row_in['title'], theatre)
    genres = get_genre_fields(row_in['genre'], country, city, ts)
    base.update(titles)
    base.update(genres)
    base.update(dates)
    return base


def order(key):
    return re.findall(r'\d{3}', key[0])[0]

def output_data(data):
    out = []
    for key in data:
        row_out = get_row_out(data[key])
        if row_out:
            row_out['Uniform Resource Identifier (856 $u)'] = key
            ordered_row_out = OrderedDict(sorted(row_out.items(), key=order))
            out.append(ordered_row_out)

    df = pandas.DataFrame(out)
    fn = '{}_marc_template.csv'.format(CONTAINER_ID)
    out_path = os.path.join(os.path.dirname(__file__), 'data', fn)
    df.to_csv(out_path, index=False)
    print '{} records exported'.format(len(out))


def run():
    iri = '{0}/export/{1}/'.format(BASE_IRI, CONTAINER_ID)
    r = requests.get(iri)

    data = {}
    for annotation in r.json():
        if annotation['motivation'] != 'describing':
            continue

        target = get_target(annotation)
        tag = get_tag(annotation)
        value = get_value(annotation)

        row = data.get(target, {})
        tag_values = row.get(tag, [])
        tag_values.append(value)
        row[tag] = tag_values
        data[target] = row

    output_data(data)


if __name__ == "__main__":
    run()
