"""Run Planner"""

from jinja2 import StrictUndefined
from flask import Flask, jsonify, render_template, redirect, request, flash, session, Response, url_for
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, Runner, Plan, Run
from datetime import datetime, date, timedelta, time
import pytz
from tzlocal import get_localzone
from apiclient import discovery as gcal_client
from oauth2client import client
import httplib2
from running_plan import create_excel_text, handle_edgecases, calculate_start_date, calculate_number_of_weeks_to_goal
from server_utilities import *
import random
from twilio import twiml
import sendgrid
import os
from sendgrid.helpers.mail import *

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "amcio9320e9wjadmclswep9q2-[ie290qfmvwnuq34op092iwopqk;dsmlcvq84yp9hrwafousdzncjlkx2[qOAPDSSGURW9EI"

app.jinja_env.undefined = StrictUndefined

@app.route('/')
def index():
    """Homepage."""

    today = calculate_today_date()
    year_from_today = today + timedelta(365)
    date_today = datetime.strftime(today, '%Y-%m-%d')
    date_year_from_today = datetime.strftime(year_from_today, '%Y-%m-%d')

    distances = range(2, 26)

    if session.get('admin'):
        redirect('/admin')
    try:
        session['runner_id']
    except KeyError:
        return render_template("homepage.html",
                                today=date_today,
                                yearaway=date_year_from_today,
                                distances=distances)

    return redirect("/dashboard")


@app.route('/plan.json', methods=["GET"])
def generate_plan():
    """Generates and displays a runner's plan based on the information
    they entered.
    """

    raw_current_ability = request.args.get("current-ability")
    raw_goal_distance = request.args.get("goal-distance")
    raw_end_date = request.args.get("goal-date")

    # try:
    weekly_plan = generate_weekly_plan(raw_current_ability, raw_goal_distance, raw_end_date)
    # except Exception, e:
    #     weekly_plan = {'response': "Please complete all fields before clicking 'Generate Plan'"}
    results = jsonify(weekly_plan)
    # response = Response(status=200)
    # response.mimetype = "application/json"

    # response.headers["Content-Type"] = "text/html"
    # print results
    # print response.headers
    # print response.mimetype
    return results


@app.route('/download', methods=["GET"])
def download_excel():
    """Creates an excel file and downloads it to the users computer."""

    weekly_plan = session.get('weekly_plan')

    # weekly_plan = session.get('weekly_plan')
    excel_text = create_excel_text(weekly_plan)

    # Create a response object that takes in the excel_text (string of excel doc) and the mimetime (format) for the doc
    response = Response(response=excel_text, status=200, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # Says the header will contain an attachement of the filename RunPlan.xlsx
    response.headers["Content-Disposition"] = "attachment; filename=RunPlan.xlsx"

    return response

@app.route('/sign-up')
def display_sign_up_page():
    """Sign-up Page."""

    weekly_plan = session.get('weekly_plan')

    if not weekly_plan:
        flash("Please complete all questions before trying to sign-up!")
        return redirect('/')

    else:
        return render_template('registration.html')


@app.route('/sign-up-complete', methods=["POST"])
def process_sign_up():
    """Checks if user exists. If not, creates new account."""

    raw_runner_email = request.form.get("email")
    raw_runner_password = request.form.get("password")
    email_query = Runner.query.filter_by(email=raw_runner_email).all()

    if email_query:
        flash('This user already exists. Please try to login or create an account with a different email.')
        return redirect('/')

    else:
        salt = generate_salt()
        hashed_password = generate_hashed_password(raw_runner_password, salt)

        current_runner = add_runner_to_database(raw_runner_email, hashed_password, salt)

        current_runner_id = current_runner.runner_id
        session['runner_id'] = current_runner_id

        current_plan = add_plan_to_database(current_runner_id)

        current_plan_id = current_plan.plan_id
        current_plan.name = "Running Plan %s" % current_plan_id
        db.session.commit()

        weekly_plan = session.get('weekly_plan')
        add_runs_to_database(weekly_plan, current_plan_id)

        return redirect('/dashboard')


@app.route('/login-complete', methods=["POST"])
def process_login():
    """Checks if user email and password exist on same account.
    If so, logs them into their account. If not, flashes a message.
    """

    raw_runner_email = request.form.get("email")
    raw_runner_password = request.form.get("password")

    if raw_runner_email == 'admin@admin.com' and raw_runner_password == 'cheese':
        session['admin'] = 'admin'
        return redirect('/admin')
    try:
        runner_account = Runner.query.filter_by(email=raw_runner_email).one()
    except Exception, e:
        runner_account = False

    if runner_account:
        hashed_password = generate_hashed_password(raw_runner_password, runner_account.salt)

    if runner_account and runner_account.password == hashed_password:
        session["runner_id"] = runner_account.runner_id
        return redirect('/dashboard')
    else:
        flash("Email or Password is incorrect. Please try again!")
        return redirect("/")


@app.route('/logout-complete')
def process_logout():
    """Logout user and clear their session."""

    session.clear()
    return redirect("/")


@app.route('/dashboard')
def display_runner_page():
    """Displays the runner's dashboard with current plan and tracking information."""

    times = range(1, 25)

    runner_id = session.get('runner_id')
    runner = Runner.query.get(runner_id)

    if not runner:
        return redirect('/')

    today_date = calculate_today_date()

    current_plan = db.session.query(Plan).join(Runner).filter(Runner.runner_id==runner_id,
                                                              Plan.end_date>=today_date).one()

    dates = generate_running_dates(current_plan.start_date, current_plan.end_date)

    if current_plan:
        days_left_to_goal = calculate_days_to_goal(today_date, current_plan.end_date)
        total_workouts_completed = calculate_total_workouts_completed(current_plan.runs)
        total_miles_completed = calculate_total_miles_completed(current_plan.runs)
    else:
        flash("It seems like all of your plans have expired. Feel free to click and view and old plan or make a new one!")

    weeks_in_plan = calculate_weeks_in_plan(current_plan)
    runs = {}
    for run in current_plan.runs:
        runs[run.date] = {'run_id': run.run_id,
                          'distance': run.distance,
                          'is_completed': run.is_completed}

    return render_template("runner_dashboard.html", runner=runner,
                                                    plan=current_plan,
                                                    runs=runs,
                                                    weeks_in_plan=weeks_in_plan,
                                                    days_left_to_goal=days_left_to_goal,
                                                    total_workouts_completed=total_workouts_completed,
                                                    total_miles_completed=total_miles_completed,
                                                    dates=dates,
                                                    times=times)


@app.route('/update-run.json', methods=["POST"])
def update_run_and_dashboard_as_completed():
    """When a runner clicks a run checkbox, updates run is_completed as true,
    commits updated run to database, and updates the total miles and total workouts
    completed on the dashboard.
    """

    run_id = request.form.get("run-id")
    update_run(run_id, True)
    result_data = gather_info_to_update_dashboard(run_id)

    return jsonify(result_data)


@app.route('/update-run-incomplete.json', methods=["POST"])
def update_run__and_dashboard_as_incompleted():
    """When a runner unclicks a run checkbox, updates run is_completed as false,
    commits updated run to database, and updates the total miles and total workouts
    completed on the dashboard.
    """

    run_id = request.form.get("run-id")
    update_run(run_id, False)
    result_data = gather_info_to_update_dashboard(run_id)

    return jsonify(result_data)


@app.route('/workout-info.json', methods=["GET"])
def return_workout_info_for_doughnut_chart():
    """Get info for workout doughnut chart."""

    today_date = calculate_today_date()
    runner_id = session.get('runner_id')
    print runner_id
    count_total_plan_runs = db.session.query(Run).join(Plan).join(Runner).filter(Runner.runner_id==runner_id, 
                                                                                 Plan.end_date>=today_date).count()
    count_plan_runs_completed = db.session.query(Run).join(Plan).join(Runner).filter(Runner.runner_id==runner_id, 
                                                                                     Plan.end_date>=today_date, 
                                                                                  Run.is_completed==True).count()
    workouts_remaining = count_total_plan_runs - count_plan_runs_completed
    
    data_dict = {
                "labels": [
                    "Total Workouts Completed", 
                    "Workouts Remaining"
                ],
                "datasets": [
                    {
                        "data": [count_plan_runs_completed, workouts_remaining],
                        "backgroundColor": [
                            "#FFED82",
                            "#B0E85F"
                        ],
                        "hoverBackgroundColor": [
                            "#37E8E4",
                            "0E60FF"
                        ]
                    }]
            }

    return jsonify(data_dict)


@app.route('/mileage-info.json', methods=["GET"])
def return_total_miles_info_for_doughnut_chart():
    """Get info for mileage doughnut chart."""

    today_date = calculate_today_date()
    runner_id = session.get('runner_id')
    runs_in_plan = db.session.query(Run).join(Plan).join(Runner).filter(Runner.runner_id==runner_id, 
                                                                                 Plan.end_date>=today_date).all()

    total_mileage = calculate_total_mileage(runs_in_plan)
    total_miles_completed = calculate_total_miles_completed(runs_in_plan)
    miles_remaining = total_mileage - total_miles_completed

    data_dict = {
                "labels": [
                    "Total Miles Completed",
                    "Total Miles Remaining"
                ],
                "datasets": [
                    {
                        "data": [total_miles_completed, miles_remaining],
                        "backgroundColor": [
                            "#37E8E4",
                            "#B0E85F"
                        ],
                        "hoverBackgroundColor": [
                            "#FFED82",
                            "0E60FF"
                        ]
                    }]
            }

    return jsonify(data_dict)

@app.route('/add-timezone-to-session', methods=["GET"])
def add_timezone_to_session():
    """Adds the users selected timezone to the session to be
    added to their Google Calendar.
    """

    timezone = request.args.get("time-zone")
    session['timezone'] = timezone
    message = {'message': 'timezone updated'}

    return jsonify(message)


@app.route('/add-start-time-to-session', methods=["GET"])
def add_start_time_to_session():
    """Adds the users selected run start time to the session to be
    added to their Google Calendar.
    """

    entered_start_time = request.args.get("cal-run-start-time")
    formatted_start_time = datetime.strptime(entered_start_time, '%H:%M')
    session['preferred_start_time'] = formatted_start_time

    message = {'message': 'start time updated'}

    return jsonify(message)

@app.route('/add-to-google-calendar', methods=["POST", "GET"])
def add_runs_to_runners_google_calendar_account():
    """Adds a runner's runs to their Google Calendar account."""

    # if request.method == "POST":
    #     timezone = request.form.get("time-zone")
    #     preferred_start_time = request.form.get("cal-run-start-time")
    #     session['timezone'] = timezone
    #     session['preferred_start_time'] = preferred_start_time

    timezone = session.get('timezone')
    preferred_start_time = session.get('preferred_start_time')

    # If there are no credentials in the current session, redirect to get oauth permisssions
    if not session.get('credentials'):
        return redirect(url_for('oauth2callback'))

    # Otherwise get the credentials
    credentials = client.OAuth2Credentials.from_json(session['credentials'])

    # If the credentials have expired, redirect to get oauth permissions
    if credentials.access_token_expired:
        return redirect(url_for('oauth2callback'))

    else:
        # Get the autorization to the user's google calendar
        http_auth = credentials.authorize(httplib2.Http())

        # Gather the user's google calendar using the authorization to add events
        calendar = gcal_client.build('calendar', 'v3', http_auth)

        runner_id = session.get('runner_id')
        update_runner_to_is_using_gCal(runner_id, True)

        today_date = calculate_today_date()
        current_plan = db.session.query(Plan).join(Runner).filter(Runner.runner_id == runner_id,
                                                                  Plan.end_date >= today_date).one()

        if current_plan:
            if timezone and preferred_start_time:
                run_events = generate_run_events_for_google_calendar(current_plan, timezone, preferred_start_time)
                del session['timezone']
                del session['preferred_start_time']
            elif timezone and not preferred_start_time:
                run_events = generate_run_events_for_google_calendar(current_plan, timezone, current_plan.start_time)
                del session['timezone']
            elif preferred_start_time and not timezone:
                run_events = generate_run_events_for_google_calendar(current_plan, "America/Los_Angeles", preferred_start_time)
                del session['preferred_start_time']
            else:
                run_events = generate_run_events_for_google_calendar(current_plan, "America/Los_Angeles", current_plan.start_time)
            if not run_events:
                flash('There are no new runs to add to your Google Calendar.')
            else:
                for event in run_events:
                    event_to_add = calendar.events().insert(calendarId='primary', body=event).execute()
                    flash('Added event to Google Calendar: %s on %s' % (event['summary'], event['start']['dateTime']))
                    print'Event created: %s' % (event_to_add.get('htmlLink'))
        else:
            flash('There are no new runs to add to your Google Calendar.')

    return redirect("/dashboard")


@app.route('/oauth2callback')
def oauth2callback():
    """Flow stores application secrets and site access we are requesting.
    Then, redirects the user to the authorization uri - site for them to login
    and/or provide permissions for the application to access their protected
    resources.
    """

    flow = client.flow_from_clientsecrets(
        'client_secret.json',
        scope='https://www.googleapis.com/auth/calendar',
        redirect_uri=url_for('oauth2callback', _external=True))
    if 'code' not in request.args:
        # Send user to email page & asks permission to send info to calendar
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        # answer from user re: using calendar, gives back oauth token to send info to calendar
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        add_oauth_token_to_database(credentials)
        return redirect(url_for('add_runs_to_runners_google_calendar_account'))


@app.route('/update-plan-name.json', methods=["POST"])
def update_plan_name():
    """Update plan name in the database"""

    new_name = request.form.get("newName")
    plan_id = request.form.get("planId")
    plan = Plan.query.get(plan_id)
    plan.name = new_name
    db.session.commit()

    results = {'newName': new_name}

    return jsonify(results)


@app.route('/update-account', methods=["POST"])
def update_account_settings():
    """Update user account settings based on preferences specified."""

    runner_id = session.get('runner_id')
    runner = Runner.query.get(runner_id)

    opt_email = request.form.get("opt-email")
    opt_text = request.form.get("opt-text")
    phone = request.form.get("phone-number")
    opt_gcal = request.form.get("opt-gcal")
    timezone = request.form.get("time-zone")
    start_time = request.form.get("cal-run-start-time")

    if runner.is_subscribed_to_email is not opt_email:
        update_runner_email_subscription(runner_id, opt_email)
    if runner.is_subscribed_to_texts is not opt_text:
        update_runner_text_subscription(runner_id, opt_text)
    if runner.is_using_gCal is not opt_gcal:
        update_runner_to_is_using_gCal(runner_id, opt_gcal)
        return redirect('/add-to-google-calendar')


    print "Opt_email is %s" % opt_email
    print "Opt_text is %s" % opt_text
    print "Opt_gcal is %s" % opt_gcal
    print "phone is %s" % phone
    print "timezone is %s" % timezone
    print "start_time is %s" % start_time

    return redirect("/dashboard")


@app.route('/opt-into-text-reminders.json', methods=["POST"])
def opt_into_text_reminders():
    """Opts the runner into receiving text reminders. Updates their phone number
    and is_subscribed_to_texts in the database.
    """

    runner_id = request.form.get('runnerId')
    raw_phone = request.form.get('phone')

    update_runner_text_subscription(runner_id, True)
    update_runner_phone(runner_id, raw_phone)

    return jsonify({'success': 'success!'})


@app.route('/opt-out-of-text-reminders.json', methods=["POST"])
def opt_out_of_text_reminders():
    """Opts the runner out of receiving text reminders and updates
    is_subscribed_to_texts to false in the database.
    """

    runner_id = request.form.get('runnerId')
    update_runner_text_subscription(runner_id, False)

    return jsonify({'success': 'success!'})


@app.route('/send-sms-reminders', methods=["POST"])
def send_sms_reminders():
    """Gets a list of runs for the day and sends an sms reminder to the runners."""

    run_date = request.form.get("run-date")
    if send_reminder_sms_messages(run_date):
        flash("Messages sent successfully!")
    else:
        flash("No messages sent.")

    return redirect('/admin')


@app.route('/admin')
def render_admin_page():
    """Displays the admin page."""

    if session.get('admin'):
        return render_template('admin.html')
    else:
        redirect('/')


@app.route('/inbound-text', methods=["POST"])
def receive_and_respond_to_inbound_text():
    """Receive and inbound text, update database and respond to the runner."""

    number = request.form.get('From')
    message_body = request.form.get('Body')
    resp = response_to_inbound_text(number, message_body)

    return str(resp)


@app.route('/send-emails', methods=["POST"])
def send_weekly_emails():
    """Gets list of users who have opted into weekly email sand then sends a
    weekly reminder email to them."""

    runners = send_email_reminders()
    if runners:
        flash("Emails sent successfully!")
    else:
        flash("No emails to send.")

    return redirect('/admin')


@app.route('/opt-into-email-reminders.json', methods=["POST"])
def opt_into_email_reminders():
    """Updates runner in database to receive text reminders."""

    response = request.form.get("subscription")
    runner_id = request.form.get("runnerId")

    if response == 'yes':
        runner = Runner.query.get(runner_id)
        runner.is_subscribed_to_email = True
        db.session.commit()
        return jsonify({"response": 'yes'})
    else:
        return jsonify({"response": 'no'})


@app.route('/opt-out-of-email-reminders.json', methods=["POST"])
def opt_out_of_email_reminders():
    """Opt user out of emails by updating the database."""

    runner_id = request.form.get("runnerId")
    runner = Runner.query.get(runner_id)
    runner.is_subscribed_to_email = False
    db.session.commit()

    return jsonify({"response": "done"})


@app.route('/dailymile-oauth2callback')
def dailymile_oauth2callback():
    """Flow stores application secrets and site access we are requesting.
    Then, redirects the user to the authorization uri - site for them to login
    and/or provide permissions for the application to access their protected
    resources.
    """

    CLIENT_ID = os.environ['DAILYMILE_ACCOUNT_ID']
    DAILYMILE_SECRET = os.environ['DAILYMILE_SECRET']


    oauth = OAuth()

    dmile = oauth.remote_app(
        'dailymile',
        consumer_key=CLIENT_ID,
        consumer_secret=DAILYMILE_SECRET,
        request_token_params={'scope': 'email,statuses_to_me_read'},
        base_url='https://api.weibo.com/2/',
        authorize_url='https://api.weibo.com/oauth2/authorize',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://api.weibo.com/oauth2/access_token',

        # force to parse the response in applcation/json
        content_type='application/json',
    )

    flow = client.flow_from_clientsecrets(
        'secrets.sh',
        scope='https://api.dailymile.com/oauth/authorize?',
        redirect_uri=url_for('display_runner_page')
        )
    if 'code' not in request.args:
        # Send user to email page & asks permission to send info to calendar
        auth_uri = flow.step1_get_authorize_url()
        return redirect(auth_uri)
    else:
        # answer from user re: using calendar, gives back oauth token to send info to calendar
        auth_code = request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        session['credentials'] = credentials.to_json()
        add_oauth_token_to_database(credentials)
        return redirect(url_for('add_runs_to_runners_google_calenadr_account'))




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
