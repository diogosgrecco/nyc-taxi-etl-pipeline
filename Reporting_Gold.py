# Databricks notebook source
# DBTITLE 1,Standard config
# MAGIC %run ./_Setup_Config

# COMMAND ----------

# DBTITLE 1,Create Dim tables
# MAGIC %sql
# MAGIC
# MAGIC USE taxi_db;
# MAGIC -- ==========================================
# MAGIC -- 1. Payment Type Dimension
# MAGIC -- ==========================================
# MAGIC CREATE OR REPLACE TABLE dim_payment_type (payment_type_id INT, payment_desc STRING)
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/gold/dim_payment_type';
# MAGIC
# MAGIC INSERT INTO dim_payment_type VALUES
# MAGIC (1, 'Credit card'),
# MAGIC (2, 'Cash'),
# MAGIC (3, 'No charge'),
# MAGIC (4, 'Dispute'),
# MAGIC (5, 'Unknown'),
# MAGIC (6, 'Voided trip');
# MAGIC
# MAGIC -- ==========================================
# MAGIC -- 2. Rate Code Dimension
# MAGIC -- ==========================================
# MAGIC CREATE OR REPLACE TABLE dim_rate_code (rate_code_id INT, rate_desc STRING)
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/gold/dim_rate_code';
# MAGIC
# MAGIC INSERT INTO dim_rate_code VALUES
# MAGIC (1, 'Standard rate'),
# MAGIC (2, 'JFK'),
# MAGIC (3, 'Newark'),
# MAGIC (4, 'Nassau or Westchester'),
# MAGIC (5, 'Negotiated fare'),
# MAGIC (6, 'Group ride'),
# MAGIC (99, 'Unknown');
# MAGIC
# MAGIC -- ==========================================
# MAGIC -- 3. Taxi Zones Dimension
# MAGIC -- ==========================================
# MAGIC CREATE OR REPLACE VIEW dim_taxi_zones  
# MAGIC AS
# MAGIC SELECT DISTINCT location_key, borough, zone 
# MAGIC FROM silver_taxi_zones;
# MAGIC
# MAGIC -- ==========================================
# MAGIC -- 4. Vendor Dimension
# MAGIC -- ==========================================
# MAGIC CREATE OR REPLACE TABLE dim_vendor (vendor_id INT, vendor_name STRING)
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/gold/dim_vendor';
# MAGIC
# MAGIC INSERT INTO dim_vendor VALUES
# MAGIC (1, 'Creative Mobile Technologies, LLC'),
# MAGIC (2, 'VeriFone Inc');

# COMMAND ----------

# DBTITLE 1,Create Fact tables
# MAGIC %sql
# MAGIC
# MAGIC -- ==========================================
# MAGIC -- 1. Taxi Trips Fact
# MAGIC -- ==========================================
# MAGIC CREATE OR REPLACE TABLE fact_taxi_trips
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/gold/fact_taxi_trips'
# MAGIC TBLPROPERTIES ('delta.feature.timestampNtz' = 'supported')
# MAGIC AS
# MAGIC SELECT vendor_id,
# MAGIC   pickup_datetime,
# MAGIC   dropoff_datetime,
# MAGIC   duration_minutes,
# MAGIC   passenger_count,
# MAGIC   trip_distance,
# MAGIC   rate_code_id,
# MAGIC   store_and_fwd_flag,
# MAGIC   tz.location_key AS pickup_location_key,
# MAGIC   tz2.location_key AS dropoff_location_key,
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
# MAGIC FROM silver_taxi_trips tt
# MAGIC LEFT JOIN silver_taxi_zones tz on tz.location_id=tt.pickup_location_id
# MAGIC LEFT JOIN silver_taxi_zones tz2 on tz2.location_id=tt.dropoff_location_id;
# MAGIC
# MAGIC -- ==========================================
# MAGIC -- 1. Taxi Trips Fact
# MAGIC -- Aggregated - Daily by Vendor
# MAGIC -- ==========================================
# MAGIC CREATE OR REPLACE TABLE fact_taxi_daily_metrics
# MAGIC USING DELTA
# MAGIC LOCATION 'abfss://nyc-taxi@stportfoliodata01.dfs.core.windows.net/gold/fact_taxi_daily_metrics'
# MAGIC AS
# MAGIC SELECT 
# MAGIC   DATE(pickup_datetime) AS trip_date,
# MAGIC   vendor_id,
# MAGIC   COUNT(*) AS total_trips,
# MAGIC   SUM(total_amount) AS total_revenue,
# MAGIC   AVG(duration_minutes) AS avg_duration_minutes,
# MAGIC   AVG(trip_distance) AS avg_trip_distance,
# MAGIC   AVG(fare_amount) AS avg_fare_amount
# MAGIC FROM fact_taxi_trips
# MAGIC GROUP BY DATE(pickup_datetime), vendor_id;