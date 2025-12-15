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

# Should come back to refactor pre-validation checks in practice sessions and admin crud at some point

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

def get_all_exercises(search_query=None, musical_concept=None) -> list:
    """
    Get all exercises from the database with optional filtering
    :param search_query: Optional text to search in title and description
    :param musical_concept: Optional musical concept to filter by
    :return: List of all exercise rows matching the filters
    """
    db = get_db()
    cursor = db.cursor()

    query = 'SELECT * FROM exercises '
    sql_parameters = []

    if search_query:
        query += 'WHERE (title LIKE ? OR description LIKE ?) '
        sql_parameters.append(f'%{search_query}%')
        sql_parameters.append(f'%{search_query}%')

        if musical_concept:
            query += 'AND musical_concept = ? '
            sql_parameters.append(musical_concept)
    elif musical_concept:
        query += 'WHERE musical_concept = ? '
        sql_parameters.append(musical_concept)

    query += 'ORDER BY created_at DESC'
    return cursor.execute(query, tuple(sql_parameters)).fetchall()

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

#-------------------Admin CRUD Functions-------------------#

def create_exercise(title, description, note_range, musical_concept, svg_diagram_path, created_by) -> bool:
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: No other exercises with the same title exists
    if cursor.execute('SELECT * FROM exercises WHERE title = ?', (title,)).fetchone() is not None:
        logger.debug(f"Exercise with title: '{title}' already exists")
        return False

    # Insert the new exercise
    cursor.execute('INSERT INTO exercises (title, description, note_range, musical_concept, svg_diagram_path, created_by) ' # Missing the svg_diagram_path 
               'VALUES (?, ?, ?, ?, ?, ?)',
               (title, description, note_range, musical_concept, svg_diagram_path, created_by,))

    db.commit()
    return True


def update_exercise(exercise_id, title, description, note_range, musical_concept, svg_diagram_path = None) -> bool:
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: Exercise exists
    if get_exercise_by_id(exercise_id) is None:
        logger.debug(f"Exercise with id: '{exercise_id}' does not exist")
        return False
    # Pre-validation Check 2: No other exercise with this ID has the same Title
    if cursor.execute('SELECT * FROM exercises WHERE title = ? AND id != ?', (title, exercise_id,)).fetchone() is not None:
        logger.debug(f"Exercise with title: '{title}' already exists")
        return False

    # Update the exercise
    if svg_diagram_path:
        cursor.execute('UPDATE exercises '
                       'SET title = ?, description = ?, note_range = ?, musical_concept = ?, svg_diagram_path = ? '
                       'WHERE id = ?',
                       (title, description, note_range, musical_concept, svg_diagram_path, exercise_id))
    else:
        cursor.execute('UPDATE exercises '
                       'SET title = ?, description = ?, note_range = ?, musical_concept = ? '
                       'WHERE id = ?',
                       (title, description, note_range, musical_concept, exercise_id))

    db.commit()
    return True

def delete_exercise(exercise_id) -> bool:
    db = get_db()

    # Pre-validation Check: Exercise exists?
    if get_exercise_by_id(exercise_id) is None:
        logger.debug(f"Exercise with id: '{exercise_id}' does not exist")
        return False

    # Delete the exercise
    db.execute('DELETE FROM exercises WHERE id = ?', (exercise_id,))

    db.commit()
    return True


#-------------------Practice Session Functions-------------------#

def get_session_by_id(session_id) -> sqlite3.Row | None:
    db = get_db()
    return db.execute('SELECT * FROM practice_sessions '
                      'WHERE id = ?', (session_id,)).fetchone()


def get_user_practice_sessions(user_id) -> list:
    db = get_db()

    sessions = db.execute('SELECT * FROM practice_sessions '
                          'WHERE user_id = ? '
                          'ORDER BY practice_date DESC', (user_id,)).fetchall()
    if not sessions:
        logger.debug(f"No practice sessions for user: {user_id} found")
    return sessions

def create_practice_session(user_id, exercise_id, difficulty_rating, session_notes, practice_date) -> bool:
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: exercise_id exists?
    if get_exercise_by_id(exercise_id) is None:
        logger.debug(f"Exercise with id: '{exercise_id}' does not exist")
        return False
    # Pre-validation Check 2: Is difficulty_rating between 1-5?
    if not (1 <= difficulty_rating <= 5):
        logger.debug(f"Difficulty rating of {difficulty_rating} is out of bounds (1 - 5)")
        return False

    cursor.execute('INSERT INTO practice_sessions (user_id, exercise_id, difficulty_rating, session_notes, practice_date)'
               'VALUES (?, ?, ?, ?, ?)', (user_id, exercise_id, difficulty_rating, session_notes, practice_date,))
    db.commit()
    return True


def update_practice_session(session_id, difficulty_rating, session_notes, practice_date) -> bool:
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: Does session_id exist?
    if cursor.execute('SELECT * FROM practice_sessions WHERE id = ?', (session_id,)).fetchone() is None:
        logger.debug(f"Practice session with id: '{session_id}' does not exist")
        return False
    # Pre-validation Check 2: Is difficulty_rating between 1-5?
    if not (1 <= difficulty_rating <= 5):
        logger.debug(f"Difficulty rating of {difficulty_rating} is out of bounds (1 - 5)")
        return False

    cursor.execute('UPDATE practice_sessions '
               'SET difficulty_rating = ?, session_notes = ?, practice_date = ?'
               'WHERE id = ?', (difficulty_rating, session_notes, practice_date, session_id))
    db.commit()
    return True


def delete_practice_session(session_id) -> bool:
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: Does session_id exist?
    if cursor.execute('SELECT * FROM practice_sessions WHERE id = ?', (session_id,)).fetchone() is None:
        logger.debug(f"Practice session with id: '{session_id}' does not exist")
        return False

    cursor.execute('DELETE FROM practice_sessions WHERE id = ?', (session_id,))
    db.commit()
    return True