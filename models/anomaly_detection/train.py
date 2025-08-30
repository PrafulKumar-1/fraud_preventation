import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from google.cloud import bigquery, storage
from model import build_lstm_autoencoder
import tensorflow as tf

# --- Configuration ---
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME")
TIME_STEPS = 30  # Use 30 days of historical data to predict the next
FEATURES = ['close', 'volume', 'avg_sentiment_score', 'message_volume']

# Initialize Clients
bq_client = bigquery.Client(project=GCP_PROJECT_ID)
storage_client = storage.Client(project=GCP_PROJECT_ID)


def fetch_training_data():
    """Fetches and fuses market and sentiment data from BigQuery."""
    query = f"""
    WITH market AS (
        SELECT ticker, trade_date, close, volume
        FROM `{GCP_PROJECT_ID}.market_data.daily_prices`
    ),
    sentiment AS (
        SELECT ticker, analysis_date, avg_sentiment_score, message_volume
        FROM `{GCP_PROJECT_ID}.market_intelligence.daily_sentiment_scores`
    )
    SELECT
        m.ticker, m.trade_date, m.close, m.volume,
        s.avg_sentiment_score, s.message_volume
    FROM market m
    JOIN sentiment s ON m.ticker = s.ticker AND m.trade_date = s.analysis_date
    ORDER BY m.ticker, m.trade_date
    """
    return bq_client.query(query).to_dataframe()


def create_sequences(data, time_steps=TIME_STEPS):
    """Creates sequences of data for LSTM model."""
    X = []
    for i in range(len(data) - time_steps):
        X.append(data[i:(i + time_steps)])
    return np.array(X)


def train_model():
    """Main function to fetch data, preprocess, train, and save the model."""
    print("Fetching training data...")
    df = fetch_training_data()

    # For simplicity, we train one model on all data.
    # A more advanced approach would be per-stock or per-sector models.
    df_train = df  # Select only the features for training

    scaler = StandardScaler()
    data_scaled = scaler.fit_transform(df_train)

    print("Creating sequences...")
    X_train = create_sequences(data_scaled)

    if X_train.shape == 0:  # Check if any sequences were created
        print("Not enough data to create sequences. Exiting.")
        return
    print(f"Training data shape: {X_train.shape}")

    print("Building model...")
    model = build_lstm_autoencoder((X_train.shape, X_train.shape))  # Pass (timesteps, n_features)

    print("Training model...")
    # Define callbacks for training
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.2,
            patience=3,
            min_lr=1e-6
        )
    ]

    history = model.fit(
        X_train, X_train,
        epochs=50,
        batch_size=32,
        validation_split=0.1,
        callbacks=callbacks,
        verbose=1
    )

    # Save the trained model to GCS
    model_path = "lstm_autoencoder.h5"
    model.save(model_path)

    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    blob = bucket.blob(f"models/{model_path}")
    blob.upload_from_filename(model_path)

    print(f"Model saved to gs://{GCS_BUCKET_NAME}/models/{model_path}")


if __name__ == "__main__":
    train_model()