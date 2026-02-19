import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import pickle
import warnings
warnings.filterwarnings('ignore')

def train_models():
    # Load data
    print("Loading training data...")
    df = pd.read_csv('model/training_data.csv')
    
    # Prepare features
    print("Preparing features...")
    
    # Select relevant columns
    feature_cols = ['Transaction Amount', 'Payment Method', 'Product Category', 
                   'Quantity', 'Customer Age', 'Device Used', 'Account Age Days', 
                   'Transaction Hour', 'Is Fraudulent']
    
    # Create a clean dataset with only needed columns
    clean_df = df[feature_cols].copy()
    
    # Handle categorical variables
    le_payment = LabelEncoder()
    le_category = LabelEncoder()
    le_device = LabelEncoder()
    
    # Encode payment methods
    payment_mapping = {'PayPal': 0, 'credit card': 1, 'debit card': 2, 'bank transfer': 3}
    clean_df['Payment Method'] = clean_df['Payment Method'].map(payment_mapping)
    
    # Encode product categories
    category_mapping = {'electronics': 0, 'toys & games': 1, 'clothing': 2, 
                       'home & garden': 3, 'health & beauty': 4}
    clean_df['Product Category'] = clean_df['Product Category'].map(category_mapping)
    
    # Encode devices
    device_mapping = {'desktop': 0, 'tablet': 1, 'mobile': 2}
    clean_df['Device Used'] = clean_df['Device Used'].map(device_mapping)
    
    # Handle address match (assuming it's in the data)
    if 'Address Match' in df.columns:
        clean_df['Address Match'] = df['Address Match'].map({'No': 0, 'yes': 1, 'Yes': 1})
        clean_df['Address Match'] = clean_df['Address Match'].fillna(0)
    else:
        # Create dummy address match column
        clean_df['Address Match'] = np.random.choice([0, 1], size=len(clean_df))
    
    # Convert fraud labels
    clean_df['Is Fraudulent'] = clean_df['Is Fraudulent'].astype(int)
    
    # Remove any rows with missing values
    clean_df = clean_df.dropna()
    
    print(f"Dataset shape: {clean_df.shape}")
    print(f"Fraud distribution: {clean_df['Is Fraudulent'].value_counts()}")
    
    # Prepare features and target
    X = clean_df.drop('Is Fraudulent', axis=1)
    y = clean_df['Is Fraudulent']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training XGBoost model...")
    # Train XGBoost
    xgb_model = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    xgb_model.fit(X_train, y_train)
    
    print("Training Random Forest model...")
    # Train Random Forest (as stacking alternative)
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    rf_model.fit(X_train, y_train)
    
    # Evaluate models
    xgb_score = xgb_model.score(X_test, y_test)
    rf_score = rf_model.score(X_test, y_test)
    
    print(f"XGBoost accuracy: {xgb_score:.3f}")
    print(f"Random Forest accuracy: {rf_score:.3f}")
    
    # Save models
    print("Saving models...")
    with open('fraud_xg.pkl', 'wb') as f:
        pickle.dump(xgb_model, f)
    
    with open('fraud_stack.pkl', 'wb') as f:
        pickle.dump(rf_model, f)  # Using RF as stacking alternative
    
    print("Models saved successfully!")
    print("XGBoost model: fraud_xg.pkl")
    print("Stacking model: fraud_stack.pkl")

if __name__ == "__main__":
    train_models()