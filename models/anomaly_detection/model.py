from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dropout, RepeatVector, TimeDistributed, Dense


def build_lstm_autoencoder(input_shape):
    """
    Builds the LSTM Autoencoder model architecture.
    :param input_shape: Tuple of (timesteps, n_features)
    """
    model = Sequential()

    # Encoder
    model.add(LSTM(128, activation='relu', input_shape=input_shape, return_sequences=False))
    model.add(Dropout(rate=0.2))
    model.add(RepeatVector(input_shape))  # Repeats the input n times (timesteps)

    # Decoder
    model.add(LSTM(128, activation='relu', return_sequences=True))
    model.add(Dropout(rate=0.2))
    model.add(TimeDistributed(Dense(input_shape)))

    model.compile(optimizer='adam', loss='mae')
    model.summary()
    return model