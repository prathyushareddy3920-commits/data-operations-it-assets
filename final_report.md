# Final report — data-operations-it-assets

Project: automated ingestion, transformation, and visualization of IT asset inventory using a cleaned CSV source and Elasticsearch.

## Overview of each phase
- Data preparation (Excel)
  - Clean, normalize, deduplicate, and export the canonical CSV: it_asset_inventory_cleaned.csv.
- Indexing
  - Bulk ingest CSV into Elasticsearch using index_data.py to create the initial index.
- Transformation
  - Reindex, enrich (derived fields), and prune records with transform_data.py to produce the final index used for analysis.
- Visualization & analysis
  - Build dashboards and charts from the final index to support operational decisions and reporting.

## Excel cleaning techniques used
- Remove empty rows/columns and trim whitespace.
- Standardize casing and normalize provider/manufacturer names.
- Normalize date formats (YYYY-MM-DD) and split combined fields.
- Deduplicate using hostname and serial number.
- Convert types (dates → date, numeric strings → integers) and validate anomalies using conditional formatting.

## Python scripts and their purpose
- index_data.py
  - Loads cleaned CSV with pandas, prepares bulk actions, and pushes documents to TARGET_INDEX via helpers.bulk.
- transform_data.py
  - Validates ES connection, deletes/recreates target index, reindexes from SOURCE_INDEX, runs a Painless enrichment script to add derived fields (e.g., risk_level, system_age_years), and removes records with unknown hostnames.

## Screenshots (saved in visualization_screenshots/)
- indexing_success.png — confirmation of successful bulk upload / indexing logs.
- transformation_success.png — sample transformed record and reindex summary.
- visualization_dashboard.png — final dashboard showing key metrics (risk distribution, asset age, vendor breakdown).

Embed examples in reports or README:
![Indexing success](visualization_screenshots/indexing_success.png)
![Transformation success](visualization_screenshots/transformation_success.png)
![Visualization dashboard](visualization_screenshots/visualization_dashboard.png)

## Final business insights and learnings
- Risk prioritization: risk_level enables focus on EOL/EOS and high-risk systems for remediation.
- Asset lifecycle visibility: system_age_years surfaces legacy systems that may need replacement budgeting.
- Data quality impact: standardization and deduplication improved integration with CMDBs and patching tools.
- Operational efficiency: automation reduced manual effort and shortened time-to-reporting.
- Recommended next steps: schedule pipelines, enrich with vulnerability scan data, and add alerting for high-risk devices.

## Quick run commands
- Ingest cleaned CSV:
    python index_data.py
- Transform and enrich index:
    python transform_data.py