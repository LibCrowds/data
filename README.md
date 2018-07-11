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

Convert-a-Card results data can be produced by running the following command.

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

In the Spotlight results data can be produced by running the following command.

```
python scripts/its.py
```

The following files will be saved to [data/its](data/its).

### title-index.csv

This file is used to enhance the structural metadata in the IIIF manifests,
which in turn generates an index of titles in the Universal Viewer.
It contains the first appearing title on each sheet, followed by "etc." for
multiple titles, mapped against the related L-ARKs and canvas ARKs against
each title.

### marc.csv

This file is used to generate MARC records from the results data. It should be
passed to metadata services and work request number [TBC].

### sheets.csv

Each row in this file gives all of the data we have for a single sheet,
identified by the IIIF canvas ID in the *id* column. The *sys_no* column
identifies the volume-level record, from which we can identify any information
we already have about location etc. We then have our crowdsourced data
against keys in the form *entity_n* (e.g. *title_0*, *title_1*, *date_0*).

### performances.csv

Each row in this file contains all known data for a specific performance
(e.g. title, date, genre and theatre).

### tweets.csv

This file contains [#onthisday](https://twitter.com/hashtag/onthisday) tweets
based on all known performance data. Tweets are produced for every day and
month of the year.
