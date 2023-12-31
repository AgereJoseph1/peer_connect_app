from flask import render_template, request, redirect, url_for, flash, session
from .controllers import user_controller,preference_controller,group_controller, invitetoken_controller, event_controller, places_controller
from werkzeug.exceptions import BadRequest, NotFound
from flask import Blueprint, jsonify
from config import Config
import googlemaps
from flask import current_app as app
app= Blueprint('main', __name__)
gmaps = googlemaps.Client(key=Config.API_KEY)

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
        address = request.form.get('address')
        profile_pic = request.files.get('profile_pic')

        try:
            user_controller.UserController.update_user_profile(
                user_id=session.get('user_id'),
                email=email,
                phone_number=phone,
                address=address,
                profile_picture=profile_pic
            )
            flash('Profile updated successfully', 'success')
            # Redirect to a profile page
            return redirect(url_for('main.preferences', username=username))
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
        activity_type = request.form.get('activity')
        date = request.form.get('date')
        time = request.form.get('time')
        duration = request.form.get('duration')

        try:
            # Create Activity
            event_controller.EventController.create_event(
                activity_type,  group_id,duration,date,time
            )

            activity_details = {
                'activity': places_controller.activity_type_mapping.get(activity_type),
                'date': date,
                'time': time,
                'group_id': group_id
            }
            
            # Redirect to the places page
            return redirect(url_for('main.places', group_id=group_id, activity_details=activity_details))
        
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
        # Get group preferences
        grp_preferences = group_controller.GroupController.get_group_member_preferences(
            group_id
        )
        
        # If there's only one member, use their location as the central point
        if len(grp_member_locations) == 1:
            central_location = grp_member_locations[0]
        else:
            # Calculate centroid for multiple members
            avg_lat = sum(location[0] for location in grp_member_locations) / len(grp_member_locations)
            avg_lng = sum(location[1] for location in grp_member_locations) / len(grp_member_locations)
            central_location = (avg_lat, avg_lng)
        
        # Retrieve activity type from query parameters or default to 'social'
        activity_type = request.args.get('at', 'social')
        
        
        # Get nearby places based on the activity type
        nearby_places = places_controller.get_nearby_places(central_location, places_controller.activity_type_mapping, activity_type, gmaps)
        
        #TODO: Future implementation
        # Filter nearby places based on group preferences
        # filtered_places = places_controller.filter_places(nearby_places, grp_preferences)

        activity_details = request.args.get('activity_details')
        # Render the places in the template
        return render_template('places.html', places=nearby_places, api_key=Config.API_KEY, activity_details=activity_details, group_id=group_id)



'''
================================================
Generate Invite Token
================================================
'''
@app.route('/generate-invite/<group_id>')
def generate_invite(group_id):
    # generate invite token
    invite_token =   invitetoken_controller.InviteTokenController.generate_invite_token(group_id)
    invite_link = Config.BASE_URL + '/join-group/' + invite_token
    # return invite link
    return jsonify({'inviteLink': invite_link})


'''
================================================
Broadcast Message to Group Members
================================================
'''
@app.route('/broadcast', methods=['get'])
def broadcast_email():
    try:
        # # Retrieve data from form submission
        # place_name = request.args.get('place_name')
        # place_address = request.args.get('place_address')
        # activity_type = request.args.get('at')
        # act_time = request.args.get('time')
        # act_date = request.args.get('date')
        # group_id = request.args.get('group_id')
        
        # # Construct the meeting details dictionary expected by the send_meeting_email function
        # meeting_details = {
        #     'activity': activity_type,
        #     'time': act_time,
        #     'date': act_date,
        #     'location': f"{place_name}, {place_address}"
        # }

        # Call the send_meeting_email function
        # group_controller.GroupController.send_meeting_email(group_id, meeting_details)
    
        # flash('Email sent successfully', 'success')
        # return redirect(url_for('main.group_profile'))
        return "<h1> Feature Under Development </h1>"
    except NotFound as e:
        # Handle not found errors (group or members not found)
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        # Handle other exceptions
        return jsonify({'error': 'An error occurred while sending emails.'}), 500