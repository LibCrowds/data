# Playbills Scripts

> Data management scripts for the In the Spotlight projects on LibCrowds

## Installation

```
pip install -r requirements.txt
```

### Usage

The repository contains the following scripts, all of which will output data
to the /data folder.

## MARC Template transformation

Download all Playbills results data and transform into the format required
for ingest by metadata services.

```
python bin/to_marc_csv.py
```

## Transcriptions to CSV

Download all Playbills transcription Annotations and output a set of basic
CSV files with values against Annotation IDs for each tag type
(title, genre, date etc.).

```
python bin/transcriptions_to_csv.py
```

## Download PYBOSSA tasks into a dataframe

The functions here are used within other scripts in this repository that
require access to all of the PYBOSSA task data. It can also be run as a
standalone script, in which case the tasks will be output to CSV.

```
python bin/get_tasks.py
```

## Generate index of titles for the IIIF manifests

Get the first appearing title on each sheet, followed by "etc." for
multiple titles. Return these as a CSV file mapping the related L-ARKs and
canvas ARKs against each title. This file can be used enhance the structural
metadata in the IIIF manifests, generating an index of titles in the Universal
Viewer.

Run the following command:

```
python bin/generate_title_index.py
```

The CSV file will be saved to `data/title_index.csv`.
