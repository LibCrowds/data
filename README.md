# Playbills Scripts

> Data management scripts for the In the Spotlight projects on LibCrowds

## Installation

```
pip install -r requirements.txt
```

### Usage

The repository contains the following scripts, all of which will output data to
the /data folder.

## MARC Template transformation

Download all Playbills results data and transform into the format required
for ingest by metadata services.

```
python marc-tmpl.py
```

## Transcriptions to CSV

Download all Playbills transcription Annotations and output a set of basic
CSV files with values against Annotation IDs for each tag type
(title, genre, date etc.).

```
python transcriptions-to-csv.py
```
