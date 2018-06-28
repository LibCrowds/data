#-*- coding: utf8 -*-

import pandas
import datetime

from generate_its_plays import get_its_plays_df
from helpers import write_to_csv


def get_day(date):
    return str(date)[8:]

def get_month(date):
    return str(date)[5:7]

def get_year(date):
    return str(date)[:4]

def run():
  df = get_its_plays_df()
  df['day'] = df['date'].apply(get_day)
  df['month'] = df['date'].apply(get_month)
  df['year'] = df['date'].apply(get_year)

  ts=datetime.datetime.now()
  day = str(ts.day).zfill(2)
  month = str(ts.month).zfill(2)
  df = df[df['month'] == month]
  df = df[df['day'] == '05']

  if df.empty:
      print("We don't have the data for any plays performed on this day")

  out = []
  for index, row in df.iterrows():
      tweet = 'On this day, in {0}, {1} was performed at {2} {3}'.format(row['year'], row['title'], row['theatre'], row['link'])
      row = {
        'tweets for {}'.format(ts): tweet
      }
      out.append(row)

  out_df = pandas.DataFrame(out)
  write_to_csv(out_df, 'its_tweets.csv')

if __name__=="__main__":
  run()
