from flask import render_template, request, redirect, url_for, flash, session
from .controllers import user_controller
from werkzeug.exceptions import BadRequest
from flask import Blueprint

app= Blueprint('main', __name__)


'''
================================================
Home page/Authentication route
================================================
'''
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

'''
================================================
Register new user route
================================================
'''
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Register user
        try:
            user_controller.UserController.create_user(username, password)
            # flash('Registration successful', 'success')
            # Get user id
            user_id = session.get('user_id')
            # Redirect user to profile page
            print(user_id)
            return redirect(url_for('main.user_profile', username=username)) 
        except BadRequest as e:
            flash('Registration failed. Username already exists.', 'error')
    
    # Default route
    return render_template('sign-up.html')

'''
================================================
TODO: Add route for creating a group
================================================
'''
@app.route('/create-group')
def create_group():
    if request.method == 'POST':
        pass

    # Default route
    return render_template('create-group.html')


'''
================================================
Route to view/update user profile
================================================
'''
@app.route('/<username>/profile', methods=['GET', 'POST'])
def user_profile(username):
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        location_name = request.form.get('address')

        '''
        JOSEPH: Image is part of the profile.
        Plz modify the "update_user_profile" in user_controller and it's subsequent model
        to include the image.
        '''
        # TODO: 

    return render_template('profile.html', username=username)

'''
================================================
Route to view/update user preferences
================================================
'''
@app.route('/<username>/preferences', methods=['GET', 'POST'])
def preferences(username):
    if request.method == 'POST':
        pass

    return render_template('preference.html')
