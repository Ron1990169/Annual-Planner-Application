This document is an academic report submitted by Rohin Mehra for Assignment 2 at Griffith College Dublin, as part of the Big Data Analysis and Management department. 
The report provides a detailed overview of a Flask-based application designed to manage user calendars and events. 
The application offers a range of functionalities, including user management, calendar creation and sharing, event management, and schedule comparison. 
Below is a summary of the key functions and routes described in the report:

User Management:
createUserInfo(claims): Creates a new user entity in the datastore, storing user information such as email and name.
retrieveUserInfo(claims): Retrieves existing user information from the datastore or creates a new record if it doesn't exist.

Calendar Management:
add_calendar(user_info, calendar_name, ...): Adds a new calendar for a user, with optional features like shared status.
share_calendar(user_info, calendar_id, recipient_email): Shares a user's calendar with another user by adding the recipient to the calendar's shared list.
delete_calendar(calendar_id): Removes a calendar from the user's list of calendars.
update_calendar(calendar_id): Updates the name of a calendar specified by its unique ID.

Event Management:
add_event(user_info, day, month, year, ...): Adds a new event to a user's calendar, including details such as date, time, and description.
update_event(event_id): Updates the details of an existing event based on its ID.
delete_event(event_id): Deletes a specific event from the user's calendar.
recent_events(user_info, days=7): Retrieves events from the past week for the user.

Schedule Comparison:
compare_schedules(user_info, selected_calendar_ids): Compares multiple calendars to find common free time slots between them.

Flask Routes:
@app.route('/login'): Manages user login, verifying credentials and setting session variables.
@app.route('/logout'): Logs out the user by clearing session data.
@app.route('/'): Handles the home page, retrieving or creating user information and rendering the main interface.
@app.route('/create_calendar'): Displays a page for creating a new calendar.
@app.route('/edit_calendar/<calendar_id>'): Provides functionality to edit an existing calendar.
@app.route('/create_event'): Manages the creation of new events.
@app.route('/edit_event/<event_id>'): Allows users to edit details of an existing event.
@app.route('/compare_schedules'): Enables users to compare schedules across selected calendars.
@app.route('/search_events'): Implements a search feature for finding specific events.
@app.route('/recent_events'): Displays a list of recent events that have occurred in the last week.

Key Features:
User Authentication: Secure user sessions are managed using Firebase authentication.
Data Storage: All user, calendar, and event data is stored in Google Datastore.
Event Sharing: Facilitates sharing of calendars and events with other users for collaboration.
Schedule Comparison: Identifies common free time slots across multiple calendars.
