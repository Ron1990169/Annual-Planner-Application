import uuid  # this is the library we will use to generate unique ids.
from datetime import datetime, timedelta  # this is the library we will use to check if events overlap.
import flask  # this is the library we will use to create the web app.
import google.oauth2.id_token  # this is the library we will use to authenticate users.
from flask import flash, Flask, url_for, session  # this is the library we will use to create the web app.
from flask import redirect, render_template, request  # this is the library we will use to create the web app.
from google.auth.transport import requests  # this is the library we will use to authenticate users.
from google.cloud import datastore  # this is the library we will use to store data in the datastore.

app: Flask = flask.Flask(__name__)  # create the web app object. This is the main object we will use to create
# the web app.

# get access to the datastore client, so we can add and store data in the datastore.
datastore_client = datastore.Client()

# get access to a request adapter for firebase as we will need this to authenticate users.
firebase_request_adapter = requests.Request()  # this is the request adapter for firebase.


def createUserInfo(claims):  # this function creates the user info in the datastore.
    entity_key = datastore_client.key('UserInfo', claims['email'])  # this is the key of the child object.
    entity = datastore.Entity(key=entity_key)  # this is the entity object.
    entity.update({  # this is the data we want to store.
        'email': claims['email'],  # this is the email of the user.
        'name': claims.get('name', 'No Name'),  # this is the name of the user, or 'No Name' if the key doesn't exist.
    })
    datastore_client.put(entity)  # store the entity object in the datastore.


def retrieveUserInfo(claims):  # this function retrieves the user info from the datastore.
    entity_key = datastore_client.key('UserInfo', claims['email'])  # create a key for the user info.
    user_info = datastore_client.get(entity_key)  # get the user info from the datastore.
    if not user_info:  # if the user doesn't exist.
        user_info = datastore.Entity(entity_key)
        user_info.update({
            'email': claims['email'],  # this is the email of the user.
            'event_list': [],  # this is the list of events.
            'calendar_list': [],  # this is the list of calendars.
            'calendar_keys': []  # this is the list of calendar keys.
        })
        datastore_client.put(user_info)
    return user_info  # return the user info.


def add_calendar(user_info, calendar_name, event_id, calendar_id=None, calendar_shared=False,
                 calendar_shared_id=None):
    # Check if a calendar with the same name already exists in the user's info and raise an error if it does.
    for calendar in user_info.get('calendar_list', []):  # get the list of calendars from the user's info.
        if calendar['calendar_name'] == calendar_name:  # check if the calendar name already exists.
            raise ValueError("A calendar with this name already exists")  # raise an error if it does.
    # create a new calendar entity in the datastore.
    if calendar_id is None:
        calendar_id = str(uuid.uuid4())  # generate a unique id if one is not provided
    calendar_key = datastore_client.key('Calendar', calendar_id)  # create a key for the calendar.
    calendar = datastore.Entity(calendar_key)
    calendar.update({
        'calendar_name': calendar_name,  # the name of the calendar is stored in the calendar entity.
        'event_id': event_id,  # the id of the event is stored in the calendar entity.
        'calendar_id': calendar_id,  # the id of the calendar is stored in the calendar entity.
        'calendar_shared': calendar_shared,  # the shared status of the calendar is stored in the calendar entity.
        'calendar_shared_id': calendar_shared_id,  # the id of the shared status is stored in the calendar entity.
        'calendar_owner': user_info.get('user_email'),  # the owner email id of the calendar is stored in the
        # calendar entity.
        'calendar_owner_id': user_info.get('user_id'),  # the id of the owner is stored in the calendar entity.
    })
    datastore_client.put(calendar)
    # get the list of calendars from the user's info and add the new calendar to it if it doesn't exist.
    # If already exist in the list of calendars for the user.
    calendar_list = user_info.get('calendar_list', [])
    calendar_list.append(calendar)
    user_info.update({'calendar_list': calendar_list})
    # update the user's info with the new calendar key and store it in the datastore.
    calendar_keys = user_info.get('calendar_keys', [])
    calendar_keys.append(calendar.key)
    user_info.update({'calendar_keys': calendar_keys})
    # store the user's info in the datastore.
    datastore_client.put(user_info)


def add_event(user_info, day, month, year, event_name, event_start, event_end, event_description,
              event_shared, event_shared_with, event_id):
    # get the list of events from the user's info and add the new event to it if it doesn't exist.
    event_list = user_info.get('event_list', [])
    # create a new event entity and add it to the list of events for the user.
    day_id = day + month + year if day and month and year else None  # the id of the day is stored in the event entity.
    event_start_id = event_start + event_name  # the id of the start time is stored in the event entity.
    event_end_id = event_end + event_name  # the id of the end time is stored in the event entity.
    event_description_id = day_id + event_start_id + event_end_id if day_id else event_start_id + event_end_id
    event_name_id = event_name + (day_id if day_id else '')
    event_shared + (event_shared_with if event_shared_with else '')
    event_shared_id = event_name_id
    event_keys = datastore_client.key('event', event_id)  # create a key for the calendar.
    event = datastore.Entity(event_keys)
    event.update({
            'day': day,  # the day of the event is stored in the event entity.
            'month': month,  # the month of the event is stored in the event entity.
            'year': year,  # the year of the event is stored in the event entity.
            'day_id': day_id,  # the id of the day is stored in the event entity.
            'event_start': event_start,  # the start time of the event is stored in the event entity.
            'event_start_id': event_start_id,  # the id of the start time is stored in the event entity.
            'event_end': event_end,  # the end time of the event is stored in the event entity.
            'event_end_id': event_end_id,  # the id of the end time is stored in the event entity.
            'event_description': event_description,  # the description of the event is stored in the event entity.
            'event_description_id': event_description_id,  # the id of the description is stored in the event entity.
            'event_name': event_name,  # the name of the event is stored in the event entity.
            'event_name_id': event_name_id,  # the id of the name is stored in the event entity.
            'event_shared': event_shared,  # the shared status of the event is stored in the event entity.
            'event_shared_id': event_shared_id,  # the id of the shared status is stored in the event entity.
        })
    datastore_client.put(event)
    user_info.update({'event_list': event_list})
    # update the user's info with the new calendar key and store it in the datastore.
    calendar_keys = user_info.get('event_keys', [])
    calendar_keys.append(event.key)
    user_info.update({'event_keys': event_keys})
    # store the user's info in the datastore.
    datastore_client.put(user_info)


def share_calendar(user_info, calendar_id, recipient_email):  # Check if the recipient exists in the datastore
    # and is a user of the app.
    # Check if the owner is trying to share the calendar with themselves and raise an error if they are.
    if user_info['email'] == recipient_email:
        raise ValueError("You cannot add yourself to your own calendar")
    # Find the calendar to share in the user's info.
    calendar_list = user_info['calendar_list']  # the list of calendars is stored in the user's info.
    calendar_to_share = None
    for calendar in calendar_list:  # the calendar is stored in the calendar entity.
        if calendar['calendar_id'] == calendar_id:  # the id of the calendar is stored in the calendar entity.
            calendar_to_share = calendar  # the calendar to share is found.
            break
    if calendar_to_share:  # Check if the calendar exists in the user's info and is not already shared with the
        # recipient email.
        # Update the calendar_shared and calendar_shared_id fields of the calendar to share with the recipient email.
        calendar_to_share['calendar_shared'] = True
        calendar_to_share['calendar_shared_id'] = recipient_email
        # Add the shared calendar to the recipient's calendar_list in the datastore.
        recipient_key = datastore_client.key('UserInfo', recipient_email)
        recipient_info = datastore_client.get(recipient_key)
        if recipient_info:  # Check if the recipient exists in the datastore and is a user of the app.
            recipient_calendar_list = recipient_info.get('calendar_list', [])
            recipient_calendar_list.append(calendar_to_share)  # add the shared calendar to the
            # recipient's calendar_list.
            recipient_info.update({'calendar_list': recipient_calendar_list})  # update the recipient's info with the
            # new calendar key and store it in the datastore.
            datastore_client.put(recipient_info)  # store the recipient's info in the datastore.
        else:
            # Handle the case when the recipient email is not found in the datastore.
            # This means that the recipient is not a user of the app.
            return "Recipient not found"
    else:
        # Handle the case when the calendar_id is not found in the user's info or is already
        # shared with the recipient email.
        return "Calendar not found"
    return "Calendar shared successfully"


def compare_schedules(user_info, selected_calendar_ids):  # Find the common time slots between the selected calendars.
    calendars_to_compare = [cal for cal in user_info['calendar_list'] if cal['calendar_id'] in selected_calendar_ids]
    # Initialize the common time slots as empty list of events and the list of common time slots as empty.
    common_time_slots = []
    # Loop through all possible pairs of calendars to compare.
    for i in range(len(calendars_to_compare)):  # the calendar is stored in the calendar entity.
        for j in range(i + 1, len(calendars_to_compare)):  # the calendar is stored in the calendar entity.
            cal1 = calendars_to_compare[i]  # the calendar 1 is stored in the calendar entity.
            cal2 = calendars_to_compare[j]  # the calendar 2 is stored in the calendar entity.
            # Find common time slots between calendar 1 and calendar 2. Loop through all possible pairs of events.
            for event1 in cal1['event_list']:  # the event is stored in the event entity.
                for event2 in cal2['event_list']:  # the event is stored in the event entity.
                    event1_start = event1['event_start']  # the start time of the event 1 is stored in the event entity.
                    event1_end = event1['event_end']  # the end time of the event is stored in the event entity.
                    event2_start = event2['event_start']  # the start time of the event 2 is stored in the event entity.
                    event2_end = event2['event_end']  # the end time of the event is stored in the event entity.
                    # Check if event1 and event2 overlap in time and add the common
                    # time slot to the list of common time.
                    if event1_start <= event2_end and event1_end >= event2_start:  # slots.
                        common_start = max(event1_start, event2_start)  # the start time of the common time slot is
                        # stored in the event entity.
                        common_end = min(event1_end, event2_end)  # the end time of the common time slot is stored in
                        # the event entity.
                        common_time_slots.append({'start': common_start, 'end': common_end})
    return common_time_slots  # return the list of common time slots.


def recent_events(user_info, days=7):  # Find the events that occurred in the last 7 days.
    calendar_keys = user_info['calendar_keys']  # the list of calendar keys is stored in the user's info.
    end_time = datetime.now()  # the end time is the current time.
    start_time = end_time - timedelta(days=days)  # the start time is 7 days before the current time.
    recent_events_list = []  # the list of recent events is initialized as an empty list.
    for calendar_key in calendar_keys:  # the calendar key is stored in the calendar entity.
        calendar = datastore_client.get(calendar_key)  # the calendar is stored in the calendar entity.
        for event in calendar['event_list']:  # the event is stored in the event entity.
            event_start = datetime.strptime(event['event_start'], "%Y-%m-%dT%H:%M")  # the start time of the event is
            # stored in the event entity.
            if start_time <= event_start <= end_time:  # if the event occurred in the last 7 days.
                recent_events_list.append(event)  # add the event to the list of recent events.
    return recent_events_list  # return the list of recent events.


@app.route('/login', methods=['GET', 'POST'])  # this is the route for the login page.
def login():  # this is the function for the login page.
    error = None
    if request.method == 'POST':  # if the user is trying to log in.
        username = request.form['username']  # get the username from the form.
        password = request.form['password']  # get the password from the form.
        if username != 'admin' or password != 'admin':  # if the username or password is incorrect.
            error = 'Invalid credentials. Please try again.'  # set the error message.
        else:
            session['logged_in'] = True  # set the session variable.
            flash('You were logged in')  # display a flash message.
            return redirect(url_for('index'))  # redirect to the index page.
    return render_template('index.html', error=error)  # render the login page.


@app.route('/logout')  # this is the route for the logout page.
def logout():  # this is the function for the logout page.
    session.pop('logged_in', None)  # remove the session variable.
    flash('You were logged out')  # display a flash message.
    return redirect(url_for('index'))  # redirect to the index page.


@app.route('/')  # this is the route for the home page.
def root():  # this is the function that handles the home page.
    id_token = request.cookies.get("token")  # get the token from the cookies.
    error_message = None  # this is the error message.
    claims = None  # this is the claims object.
    user_info = None  # this is the user_info object.
    if id_token:  # if the token exists, it means that the user is logged in.
        try:  # try to authenticate the user.
            claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)  # this is the
            # claims object.
            user_info = retrieveUserInfo(claims)  # retrieve the user info from the datastore.
            if user_info is None:  # if the user info does not exist, it means that
                # the user is logging in for the first time.
                createUserInfo(claims)  # create the user info in the datastore.
                user_info = retrieveUserInfo(claims)  # retrieve the user info from the datastore.
        except ValueError as exc:  # if the token is invalid, show an error message.
            error_message = exc  # set the error message.
    return render_template('index.html', user_data=claims, user_info=user_info, error_message=error_message)


@app.route('/update_event/<event_id>', methods=['GET', 'POST'])  # this is the route for the update event page.
def update_event(event_id):  # this is the function that handles the update event page.
    # Retrieve the form data from the request.
    event_name = request.form['event_name']  # get the event name from the form.
    event_date = request.form['event_date']  # get the event date from the form.
    event_start_time = request.form['event_start_time']  # get the event start time from the form.
    event_end_time = request.form['event_end_time']  # get the event end time from the form.
    event_description = request.form['event_description']  # get the event description from the form.
    id_token = request.cookies.get("token")  # get the token from the cookies.
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)  # retrieve the user info from the datastore.
    # Find the event and update it with the new data from the form fields above (event_name, event_date,
    # event_start_time, event_end_time, event_description)
    event_list = user_info['event_list']  # get the event list from the user's info.
    for event in event_list:  # loop through the event list.
        if event['event_name_id'] == event_id:  # if the event name id matches the event id, update the event.
            event['event_name'] = event_name  # update the event name.
            event_date_parts = event_date.split('-')  # split the date into day, month, and year.
            event['day'] = event_date_parts[2]  # update the day.
            event['month'] = event_date_parts[1]  # update the month.
            event['year'] = event_date_parts[0]  # update the year.
            event['event_start'] = f"{event_date}T{event_start_time}:00"  # update the event start time.
            event['event_end'] = f"{event_date}T{event_end_time}:00"  # update the event end time.
            event['event_description'] = event_description  # update the event description.
            break
    # Update the user's info with the updated event list in the datastore.
    user_info.update({'event_list': event_list})  # update the user's info with the updated event list.
    datastore_client.put(user_info)  # put the user's info in the datastore.
    return redirect('update_event.html')  # redirect to the update event page.


@app.route('/delete_event/<event_id>', methods=['POST', 'GET'])  # this is the route for the delete event page.
def delete_event(event_id):  # this is the function that handles the delete event page.
    # Get the user's info from the datastore and delete the event from the event list in the user's info entity.
    id_token = request.cookies.get("token")  # get the token from the cookies.
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)  # retrieve the user info from the datastore.
    # Remove the event from the event_list in the user's info.
    event_list = user_info['event_list']  # get the event list from the user's info.
    event_list = [event for event in event_list if event['event_name_id'] != event_id]  # remove the event from
    # the event list.
    # Update the user's info with the updated event list in the datastore.
    user_info.update({'event_list': event_list})
    datastore_client.put(user_info)
    # Redirect to the main page to show the updated event list without the deleted event in it.
    return redirect('delete_event.html')  # redirect to the delete event page.


@app.route('/share_calendar', methods=['GET', 'POST'])
def handle_share_calendar():
    calendar_id = request.form['calendar_id']  # get the calendar id from the form.
    recipient_email = request.form['recipient_email']  # get the recipient email from the form.
    id_token = request.cookies.get("token")  # get the token from the cookies.
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)  # retrieve the user info from the datastore.
    result = share_calendar(user_info, calendar_id, recipient_email)  # share the calendar.
    if result:  # if the calendar was shared successfully, show a success message.
        flash("Calendar shared successfully", "success")  # show a success message.
    else:
        flash("Error sharing calendar", "error")  # show an error message.
    return redirect('share_calendar.html')  # redirect to the share calendar page.


@app.route('/share_calendar', methods=['GET', 'POST'])  # this is the route for the share calendar page.
def share_calendar_page():  # this is the function that handles the share calendar page.
    return render_template('share_calendar.html')  # render the share calendar page.


@app.route('/create_event', methods=['GET', 'POST'])  # this is the route for the create event page.
def create_event():  # this is the function that handles the create event page.
    if request.method == 'POST':  # if the request method is POST, get the form data.
        event_name = request.form.get('event_name')  # get the event name from the form.
        event_date = request.form.get('event_date')  # get the event date from the form.
        event_start_time = request.form.get('event_start_time')  # get the event start time from the form.
        event_end_time = request.form.get('event_end_time')  # get the event end time from the form.
        event_description = request.form.get('event_description')  # get the event description from the form.
        event_shared_with = request.form.get('event_shared_with')  # get the event shared with from the form.
        calendar_id = request.form.get('calendar_id')  # get the calendar id from the form.
        if not event_name:  # if the event name is empty, show an error message.
            return render_template('create_event.html', error='Please provide an event name.')
        if not event_date:  # if the event date is empty, show an error message.
            return render_template('create_event.html', error='Please provide a valid date format (YYYY-MM-DD).')
        try:  # try to split the event date into day, month, and year.
            day, month, year = event_date.split('-')
        except ValueError:  # if the event date is not in the correct format, show an error message.
            return render_template('create_event.html', error='Please provide a valid date format (YYYY-MM-DD).')
        event_start = f"{event_date}T{event_start_time}"
        event_end = f"{event_date}T{event_end_time}"
        id_token = request.cookies.get('token')
        claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
        if not claims:  # if the token is invalid, show an error message.
            return render_template('index.html', error='Authentication failed')  # show an error message.
        user_info = retrieveUserInfo(claims)  # retrieve the user info from the datastore.
        add_event(user_info, calendar_id, day, month, year, event_name, event_start, event_end, event_description,
                  False, event_shared_with)  # add the event to the user's info.
        return redirect('create_event.html')  # redirect to the create event page.
    return render_template('create_event.html')  # render the create event page.


@app.route('/edit_event/<event_id>', methods=['GET', 'POST'])  # this is the route for the edit event page.
def edit_event(event_id):  # this is the function that handles the edit event page.
    id_token = request.cookies.get("token")  # get the token from the cookies.
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)  # retrieve the user info from the datastore.
    event = next((e for e in user_info['event_list'] if e['event_name_id'] == event_id), None)
    if not event:  # if the event is not found, return an error message.
        return "Event not found", 404
    # Get calendar_id from the form data
    calendar_id = request.form.get('calendar_id')
    # Pass calendar_id to the template
    return render_template('edit_event.html', event=event, event_id=event_id, calendar_id=calendar_id)


@app.route('/compare_schedules', methods=['GET', 'POST'])  # this is the route for the compare schedules page.
def compare_schedules_route():  # this is the function that handles the compare schedules page.
    # Get the selected calendar IDs from the form data (this is a list of calendar IDs)
    selected_calendar_ids = request.form.getlist('calendar_ids[]')  # get the calendar ids from the form.
    # Get the user's info from the datastore and delete the event from the event list in the user's info entity.
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)
    # Call the compare_schedules function to find common time slots between the selected calendars
    common_time_slots = compare_schedules(user_info, selected_calendar_ids)
    # Render a template with the common time slots or return the data in a desired format
    return render_template('compare_schedules.html', common_time_slots=common_time_slots)  # render the compare
    # schedules page.


@app.route('/delete_calendar/<calendar_id>', methods=['POST', 'GET'])  # this is the route for the delete calendar page.
def delete_calendar(calendar_id):  # this is the function that handles the delete calendar page.
    # Get the user's info from the datastore and delete the calendar from the calendar list in the user's info entity.
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)
    # Remove the calendar from the calendar_list and delete the calendar from the user's calendar.
    calendar_list = user_info['calendar_list']  # get the calendar list from the user's info.
    calendar_list = [calendar for calendar in calendar_list if calendar['calendar_id'] != calendar_id]
    # Update the user's info with the updated calendar list and delete the calendar from the user's calendar.
    user_info.update({'calendar_list': calendar_list})  # update the user's info with the updated calendar list.
    datastore_client.put(user_info)  # update the user's info in the datastore.
    # Redirect to the main page or render a template with the updated calendar list or return the data in a desired
    # format.
    return redirect('delete_calendar.html')  # redirect to the delete calendar page.


@app.route('/create_calendar', methods=['POST', 'GET'])  # this is the route for the create calendar page.
def create_calendar():
    calendar_name = request.form.get('calendar_name')
    if not calendar_name:
        return render_template('index.html', error="Please provide a calendar name.")
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    if not claims:
        return render_template('index.html', error='Authentication failed')
    claims.get('sub')
    user_info = retrieveUserInfo(claims)
    calendar_id = str(uuid.uuid4())  # generate a unique identifier for the new calendar
    add_calendar(user_info, calendar_name, "", calendar_id, False)
    return redirect('index.html')


@app.route('/edit_calendar/<calendar_id>', methods=['GET', 'POST'])  # this is the route for the edit calendar page.
def edit_calendar(calendar_id):  # this is the function that handles the edit calendar page.
    id_token = request.cookies.get("token")  # get the id token from the cookies.
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)  # get the user's info from the datastore.
    calendar = next((cal for cal in user_info['calendar_list'] if cal['calendar_id'] == calendar_id), None)
    if not calendar:  # if the calendar is not found.
        return "Calendar not found", 404  # return the calendar not found page.
    return render_template('edit_calendar.html', calendar=calendar, calendar_id=calendar_id)  # render the edit
    # calendar page.


@app.route('/update_calendar/<calendar_id>', methods=['GET', 'POST'])  # this is the route for the update calendar page.
def update_calendar(calendar_id):  # this is the function that handles the update calendar page.
    calendar_name = request.form['calendar_name']  # get the calendar name from the form.
    id_token = request.cookies.get("token")
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)
    calendar_list = user_info['calendar_list']  # get the calendar list from the user's info.
    for calendar in calendar_list:  # update the calendar name in the calendar list.
        if calendar['calendar_id'] == calendar_id:  # if the calendar id matches the calendar id in the calendar list.
            calendar['calendar_name'] = calendar_name  # update the calendar name.
            break
    user_info.update({'calendar_list': calendar_list})  # update the user's info with the updated calendar list.
    datastore_client.put(user_info)
    return redirect('update_calendar.html')


@app.route('/search_events', methods=['GET', 'POST'])  # this is the route for the search events page.
def search_events():  # this is the function that handles the search events page.
    search_query = request.args.get('search_query', '').lower()  # get the search query from the form.
    id_token = request.cookies.get("token")  # get the id token from the cookies.
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)  # get the user's info from the datastore.
    event_list = user_info['event_list']  # get the event list from the user's info.
    # Filter events based on the search query and return the matching events to the search results page.
    matching_events = [event for event in event_list if search_query in event['event_name'].lower()]
    return render_template('search_results.html', events=matching_events)


@app.route('/recent_events', methods=['GET', 'POST'])  # this is the route for the search events page.
def recent_events():  # this is the function that handles the search events page.
    search_query = request.args.get('search_query', '').lower()  # get the search query from the form.
    id_token = request.cookies.get("token")  # get the id token from the cookies.
    claims = google.oauth2.id_token.verify_firebase_token(id_token, firebase_request_adapter)
    user_info = retrieveUserInfo(claims)  # get the user's info from the datastore.
    # Get the user's calendar keys from the user's info entity and initialize an empty
    # list for event_list to store the events.
    calendar_keys = user_info.get('calendar_keys', [])
    # Initialize an empty list for event_list to store the events.
    event_list = []
    # Iterate through the calendar keys and fetch the events from each calendar.
    for calendar_key in calendar_keys:  # get the events from each calendar.
        calendar = datastore_client.get(calendar_key)  # get the calendar from the datastore.
        event_list.extend(calendar.get('event_list', []))
        # Filter events based on the search query and return the matching events to the search results page.
    matching_events = [event for event in event_list if search_query in event['event_name'].lower()]
    # Filter events from the past week and return the matching events to the recent events page.
    now = datetime.now()  # get the current date and time.
    one_week_ago = now - timedelta(days=7)  # 7 days ago from now.
    recent_events_list = [event for event in event_list if one_week_ago <= event['event_start'] <= now]
    return render_template('recent_events.html', events=matching_events, recent_events=recent_events_list)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
