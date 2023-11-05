from flask import render_template, request, redirect, url_for, flash, session
from .controllers import user_controller,preference_controller
from werkzeug.exceptions import BadRequest
from flask import Blueprint

app= Blueprint('main', __name__)

# Home page/login route
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def index():
    # Check if user is logged in
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Authenticate user
        try:
            user_controller.UserController.authenticate(username, password)
            flash('Login successful', 'success')
            # return redirect(url_for(''))  # Redirect to a protected route
            return "Login successful"
        except BadRequest as e:
            flash('Login failed. Invalid username or password.', 'error')


    # Default route
    return render_template('login.html')


# Register new user route
@app.route('/register')
def register():
    if request.method == 'POST':
        pass
    
    # Default route
    return render_template('sign-up.html')

# Create new group route
@app.route('/create-group')
def create_group():
    if request.method == 'POST':
        pass

    # Default route
    return render_template('create-group.html')

@app.route('/<username>/profile')
def user_profile(username):
    return render_template('profile.html')

@app.route('/<username>/preferences')
def preferences(username):
    return render_template('preference.html')


# routes.py


@app.route('/update_preferences', methods=['POST'])
def update_preferences():
    user_id = request.form.get('user_id')
    
    # Get lists of preference IDs from the form
    ambiance_ids = request.form.getlist('ambiance')
    cuisine_ids = request.form.getlist('cuisine')
    dietary_ids = request.form.getlist('dietary')
    budget_ids = request.form.getlist('budget')
    
    # Update user preferences
   
    preference_controller.PreferencesController.update_user_preferences.update_user_preferences(
        user_id, ambiance_ids, cuisine_ids, dietary_ids, budget_ids
    )
    
    # Redirect or render template with a success message
    return redirect('/some_success_page')
