# data-operations-it-assets

## Project files
- [index_data.py](index_data.py) — ingestion script that reads the cleaned CSV and bulk-indexes documents.
- [transform_data.py](transform_data.py) — transformation pipeline that reindexes, enriches, and prunes records.
- [it_asset_inventory_cleaned.csv](it_asset_inventory_cleaned.csv) — cleaned source dataset exported from Excel.
- [visualization_screenshots/](visualization_screenshots/) — folder containing screenshots for indexing, transformation, and visualizations.

## Overview of each phase
1. Data preparation (Excel)
   - Clean and normalize the raw IT asset spreadsheet, export to [it_asset_inventory_cleaned.csv](it_asset_inventory_cleaned.csv).
2. Indexing
   - Run [index_data.py](index_data.py) which uses [`CSV_FILE`](index_data.py), [`TARGET_INDEX`](index_data.py) and [`helpers.bulk`](index_data.py) to push documents to Elasticsearch.
3. Transformation
   - Run [transform_data.py](transform_data.py) which reads from [`SOURCE_INDEX`](transform_data.py), reindexes to [`TARGET_INDEX`](transform_data.py), applies [`update_script`](transform_data.py) (derived fields) and uses [`reindex_body`](transform_data.py).
4. Visualization & Analysis
   - Build dashboards / charts from the final index and capture screenshots in [visualization_screenshots/](visualization_screenshots/).

## Excel cleaning techniques used
- Remove empty rows and columns.
- Trim whitespace and standardize casing (lower/upper) for key columns.
- Normalize date formats (YYYY-MM-DD) and split combined fields into columns.
- Deduplicate records using hostname/serial number.
- Use Find & Replace to standardize provider/manufacturer names.
- Data type coercion (dates → date, numeric strings → integers).
- Validation rows and conditional formatting to find anomalies.

Cleaned CSV available: [it_asset_inventory_cleaned.csv](it_asset_inventory_cleaned.csv)

## Python scripts and their purpose
- [index_data.py](index_data.py)
  - Connects to Elasticsearch using [`Elasticsearch`](index_data.py).
  - Loads [`CSV_FILE`](index_data.py) with pandas and prepares `actions` for bulk upload.
  - Calls [`helpers.bulk`](index_data.py) to index documents to [`TARGET_INDEX`](index_data.py).
- [transform_data.py](transform_data.py)
  - Connects to Elasticsearch and validates connection.
  - Deletes/recreates target index, then copies from [`SOURCE_INDEX`](transform_data.py) using [`reindex_body`](transform_data.py).
  - Runs an enrichment Painless script (`[`update_script`](transform_data.py)`) to add `risk_level` and `system_age_years`.
  - Deletes records with unknown hostnames and refreshes the index.

Open the scripts: [index_data.py](index_data.py), [transform_data.py](transform_data.py)

## Screenshots

Embed images in Markdown where needed:
![Indexing success](visualization_screenshots/indexing_success.png)

## Final business insights and learnings
- Risk prioritization: derived `risk_level` helps focus remediation on EOL/EOS systems.
- Asset aging: `system_age_years` highlights legacy systems that may need replacement.
- Data quality matters: standardized provider/name fields and deduplication significantly improved joinability with CMDB and patching tools.
- Operational benefit: automated ingestion + transformation reduces manual effort and speeds up reporting.
- Next steps: add scheduled pipelines, enrich with vulnerability scan data, and build alerting on high-risk devices.

## Quick run commands
- Ingest cleaned CSV:
  ```sh
  python index_data.py
  ```