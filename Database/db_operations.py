import sqlite3

from flask import session

from config import DATABASE_PATH
from werkzeug.security import check_password_hash
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
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,)) # I had security concerns about using SELECT * FROM... but it appears to be fine
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
