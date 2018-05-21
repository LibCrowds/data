# -*- coding: utf8 -*-

import os
import json
import pandas
import requests
import flatten_json


BASE_IRI = 'https://annotations.libcrowds.com'
CONTAINER_ID = 'playbills-results'


def get_tag(annotation):
    return [body['value'] for body in annotation['body']
            if body['purpose'] == 'tagging'][0]


def get_value(annotation):
    return [body['value'] for body in annotation['body']
            if body['purpose'] == 'describing'][0]


def run():
    iri = '{0}/export/{1}/'.format(BASE_IRI, CONTAINER_ID)
    r = requests.get(iri)

    transcriptions = {}
    for annotation in r.json():
        if annotation['motivation'] != 'describing':
            continue

        tag = get_tag(annotation)
        value = get_value(annotation)
        tag_data = transcriptions.get(tag, [])
        row = dict(id=annotation['id'], tag=tag, value=value)
        tag_data.append(row)
        transcriptions[tag] = tag_data

    for key in transcriptions:
        out_data = transcriptions[key]
        df = pandas.DataFrame(out_data)
        fn = '{0}_{1}.csv'.format(CONTAINER_ID, key)
        out_path = os.path.join(os.path.dirname(__file__), 'data', fn)
        df.to_csv(out_path)


if __name__ == "__main__":
    run()
