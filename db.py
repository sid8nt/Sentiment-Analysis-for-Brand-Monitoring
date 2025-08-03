import sqlite3
import os
from datetime import datetime

# Set your database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Create required tables if not exists
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # History table for analysis tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT,
            url TEXT,
            model TEXT,
            result_summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# User functions
def add_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("Username already exists")

    # Insert user
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()

def validate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

# Save analysis history
def save_analysis_history(username, filename, url, model, result_summary):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO analysis_history (username, filename, url, model, result_summary)
        VALUES (?, ?, ?, ?, ?)
    """, (username, filename, url, model, str(result_summary)))
    conn.commit()
    conn.close()

# Fetch user analysis history
def get_user_history(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history WHERE username = ? ORDER BY created_at DESC", (username,))
    history = cursor.fetchall()
    conn.close()
    return history

# Admin statistics (example: count users and total analyses)
def get_admin_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total_users FROM users")
    users_count = cursor.fetchone()["total_users"]

    cursor.execute("SELECT COUNT(*) AS total_analyses FROM analysis_history")
    analyses_count = cursor.fetchone()["total_analyses"]

    conn.close()
    return {
        "total_users": users_count,
        "total_analyses": analyses_count
    }
