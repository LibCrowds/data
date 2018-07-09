# LibCrowds Data

> Data management scripts for LibCrowds projects.

This repository contains a set of Python scripts for downloading and
manipulating LibCrowds data.

## Installation

Run the following commands to install the required packages.

```bash
# clone
git clone https://github.com/LibCrowds/data

# change directory
cd data

# install
pip install -r requirements.txt
```

## Convert-a-Card

A set of CSV files containing the Convert-a-Card results data can be produced
by running the following command.

```
python scripts/cac.py
```

The following files will be saved to [data/cac](data/cac).

### new.csv

This file contains all results where a minimum of two volunteers have
selected the same WorldCat record and transcribed the same British Library
shelfmark. Entries already ingested (see below) will be excluded from this
file. So, the intention is that this file can be produced and sent off
periodically to metadata services, under work request number WR15.045.

### ingested.csv

After the above file is sent off to metadata services a `.lex` file containing
the records that will be created should be returned. This file will contain
the copies of WorldCat records, such as those seen in
[metadata/convert-a-card](metadata/convert-a-card), modified with the British
Library shelfmark. By storing copies of these files
in this repository we can track the shelfmarks for which records have already
been created. This is how we identify any new records to be created, so it
is important that any `.lex` files returned from metadata services are saved
to [metadata/convert-a-card](metadata/convert-a-card) and the changes
**pushed back to GitHub**.


## In the Spotlight

### Download annotations

Download all annotations for a collection and load them into a pandas
dataframe. This functionality is used as part of the input for various other
scripts in this repository. If run as a standalone script, using the command
below, the annotations will be output to a CSV file.

```
python scripts/get_annotations.py http://annotations.libcrowds.com/annotations/my-collection
```

The CSV file will be saved to `data/annotations.csv`.


### Download PYBOSSA domain objects

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


### Generate In the Spotlight title index

Get the first appearing title on each sheet, followed by "etc." for
multiple titles. Return these as a CSV file mapping the related L-ARKs and
canvas ARKs against each title. This file can be used enhance the structural
metadata in the IIIF manifests, generating an index of titles in the Universal
Viewer.

```
python scripts/generate_its_title_index.py
```

The CSV file will be saved to `data/its_title_index.csv`.


### Generate In the Spotlight MARC template

Generate a CSV file containing In the Spotlight results data to be passed to
Metadata Services for the creation of MARC records.

```
python scripts/generate_its_marc.py
```

The CSV file will be saved to `data/its_marc.csv`.

### Generate In the Spotlight performances dataframe

Generate a CSV file where each row contains the data collected for a specific
performance (e.g. title, date, genre and theatre).

```
python scripts/generate_its_plays.py
```

The CSV file will be saved to `data/its_plays.csv`.

### Generate In the Spotlight Tweets

Generate [#onthisday](https://twitter.com/hashtag/onthisday) tweets based on
In the Spotlight performance data and save to CSV. The following command
will produce a CSV file containing a tweet for each play performed on today's
day and month. Note that the file may be blank if there is no data available
for the given day and month.

```
python scripts/generate_its_tweets.py
```

It is also possible to produce tweets for every day and month by adding the
`--all` argument.

```
python scripts/generate_its_tweets.py --all
```

The CSV file will be saved to `data/its_tweets.csv`.
