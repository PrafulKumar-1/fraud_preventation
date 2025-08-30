import os
import json
import requests
from google.cloud import bigquery
import functions_framework
from datetime import datetime, timedelta

# --- Configuration ---
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BQ_DATASET_ID = "market_data"
BQ_TABLE_ID = "daily_prices"

# List of stock tickers to monitor (NSE format).
# In a real system, this would be managed dynamically.
# Added example tickers for testing.
TARGET_TICKERS = ["RELIANCE.BSE", "TCS.BSE"]

# Initialize BigQuery Client
if GCP_PROJECT_ID:
    client = bigquery.Client(project=GCP_PROJECT_ID)
else:
    client = None

def fetch_daily_data(symbol):
    """Fetches end-of-day stock data from Alpha Vantage."""
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}&outputsize=compact"
    try:
        response = requests.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        # Get the latest trading day's data
        time_series = data.get("Time Series (Daily)")
        if not time_series:
            print(f"No time series data found for {symbol}. Response: {data}")
            return None
            
        latest_date_str = sorted(time_series.keys(), reverse=True)[0]
        latest_data = time_series[latest_date_str]
        
        return {
            "ticker": symbol,
            "trade_date": latest_date_str,
            "open": float(latest_data["1. open"]),
            "high": float(latest_data["2. high"]),
            "low": float(latest_data["3. low"]),
            "close": float(latest_data["4. close"]),
            "volume": int(latest_data["5. volume"]),
            "fetched_at": datetime.utcnow().isoformat()
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
    except (KeyError, IndexError, TypeError) as e:
        print(f"Error parsing data for {symbol}: {e}. Response: {data}")
        return None

def load_to_bigquery(rows_to_insert):
    """Loads a list of dictionary rows into the specified BigQuery table."""
    if not rows_to_insert:
        print("No rows to insert into BigQuery.")
        return

    if not client:
        print("BigQuery client not initialized. Skipping load.")
        return

    table_ref = client.dataset(BQ_DATASET_ID).table(BQ_TABLE_ID)
    
    # Define table schema if it doesn't exist
    schema = [
        bigquery.SchemaField("ticker", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("trade_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("open", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("high", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("low", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("close", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("volume", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("fetched_at", "TIMESTAMP", mode="NULLABLE"),
    ]
    
    try:
        table = bigquery.Table(table_ref, schema=schema)
        table = client.create_table(table, exists_ok=True)
        print(f"Ensured table {table.project}.{table.dataset_id}.{table.table_id} exists.")
    except Exception as e:
        print(f"Error creating/getting table: {e}")
        return

    errors = client.insert_rows_json(table, rows_to_insert)
    if not errors:
        print(f"Successfully inserted {len(rows_to_insert)} rows into BigQuery.")
    else:
        print(f"Encountered errors while inserting rows: {errors}")

def run_fetcher_logic():
    """Contains the core logic for fetching and loading data."""
    print("Starting market data fetcher.")
    
    all_data = []
    for ticker in TARGET_TICKERS:
        print(f"Fetching data for {ticker}...")
        daily_data = fetch_daily_data(ticker)
        if daily_data:
            all_data.append(daily_data)
    
    load_to_bigquery(all_data)
    
    print("Market data fetcher finished.")

@functions_framework.http
def main_market_data_fetcher(request):
    """
    Main function triggered by HTTP request, for cloud deployment.
    """
    run_fetcher_logic()
    return "Market data fetching process completed.", 200

# --- For local testing ---
if __name__ == "__main__":
    # Check that environment variables are set before running
    if not ALPHA_VANTAGE_API_KEY or not GCP_PROJECT_ID:
        print("Error: Make sure ALPHA_VANTAGE_API_KEY and GCP_PROJECT_ID environment variables are set.")
    else:
        run_fetcher_logic()