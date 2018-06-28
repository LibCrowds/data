#-*- coding: utf8 -*-

import csv
import pandas

from get_annotations import get_annotations_df
from helpers import write_to_csv, get_tag, get_task_id, get_transcription


def run():
    url = 'https://annotations.libcrowds.com/annotations/convert-a-card-results/'
    df = get_annotations_df(url)
    df['tag'] = df['body'].apply(get_tag)
    df['task_id'] = df['generator'].apply(get_task_id)
    df['transcription'] = df['body'].apply(get_transcription)
    df = df[df['motivation'] == 'describing']

    groups = df.groupby('task_id')
    out = []

    for task_id, group in groups:
        group.sort_values('tag', inplace=True)
        transcriptions = group['transcription'].tolist()
        row = {
            'reference': transcriptions[0],
            'control_number': transcriptions[1]
        }
        out.append(row)

    out_df = pandas.DataFrame(out)
    write_to_csv(out_df, 'test.csv')


if __name__ == "__main__":
    run ()