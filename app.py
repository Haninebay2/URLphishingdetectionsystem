import pandas as pd
import pickle
import tldextract
import socket
from urllib.parse import urlparse
import logging
from preprocess import ExtendedLabelEncoder, preprocess_data
import pandas as pd
import tldextract
import socket
from urllib.parse import urlparse
from sklearn.preprocessing import LabelEncoder
from sklearn.base import BaseEstimator, TransformerMixin

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load LabelEncoders
with open('protocol_encoder.pkl', 'rb') as f:
    le_protocol = pickle.load(f)
with open('domain_encoder.pkl', 'rb') as f:
    le_domain = pickle.load(f)
with open('suffix_encoder.pkl', 'rb') as f:
    le_suffix = pickle.load(f)

# Load models
models = {
    'SVM': pickle.load(open('svm_model (1).pkl', 'rb')),
    'RF': pickle.load(open('rf_model (1).pkl', 'rb')),
    'LR': pickle.load(open('Lr_model (1).pkl', 'rb'))
}


class SafeLabelEncoder(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.encoder = LabelEncoder()
        self.classes_ = None

    def fit(self, X, y=None):
        self.encoder.fit(X)
        self.classes_ = set(self.encoder.classes_)
        return self

    def transform(self, X, y=None):
        if X is None or X not in self.classes_:
            return self.unknown_class_
        else:
            return self.encoder.transform([X])[0]

def contains_ip(url):
    if '://' not in url:
        url = 'http://' + url
    try:
        hostname = urlparse(url).hostname
        if hostname:
            ip_address = socket.gethostbyname(hostname)
            return True
    except socket.gaierror:
        pass
    return False

import dns.resolver

def has_dns_server(domain):
    record_types = ['A', 'MX', 'NS']
    for record_type in record_types:
        try:
            result = dns.resolver.resolve(domain, record_type)
            if result:
                return True
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            continue
    return False


def url_to_features(url, protocol_encoder, domain_encoder, suffix_encoder):
    url_extract = tldextract.extract(url)
    features = {
        'length': len(url),
       'protocol': url.split('://')[0] if '://' in url else 'http',
        'domain': url_extract.domain if url_extract.domain else 'unknown',
        'suffix': url_extract.suffix.split('.')[0] if url_extract.suffix and url_extract.suffix.split('.')[0] in ['com', 'edu', 'gov', 'org', 'net'] else 'unknown',
        'number_of_subdomains': len(url_extract.subdomain.split('.')) if url_extract.subdomain else 0,
        'has_ip_address': contains_ip(url),
        'is_https': 1 if url.startswith('https') else 0,
        'special_char_count': sum(not c.isalnum() for c in url),
        'has_suspicious_word': 1 if any(word in url for word in ['login', 'verify', 'account', 'secure', 'update', 'banking']) else 0,
        'is_suspicious_tld': 1 if url_extract.suffix in ['xyz', 'info', 'top', 'gq', 'cf', 'tk', 'ml', 'ga', 'men', 'loan', 'date', 'win', 'faith', 'review', 'party', 'webcam', 'trade', 'accountant', 'download', 'racing', 'science', 'cricket', 'bid'] else 0,
        'DNS records': has_dns_server(url_extract.domain)
    }
    features_df = pd.DataFrame([features])
    features_df['protocol'] = protocol_encoder.transform(features_df['protocol'])
    features_df['domain'] = domain_encoder.transform(features_df['domain'])
    features_df['suffix'] = suffix_encoder.transform(features_df['suffix'])
    return features_df

def predict_url(url, model, protocol_encoder, domain_encoder, suffix_encoder):
    try:
        features_df = url_to_features(url, protocol_encoder, domain_encoder, suffix_encoder)
    except ValueError:
        url_extract = tldextract.extract(url)  # Catch the error when the encoder encounters an unseen label
        if has_dns_server(url_extract.domain):
            return "Real"
        else:
            return "Phishing"  # Treat unseen labels as 'phishing'
    # Additional model prediction logic if needed
    predicted_label = model.predict(features_df)
    if predicted_label == [1]:
        return "Real"
    else:
        return "Phishing"# Or use your model to make further predictions if necessary

# # Fit the encoders appropriately with training data

# sample_url = "https://www.lau.edu.lb"
# predicted_label = predict_url(sample_url,'RF', le_protocol, le_domain, le_suffix)

# print(f"Predicted label for URL '{sample_url}': {predicted_label}" )
# print()
# print(url_to_features(sample_url, le_protocol, le_domain, le_suffix))
