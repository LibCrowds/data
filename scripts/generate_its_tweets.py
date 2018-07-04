#-*- coding: utf8 -*-
"""
Generate #onthisday tweets from In the Spotlight data.
"""
import click
import pandas
import datetime

from generate_its_plays import get_its_plays_df
from helpers import write_to_csv


def filter_incomplete_dates(df):
    """Remove incomplete dates from the dataframe."""
    df = df[df.date.str.contains('\d{4}-\d{2}-\d{2}', na=False)]
    return df


def add_date_parts(df):
    """Add day, month and year columns to the dataframe."""
    df['date'] = pandas.to_datetime(df['date'])
    df['day'] = df['date'].dt.strftime('%d')
    df['month'] = df['date'].dt.strftime('%m')
    df['year'] = df['date'].dt.strftime('%Y')
    return df


def filter_by_today(df):
    """Filter out those rows that are not for today's day and month."""
    ts = datetime.datetime.now()
    day = str(ts.day).zfill(2)
    month = str(ts.month).zfill(2)
    df = df[df['month'] == month]
    df = df[df['day'] == day]
    return df


def get_tweet(row):
    """Return a tweet for the given row."""
    return '#Onthisday, in {0}, {1} was performed at {2} {3}'.format(row['year'], row['title'], row['theatre'], row['link'])


def get_its_tweets_df(include_all=False):
    """Return In the Spotlight tweets in a dataframe."""
    df = get_its_plays_df()
    df = filter_incomplete_dates(df)
    df = add_date_parts(df)

    if not include_all:
        df = filter_by_today(df)

    if df.empty:
        print("There is not enough data to produce #onthisday tweets")
        df['tweet'] = None
    else:
        df['tweet'] = df.apply(lambda row: get_tweet(row), axis=1)

    df.sort_values(['month', 'day'], inplace=True)
    return df[['day', 'month', 'year', 'tweet']]


@click.command()
@click.option('--all', is_flag=True, default=False)
def main(all):
    df = get_its_tweets_df(all)
    write_to_csv(df, 'its_tweets.csv')


if __name__ == "__main__":
    main()
