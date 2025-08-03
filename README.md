
# Sentiment Analysis for Brand Monitoring


This is a Flask-based web application for analyzing customer sentiment in product reviews. It allows users to upload files or scrape reviews from product URLs, perform sentiment classification using a machine learning model, and view results in a dashboard.

# Features

- Upload `.csv`, `.txt`, or `.xlsx` files containing reviews
- Scrape reviews from product URLs using Selenium
- Sentiment analysis using a trained Random Forest model
- Visual dashboard showing sentiment distribution
- User registration and login system
- Admin panel for viewing system-wide statistics

# Technology Stack

- Python, Flask
- HTML, CSS, Bootstrap (Jinja templates)
- SQLite for data storage
- Scikit-learn for ML
- Selenium and Chrome WebDriver for scraping

# Project Structure


sentiment\_analysis\_for\_brand\_monitoring/
├── app.py
├── db.py
├── model\_utils.py
├── models/
│   ├── random\_forest\_model.pkl
│   └── vectorizer.pkl
├── Templates/
│   ├── dashboard.html
│   ├── admin.html
│   └── login.html, register.html
├── uploads/
├── database.db
├── users.db


# Getting Started

#1. Clone the repository


git clone https://github.com/your-username/sentiment-analysis-brand-monitoring.git
cd sentiment-analysis-brand-monitoring

# 2. Create a virtual environment

python -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate


#3. Install dependencies

pip install -r requirements.txt


### 4. Run the application

python app.py


# 5. Open in browser

http://127.0.0.1:5000/


# Requirements.txt
Flask>=2.2.0
Werkzeug>=2.2.0
pandas>=1.4.0
selenium>=4.1.0
webdriver-manager>=3.5.0

