# Databricks notebook source
# DBTITLE 1,Standard config
# MAGIC %run ./_Setup_Config

# COMMAND ----------

# DBTITLE 1,Create silver_taxi_trips table
# MAGIC %sql
# MAGIC
# MAGIC USE taxi_db;
# MAGIC
# MAGIC CREATE OR REPLACE TABLE silver_taxi_trips
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/silver/silver_taxi_trips'
# MAGIC TBLPROPERTIES ('delta.feature.timestampNtz' = 'supported')
# MAGIC AS
# MAGIC SELECT 
# MAGIC   VendorID AS vendor_id,
# MAGIC   tpep_pickup_datetime AS pickup_datetime,
# MAGIC   tpep_dropoff_datetime AS dropoff_datetime,
# MAGIC   ROUND(
# MAGIC     (UNIX_TIMESTAMP(tpep_dropoff_datetime) - UNIX_TIMESTAMP(tpep_pickup_datetime)) / 60, 
# MAGIC     2
# MAGIC   ) AS duration_minutes,
# MAGIC   passenger_count,
# MAGIC   trip_distance,
# MAGIC   RatecodeID AS rate_code_id,
# MAGIC   store_and_fwd_flag,
# MAGIC   PULocationID AS pickup_location_id,
# MAGIC   DOLocationID AS dropoff_location_id,
# MAGIC   payment_type,
# MAGIC   fare_amount,
# MAGIC   extra,
# MAGIC   mta_tax,
# MAGIC   tip_amount,
# MAGIC   tolls_amount,
# MAGIC   improvement_surcharge,
# MAGIC   total_amount,
# MAGIC   congestion_surcharge,
# MAGIC   airport_fee
# MAGIC FROM bronze_taxi_trips
# MAGIC WHERE passenger_count > 0 AND trip_distance > 0 AND fare_amount > 0 AND total_amount > 0 AND tpep_pickup_datetime IS NOT NULL AND tpep_dropoff_datetime IS NOT NULL;

# COMMAND ----------

# DBTITLE 1,Create silver_taxi_zones table
# MAGIC %sql
# MAGIC
# MAGIC CREATE OR REPLACE TABLE silver_taxi_zones (
# MAGIC   location_key BIGINT GENERATED ALWAYS AS IDENTITY,
# MAGIC   location_id INT,
# MAGIC   borough STRING,
# MAGIC   zone STRING,
# MAGIC   service_zone STRING
# MAGIC )
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/silver/silver_taxi_zones';
# MAGIC
# MAGIC INSERT INTO silver_taxi_zones (location_id, borough, zone, service_zone)
# MAGIC SELECT 
# MAGIC     LocationID,
# MAGIC     Borough,    
# MAGIC     Zone,
# MAGIC     service_zone
# MAGIC FROM
# MAGIC     bronze_taxi_zones;