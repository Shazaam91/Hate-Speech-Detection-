from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask_cors import CORS
from flask import send_file
import pandas as pd
from io import BytesIO
import mysql.connector

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a strong secret key, ideally from an environment variable

# Configure MySQL connection
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Digibrush@123',  # Secure your password; consider using environment variables
    'database': 'hatespeech'
}

# Function to connect to the database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

# Load the hate speech detection model and tokenizer
model = load_model('hate_speech_model.keras')
with open('tokenizer.pkl', 'rb') as file:
    tokenizer = pickle.load(file)

# Prediction function
def predict_hate_speech(texts, model, tokenizer, max_length=50, threshold=0.4):
    sequences = tokenizer.texts_to_sequences(texts)
    padded_sequences = pad_sequences(sequences, maxlen=max_length, padding='post', truncating='post')
    predictions = model.predict(padded_sequences)

    results = []
    for i, prediction in enumerate(predictions):
        label = 'Hate Speech' if prediction > threshold else 'Non-Hate Speech'
        confidence = float(prediction)
        results.append((texts[i], label, confidence))
    return results

@app.route('/')
def home():
    # Redirect to the home page on the initial run
    return render_template('home.html')

@app.route('/index', methods=['GET', 'POST'])
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        text = request.form['text']
        results = predict_hate_speech([text], model, tokenizer)
        result = results[0]

        # Save non-hate speech to the database
        if result[1] == 'Non-Hate Speech':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO non_hate_speech (user_id, text, confidence) VALUES (%s, %s, %s)",
                           (session['user_id'], result[0], result[2]))
            conn.commit()
            cursor.close()
            conn.close()

        print(f"Result: {result}")  # Debug: Print result to console
        return render_template('index.html', text=result[0], label=result[1], confidence=result[2])

    return render_template('index.html', text='', label='', confidence='')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        role = 'user'  # Default role is 'user'

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                           (username, hashed_password, role))
            conn.commit()
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            flash('Username already exists. Please try a different one.', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password'], password) and user['role'] == role:
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['role'] = user['role']
            flash('Login successful!', 'success')

            # Check user role and redirect accordingly
            if session['role'] == 'admin':
                return redirect(url_for('home'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid username, password, or role', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        text = request.form['text']
        results = predict_hate_speech([text], model, tokenizer)
        result = results[0]

        # Save non-hate speech to the database
        if result[1] == 'Non-Hate Speech':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO non_hate_speech (user_id, text, confidence) VALUES (%s, %s, %s)",
                           (session['user_id'], result[0], result[2]))
            conn.commit()
            cursor.close()
            conn.close()

        print(f"Result: {result}")  # Debug: Print result to console
        return render_template('index.html', text=result[0], label=result[1], confidence=result[2])

    return render_template('index.html', text='', label='', confidence='')


@app.route('/manage_entries', methods=['GET'])
def manage_entries():
    if 'user_id' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch entries for admin or particular user
    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM non_hate_speech")
    else:
        cursor.execute("SELECT * FROM non_hate_speech WHERE user_id = %s", (session['user_id'],))

    entries = cursor.fetchall()

    # Fetch feedbacks for admin
    feedbacks = []
    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM feedback")
        feedbacks = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('manage_entries.html', entries=entries, feedbacks=feedbacks)

@app.route('/delete_entry/<int:entry_id>', methods=['GET'])
def delete_entry(entry_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM non_hate_speech WHERE entry_id = %s", (entry_id,))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Entry deleted successfully.', 'success')
    return redirect(url_for('manage_entries'))

@app.route('/download_entries', methods=['GET'])
def download_entries():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM non_hate_speech")
    entries = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convert the entries to a pandas DataFrame
    df = pd.DataFrame(entries)

    # Create a BytesIO object to hold the Excel file in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Non-Hate Speech Entries')

    output.seek(0)
    return send_file(
        output,
        download_name="non_hate_speech_entries.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# Add route to handle feedback submission
@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session or session['role'] != 'user':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    entry_id = request.form['entry_id']
    feedback_text = request.form['feedback_text']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (entry_id, user_id, feedback_text) VALUES (%s, %s, %s)",
                   (entry_id, session['user_id'], feedback_text))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Feedback submitted successfully.', 'success')
    return redirect(url_for('manage_entries'))

# Route for admin to view feedback
@app.route('/view_feedback/<int:entry_id>', methods=['GET'])
def view_feedback(entry_id):
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM feedback WHERE entry_id = %s", (entry_id,))
    feedbacks = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('view_feedback.html', feedbacks=feedbacks)

if __name__ == '__main__':
    app.run(debug=True)
