from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import DATABASE_PATH, SECRET_KEY
import logging

from database.db_operations import authenticate_user, create_user


# Flask app initialisation
app = Flask(__name__)

# Secret Key set using Config file
app.config['SECRET_KEY'] = SECRET_KEY

#-------------------Logging-------------------#

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


#-------------------Routes-------------------#

# Home page
@app.route('/')
def home():
    # TODO(): Proper home page implementation
    return render_template('index.html')


# Login page
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
            flash('Successful login', 'success')
            return redirect(url_for('home'))
        else:
            logger.warning(f"Failed login: user='{username}' ip='{ip}'")
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')
    else:
        return render_template('auth/login.html')



# Register page
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


# Logout
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



if __name__ == '__main__':
    app.run(port=5001)