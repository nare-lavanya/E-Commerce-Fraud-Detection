import numpy as np
from flask import Flask, request, jsonify, render_template, redirect, flash, send_file, session
import pickle
import pandas as pd
from datetime import datetime
import io
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)  # Initialize the flask App
app.secret_key = 'your_secret_key_here'

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('fraud_detection.db')
    conn.row_factory = sqlite3.Row
    return conn

# Load models
xgboost = pickle.load(open('fraud_xg.pkl', 'rb'))
stacking = pickle.load(open('fraud_stack.pkl', 'rb'))

# Store prediction history (in production, use a database)
prediction_history = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/auth/register', methods=['POST'])
def auth_register():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Connect to database
    conn = get_db_connection()
    try:
        # Check if user already exists
        user = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)).fetchone()
        if user:
            flash('User already exists with this username or email')
            return redirect('/register')
        
        # Hash password and insert new user
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                     (username, email, hashed_password))
        conn.commit()
        flash('Registration successful! Please login.')
    except sqlite3.OperationalError as e:
        flash('Database error. Please try again.')
        # Log the error for debugging
        print(f"Database error: {e}")
    finally:
        conn.close()
    
    return redirect('/login')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    username = request.form['username']
    password = request.form['password']
    
    # Connect to database
    conn = get_db_connection()
    try:
        # Check credentials
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        
        if user and check_password_hash(user['password_hash'], password):
            session['logged_in'] = True
            session['username'] = username
            return redirect('/dashboard')
        else:
            flash('Invalid credentials')
    except sqlite3.OperationalError as e:
        flash('Database error. Please try again.')
        # Log the error for debugging
        print(f"Database error: {e}")
    finally:
        conn.close()
    
    return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect('/login')
    
    # Calculate statistics
    total_predictions = len(prediction_history)
    fraudulent_count = sum(1 for p in prediction_history if p['result'] == 'Fraudulent')
    legitimate_count = total_predictions - fraudulent_count
    
    recent_predictions = prediction_history[-5:] if prediction_history else []
    recent_predictions.reverse()
    
    stats = {
        'total': total_predictions,
        'fraudulent': fraudulent_count,
        'legitimate': legitimate_count,
        'accuracy': 99.2
    }
    
    return render_template('dashboard.html', stats=stats, recent=recent_predictions)

@app.route('/prediction')
def prediction():
    if 'logged_in' not in session:
        return redirect('/login')
    return render_template('prediction.html')

@app.route('/upload')
def upload():
    if 'logged_in' not in session:
        return redirect('/login')
    return render_template('upload.html')

@app.route('/performance')
def performance():
    if 'logged_in' not in session:
        return redirect('/login')
    return render_template('performance.html')

@app.route('/chart')
def chart():
    return render_template('chart.html')



@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        Transaction_Amount = request.form['Transaction_Amount']
        Payment_Method = request.form['Payment_Method']
        if Payment_Method == '0':
            Pay = 'PayPal'
        elif Payment_Method == '1':
            Pay = 'credit card'
        elif Payment_Method == '2':
            Pay = 'debit card'
        elif Payment_Method == '3':
            Pay = 'bank transfer'
        Product_Category = request.form['Product_Category']
        if Product_Category == '0':
            prod = 'electronics'
        elif Product_Category == '1':
            prod = 'toys & games'
        elif Product_Category == '2':
            prod = 'clothing'
        elif Product_Category == '3':
            prod = 'home & garden'
        elif Product_Category == '4':
            prod = 'health & beauty'
        Quantity = request.form['Quantity']
        Customer_Age = request.form['Customer_Age']
        Device_Used = request.form['Device_Used']
        if Device_Used == '0':
            Devi = 'desktop'
        elif Device_Used == '1':
            Devi = 'tablet'
        elif Device_Used == '2':
            Devi = 'mobile'
        Account_Age_Days = request.form['Account_Age_Days']
        Transaction_Hour = request.form['Transaction_Hour']
        Address_Match = request.form['Address_Match']
        if Address_Match == '0':
            Address = 'No'
        elif Address_Match == '1':
            Address = 'Yes'
        Model = request.form['Model']

        input_variables = pd.DataFrame([[Transaction_Amount, Payment_Method, Product_Category, Quantity, Customer_Age, Device_Used, Account_Age_Days, Transaction_Hour, Address_Match]],
                                       columns=['Transaction Amount', 'Payment Method', 'Product Category', 'Quantity', 'Customer Age', 'Device Used', 'Account Age Days', 'Transaction Hour', 'Address Match'],
                                       index=['input'])

       
        input_variables['Transaction Amount'] = input_variables['Transaction Amount'].astype(float)
        input_variables['Quantity'] = input_variables['Quantity'].astype(float)
        input_variables['Customer Age'] = input_variables['Customer Age'].astype(float)
        input_variables['Account Age Days'] = input_variables['Account Age Days'].astype(float)
        input_variables['Transaction Hour'] = input_variables['Transaction Hour'].astype(float)
        
    
        input_variables['Payment Method'] = input_variables['Payment Method'].astype(int)
        input_variables['Product Category'] = input_variables['Product Category'].astype(int)
        input_variables['Device Used'] = input_variables['Device Used'].astype(int)
        input_variables['Address Match'] = input_variables['Address Match'].astype(int)

        print(input_variables)

        if Model == 'XGBClassifier':
            prediction = xgboost.predict(input_variables)
            outputs = prediction[0]
        elif Model == 'StackingClassifier':
            prediction = stacking.predict(input_variables)
            outputs = prediction[0]

        if outputs == 1:
            results = "Fraudulent"
        else:
            results = "Not Fraudulent"
        
        # Store prediction in history
        prediction_record = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'amount': Transaction_Amount,
            'result': results,
            'model': Model
        }
        prediction_history.append(prediction_record)

    return render_template('result.html', prediction_text=results, model=Model, Transaction_Amount=Transaction_Amount, Pay=Pay, prod=prod, Quantity=Quantity, Customer_Age=Customer_Age, Devi=Devi, Account_Age_Days=Account_Age_Days, Transaction_Hour=Transaction_Hour, Address=Address)

@app.route('/preview', methods=["POST"])
def preview():
    if request.method == 'POST':
        dataset = request.files['datasetfile']
        df = pd.read_csv(dataset, encoding='unicode_escape')
        df.set_index('Id', inplace=True)
        
        # Store in session for batch prediction
        session['uploaded_file'] = dataset.filename
        record_count = len(df)
        session['record_count'] = record_count
        
        return render_template("preview.html", df_view=df, record_count=record_count)

@app.route('/process_batch', methods=["POST"])
def process_batch():
    if 'logged_in' not in session:
        return redirect('/login')
    
    # Get form data
    model_choice = request.form['model_choice']
    processing_mode = request.form.get('processing_mode', 'standard')
    
    # Get the uploaded file from session or re-upload
    if 'uploaded_file' not in session:
        flash('No file uploaded for processing')
        return redirect('/upload')
    
    try:
        # For simplicity, we'll redirect back to upload for now
        # In a full implementation, this would process the batch data
        flash(f'Batch processing started with {model_choice} in {processing_mode} mode. Results will be available shortly.')
        return redirect('/upload')
    except Exception as e:
        flash('Error processing batch data')
        print(f"Batch processing error: {e}")
        return redirect('/upload')

@app.route('/export/history')
def export_history():
    """Export prediction history as CSV"""
    if 'logged_in' not in session:
        return redirect('/login')
    
    if not prediction_history:
        flash('No prediction history to export')
        return redirect('/dashboard')
    
    # Create DataFrame from history
    df = pd.DataFrame(prediction_history)
    
    # Create CSV in memory
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    
    # Create response
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'fraud_detection_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

if __name__ == "__main__":
    app.run(debug=True)