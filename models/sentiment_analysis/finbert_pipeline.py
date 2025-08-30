import os
from transformers import pipeline
from google.cloud import bigquery
from datetime import datetime, timedelta
import pandas as pd

# --- Configuration ---
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
BQ_SOURCE_DATASET = "social_media_data"
BQ_SOURCE_TABLE = "raw_messages"
BQ_DEST_DATASET = "market_intelligence"
BQ_DEST_TABLE = "daily_sentiment_scores"

# Initialize BigQuery Client
if GCP_PROJECT_ID:
    client = bigquery.Client(project=GCP_PROJECT_ID)
else:
    client = None

# Initialize FinBERT pipeline
# This will download the model on first run (can take a few minutes).
print("Initializing FinBERT model...")
sentiment_pipeline = pipeline("sentiment-analysis", model="ProsusAI/finbert")
print("Model initialized.")


def fetch_recent_messages():
    """Fetches messages from the last 24 hours from BigQuery."""
    if not client:
        print("BigQuery client not available. Returning empty DataFrame.")
        return pd.DataFrame()
        
    yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    query = f"""
        SELECT message_id, ticker, message_text
        FROM `{GCP_PROJECT_ID}.{BQ_SOURCE_DATASET}.{BQ_SOURCE_TABLE}`
        WHERE timestamp >= '{yesterday}'
    """
    print(f"Executing query: {query}")
    try:
        return client.query(query).to_dataframe()
    except Exception as e:
        print(f"Could not fetch data from BigQuery: {e}. Returning empty DataFrame.")
        return pd.DataFrame()

# --- NEW FUNCTION FOR LOCAL TESTING ---
def create_test_dataframe():
    """Creates a small pandas DataFrame for testing the sentiment analysis."""
    print("Creating sample data for testing...")
    data = {
        'message_id': ['1', '2', '3', '4'],
        'ticker': ['RELIANCE.BSE', 'RELIANCE.BSE', 'TCS.BSE', 'TCS.BSE'],
        'message_text': [
            "Reliance is hitting new highs, great quarter ahead!",
            "I am selling my Reliance stock, the market looks weak.",
            "TCS results were stable, nothing exciting.",
            "Bullish on TCS for the long term, amazing company."
        ]
    }
    return pd.DataFrame(data)


def analyze_and_aggregate(df):
    """Analyzes sentiment and aggregates scores per ticker per day."""
    if df.empty:
        print("Input DataFrame is empty. Nothing to analyze.")
        return None

    print("Analyzing sentiment...")
    sentiments = sentiment_pipeline(df['message_text'].tolist())
    df['sentiment_label'] = [s['label'] for s in sentiments]
    df['sentiment_score'] = [s['score'] for s in sentiments]

    def label_to_value(row):
        if row['sentiment_label'] == 'positive':
            return row['sentiment_score']
        elif row['sentiment_label'] == 'negative':
            return -row['sentiment_score']
        return 0.0

    df['numeric_sentiment'] = df.apply(label_to_value, axis=1)

    today_str = datetime.utcnow().strftime('%Y-%m-%d')
    aggregated = df.groupby('ticker').agg(
        avg_sentiment_score=('numeric_sentiment', 'mean'),
        message_volume=('message_id', 'count'),
        positive_ratio=('sentiment_label', lambda x: (x == 'positive').sum() / len(x))
    ).reset_index()

    aggregated['analysis_date'] = today_str
    return aggregated


def load_to_bigquery(df):
    """Loads the aggregated sentiment dataframe to a new BigQuery table."""
    if df is None or df.empty:
        print("No data to load to BigQuery.")
        return
    if not client:
        print("BigQuery client not initialized. Skipping load.")
        return

    table_ref = client.dataset(BQ_DEST_DATASET).table(BQ_DEST_TABLE)
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND",
        schema=[
            bigquery.SchemaField("ticker", "STRING"),
            bigquery.SchemaField("avg_sentiment_score", "FLOAT"),
            bigquery.SchemaField("message_volume", "INTEGER"),
            bigquery.SchemaField("positive_ratio", "FLOAT"),
            bigquery.SchemaField("analysis_date", "DATE")
        ]
    )

    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Loaded {job.output_rows} rows to {BQ_DEST_TABLE}.")


def run_sentiment_pipeline(use_test_data=False):
    """The main entry point for the sentiment analysis job."""
    print("Starting FinBERT sentiment analysis pipeline.")
    
    if use_test_data:
        messages_df = create_test_dataframe()
    else:
        messages_df = fetch_recent_messages()
        
    aggregated_df = analyze_and_aggregate(messages_df)
    
    if aggregated_df is not None:
        print("\n--- Analysis Results ---")
        print(aggregated_df)
        print("----------------------\n")
    
    # We will skip loading to BigQuery when using test data
    if not use_test_data:
        load_to_bigquery(aggregated_df)
        
    print("FinBERT pipeline finished successfully.")


if __name__ == "__main__":
    # This allows running the script locally for testing.
    # We set use_test_data=True to avoid the BigQuery error.
    run_sentiment_pipeline(use_test_data=True)
