# Databricks notebook source
# DBTITLE 1,Standard config
# MAGIC %run ./_Setup_Config

# COMMAND ----------

# DBTITLE 1,Create DB - catalog
# MAGIC %sql
# MAGIC CREATE DATABASE IF NOT EXISTS taxi_db;

# COMMAND ----------

# DBTITLE 1,Create bronze_taxi_trips table
# MAGIC %sql
# MAGIC
# MAGIC USE taxi_db;
# MAGIC
# MAGIC DROP TABLE IF EXISTS bronze_taxi_trips;
# MAGIC
# MAGIC CREATE TABLE bronze_taxi_trips (
# MAGIC   VendorID LONG,
# MAGIC   tpep_pickup_datetime TIMESTAMP_NTZ,
# MAGIC   tpep_dropoff_datetime TIMESTAMP_NTZ,
# MAGIC   passenger_count DOUBLE,
# MAGIC   trip_distance DOUBLE,
# MAGIC   RatecodeID DOUBLE,
# MAGIC   store_and_fwd_flag STRING,
# MAGIC   PULocationID LONG,
# MAGIC   DOLocationID LONG,
# MAGIC   payment_type LONG,
# MAGIC   fare_amount DOUBLE,
# MAGIC   extra DOUBLE,
# MAGIC   mta_tax DOUBLE,
# MAGIC   tip_amount DOUBLE,
# MAGIC   tolls_amount DOUBLE,
# MAGIC   improvement_surcharge DOUBLE,
# MAGIC   total_amount DOUBLE,
# MAGIC   congestion_surcharge DOUBLE,
# MAGIC   airport_fee DOUBLE
# MAGIC )
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/bronze/taxi_trips'
# MAGIC TBLPROPERTIES ('delta.feature.timestampNtz' = 'supported');

# COMMAND ----------

# DBTITLE 1,Load and Standardize NYC Taxi Trip Data for Processing
from pyspark.sql.functions import col, lit

# 1. Configuration
source_path = "abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/raw/trip_data/"
years_to_process = ["2023", "2024", "2025"]

# 2. Get list of ALL files to process
all_files = dbutils.fs.ls(source_path)
files_to_process = []

for file_info in all_files:
    # Filter for the years we want (e.g., yellow_tripdata_2023-01.parquet)
    if any(year in file_info.name for year in years_to_process) and file_info.name.endswith(".parquet"):
        files_to_process.append(file_info.path)

print(f"Found {len(files_to_process)} files total. Starting robust load...")

# 3. Define the Universal Standardization Logic
#    This handles the renaming, the casting, and the case-sensitivity (Airport_fee)
def standardize_schema(df):
    return df.select(
        col("VendorID").cast("long"),
        col("tpep_pickup_datetime").cast("timestamp_ntz"),
        col("tpep_dropoff_datetime").cast("timestamp_ntz"),
        col("passenger_count").cast("double"),
        col("trip_distance").cast("double"),
        col("RatecodeID").cast("double"),
        col("store_and_fwd_flag").cast("string"),
        col("PULocationID").cast("long"),
        col("DOLocationID").cast("long"),
        col("payment_type").cast("long"),
        col("fare_amount").cast("double"),
        col("extra").cast("double"),
        col("mta_tax").cast("double"),
        col("tip_amount").cast("double"),
        col("tolls_amount").cast("double"),
        col("improvement_surcharge").cast("double"),
        col("total_amount").cast("double"),
        col("congestion_surcharge").cast("double"),
        # Check which version of "airport_fee" exists
        (col("Airport_fee") if "Airport_fee" in df.columns else 
         col("airport_fee") if "airport_fee" in df.columns else lit(None).cast("double")).alias("airport_fee")
    )

# 4. The Loop (The "Safety Mechanism")
#    Process one file at a time so Spark never gets confused by conflicting formats.
success_count = 0
for file_path in sorted(files_to_process):
    file_name = file_path.split("/")[-1]
    try:
        # Read raw (Spark infers schema for this single file)
        temp_df = spark.read.parquet(file_path)
        
        # Standardize (Fix types and names)
        clean_df = standardize_schema(temp_df)
        
        # Append to Bronze
        clean_df.write.format("delta").mode("append").saveAsTable("bronze_taxi_trips")
        
        print(f"  [OK] {file_name}")
        success_count += 1
        
    except Exception as e:
        print(f"  [ERROR] {file_name}: {e}")

print(f"Pipeline finished. Successfully loaded {success_count}/{len(files_to_process)} files.")

# COMMAND ----------

# DBTITLE 1,Create bronze_taxi_zones table
# MAGIC %sql
# MAGIC
# MAGIC -- Read CSV using 'read_files' to handle headers correctly
# MAGIC CREATE OR REPLACE TABLE bronze_taxi_zones
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/bronze/taxi_zones'
# MAGIC AS
# MAGIC SELECT * 
# MAGIC FROM read_files(
# MAGIC   'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/raw/zone_lookup/taxi_zone_lookup.csv',
# MAGIC   format => 'csv',
# MAGIC   header => true,
# MAGIC   inferSchema => true
# MAGIC );