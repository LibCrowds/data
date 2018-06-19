# Playbills Scripts

> Data management scripts for the In the Spotlight projects on LibCrowds


## Installation

```
pip install -r requirements.txt
```


## Usage

The scripts contained in this repository are described below.


### Download annotations

Download all *In the Spotlight* annotations and load them into a pandas
dataframe. If run as a standalone script, using the command below, the
annotations will be output to a CSV file.

```
python bin/get_annotations.py
```

The CSV file will be saved to `data/annotations.csv`.


### Download PYBOSSA tasks

Download all PYBOSSA tasks and load them into a pandas dataframe. If run as
a standalone script, using the command below, the task data will be output to
a CSV file.

```
python bin/get_tasks.py
```

The CSV file will be saved to `data/tasks.csv`.


### Generate title index

Get the first appearing title on each sheet, followed by "etc." for
multiple titles. Return these as a CSV file mapping the related L-ARKs and
canvas ARKs against each title. This file can be used enhance the structural
metadata in the IIIF manifests, generating an index of titles in the Universal
Viewer.

```
python bin/generate_title_index.py
```

The CSV file will be saved to `data/title_index.csv`.


### Generate MARC template

Using the current results data, generate a CSV file containing a template
to be passed to metadata services for the creation of MARC records.

```
python bin/generate_marc_csv.py
```

The CSV file will be saved to `data/marc.csv`.


### Transcriptions to CSV

Download all Playbills transcription Annotations and output a set of basic
CSV files with values against Annotation IDs for each tag type
(title, genre, date etc.).

```
python bin/transcriptions_to_csv.py
```
