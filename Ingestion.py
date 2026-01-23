# Databricks notebook source
# DBTITLE 1,Standard config
# MAGIC %run ./_Setup_Config

# COMMAND ----------

# DBTITLE 1,Load Raw Trip Data
import requests
import os

# 1. Define the years you want to backfill
years_to_process = [2023, 2024, 2025]

storage_account = "storage_account"
container_name = "nyc-taxi"
folder_name = "raw"

# 2. Loop through each year and month
for year in years_to_process:
    for month in range(1, 13):
        
        # Format month to be two digits (e.g., 1 -> "01")
        month_str = f"{month:02d}"
        
        file_name = f"yellow_tripdata_{year}-{month_str}.parquet"
        download_url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/{file_name}"
        output_path = f"abfss://{container_name}@{storage_account}.dfs.core.windows.net/{folder_name}/trip_data/{file_name}"

        print(f"Checking: {file_name}...")

        try:
            response = requests.get(download_url)
            
            # If the file doesn't exist (e.g., future date), skip it gracefully
            if response.status_code == 404:
                print(f"  -> Not found (Source 404). Skipping.")
                continue

            response.raise_for_status()

            # Save to local Databricks temp storage
            local_path = f"/tmp/{file_name}"
            with open(local_path, "wb") as f:
                f.write(response.content)
            
            # Move from local temp to ADLS
            dbutils.fs.cp(f"file:{local_path}", output_path)
            
            # Clean up local temp file
            os.remove(local_path)
            print(f"  -> Success! Uploaded to ADLS.")

        except requests.exceptions.RequestException as e:
            print(f"  -> Error downloading {file_name}: {e}")

print("Backfill complete!")

# COMMAND ----------

# DBTITLE 1,Load Raw Zone Lookup
import requests

# 1. Define Source and Destination
csv_url = "https://d37ci6vzurychx.cloudfront.net/misc/taxi+_zone_lookup.csv"
file_name = "taxi_zone_lookup.csv"

storage_account = "stportfoliodata01"
container_name = "nyc-taxi"

output_path = f"abfss://{container_name}@{storage_account}.dfs.core.windows.net/raw/zone_lookup/{file_name}"
local_path = f"/tmp/{file_name}"

try:
    # 2. Download to local Temp
    response = requests.get(csv_url)
    response.raise_for_status() # The "Gatekeeper" checks for errors

    with open(local_path, "wb") as f:
        f.write(response.content)

    # 3. Move to Data Lake (Overwrite if exists)
    dbutils.fs.cp(f"file:{local_path}", output_path)
    os.remove(local_path)
except requests.exceptions.RequestException as e:
    print(f"Error downloading file: {e}")