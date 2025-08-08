import sqlite3
import json

DATABASE_NAME = "quiz.db"


def initialize_database():
    # Initializes the SQLite database and creates the necessary tables
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create the 'users' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT UNIQUE
        )
    """)

    # Create the 'questions' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY,
            question TEXT,
            options TEXT,
            answer INTEGER,
            topic TEXT
        )
    """)

    # Create the 'results' table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            score INTEGER,
            percent INTEGER
        )
    """)

    conn.commit()
    conn.close()


def load_questions_from_json(questions_data):
    # Loads questions from a list into the database, clearing old questions first
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Clear existing questions to prevent duplicates on subsequent loads
    cursor.execute("DELETE FROM questions")

    for q in questions_data:
        # Serialize the options list to a JSON string for storage
        options_json = json.dumps(q['options'])
        cursor.execute(
            "INSERT INTO questions (question, options, answer, topic) VALUES (?, ?, ?, ?)",
            (q['question'], options_json, q['answer'], q['topic'])
        )

    conn.commit()
    conn.close()


def get_user_by_username(username):
    # Retrieves a user from the database by their username
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    return user


def insert_user(username):
    # Inserts a new user into the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
    except sqlite3.IntegrityError:
        # User already exists, which is handled in app.py
        pass
    finally:
        conn.close()


def get_all_questions():
    # Fetches all questions from the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT question, options, answer, topic FROM questions")
    questions = []
    for row in cursor.fetchall():
        # Deserialize the options from JSON string back to a list
        question_data = {
            'question': row[0],
            'options': json.loads(row[1]),
            'answer': row[2],
            'topic': row[3]
        }
        questions.append(question_data)
    conn.close()
    return questions


def insert_result(username, score, percent):
    # Inserts a new quiz result into the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO results (username, score, percent) VALUES (?, ?, ?)",
        (username, score, percent)
    )
    conn.commit()
    conn.close()


def get_user_results(username):
    # Fetches all quiz results for a specific user
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT score, percent FROM results WHERE username = ?", (username,))
    results = [{'score': row[0], 'percent': row[1]} for row in cursor.fetchall()]
    conn.close()
    return results


def get_all_results():
    # Fetches all quiz results from the database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM results")
    results = [{'score': row[0]} for row in cursor.fetchall()]
    conn.close()
    return results