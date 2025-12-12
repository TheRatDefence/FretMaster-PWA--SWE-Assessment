import sqlite3

from flask import session

from config import DATABASE_PATH
from werkzeug.security import check_password_hash, generate_password_hash
import logging

logger = logging.getLogger(__name__)

def get_db() -> sqlite3.Connection:
    """ Returns an sqlite3 database connection"""
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db



def authenticate_user(username, password) -> sqlite3.Row | None:
    """
    Handles steps 4, 5, 6 of the LOGIN PROCESS:
  4. Query database for user record by username (SQL SELECT)
  5. Verify password using check_password_hash() from werkzeug (compares submitted password with stored hash)
  6. Return result: User object if successful, None/False if failed

    :param username: The target username
    :param password: The target password
    :return: True if credentials match. False otherwise
    """


    # Get the database connection
    db = get_db()

    # Query the database for the user.
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()

    #Check if the user exists
    if user is None:
        logger.debug(f"User '{username}' not found in database")
        return None

    if check_password_hash(user['password_hash'], password):
        logger.info(f"Successfully authenticated user '{username}'")
        return user
    else:
        logger.debug(f"Invalid password for user '{username}'")
        return None

def create_user(username, password, email) -> bool:
    db = get_db()
    cursor = db.cursor()

    # Check if the Username or Email already exists in the database
    if cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone() is not None:
        logger.debug(f"User '{username}' already exists in the database")
        return False

    if cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone() is not None:
        logger.debug(f"Email '{email}' already exists in the database")
        return False

    password_hash = generate_password_hash(password)

    # Insert the new user details
    cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', (username, email, password_hash,))
    db.commit()
    return True


#-------------------Exercise Functions-------------------#

def get_all_exercises() -> list:
    """
    Get all exercises from the database
    :return: List of all exercise rows
    """
    db = get_db()
    return db.execute('SELECT * FROM exercises '
                      'ORDER BY created_at DESC').fetchall()

def get_exercise_by_id(exercise_id: str) -> sqlite3.Row | None:
    """
    Get a single exercise by its ID
    :param exercise_id: The ID of the exercise to fetch
    :return: Exercise row or None if not found
    """
    db = get_db()
    return db.execute('SELECT * FROM exercises '
                      'WHERE id = ?', (exercise_id,)).fetchone()


def get_exercise_with_avg_difficulty(exercise_id) -> sqlite3.Row | None:
    """
    Get a single exercise with its average difficulty rating

    :param exercise_id: The ID of the exercise to fetch
    :return: Exercise row with avg_difficulty, or None if not found
    """
    db = get_db()

    exercise = db.execute(
        'SELECT exercises.*, AVG(practice_sessions.difficulty_rating) AS avg_difficulty '
        'FROM exercises '
        'LEFT JOIN practice_sessions ON exercises.id = practice_sessions.exercise_id '
        'WHERE exercises.id = ? '
        'GROUP BY exercises.id', (exercise_id,)
    ).fetchone()

    return exercise