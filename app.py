from flask import Flask, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import pickle
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from flask_cors import CORS
from flask import send_file
import pandas as pd
from io import BytesIO
import re
from collections import Counter
from flask import render_template, request, redirect, url_for
from flask import make_response
import csv
from io import StringIO
from flask import Response
from functools import wraps
import mysql.connector


# Initialize the Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
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

from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Unauthorized access. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated_function


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


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        text = request.form['text']
        results = predict_hate_speech([text], model, tokenizer)
        result = results[0]

        return jsonify({
            'text': result[0],
            'label': result[1],
            'confidence': result[2]
        })

    return render_template('home.html')

@app.route('/analyze_text', methods=['POST'])
def analyze_text():
    # Check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized access. Please log in.'}), 401

    text = request.form['text']
    results = predict_hate_speech([text], model, tokenizer)
    result = results[0]

    response = {
        'text': result[0],
        'label': result[1],
        'confidence': result[2]
    }
    return jsonify(response)

@app.route('/analyze_text_get', methods=['POST'])
@login_required
def analyze_text_get():
    text = request.form['text']
    results = predict_hate_speech([text], model, tokenizer)
    result = results[0]

    response = {
        'text': result[0],
        'label': result[1],
        'confidence': result[2]
    }
    return jsonify(response)


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

    # Get the current page number from request args (default to 1)
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of entries per page
    offset = (page - 1) * per_page

    # Fetch total count for pagination
    if session['role'] == 'admin':
        cursor.execute("SELECT COUNT(*) AS total FROM non_hate_speech")
        total_count = cursor.fetchone()['total']
        cursor.execute("SELECT * FROM non_hate_speech LIMIT %s OFFSET %s", (per_page, offset))
    else:
        cursor.execute("SELECT COUNT(*) AS total FROM non_hate_speech WHERE user_id = %s", (session['user_id'],))
        total_count = cursor.fetchone()['total']
        cursor.execute("SELECT * FROM non_hate_speech WHERE user_id = %s LIMIT %s OFFSET %s", (session['user_id'], per_page, offset))

    entries = cursor.fetchall()

    # Fetch feedbacks for admin
    feedbacks = []
    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM feedback")
        feedbacks = cursor.fetchall()

    cursor.close()
    conn.close()

    # Calculate total pages
    total_pages = (total_count + per_page - 1) // per_page  # Ceiling division

    return render_template('manage_entries.html', entries=entries, feedbacks=feedbacks, page=page, total_pages=total_pages)

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

@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the total number of entries
    cursor.execute("SELECT COUNT(*) AS total_entries FROM non_hate_speech")
    total_entries = cursor.fetchone()['total_entries']

    # Get the total number of feedbacks
    cursor.execute("SELECT COUNT(*) AS total_feedbacks FROM feedback")
    total_feedbacks = cursor.fetchone()['total_feedbacks']

    # Get the most common words from non_hate_speech entries
    cursor.execute("SELECT text FROM non_hate_speech")
    texts = cursor.fetchall()
    all_texts = ' '.join(text['text'] for text in texts)

    # Use pandas to handle text processing
    import pandas as pd
    from collections import Counter
    import re

    # Basic text processing
    words = re.findall(r'\b\w+\b', all_texts.lower())
    word_freq = Counter(words)
    most_common_words = word_freq.most_common(10)

    # Get the most common feedback types
    cursor.execute("SELECT feedback_text, COUNT(*) AS count FROM feedback GROUP BY feedback_text ORDER BY count DESC LIMIT 10")
    feedback_counts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('admin_dashboard.html', total_entries=total_entries,
                           total_feedbacks=total_feedbacks, most_common_words=most_common_words,
                           feedback_counts=feedback_counts)

@app.route('/download_dashboard_report_csv', methods=['GET'])
def download_dashboard_report_csv():
    """Route for downloading the dashboard report as a CSV file."""
    if 'user_id' not in session or session['role'] != 'admin':
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Get the most common words from non_hate_speech entries
    cursor.execute("SELECT text FROM non_hate_speech")
    texts = cursor.fetchall()
    all_texts = ' '.join(text['text'] for text in texts)

    # Basic text processing
    words = re.findall(r'\b\w+\b', all_texts.lower())
    word_freq = Counter(words)
    most_common_words = word_freq.most_common(10)

    # Get the most common feedback types
    cursor.execute("SELECT feedback_text, COUNT(*) AS count FROM feedback GROUP BY feedback_text ORDER BY count DESC LIMIT 10")
    feedback_counts = cursor.fetchall()

    # Get total entries and non-hate speech entries
    cursor.execute("SELECT COUNT(*) AS total_entries FROM non_hate_speech")
    total_entries = cursor.fetchone()['total_entries']

    cursor.execute("SELECT COUNT(*) AS non_hate_speech_entries FROM non_hate_speech")
    non_hate_speech_entries = cursor.fetchone()['non_hate_speech_entries']

    cursor.close()
    conn.close()

    # Convert data to DataFrames
    word_freq_df = pd.DataFrame(most_common_words, columns=['Word', 'Frequency'])
    feedback_counts_df = pd.DataFrame(feedback_counts)
    summary_df = pd.DataFrame({
        'Total Entries': [total_entries],
        'Non-Hate Speech Entries': [non_hate_speech_entries]
    })

    # Concatenate DataFrames into a single DataFrame
    final_df = pd.concat([summary_df, word_freq_df, feedback_counts_df], axis=1)

    # Convert the DataFrame to CSV format
    csv_output = final_df.to_csv(index=False)

    # Prepare the response for downloading
    response = make_response(csv_output)
    response.headers["Content-Disposition"] = "attachment; filename=dashboard_report.csv"
    response.headers["Content-Type"] = "text/csv"

    return response


# Route for downloading manage_entries data as CSV
@app.route('/download_manage_entries_csv', methods=['GET'])
def download_manage_entries_csv():
    if 'user_id' not in session:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch entries based on user role
    if session['role'] == 'admin':
        cursor.execute("SELECT * FROM non_hate_speech")
    else:
        cursor.execute("SELECT * FROM non_hate_speech WHERE user_id = %s", (session['user_id'],))

    entries = cursor.fetchall()
    cursor.close()
    conn.close()

    # Create CSV file in memory
    si = StringIO()
    writer = csv.writer(si)

    # Write header
    if entries:
        writer.writerow(entries[0].keys())  # header row

    # Write data rows
    for entry in entries:
        writer.writerow(entry.values())

    # Prepare response
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=manage_entries.csv"
    output.headers["Content-type"] = "text/csv"

    return output

if __name__ == '__main__':
    app.run(debug=True)