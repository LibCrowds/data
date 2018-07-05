# Convert-a-Card

## Workflow


### Generate Convert-a-Card index

Generate the index of OCLC numbers against shelfmarks, required by metadata
services for the creation of new MARC records.

```
python scripts/cac.py
```

The CSV file will be saved to `data/cac_index.csv`.

### Generate Convert-a-Card summary of records ingested

Generate a summary of the MARC records already ingested from the Convert-a-Card
projects. To keep this list up-to-date any MARC files sent back from metadata
services of records created should be added to
[metadata/convert-a-card](metadata/convert-a-card).

```
python scripts/generate_cac_summary.py
```

The CSV file will be saved to `data/cac_summary.csv`.
