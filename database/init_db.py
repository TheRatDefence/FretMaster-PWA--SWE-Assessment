# DATABASE INITIALIZATION SCRIPT
# This script creates the FretMaster database and tables using schema.sql

# DATABASE STRUCTURE
#
# ⏺ Users Table (stores user information)
#  ├─ id (PRIMARY KEY)
#  ├─ username
#  ├─ email
#  ├─ password_hash
#  ├─ is_admin (0 or 1 for False/True)
#  └─ created_at
#
# ⏺ Exercises Table (admin-created guitar practice exercises)
#  ├─ id (PRIMARY KEY)
#  ├─ title
#  ├─ description
#  ├─ note_range
#  ├─ musical_concept
#  ├─ svg_diagram_path
#  ├─ created_by (FOREIGN KEY → users.id)
#  └─ created_at
#
# ⏺ PracticeSessions Table (user practice attempts with difficulty ratings)
#  ├─ id (PRIMARY KEY)
#  ├─ user_id (FOREIGN KEY → users.id)
#  ├─ exercise_id (FOREIGN KEY → exercises.id)
#  ├─ difficulty_rating (1-5)
#  ├─ session_notes
#  ├─ practice_date
#  └─ created_at

import sqlite3
import os
from werkzeug.security import generate_password_hash

# Get the directory where this script is located
current_dir = os.path.dirname(os.path.abspath(__file__))
schema_path = os.path.join(current_dir, 'schema.sql')
db_path = os.path.join(current_dir, 'fretmaster.db')

def init_database():
    """
    Initialises the database by:
    1. Reading schema.sql
    2. Creating tables
    3. Adding sample data for testing
    """

    # Remove an existing database if it already exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"[*] Removed existing database at {db_path}")

    # Connect to the database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    print(f"[*] Connected to database at {db_path}")

    # Read and execute the schema.sql file
    try:
        with open(schema_path, 'r') as schema_file:
            schema_sql = schema_file.read()
            cursor.executescript(schema_sql)
            print("[*] Tables created successfully from schema.sql")
    except FileNotFoundError:
        print(f"[x] Error: Could not find schema.sql at {schema_path}")
        return
    except sqlite3.Error as e:
        print(f"[x] Database error: {e}")
        return

    # Sample data for testing
    print("\n--- Sample Data ---")

    # 1 admin, 2 regular users
    sample_users = [
        ('admin', 'admin@fretmaster.com', generate_password_hash('admin123'), 1),
        ('John_guitarist', 'john@example.com', generate_password_hash('password123'), 0),
        ('sarah_bass', 'sarah@example.com', generate_password_hash('password123'), 0)
    ]

    cursor.executemany(
        'INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)',
        sample_users
    )
    print(f"[*] Added {len(sample_users)} sample users")

    # Sample Exercises (created by the admin with user_id=1)
    sample_exercises = [
        ('C Major Scale - Position 1', 'Learn the C Major scale in first position', 'C3-G4', 'scales', '/static/diagrams/c_major_pos1.svg', 1),
        ('E Minor Pentatonic', 'Essential pentatonic scale for blues and rock', 'E2-E4', 'scales', '/static/diagrams/e_minor_pent.svg', 1),
        ('Open C Chord', 'Basic open C major chord voicing', 'C2-E4', 'chords', '/static/diagrams/open_c.svg', 1),
        ('Perfect Fifth Intervals', 'Practice recognizing perfect fifths on adjacent strings', 'E2-A4', 'intervals', '/static/diagrams/perfect_fifths.svg', 1)
    ]

    cursor.executemany(
        'INSERT INTO exercises (title, description, note_range, musical_concept, svg_diagram_path, created_by) VALUES (?, ?, ?, ?, ?, ?)',
        sample_exercises
    )
    print(f"[*] Added {len(sample_exercises)} sample exercises")

    # Sample Practice Sessions (users practicing exercises)
    sample_sessions = [
        (2, 1, 3, 'Found this challenging at first, but getting smoother', '2025-11-20'),
        (2, 1, 2, 'Much easier after a few days of practice', '2025-11-25'),
        (2, 2, 4, 'Really tough to get clean notes on all strings', '2025-11-21'),
        (3, 1, 2, 'Easy scale, good for warming up', '2025-11-22'),
        (3, 3, 3, 'Finger placement took some time to figure out', '2025-11-23'),
        (3, 4, 5, 'Very difficult! Need more practice with intervals', '2025-11-24')
    ]

    cursor.executemany(
        'INSERT INTO practice_sessions (user_id, exercise_id, difficulty_rating, session_notes, practice_date) VALUES (?, ?, ?, ?, ?)',
        sample_sessions
    )
    print(f"[*] Added {len(sample_sessions)} sample practice sessions")

    # Commit changes and close connection
    connection.commit()
    connection.close()

    print(f"\n✓ Database initialized successfully at {db_path}")
    print("\nSample Login Credentials:")
    print("\tAdmin: username='admin', password='admin123'")
    print("\tUser 1: username='john_guitarist', password='password123'")
    print("\tUser 2: username='sarah_bass', password='password123'")


if __name__ == '__main__':
    init_database()