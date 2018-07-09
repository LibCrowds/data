#-*- coding: utf8 -*-
"""
Generate In the Spotlight data.
"""
import click

from get_its_performances import get_performances_df
from get_its_marc import get_marc_df
from get_its_tweets import get_tweets_df
from get_its_title_index import get_title_index_df
from helpers import write_to_csv


@click.command()
def main():
    marc_df = get_marc_df()
    write_to_csv(marc_df, 'data', 'its', 'marc.csv')

    performances_df = get_performances_df()
    write_to_csv(performances_df, 'data', 'its', 'performances.csv')

    title_index_df = get_title_index_df()
    write_to_csv(title_index_df, 'data', 'its', 'title-index.csv')

    tweets_df = get_tweets_df()
    write_to_csv(tweets_df, 'data', 'its', 'tweets.csv')


if __name__ == "__main__":
    main()
