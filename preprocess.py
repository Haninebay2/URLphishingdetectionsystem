from sklearn.preprocessing import LabelEncoder
import numpy as np
import pandas as pd
import pickle

class ExtendedLabelEncoder(LabelEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes_ = None

    def fit(self, y):
        unique_labels = np.unique(y)
        if 'unknown' not in unique_labels:
            unique_labels = np.append(unique_labels, 'unknown')
        super().fit(unique_labels)
        return self

    def transform(self, y):
        new_y = np.array([item if item in self.classes_ else 'unknown' for item in y])
        return super().transform(new_y)

def encode_availability(column):
    """Encode 'Unavailable' as 0 and available as 1."""
    return column.apply(lambda x: 0 if x == 'Unavailable' else 1)

def preprocess_data(df, is_training=False):
    """
    Process the data for training or prediction.
    Args:
        df (DataFrame): The data frame containing URL data.
        is_training (bool): Flag to indicate if the function is used for training.
    Returns:
        DataFrame: The processed DataFrame.
    """
    # Drop unnecessary columns
    df = df.drop(['URL', 'path', 'subdomain'], axis=1)

    # Initialize and fit LabelEncoders if training, else load pre-fitted encoders
    if not is_training:
    # Load pre-trained encoders
        with open('protocol_encoder.pkl', 'rb') as f:
            le_protocol = pickle.load(f)
        with open('domain_encoder.pkl', 'rb') as f:
            le_domain = pickle.load(f)
        with open('suffix_encoder.pkl', 'rb') as f:
            le_suffix = pickle.load(f)

        # Transform data using pre-loaded encoders
        df['protocol'] = le_protocol.transform(df['protocol'])
        df['domain'] = le_domain.transform(df['domain'])
        df['suffix'] = le_suffix.transform(df['suffix'])

        # Optionally save encoders for later use
        with open('protocol_encoder.pkl', 'wb') as f:
            pickle.dump(le_protocol, f)
        with open('domain_encoder.pkl', 'wb') as f:
            pickle.dump(le_domain, f)
        with open('suffix_encoder.pkl', 'wb') as f:
            pickle.dump(le_suffix, f)
        with open('label_encoder.pkl', 'wb') as f:
            pickle.dump(le_label, f)
    else:
        # Load pre-trained encoders
        with open('protocol_encoder.pkl', 'rb') as f:
            le_protocol = pickle.load(f)
        with open('domain_encoder.pkl', 'rb') as f:
            le_domain = pickle.load(f)
        with open('suffix_encoder.pkl', 'rb') as f:
            le_suffix = pickle.load(f)

        # Transform data using pre-loaded encoders
        df['protocol'] = le_protocol.transform(df['protocol'])
        df['domain'] = le_domain.transform(df['domain'])
        df['suffix'] = le_suffix.transform(df['suffix'])

    # Encode availability features
    df['A'] = encode_availability(df['A'])
    df['MX'] = encode_availability(df['MX'])
    df['NS'] = encode_availability(df['NS'])

    # Create a new 'DNS records' column based on the availability of A, MX, or NS
    df['DNS records'] = (df['A'] | df['MX'] | df['NS']).astype(int)

    # Optionally drop the original availability columns if they are no longer needed
    df.drop(['A', 'MX', 'NS'], axis=1, inplace=True)

    return df
