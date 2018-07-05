# LibCrowds Data

> Data management scripts for LibCrowds projects.

This repository contains a set of scripts for downloading and manipulating
LibCrowds results data.


## Installation

```
pip install -r requirements.txt
```


## Usage

The scripts contained in this repository are described below.


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
