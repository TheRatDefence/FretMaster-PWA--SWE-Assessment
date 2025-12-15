import sys
from pathlib import Path

# Add the project root to Python path (fixes Windows import issues)
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from config import DATABASE_PATH, SECRET_KEY
import logging

from database.db_operations import authenticate_user, create_user, get_all_exercises, get_exercise_with_avg_difficulty, \
    create_exercise, update_exercise, delete_exercise, get_user_practice_sessions, create_practice_session, \
    update_practice_session, delete_practice_session, get_session_by_id

# Flask app initialisation
app = Flask(__name__)

# Secret Key set using Config file
app.config['SECRET_KEY'] = SECRET_KEY

#-------------------Flash Message Categories-------------------#
# Flash message categories (matches CSS class names in static/css/style.css)
# Available categories:
#   - 'success' -> Green background
#   - 'error'   -> Red background

#-------------------Logging-------------------#

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


#-------------------Regular Routes-------------------#

# Home page - PUBLIC
@app.route('/')
def home():
    # TODO(): Proper home page implementation
    return render_template('index.html')

# Login page - PUBLIC
@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Handles steps 1, 2, 3, 7 of the LOGIN PROCESS:
      1. Flask receives POST request with username/password (handled in app.py)
      2. Extract credentials from request.form (in app.py route)
      3. Call authentication function from db_operations.py with username and password
      7. Flask route stores user info in session if authenticated, otherwise shows error

    :return:    IF authentication successful: Redirects to home page
                ELSE: Shows error, serves login page again
    """
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        ip = request.remote_addr

        logger.info(f"Login attempt for user '{username}' from IP '{ip}'")

        user = authenticate_user(username, password)

        if user:
            logger.info(f"Successful login: user='{username}' (id='{user['id']}' ip='{ip}')")
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']
            flash('Successful login', 'success')
            return redirect(url_for('home'))
        else:
            logger.warning(f"Failed login: user='{username}' ip='{ip}'")
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')

# Register page - PUBLIC
@app.route('/register', methods=["GET", "POST"])
def register():
    """
    The registration process:
      1. User fills out form (username, email, password)
      2. Flask receives POST request
      3. Hash the password (never store plain text!)
      4. Insert new user into database
      5. Redirect to login page
      6. Show success message
    """
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        ip = request.remote_addr

        logger.info(f"Register attempt for user '{username}' from IP '{ip}'")

        registered = create_user(username, password, email)

        if registered:
            logger.info(f"Successful registration: user='{username}' ip='{ip}')")
            flash('Successful registration', 'success')
            return redirect(url_for('login'))
        else:
            logger.warning(f"Failed Registration: user='{username}' ip='{ip}'")
            flash('Could not register user', 'error')
            return render_template('auth/register.html')

    else:
        return render_template('auth/register.html')

# Logout - PUBLIC
@app.route('/logout')
def logout():
    """
    Logout Process:
    1. Clear session
    2. Flash a message
    3. Redirect to homepage
    """
    # Clear all session data
    session.clear()

    # Flash logout message
    flash("You have been logged out successfully", 'success')

    # Redirect to homepage
    return redirect(url_for('home'))

#-------------------Helper Functions-------------------#

# Used by 'LOGIN ONLY' routes
def check_login_access() -> None | Response:
    url = request.path
    if 'user_id' not in session:
        logger.debug(f"Unauthenticated request from IP '{request.remote_addr}' to url: '{url}'")
        flash(f"Unauthenticated request to '{url}'", 'error')
        return redirect(url_for('login'))
    else:
        return None

# Used by 'ADMIN ONLY' routes
def check_admin_access() -> None | Response:
    url = request.path
    logged_in = check_login_access()

    if logged_in:
        return logged_in
    if session.get('is_admin') != 1:
        logger.debug(f"Unauthorised request from: '{session.get('user_id')}' to url: '{url}'")
        flash(f"Unauthorised request to '{url}'", 'error')
        return redirect(url_for('browse_exercises'))
    else:
        return None


#-------------------Functionality Routes-------------------#

# Exercises page - PUBLIC
@app.route('/exercises')
def browse_exercises():
    """
    Displays a browser of exercises in the database with optional search/filter

    :return: Rendered browse exercises template with all exercises
    """
    search = request.args.get('search')
    musical_concept = request.args.get('musical_concept')

    exercises = get_all_exercises(search, musical_concept)
    unique_concepts = list(set(exercise['musical_concept'] for exercise in get_all_exercises()))
    return render_template('exercises/browse.html', exercises=exercises,
                           search_query=search, concepts=unique_concepts, musical_concept=musical_concept)

# Specific exercise page - PUBLIC
@app.route('/exercises/<int:exercise_id>')
def exercise_detail(exercise_id: int):
    """
    View a single exercise in detail page
    Shows exercise info + average difficulty rating

    :param exercise_id: The ID of the exercise to display
    :return: Rendered exercise detail template or redirect if not found
    """
    exercise = get_exercise_with_avg_difficulty(exercise_id)

    # Check if exercise exists
    if exercise is None:
        flash('Exercise not found', 'error')
        return redirect(url_for('browse_exercises'))

    return render_template('exercises/detail.html', exercise=exercise)

# Create new exercise page - ADMIN ONLY
@app.route('/exercises/create', methods=['GET','POST'])
def create_exercise_route():
    result = check_admin_access()
    if result:
        return result

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        note_range = request.form['note_range']
        musical_concept = request.form['musical_concept']
        svg_diagram_path = request.form['svg_diagram_path']
        user = session.get('user_id')

        if not create_exercise(title, description, note_range, musical_concept, svg_diagram_path, user):
            flash('An exercise with that name already exists, please choose a new one', 'error')
            return render_template('exercises/create.html')
        return redirect(url_for('browse_exercises'))
    else:
        return render_template('exercises/create.html')

# Edit an exercise - ADMIN ONLY
@app.route('/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
def edit_exercise_route(exercise_id: int):
    result = check_admin_access()
    if result:
        return result

    # Checking if exercise exists
    exercise = get_exercise_with_avg_difficulty(exercise_id)
    if exercise is None:
        flash('Exercise not found', 'error')
        return redirect(url_for('browse_exercises'))

    if request.method == "POST":
        title = request.form['title']
        description = request.form['description']
        note_range = request.form['note_range']
        musical_concept = request.form['musical_concept']
        diagram_path = request.form['diagram_path']

        if not update_exercise(exercise_id, title, description, note_range, musical_concept, diagram_path):
            flash('An exercise with that name already exists, please choose a new one', 'error')
            return render_template('exercises/edit.html', exercise=exercise)
        return redirect(url_for('exercise_detail', exercise_id=exercise_id))
    else:
        return render_template('exercises/edit.html', exercise=exercise)

# Delete an exercise - ADMIN ONLY
@app.route('/exercises/<int:exercise_id>/delete', methods=['POST'])
def delete_exercise_route(exercise_id: int):
    result = check_admin_access()
    if result:
        return result

    if not delete_exercise(exercise_id):
        flash('Exercise not found', 'error')
    else:
        flash('Exercise deleted', 'success')
    return redirect(url_for('browse_exercises'))


#-------------------Practice Session Routes-------------------#

# Browse sessions - LOGGED IN ONLY
@app.route('/sessions')
def sessions():
    result = check_login_access()
    if result:
        return result

    user_id = session['user_id']
    user_sessions = get_user_practice_sessions(user_id)
    return render_template('sessions/browse.html', sessions=user_sessions)

# Create session - LOGGED IN ONLY
@app.route('/sessions/create', methods=['GET', 'POST'])
def create_session_route():
    result = check_login_access()
    if result:
        return result

    exercises = get_all_exercises()

    if request.method == 'POST':
        exercise_id = int(request.form['exercise_id'])
        difficulty_rating = int(request.form['difficulty_rating'])
        session_notes = request.form['session_notes']
        practice_date = request.form['practice_date']
        user_id = session['user_id']

        if not create_practice_session(user_id, exercise_id, difficulty_rating, session_notes, practice_date):
            flash('Exercise does not exist', 'error')
            return render_template('sessions/create.html', exercises=exercises)
        return redirect(url_for('sessions'))

    else:
        return render_template('sessions/create.html', exercises=exercises)

# Edit session - LOGGED IN ONLY
@app.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session_route(session_id: int):
    result = check_login_access()
    if result:
        return result

    practice_session = get_session_by_id(session_id)

    if not practice_session:
        flash('Practice session does not exist', 'error')
        return redirect(url_for('sessions'))

    if session['user_id'] != practice_session['user_id']:
        flash('Unauthorised edit attempt', 'error')
        return redirect(url_for('sessions'))

    if request.method == 'POST':
        difficulty_rating = int(request.form['difficulty_rating'])
        session_notes = request.form['session_notes']
        practice_date = request.form['practice_date']

        if not update_practice_session(session_id, difficulty_rating, session_notes, practice_date):
            flash('Practice session does not exist','error')
            return render_template('sessions/edit.html', practice_session=practice_session)
        return redirect(url_for('sessions'))
    else:
        return render_template('sessions/edit.html', practice_session=practice_session)


# Delete session - LOGGED IN ONLY
@app.route('/sessions/<int:session_id>/delete', methods=['POST'])
def delete_session_route(session_id: int):
    result = check_login_access()
    if result:
        return result

    practice_session = get_session_by_id(session_id)
    if not practice_session:
        flash('Practice session does not exist', 'error')
        return redirect(url_for('sessions'))
    if session['user_id'] != practice_session['user_id']:
        flash('Unauthorised edit attempt', 'error')
        return redirect(url_for('sessions'))

    delete_practice_session(session_id)
    flash('Practice session deleted', 'success')
    return redirect(url_for('sessions'))


if __name__ == '__main__':
    app.run(port=5001)



