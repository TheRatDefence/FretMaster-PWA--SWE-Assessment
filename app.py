#-------------------Generic Imports-------------------#
# System modules
from pathlib import Path
import sys
import os

#-------------------Custom Imports-------------------#
# Config
from config import DATABASE_PATH, SECRET_KEY

# Diagram creation
from utils.generate_assets import create_diagram

# Database operations
from database.db_operations import authenticate_user, create_user, get_all_exercises, get_exercise_with_avg_difficulty, \
    create_exercise, update_exercise, delete_exercise, get_user_practice_sessions, create_practice_session, \
    update_practice_session, delete_practice_session, get_session_by_id

#-------------------Initialisation-------------------#

# Add the project root to Python path - fixes Windows import issues
sys.path.insert(0, str(Path(__file__).parent))

# Auto-initialize database if it doesn't exist
if not os.path.exists(DATABASE_PATH):
    print("[!] Database not found. Initializing database...")
    from database.init_db import init_database
    init_database()
    print("[X] Database initialized successfully!")

#-------------------Logging-------------------#

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

#-------------------Flask Setup-------------------#
from flask import Flask, render_template, request, redirect, url_for, session, flash, Response, make_response, send_from_directory

# Flask app initialisation
app = Flask(__name__)

# Secret Key set using Config file
app.config['SECRET_KEY'] = SECRET_KEY


#-------------------Auth Functions-------------------#

# Used by 'LOGIN ONLY' routes
def check_login_access() -> None | Response:
    """
    Checks if a user is logged in using the flask session
    :return:    If logged in: None
                Else: redirect to login page
    """
    url = request.path
    if 'user_id' not in session:
        logger.debug(f"Unauthenticated request from IP '{request.remote_addr}' to url: '{url}'")

        flash(f"Unauthenticated request to '{url}'", 'error')

        # Returns redirect for login if user is not logged in
        return redirect(url_for('login'))
    else:
        # Returns None if user is logged in
        return None


# Used by 'ADMIN ONLY' routes
def check_admin_access() -> None | Response:
    """
    Checks if a user is an admin using the flask session
    :return:    If admin in: None
                Elif logged in: Login page
                Else: redirect to Home Page
    """
    url = request.path
    logged_in = check_login_access()

    if logged_in:
        # Return redirect to login page if user is not logged in
        return logged_in
    if session.get('is_admin') != 1:
        logger.debug(f"Unauthorised request from: '{session.get('user_id')}' to url: '{url}'")
        flash(f"Unauthorised request to '{url}'", 'error')

        # Return redirect to home page if user IS logged in BUT not an admin
        return redirect(url_for('home'))
    else:
        # Return None if user IS logged in AND an admin
        return None


#--------------------------------------Public Routes--------------------------------------#

# Home page - PUBLIC
@app.route('/')
def home():
    """
    The default home / landing page
    :return: renders 'index.html'
    """
    return render_template('index.html')


#-------------------User Management Routes-------------------#
# Login page - PUBLIC
@app.route('/login', methods=["GET", "POST"])
def login():
    """
    Accepts GET and POST request methods
    Authenticates a non-logged in user
    :return:    Successful login: Redirect to the home page
                Failed login: Renders login.html again
    """
    if request.method == "POST":
        # Gets username, password and IP from the request form
        username = request.form['username']
        password = request.form['password']
        ip = request.remote_addr

        logger.info(f"Login attempt for user '{username}' from IP '{ip}'")

        # Stores the result of the authenticate_user() function
        user = authenticate_user(username, password)

        if user:
            logger.info(f"Successful login: user='{username}' (id='{user['id']}' ip='{ip}')")

            # Stores the user_id and admin status in session
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']

            flash('Successful login', 'success')

            # Returns redirect to home page once successfully logged in
            return redirect(url_for('home'))
        else:
            logger.warning(f"Failed login: user='{username}' ip='{ip}'")

            flash('Invalid username or password', 'error')

            # Returns the login template again if authentication fails
            return render_template('auth/login.html')
    else:
        # If GET request: renders the login template
        return render_template('auth/login.html')


# Register page - PUBLIC
@app.route('/register', methods=["GET", "POST"])
def register():
    """
    Accepts GET and POST request methods
    Creates a new user in the database with specified username, password and email
    :return:    If successful: redirect to login page
                Else: renders register page again
    """
    if request.method == "POST":
        # Gets username, password, IP and email from the request form
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        ip = request.remote_addr

        logger.info(f"Register attempt for user '{username}' from IP '{ip}'")

        # Calls create_user and stores result
        registered = create_user(username, password, email)

        if registered:
            logger.info(f"Successful registration: user='{username}' ip='{ip}')")

            flash('Successful registration', 'success')

            # Returns redirect for login once successfully registered
            return redirect(url_for('login'))
        else:
            logger.warning(f"Failed Registration: user='{username}' ip='{ip}'")

            flash('Could not register user', 'error')

            # Returns the register template again if registration fails
            return render_template('auth/register.html')

    else:
        # If GET request: renders the register template
        return render_template('auth/register.html')


# Logout - PUBLIC
@app.route('/logout')
def logout():
    """
    Clears a users session
    Accepts all request methods
    :return: redirect to home
    """

    # Clear all session data
    session.clear()

    # Flash logout message
    flash("You have been logged out successfully", 'success')

    # Redirect to homepage
    return redirect(url_for('home'))

#-------------------Functionality / Exercise Routes-------------------#

# Exercises page - PUBLIC
@app.route('/exercises')
def browse_exercises():
    """
    Displays a browser of exercises in the database with optional search/filter

    :return: Rendered browse exercises template with all exercises
    """
    # Get search and musical_concept from url arguments
    search = request.args.get('search')
    musical_concept = request.args.get('musical_concept')

    # gets list of exercises based on search and a list of unique concepts (for filtering by in the template)
    exercises = get_all_exercises(search, musical_concept)
    unique_concepts = list(set(exercise['musical_concept'] for exercise in get_all_exercises()))

    # Returns a rendered template of browse.html
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

        # If exercise doesn't exist: returns redirect to browse exercises page
        return redirect(url_for('browse_exercises'))

    # If exercise exists:  returns a render template filled in with the exercise's details
    return render_template('exercises/detail.html', exercise=exercise)

#--------------------------------------Admin Routes--------------------------------------#

#-------------------Functionality / Exercise Routes-------------------#

# Create new exercise page - ADMIN ONLY
@app.route('/exercises/create', methods=['GET','POST'])
def create_exercise_route():
    """
    Create a new exercise
    User must be logged in as an admin
    Accepts GET and POST methods
    Takes:
    - Title (Must be unique)
    - Description
    - Root note name + root note octave + end note octave
    - Musical concept
    Generates diagram
    Stores new exercise in the database

    :return: redirect back to browse_exercises if successfully created
    """
    result = check_admin_access()
    if result:
        return result

    if request.method == "POST":
        # Get title, description, musical concept from request form
        title = request.form['title']
        description = request.form['description']
        musical_concept = request.form['musical_concept']

        # Get note range details from request form
        root_note_name = request.form['root_note_name']
        root_note_octave = request.form['root_note_octave']
        end_note_octave = request.form['end_note_octave']
        note_range = root_note_name + root_note_octave + "-" + root_note_name + end_note_octave

        # Get user id from session
        user = session.get('user_id')

        # Create new diagram from note range
        diagram = create_diagram(target_note=root_note_name + root_note_octave)  # Doesn't use end_note_octave yet

        # URL-encode the filename to handle special characters like # in note names
        svg_diagram_path = f"/static/diagrams/{diagram.name.replace('#', '%23')}"

        if not create_exercise(title, description, note_range, musical_concept, svg_diagram_path, user):
            flash('An exercise with that name already exists, please choose a new one', 'error')

            # Returns create.html template again if an exercise with the same name already exists
            return render_template('exercises/create.html')

        # Returns redirect to browse exercises if create_exercise was successful
        return redirect(url_for('browse_exercises'))
    else:
        # Returns create.html template if GET request
        return render_template('exercises/create.html')

# Edit an exercise - ADMIN ONLY
@app.route('/exercises/<int:exercise_id>/edit', methods=['GET', 'POST'])
def edit_exercise_route(exercise_id: int):
    """
    Edit an exercise
    User must be logged in as an admin
    Accepts GET and POST methods
    Takes (and prefills):
    - Title (Must be unique)
    - Description
    - Root note name + root note octave + end note octave
    - Musical concept
    Generates new diagram
    Updates the exercise in the database

    :param exercise_id: The exercise id to update
    :return: redirect back to browse_exercises if successfully updated
    """
    result = check_admin_access()
    if result:
        return result

    # Checking if exercise exists
    exercise = get_exercise_with_avg_difficulty(exercise_id)
    if exercise is None:
        flash('Exercise not found', 'error')

        # Return redirect to browse exercises if the target exercise isn't found
        return redirect(url_for('browse_exercises'))

    if request.method == "POST":
        # Get title, description, musical concept from request form
        title = request.form['title']
        description = request.form['description']
        musical_concept = request.form['musical_concept']

        # Get note range details from request form
        root_note_name = request.form['root_note_name']
        root_note_octave = request.form['root_note_octave']
        end_note_octave = request.form['end_note_octave']
        note_range = root_note_name + root_note_octave + "-" + root_note_name + end_note_octave

        # Create new diagram from note range
        diagram = create_diagram(target_note=root_note_name + root_note_octave)  # Doesn't use end_note_octave yet

        # URL-encode the filename to handle special characters like # in note names
        svg_diagram_path = f"/static/diagrams/{diagram.name.replace('#', '%23')}"

        if not update_exercise(exercise_id, title, description, note_range, musical_concept, svg_diagram_path):
            flash('An exercise with that name already exists, please choose a new one', 'error')

            # Returns edit page again if an exercise with the same name already exists
            return render_template('exercises/edit.html', exercise=exercise)

        # Returns redirect to exercise detail page of the updated exercise
        return redirect(url_for('exercise_detail', exercise_id=exercise_id))
    else: # If GET request:
        # Splits the note range into its parts (for prefilling the form)
        parts = exercise['note_range'].split("-")
        root_note_name = parts[0][:-1]
        root_note_octave = parts[0][-1]
        end_note_octave = parts[1][-1]

        # Renders the edit template with details prefilled
        return render_template('exercises/edit.html', exercise=exercise,
                              root_note_name=root_note_name,
                              root_note_octave=root_note_octave,
                              end_note_octave=end_note_octave)

# Delete an exercise - ADMIN ONLY
@app.route('/exercises/<int:exercise_id>/delete', methods=['POST'])
def delete_exercise_route(exercise_id: int):
    """
    Delete an exercise
    Requires user to be logged in as Admin

    :param exercise_id: The exercise ID of the exercise to be deleted
    :return: Redirect to browse exercises page
    """
    result = check_admin_access()
    if result:
        return result

    # Checking if exercise exists
    if not delete_exercise(exercise_id):
        flash('Exercise not found', 'error')
    else:
        flash('Exercise deleted', 'success')

    # Redirects to browse_exercises
    return redirect(url_for('browse_exercises'))

#--------------------------------------Logged-in OR Admin Routes--------------------------------------#

#-------------------Practice Session Routes-------------------#

# Browse sessions - LOGGED IN ONLY
@app.route('/sessions')
def sessions():
    """
    Displays a user's practice sessions.
    User must be logged in.
    :return: Rendered browse sessions template with the user's sessions.
    """
    result = check_login_access()
    if result:
        return result

    # Gets user's practice sessions using their user id in session
    user_sessions = get_user_practice_sessions(session['user_id'])

    # Returns a browse template with their practice sessions
    return render_template('sessions/browse.html', sessions=user_sessions)

# Create session - LOGGED IN ONLY
@app.route('/sessions/create', methods=['GET', 'POST'])
def create_session_route():
    """
    Creates a new practice session for a logged-in user.
    Accepts GET and POST methods.
    On POST, it creates a new session with data from the form.
    On GET, it displays the form to create a session.
    :return: Redirects to the sessions list on successful creation,
             otherwise renders the create session template.
    """
    result = check_login_access()
    if result:
        return result

    # Gets a list of all exercises
    exercises = get_all_exercises()

    if request.method == 'POST':
        # Extracts details from request form
        exercise_id = int(request.form['exercise_id'])
        difficulty_rating = int(request.form['difficulty_rating'])
        session_notes = request.form['session_notes']
        practice_date = request.form['practice_date']

        # Gets user ID from session
        user_id = session['user_id']

        if not create_practice_session(user_id, exercise_id, difficulty_rating, session_notes, practice_date):
            flash('Exercise does not exist', 'error')

            # Returns template for create.html again if exercise isn't found (create_practice_session() fails)
            return render_template('sessions/create.html', exercises=exercises)
        # Returns redirect back to sessions if successful
        return redirect(url_for('sessions'))

    else:
        # Gets exercise from url args
        preselected_exercise = request.args.get('exercise_id')

        # Returns render template with exercise prefilled
        return render_template('sessions/create.html', exercises=exercises, preselected_exercise=preselected_exercise)

# Edit session - LOGGED IN ONLY
@app.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session_route(session_id: int):
    """
    Edits an existing practice session.
    User must be logged in and own the practice session.
    Accepts GET and POST methods.
    On POST, it updates the session with data from the form.
    On GET, it displays the form to edit the session, pre-filled with existing data.
    :param session_id: The ID of the practice session to edit.
    :return: Redirects to the sessions list on successful update,
             otherwise renders the edit session template.
    """
    # Checks if user is logged in
    result = check_login_access()
    if result:
        return result

    # Gets practice session by its ID
    practice_session = get_session_by_id(session_id)

    # Checks if the practice session exists
    if not practice_session:
        flash('Practice session does not exist', 'error')

        # Returns redirect to sessions page if session doesn't exist
        return redirect(url_for('sessions'))

    # Checks if the user is authorised to edit the session
    if session['user_id'] != practice_session['user_id']:
        flash('Unauthorised edit attempt', 'error')

        # Returns redirect to sessions page if user isn't authorised
        return redirect(url_for('sessions'))

    if request.method == 'POST':
        # Extracts details from request form
        difficulty_rating = int(request.form['difficulty_rating'])
        session_notes = request.form['session_notes']
        practice_date = request.form['practice_date']

        # Updates practice session and checks if it was successful
        if not update_practice_session(session_id, difficulty_rating, session_notes, practice_date):
            flash('Practice session does not exist','error')

            # Returns edit page again if the session doesn't exist
            return render_template('sessions/edit.html', practice_session=practice_session)
        # Returns redirect to sessions page if successful
        return redirect(url_for('sessions'))
    else:
        # Returns edit page with prefilled data
        return render_template('sessions/edit.html', practice_session=practice_session)


# Delete session - LOGGED IN ONLY
@app.route('/sessions/<int:session_id>/delete', methods=['POST'])
def delete_session_route(session_id: int):
    """
    Deletes a practice session.
    User must be logged in and own the practice session.
    Accepts POST method only.
    :param session_id: The ID of the practice session to delete.
    :return: Redirects to the sessions list.
    """
    # Checks if user is logged in
    result = check_login_access()
    if result:
        return result

    # Gets practice session by its ID
    practice_session = get_session_by_id(session_id)

    # Checks if the practice session exists
    if not practice_session:
        flash('Practice session does not exist', 'error')

        # Returns redirect to sessions page if session doesn't exist
        return redirect(url_for('sessions'))

    # Checks if the user is authorised to delete the session
    if session['user_id'] != practice_session['user_id']:
        flash('Unauthorised edit attempt', 'error')

        # Returns redirect to sessions page if user isn't authorised
        return redirect(url_for('sessions'))

    # Deletes the practice session
    delete_practice_session(session_id)
    flash('Practice session deleted', 'success')

    # Returns redirect to sessions page
    return redirect(url_for('sessions'))


#-------------------PWA Routes -------------------#

# Offline page
@app.route('/offline')
def offline():
    """
    Serves the offline page for the PWA.
    :return: A response containing the rendered offline.html template.
    """
    # Makes a response from the offline.html template
    response = make_response(render_template('offline.html'))

    # Returns the response
    return response

# Service Worker
@app.route('/service-worker.js')
def sw():
    """
    Serves the service worker JavaScript file for the PWA.
    Sets the correct content type and Service-Worker-Allowed header.
    :return: A response containing the service-worker.js file.
    """
    # Makes a response from the service-worker.js file
    response = make_response(
        send_from_directory(os.path.join(app.root_path, 'static/js'),
                            'service-worker.js')
    )
    # Sets the response headers
    response.headers['Content-Type'] = 'application/javascript'
    response.headers['Service-Worker-Allowed'] = '/'

    # Returns the response
    return response

# Manifest
@app.route('/manifest.json')
def manifest():
    """
    Serves the manifest.json file for the PWA.
    Sets the correct content type.
    :return: A response containing the manifest.json file.
    """
    # Makes a response from the manifest.json file
    response = make_response(
        send_from_directory(os.path.join(app.root_path, 'static'),
                            'manifest.json')
    )
    # Sets the response headers
    response.headers['Content-Type'] = 'application/json'

    # Returns the response
    return response


if __name__ == '__main__':
    # Runs the Flask app
    app.run(port=5001)



