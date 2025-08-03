import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from db import add_user, validate_user, get_user_history, save_analysis_history, get_admin_stats, create_tables
from model_utils import run_model, calculate_percentages  # <-- updated import

app = Flask(__name__)
app.secret_key = 'your-very-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
create_tables()

ALLOWED_EXTENSIONS = {'csv', 'txt', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def scrape_reviews_with_selenium(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Runs Chrome in background
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get(url)

    reviews = driver.find_elements(By.CLASS_NAME, 'review-text-content')

    data = []
    for review in reviews:
        try:
            data.append(review.text.strip())
        except:
            pass

    driver.quit()  # IMPORTANT to release resources

    if not data:
        print("No reviews found.")
        return None

    return pd.DataFrame(data, columns=['review'])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if validate_user(email, password):
            session['username'] = email
            flash('Logged in successfully', 'success')
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        try:
            add_user(email, password)
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except ValueError:
            flash('User already exists', 'danger')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out', 'info')
    return redirect(url_for('home'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    history = get_user_history(session['username'])
    return render_template('dashboard.html', username=session['username'], history=history)

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'username' not in session:
        return redirect(url_for('login'))

    model_choice = request.form.get('model', 'random_forest')  # default fallback
    file = request.files.get('file')
    url = request.form.get('url')

    df = None
    filename = None

    try:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ['csv', 'txt']:
                df = pd.read_csv(filepath)
            elif ext == 'xlsx':
                df = pd.read_excel(filepath)
            else:
                flash('Unsupported file type', 'danger')
                return redirect(url_for('dashboard'))

        elif url:
            df = scrape_reviews_with_selenium(url)
        else:
            flash('Please upload a file or provide a URL.', 'warning')
            return redirect(url_for('dashboard'))

    except Exception as e:
        flash(f"Error processing the data: {str(e)}", 'danger')
        return redirect(url_for('dashboard'))

    if df is None or df.empty:
        flash('No valid review data found.', 'warning')
        return redirect(url_for('dashboard'))

    # <-- Here is the main change: unpack tuple and calculate percentages
    results_list, counts = run_model(df, model_choice)
    percentages = calculate_percentages(counts)

    save_analysis_history(session['username'], filename, url, model_choice, results_list)

    # Pass percentages dict to template
    return render_template('results.html', results=percentages, model=model_choice)

@app.route('/admin')
def admin():
    stats = get_admin_stats()
    return render_template('admin.html', stats=stats)

if __name__ == '__main__':
    app.run(debug=True)
