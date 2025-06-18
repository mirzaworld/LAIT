import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from collections import defaultdict
import re
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK resources if not already available
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    print("Warning: Could not download NLTK resources. Text preprocessing may be limited.")

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """
    Preprocess text data for NLP analysis
    """
    if not isinstance(text, str):
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters
    text = re.sub(r'[^\w\s]', ' ', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords and lemmatize
    tokens = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words]
    
    return ' '.join(tokens)

def extract_invoice_features(invoice_data):
    """
    Extract numerical and categorical features from invoice data
    """
    features = {
        # Numerical features
        'amount': float(invoice_data.get('amount', 0)),
        'hours': float(invoice_data.get('hours', 0)),
        'rate': float(invoice_data.get('rate', 0)),
        'line_item_count': len(invoice_data.get('line_items', [])),
        
        # Timekeeper metrics
        'unique_timekeepers': len(set(item.get('timekeeper', '') for item in invoice_data.get('line_items', []))),
        'partner_hours': sum(float(item.get('hours', 0)) for item in invoice_data.get('line_items', []) 
                            if item.get('timekeeper_title', '').lower().startswith('partner')),
        'associate_hours': sum(float(item.get('hours', 0)) for item in invoice_data.get('line_items', []) 
                              if 'associate' in item.get('timekeeper_title', '').lower()),
        'paralegal_hours': sum(float(item.get('hours', 0)) for item in invoice_data.get('line_items', []) 
                              if 'paralegal' in item.get('timekeeper_title', '').lower()),
    }
    
    # Calculate derived metrics
    if features['hours'] > 0:
        features['partner_ratio'] = features['partner_hours'] / features['hours']
        features['associate_ratio'] = features['associate_hours'] / features['hours'] 
        features['paralegal_ratio'] = features['paralegal_hours'] / features['hours']
    else:
        features['partner_ratio'] = 0
        features['associate_ratio'] = 0
        features['paralegal_ratio'] = 0
    
    # Add categorical features
    categories = {
        'matter_type': invoice_data.get('matter_type', 'unknown'),
        'vendor_type': invoice_data.get('vendor_type', 'unknown'),
        'practice_area': invoice_data.get('practice_area', 'general')
    }
    
    return features, categories

def scale_features(features_df, scaler=None, fit=False):
    """
    Scale numerical features using StandardScaler
    """
    if fit:
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(features_df)
    else:
        scaled_features = scaler.transform(features_df)
        
    return scaled_features, scaler

def encode_categories(categories_df, encoder=None, fit=False):
    """
    One-hot encode categorical features
    """
    if fit:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
        encoded_categories = encoder.fit_transform(categories_df)
    else:
        encoded_categories = encoder.transform(categories_df)
        
    return encoded_categories, encoder

def combine_features(numerical_features, categorical_features):
    """
    Combine numerical and categorical features into a single array
    """
    if categorical_features.size > 0:
        return np.hstack((numerical_features, categorical_features))
    else:
        return numerical_features
