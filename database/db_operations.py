"""
Database Operations Module
Handles all database interactions for FretMaster PWA including user authentication,
exercise management, and practice session tracking using SQLite.
"""

#-------------------Imports-------------------#

import sqlite3
from typing import List
import logging

from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

from config import DATABASE_PATH

#-------------------Logging-------------------#

# Get logger instance
logger = logging.getLogger(__name__)

#-------------------Database Connection-------------------#

def get_db() -> sqlite3.Connection:
    """
    Establishes a connection to the SQLite database.
    Configures the connection to return rows as dictionary-like objects.
    :return: An sqlite3.Connection object.
    """
    # Connect to the database file specified in the config
    db = sqlite3.connect(DATABASE_PATH)
    # Set the row factory to sqlite3.Row to access columns by name
    db.row_factory = sqlite3.Row
    # Return the connection object
    return db

#-------------------User Authentication Functions-------------------#

def authenticate_user(username: str, password: str) -> sqlite3.Row | None:
    """
    Authenticates a user by checking their username and password against the database.
    :param username: The username to authenticate.
    :param password: The password to check.
    :return: The user row object if authentication is successful, otherwise None.
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

    # Verify the provided password against the stored hash
    if check_password_hash(user['password_hash'], password):
        logger.info(f"Successfully authenticated user '{username}'")
        return user
    else:
        logger.debug(f"Invalid password for user '{username}'")
        return None

def create_user(username: str, password: str, email: str) -> bool:
    """
    Creates a new user in the database.
    :param username: The desired username.
    :param password: The desired password.
    :param email: The user's email address.
    :return: True if the user was created successfully, False otherwise.
    """
    # Get the database connection
    db = get_db()
    cursor = db.cursor()

    # Check if the Username or Email already exists in the database
    if cursor.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone() is not None:
        logger.debug(f"User '{username}' already exists in the database")
        return False

    if cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone() is not None:
        logger.debug(f"Email '{email}' already exists in the database")
        return False

    # Hash the password for secure storage
    password_hash = generate_password_hash(password)

    # Insert the new user details
    cursor.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)', (username, email, password_hash,))
    db.commit()
    return True


#-------------------Exercise Functions-------------------#

def get_all_exercises(search_query: str | None = None, musical_concept: str | None = None) -> List[sqlite3.Row]:
    """
    Get all exercises from the database with optional filtering.
    :param search_query: Optional text to search in title and description.
    :param musical_concept: Optional musical concept to filter by.
    :return: List of all exercise rows matching the filters.
    """
    # Get the database connection
    db = get_db()
    cursor = db.cursor()

    # Base query
    query = 'SELECT * FROM exercises '
    sql_parameters = []

    # Append WHERE clauses based on provided filters
    if search_query:
        query += 'WHERE (title LIKE ? OR description LIKE ?) '
        sql_parameters.extend([f'%{search_query}%', f'%{search_query}%'])

        if musical_concept:
            query += 'AND musical_concept = ? '
            sql_parameters.append(musical_concept)
    elif musical_concept:
        query += 'WHERE musical_concept = ? '
        sql_parameters.append(musical_concept)

    # Order results by creation date
    query += 'ORDER BY created_at DESC'
    return cursor.execute(query, tuple(sql_parameters)).fetchall()

def get_exercise_by_id(exercise_id: int) -> sqlite3.Row | None:
    """
    Get a single exercise by its ID.
    :param exercise_id: The ID of the exercise to fetch.
    :return: Exercise row or None if not found.
    """
    # Get the database connection
    db = get_db()
    # Execute the query and return the first result
    return db.execute('SELECT * FROM exercises WHERE id = ?', (exercise_id,)).fetchone()



def get_exercise_with_avg_difficulty(exercise_id: int) -> sqlite3.Row | None:
    """
    Get a single exercise with its average difficulty rating.
    :param exercise_id: The ID of the exercise to fetch.
    :return: Exercise row with avg_difficulty, or None if not found.
    """
    # Get the database connection
    db = get_db()

    # Query for the exercise and calculate the average difficulty from related practice sessions
    exercise = db.execute(
        'SELECT exercises.*, AVG(practice_sessions.difficulty_rating) AS avg_difficulty '
        'FROM exercises '
        'LEFT JOIN practice_sessions ON exercises.id = practice_sessions.exercise_id '
        'WHERE exercises.id = ? '
        'GROUP BY exercises.id', (exercise_id,)
    ).fetchone()

    return exercise

#-------------------Admin CRUD Functions-------------------#

def create_exercise(title: str, description: str, note_range: str, musical_concept: str, svg_diagram_path: str, created_by: int) -> bool:
    """
    Creates a new exercise in the database.
    :param title: The title of the exercise.
    :param description: A description of the exercise.
    :param note_range: The range of notes covered.
    :param musical_concept: The musical concept it teaches.
    :param svg_diagram_path: The path to the associated SVG diagram.
    :param created_by: The ID of the user who created the exercise.
    :return: True if creation was successful, False otherwise.
    """
    # Get the database connection
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: No other exercises with the same title exists
    if cursor.execute('SELECT * FROM exercises WHERE title = ?', (title,)).fetchone() is not None:
        logger.debug(f"Exercise with title: '{title}' already exists")
        return False

    # Insert the new exercise
    cursor.execute('INSERT INTO exercises (title, description, note_range, musical_concept, svg_diagram_path, created_by) '
               'VALUES (?, ?, ?, ?, ?, ?)',
               (title, description, note_range, musical_concept, svg_diagram_path, created_by,))

    db.commit()
    return True


def update_exercise(exercise_id: int, title: str, description: str, note_range: str, musical_concept: str, svg_diagram_path: str | None = None) -> bool:
    """
    Updates an existing exercise in the database.
    :param exercise_id: The ID of the exercise to update.
    :param title: The new title.
    :param description: The new description.
    :param note_range: The new note range.
    :param musical_concept: The new musical concept.
    :param svg_diagram_path: The optional new SVG diagram path.
    :return: True if the update was successful, False otherwise.
    """
    # Get the database connection
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

def delete_exercise(exercise_id: int) -> bool:
    """
    Deletes an exercise from the database.
    :param exercise_id: The ID of the exercise to delete.
    :return: True if deletion was successful, False otherwise.
    """
    # Get the database connection
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

def get_session_by_id(session_id: int) -> sqlite3.Row | None:
    """
    Gets a single practice session by its ID.
    :param session_id: The ID of the session to retrieve.
    :return: The session row object, or None if not found.
    """
    # Get the database connection
    db = get_db()
    # Execute the query and return the first result
    return db.execute('SELECT * FROM practice_sessions WHERE id = ?', (session_id,)).fetchone()


def get_user_practice_sessions(user_id: int) -> List[sqlite3.Row]:
    """
    Gets all practice sessions for a specific user.
    :param user_id: The ID of the user.
    :return: A list of practice session row objects.
    """
    # Get the database connection
    db = get_db()

    # JOIN with exercises table to get exercise title for better UX
    sessions = db.execute('SELECT practice_sessions.*, exercises.title as exercise_title '
                          'FROM practice_sessions '
                          'JOIN exercises ON practice_sessions.exercise_id = exercises.id '
                          'WHERE user_id = ? '
                          'ORDER BY practice_date DESC', (user_id,)).fetchall()
    if not sessions:
        logger.debug(f"No practice sessions for user: {user_id} found")
    return sessions

def create_practice_session(user_id: int, exercise_id: int, difficulty_rating: int, session_notes: str, practice_date: str) -> bool:
    """
    Creates a new practice session record.
    :param user_id: The ID of the user who practiced.
    :param exercise_id: The ID of the exercise practiced.
    :param difficulty_rating: The user's rating of the difficulty (1-5).
    :param session_notes: Any notes the user made.
    :param practice_date: The date of the practice session.
    :return: True if creation was successful, False otherwise.
    """
    # Get the database connection
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

    # Insert the new practice session
    cursor.execute('INSERT INTO practice_sessions (user_id, exercise_id, difficulty_rating, session_notes, practice_date)'
               'VALUES (?, ?, ?, ?, ?)', (user_id, exercise_id, difficulty_rating, session_notes, practice_date,))
    db.commit()
    return True


def update_practice_session(session_id: int, difficulty_rating: int, session_notes: str, practice_date: str) -> bool:
    """
    Updates an existing practice session.
    :param session_id: The ID of the session to update.
    :param difficulty_rating: The new difficulty rating.
    :param session_notes: The new session notes.
    :param practice_date: The new practice date.
    :return: True if the update was successful, False otherwise.
    """
    # Get the database connection
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: Does session_id exist?
    if get_session_by_id(session_id) is None:
        logger.debug(f"Practice session with id: '{session_id}' does not exist")
        return False
    # Pre-validation Check 2: Is difficulty_rating between 1-5?
    if not (1 <= difficulty_rating <= 5):
        logger.debug(f"Difficulty rating of {difficulty_rating} is out of bounds (1 - 5)")
        return False

    # Update the practice session
    cursor.execute('UPDATE practice_sessions '
               'SET difficulty_rating = ?, session_notes = ?, practice_date = ?'
               'WHERE id = ?', (difficulty_rating, session_notes, practice_date, session_id))
    db.commit()
    return True


def delete_practice_session(session_id: int) -> bool:
    """
    Deletes a practice session from the database.
    :param session_id: The ID of the session to delete.
    :return: True if deletion was successful, False otherwise.
    """
    # Get the database connection
    db = get_db()
    cursor = db.cursor()

    # Pre-validation Check: Does session_id exist?
    if get_session_by_id(session_id) is None:
        logger.debug(f"Practice session with id: '{session_id}' does not exist")
        return False

    # Delete the practice session
    cursor.execute('DELETE FROM practice_sessions WHERE id = ?', (session_id,))
    db.commit()
    return True