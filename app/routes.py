from flask import render_template, request, redirect, url_for, flash, session
from .controllers import user_controller,preference_controller,group_controller, invitetoken_controller, event_controller, base_algorithm
from werkzeug.exceptions import BadRequest, NotFound
from flask import Blueprint, jsonify
from config import BASE_URL
from utils import func

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
            flash('Registration successful', 'success')
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
Route for creating a group
================================================
'''
@app.route('/create-group', methods=['GET', 'POST'])
def create_group():
    if request.method == 'POST':
        title = request.form.get('title')
        user_id = session.get('user_id')
        distribution = request.form.get('description')
        banner = request.files.get('banner')

        try:
            group_controller.GroupController.create_group(
                title,
                user_id,
                distribution,
                banner=banner
            )
            flash('Group created successfully', 'success')
            # Redirect to a page that displays the newly created group
            return redirect(url_for('main.create_group'))
        except NotFound:
            flash('User not found', 'error')
        except BadRequest as e:
            flash(str(e), 'error')

    # Default route
    user_id = session.get('user_id')
    
    user_groups = group_controller.GroupController.get_user_groups(user_id)
    return render_template('create-group.html', user_groups=user_groups)
    


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
        profile_pic = request.files.get('profile_pic')

        try:
            user_controller.UserController.update_user_profile(
                user_id=session.get('user_id'),
                email=email,
                phone=phone,
                location_name=location_name,
                profile_picture=profile_pic
            )
            flash('Profile updated successfully', 'success')
            # Redirect to a profile page
            return redirect(url_for('user_profile', username=username))
        except NotFound:
            flash('User not found', 'error')
        except BadRequest as e:
            flash(str(e), 'error')

    return render_template('profile.html', username=username)

'''
================================================
Route to view/update user preferences
================================================
'''
@app.route('/<username>/preferences', methods=['GET', 'POST'])
def preferences(username):
    if request.method == 'POST':
        user_id = session.get('user_id')

        # Get lists of preference IDs from the form
        ambiance_ids = request.form.getlist('ambiance')
        cuisine_ids = request.form.getlist('cuisine')
        dietary_ids = request.form.getlist('dietary')
        budget_ids = request.form.getlist('budget')

        # Update user preferences
        try:
            preference_controller.PreferencesController.update_user_preferences(
            user_id, ambiance_ids, cuisine_ids, dietary_ids, budget_ids
            )

            flash('Preferences updated successfully', 'success')
            return redirect(url_for('main.create_group', username=username))
        except NotFound:
            flash('User not found', 'error')
        except BadRequest as e:
            flash(str(e), 'error')

    return render_template('preference.html', username=username)


'''
================================================
Route to Group Profile
================================================
'''
@app.route('/<group_id>/group')
def group_profile(group_id):
    try:
        group = group_controller.GroupController.get_group_details(group_id)
        # Render a template with the group details
        return render_template('group-profile.html', group=group, group_id=group_id)
    except NotFound as e:
        # Handle the case where the group is not found
        flash('Group not found.', 'error')
        return redirect(url_for('main.create_group', group_id=group_id))


'''
================================================
Route to Group Meetup
================================================
'''
@app.route('/meetup/<group_id>', methods=['GET', 'POST'])
def meetup(group_id):
    if request.method == 'POST':
        # Get the meetup details from form
        activity_type = request.form.get('activity_type')
        date = request.form.get('date')
        # start_time = request.form.get('start_time')
        duration = request.form.get('duration')

        try:
            # Create Activity
            event_controller.EventController.create_event(
                group_id, activity_type, date, duration
            )
            flash('Meetup created successfully', 'success')

            # Redirect to the places page
            return redirect(url_for('main.places', group_id=group_id))
        
        except NotFound as e:
            flash('Group not found.', 'error')
        except BadRequest as e:
            flash(str(e), 'error')

    return render_template('meetup.html', group_id=group_id)


'''
================================================
Route to Places
================================================
'''
@app.route('/places/<group_id>', methods=['GET'])
def places(group_id):
    if request.method == 'GET':
        '''Create the meetup - > a controller to access 
            each member's preferences and generate a list 
            of places
        '''
        # Get group member locations
        grp_member_locations = group_controller.GroupController.get_group_member_locations(
            group_id
            )
        
        # Calculate the geographical center of the group
        center = func.find_geographical_center(grp_member_locations)

        # Get group preferences
        grp_preferences = group_controller.GroupController.get_group_member_preferences(
            group_id
        )

        # Perform Search

        results = base_algorithm.find_central_spot(group_id)
        print(results)
        exit()
        
        # Get group preferences
        grp_preferences = group_controller.GroupController.get_group_member_preferences(
            group_id
        )
    
    return render_template('places.html')


'''
================================================
Generate Invite Token
================================================
'''
@app.route('/generate-invite/<group_id>')
def generate_invite(group_id):
    # generate invite token
    invite_token =   invitetoken_controller.InviteTokenController.generate_invite_token(group_id)
    invite_link = BASE_URL + '/join-group/' + invite_token
    # return invite link
    return jsonify({'inviteLink': invite_link})