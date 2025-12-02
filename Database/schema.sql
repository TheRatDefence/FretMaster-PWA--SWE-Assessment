/*
Users Table
    ├─ id (PRIMARY KEY)
    ├─ username
    ├─ email
    ├─ password_hash
    ├─ is_admin (0 or 1 for False/True)
    └─ created_at
*/

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)

/*
Exercises Table (Admin-created guitar practice exercises)
  ├─ id (PRIMARY KEY)
  ├─ title (e.g., "C Major Scale - Position 1")
  ├─ description (Learning objectives, technique notes)
  ├─ note_range (e.g., "E2-E4")
  ├─ musical_concept (e.g., "scales", "chords", "intervals")
  ├─ svg_diagram_path (Path to generated SVG fretboard diagram)
  ├─ created_by (FOREIGN KEY → users.id, admin who created it)
  └─ created_at
*/

CREATE TABLE IF NOT EXISTS exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    note_range TEXT NOT NULL,
    musical_concept TEXT,
    svg_diagram_path TEXT,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
);

/*
PracticeSessions Table (User practice attempts with difficulty ratings)
  ├─ id (PRIMARY KEY)
  ├─ user_id (FOREIGN KEY → users.id)
  ├─ exercise_id (FOREIGN KEY → exercises.id)
  ├─ difficulty_rating (1-5 scale, user's subjective difficulty)
  ├─ session_notes (User's reflection on practice session)
  ├─ practice_date
  └─ created_at
*/

CREATE TABLE IF NOT EXISTS practice_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    exercise_id INTEGER NOT NULL,
    difficulty_rating INTEGER NOT NULL CHECK(difficulty_rating >= 1 AND difficulty_rating <= 5),
    session_notes TEXT,
    practice_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id) ON DELETE CASCADE
);