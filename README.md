## 🚀 Featured Data Engineering Project

### [NYC Taxi Data Lakehouse (Azure & Databricks)](https://github.com/diogosgrecco/nyc-taxi-etl-pipeline)
**Technologies:** Azure Data Lake Gen2, Databricks (PySpark), Delta Lake, Power BI

An end-to-end ELT pipeline processing millions of records.
* **Ingestion:** Automated file-by-file processing handling schema evolution.
* **Transformation:** Medallion architecture (Bronze/Silver/Gold) with data quality checks.
* **Reporting:** Star Schema modeling for high-performance Power BI dashboards.

[**View the full project code & documentation →**](https://github.com/diogosgrecco/nyc-taxi-etl-pipeline)

# NYC Taxi Data Lakehouse (Azure & Databricks)

## Project Overview
This project implements a scalable End-to-End ETL pipeline for the massive NYC Taxi dataset (2023-2025). Using a **Medallion Architecture** (Bronze, Silver, Gold), it ingests raw Parquet/CSV data, handles complex schema evolution issues, and produces optimized tables for Power BI reporting.

**Architecture:**
Azure Data Lake Gen2 (Storage) ? Azure Databricks (Spark Compute) ? Power BI (Visualization)

## Key Features
* **Robust Ingestion (`Load_Bronze.py`):** Implements a "file-by-file" processing loop to handle schema evolution (e.g., Integer vs. Double data type conflicts) across 3 years of data without pipeline failure.
* **Data Quality (`Transform_Silver.py`):** * Standardizes timestamps to `TIMESTAMP_NTZ` (No Time Zone) for accurate local reporting.
    * Filters invalid records (negative fares, zero distances).
    * Resolves case-sensitivity issues in schema (e.g., `Airport_fee` vs `airport_fee`).
* **Dimensional Modeling (`Reporting_Gold.py`):** * Creates a Star Schema by joining Trip Facts with Zone Dimensions.
    * Optimizes storage with Delta Lake features (Z-Ordering/Partitioning where applicable).

## Project Structure
```text
nyc-taxi-etl-pipeline/
¦
+-- notebooks/
¦   +-- Ingestion.py          # Setup & mounting ADLS Gen2 to Databricks
¦   +-- Load_Bronze.py        # Raw data ingestion & schema unification
¦   +-- Transform_Silver.py   # Data cleaning, filtering & type casting
¦   +-- Reporting_Gold.py     # Aggregations & Star Schema creation
¦
¦── reporting/          <-- CREATE THIS for your .pbix file
¦   +-- nyc_taxi_dashboard.pbix
¦── data_samples/       <-- CREATE THIS (Optional, see warning below)
    +-- dim_taxi_zones.csv
+-- architecture.png          # System design diagram

+-- README.md                 # Project documentation

