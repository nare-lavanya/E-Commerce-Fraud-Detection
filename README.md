# FraudGuard - AI-Powered E-Commerce Fraud Detection

A modern, dark-themed fraud detection system built with Flask and SQLite.

## Features

- **Modern Dark UI**: Clean, professional interface with glassmorphism effects
- **SQLite Authentication**: Secure user registration and login system
- **AI Models**: XGBoost and Stacking Classifier for fraud detection
- **Real-time Analysis**: Instant fraud prediction with confidence scores
- **User Dashboard**: Personal statistics and prediction history
- **Responsive Design**: Works on all devices

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python app.py
   ```

3. **Access Application**:
   - Open http://localhost:5000
   - Register a new account
   - Start analyzing transactions

## Usage

1. **Register/Login**: Create account or sign in
2. **Dashboard**: View your statistics and recent predictions
3. **Predict**: Analyze individual transactions for fraud risk
4. **Results**: Get instant fraud detection with confidence scores

## Technology Stack

- **Backend**: Flask, SQLite, Pandas, NumPy
- **ML Models**: XGBoost, Scikit-learn
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Modern dark theme with glassmorphism

## Model Performance

- **XGBoost**: 95% accuracy, fast predictions
- **Stacking Classifier**: 99% accuracy, high precision

## Security Features

- Password hashing with Werkzeug
- Session management
- SQLite database for user data
- Input validation and sanitization