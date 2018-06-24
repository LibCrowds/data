# LibCrowds Data

> Data management scripts for LibCrowds projects.


## Installation

```
pip install -r requirements.txt
```


## Usage

The scripts contained in this repository are described below.


### Download annotations

Download all annotations for a collection and load them into a pandas
dataframe. If run as a standalone script, using the command below, the
annotations will be output to a CSV file.

```
python scripts/get_annotations.py
```

The CSV file will be saved to `data/annotations.csv`.


### Download PYBOSSA tasks

Download all PYBOSSA tasks and load them into a pandas dataframe. If run as
a standalone script, using the command below, the task data will be output to
a CSV file.

```
python scripts/get_tasks.py
```

The CSV file will be saved to `data/tasks.csv`.


### Generate In The Spotlight title index

Get the first appearing title on each sheet, followed by "etc." for
multiple titles. Return these as a CSV file mapping the related L-ARKs and
canvas ARKs against each title. This file can be used enhance the structural
metadata in the IIIF manifests, generating an index of titles in the Universal
Viewer.

```
python scripts/generate_its_title_index.py
```

The CSV file will be saved to `data/its_title_index.csv`.


### Generate In The Spotlight MARC template

Generate a CSV file containing In The Spotlight results data to be passed to
Metadata Services for the creation of MARC records.

```
python scripts/generate_its_marc_csv.py
```

The CSV file will be saved to `data/its_marc.csv`.


### Transcriptions to CSV

Download all Playbills transcription Annotations and output a set of basic
CSV files with values against Annotation IDs for each tag type
(title, genre, date etc.).

```
python scripts/transcriptions_to_csv.py
```
