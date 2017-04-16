from datetime import datetime, date, timedelta
import xlsxwriter
import calendar
from dateutil.relativedelta import *
import StringIO


# today = datetime.today()
# start_date = today+relativedelta(days=-2)
# end_date = "2017-05-27"
# enddate = datetime.strptime(end_date, "%Y-%m-%d")


def round_quarter(x):
    """Rounds the given number to the nearest quarter."""

    return round(x * 4) / 4.0


def calculate_days_in_last_week(end_date):
    """Calculates the number of days in the last week of the running plan."""

    end_day = end_date.weekday()
    days_in_last_week = end_day + 1
    return days_in_last_week


def calculate_start_date(today_date):
    """Calculates the start date for the running plan. For now, it will be the
    day after the plan is generated.
    """

    start_date = today_date+relativedelta(days=+1)

    return start_date


def calculate_days_in_first_week(start_date):
    """Calculate the number of days in the first week of the running plan."""

    start_date_day = start_date.weekday()
    days_in_first_week = 7 - start_date_day
    return days_in_first_week


def calculate_number_of_weeks_to_goal(start_date, end_date):
    """Calculate the number of full rounded weeks in the running plan."""

    days_to_goal = (end_date - start_date).days
    days_in_first_week = calculate_days_in_first_week(start_date)
    days_in_last_week = calculate_days_in_last_week(end_date)
    weeks_to_goal = ((days_to_goal - days_in_first_week - days_in_last_week) / 7) + 1
    return weeks_to_goal


def generate_first_week_of_runs(start_date_day, start_date, increment, current_ability):
    """Generate the first week of runs for the running plan. This will depend on
    which day of the week the plan starts. It is meant to help the runner build
    a base before diving into their plan.
    """

    # Create run distances for first week
    long_run = float('%.2f' % (current_ability))
    mid_run = long_run/2
    short_run = long_run/4

    week_one = {}

    monday_of_week_one = start_date + relativedelta(days=-start_date_day)

    if start_date_day == 1:
        week_one_workouts = [0.0, short_run, 0.0, mid_run, 0.0, short_run, long_run]
    elif start_date_day == 2:
        week_one_workouts = [0.0, 0.0, short_run, 0.0, mid_run, 0.0, long_run]
    elif start_date_day == 3:
        week_one_workouts = [0.0, 0.0, 0.0, short_run, 0.0, mid_run, long_run]
    elif start_date_day == 4:
        week_one_workouts = [0.0, 0.0, 0.0, 0.0, short_run, 0.0, mid_run]
    elif start_date_day == 5:
        week_one_workouts = [0.0, 0.0, 0.0, 0.0, 0.0, short_run, 0.0]
    else:
        week_one_workouts = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, short_run]

    for i in range(7):
        week_one[str(monday_of_week_one + relativedelta(days=(i)))] = week_one_workouts[i]

    return week_one



    # week_one_workouts {
    #                     1 : [short_run, 0.0, mid_run, 0.0, short_run, long_run],
    #                     2 : [short_run, 0.0, mid_run, 0.0, long_run],
    #                     3 : [short_run, 0.0, mid_run, long_run],
    #                     4 : [short_run, 0.0, mid_run],
    #                     5 : [short_run, 0.0],
    #                     6 : [short_run],
    #                   }



    # for day in range(start_date_day):
    #     week_one[deltas[-start_date_day] = week_one_workouts[day]

    # for day in range((-start_date_day), (7 - start_date_day)):
    #     week_one[day][]


    # for day in range(-start_date_day, star):
    #     week_one[deltas[-(day+1)]] = week_one_workouts[day]
    # for day in range(start_date_day, 7):
    #     week_one[deltas[day]] = week_one_workouts[day]

    # Create runs for first week if start date is something other than a Monday - base week
    # if start_date_day == 1:
    #     week_one[str(start_date+relativedelta(days=-1))] = 0
    #     week_one[str(start_date)] = short_run
    #     week_one[str(start_date+relativedelta(days=+1))] = 0
    #     week_one[str(start_date+relativedelta(days=+2))] = mid_run
    #     week_one[str(start_date+relativedelta(days=+3))] = 0
    #     week_one[str(start_date+relativedelta(days=+4))] = short_run
    #     week_one[str(start_date+relativedelta(days=+5))] = long_run

    # elif start_date_day == 2:
    #     week_one[str(start_date+relativedelta(days=-2))] = 0
    #     week_one[str(start_date+relativedelta(days=-1))] = 0
    #     week_one[str(start_date)] = short_run
    #     week_one[str(start_date+relativedelta(days=+1))] = 0
    #     week_one[str(start_date+relativedelta(days=+2))] = mid_run
    #     week_one[str(start_date+relativedelta(days=+3))] = 0
    #     week_one[str(start_date+relativedelta(days=+4))] = long_run
       
    # elif start_date_day == 3:
    #     week_one[str(start_date+relativedelta(days=-3))] = 0
    #     week_one[str(start_date+relativedelta(days=-2))] = 0
    #     week_one[str(start_date+relativedelta(days=-1))] = 0
    #     week_one[str(start_date)] = short_run
    #     week_one[str(start_date+relativedelta(days=+1))] = 0
    #     week_one[str(start_date+relativedelta(days=+2))] = mid_run
    #     week_one[str(start_date+relativedelta(days=+3))] = long_run
        
    # elif start_date_day == 4:
    #     week_one[str(start_date+relativedelta(days=-4))] = 0
    #     week_one[str(start_date+relativedelta(days=-3))] = 0
    #     week_one[str(start_date+relativedelta(days=-2))] = 0
    #     week_one[str(start_date+relativedelta(days=-1))] = 0
    #     week_one[str(start_date)] = short_run
    #     week_one[str(start_date+relativedelta(days=+1))] = 0
    #     week_one[str(start_date+relativedelta(days=+2))] = mid_run
     
    # elif start_date_day == 5:
    #     week_one[str(start_date+relativedelta(days=-5))] = 0
    #     week_one[str(start_date+relativedelta(days=-4))] = 0
    #     week_one[str(start_date+relativedelta(days=-3))] = 0
    #     week_one[str(start_date+relativedelta(days=-2))] = 0
    #     week_one[str(start_date+relativedelta(days=-1))] = 0
    #     week_one[str(start_date)] = short_run
    #     week_one[str(start_date+relativedelta(days=+1))] = 0
       
    # else:
    #     week_one[str(start_date+relativedelta(days=-6))] = 0
    #     week_one[str(start_date+relativedelta(days=-5))] = 0
    #     week_one[str(start_date+relativedelta(days=-4))] = 0
    #     week_one[str(start_date+relativedelta(days=-3))] = 0
    #     week_one[str(start_date+relativedelta(days=-2))] = 0
    #     week_one[str(start_date+relativedelta(days=-1))] = 0
    #     week_one[str(start_date)] = short_run




def generate_middle_weeks_of_plan(weekly_plan, weeks_to_goal, start_date, current_ability, increment, start_week):
    """Generate the middle weeks of the running plan. This is where the runner
    is ramping his/her mileage by the calculated increment each week.
    """

    for week in range(start_week, weeks_to_goal + 1):
        weekly_plan[week] = {}
        long_run = float('%.2f' % (current_ability + ((week - start_week) * increment)))
        mid_run = long_run/2
        short_run = long_run/4
        typical_week_workouts = [mid_run, 0, short_run, mid_run, 0, short_run, long_run]
        for i in range(7):
            weekly_plan[week][str(start_date+relativedelta(days=+i))] = round_quarter(typical_week_workouts[i])
        start_date = start_date+relativedelta(weeks=+1)

    return (weekly_plan, start_date)


def generate_second_to_last_week_of_plan(weekly_plan, weeks_to_goal, current_ability, start_date):
    """Generates the second to last week of the running plan. This week will be
    the same as the first week of the plan to help the runner taper mileage leading
    up to their goal / event.
    """

    long_run = float(current_ability)
    short_run = long_run/4
    mid_run = long_run/2
    week = weeks_to_goal + 1

    weekly_plan[week] = {}
    for i in range(7):
        typical_week_workouts = [mid_run, 0, short_run, mid_run, 0, short_run, long_run]
        weekly_plan[week][str(start_date+relativedelta(days=+i))] = round_quarter(typical_week_workouts[i])

    return weekly_plan


def generate_last_week_of_plan(weekly_plan, weeks_to_goal, goal_distance, current_ability, end_day, end_date):
    """Generates the last week of the running plan depending on when the event/
    goal will take place.
    """
     
    quarter_goal = round_quarter(goal_distance/4)
    third_goal = round_quarter(goal_distance/3)
    sixth_goal = round_quarter(goal_distance/6)

    less_than_ten_goal_plan = [goal_distance, 1.0, 0.0, quarter_goal, 0.0, quarter_goal]
    more_than_ten_goal_plan = [goal_distance, 3.0, 0.0, quarter_goal, 0.0, quarter_goal]

    less_than_four_goal_plan_seven_days = [goal_distance, 1.0, 0.0, 1.0 , 0.0, third_goal, quarter_goal]
    less_than_twenty_goal_plan_seven_days = [goal_distance, 3.0, 0.0, quarter_goal, 0.0, third_goal, quarter_goal]
    more_than_twenty_goal_plan_seven_days = [goal_distance, 3.0, 0.0, quarter_goal, 0.0, sixth_goal, quarter_goal]


    if end_day <= 5:
        if goal_distance < 10:
            last_week_workouts = less_than_ten_goal_plan
        else:
            last_week_workouts = more_than_ten_goal_plan
    else:
        if goal_distance < 4:
            last_week_workouts = less_than_four_goal_plan_seven_days
        elif goal_distance <= 20:
            last_week_workouts = less_than_twenty_goal_plan_seven_days
        else:
            last_week_workouts = more_than_twenty_goal_plan_seven_days

    deltas = {}
    for i in range(7):
        deltas[i] = str(end_date + relativedelta(days=(-i)))

    week = weeks_to_goal + 2
    weekly_plan[week] = {}

    for day in range(end_day+1):
        weekly_plan[week][deltas[day]] = last_week_workouts[day]

    return weekly_plan


    # last_week_structure = {
    # 1: {3: small_run,
    #     5: quarter_run,
    #     6: big_run},
    # 2: {

    # }

    # structure_to_enforce = last_week_structure[end_date]

    # deltas = {
    #           0 : str(end_date),
    #           1 : str(end_date + relativedelta(days=-1)),
    #           2 : str(end_date + relativedelta(days=-2)),
    #           3 : str(end_date + relativedelta(days=-3)),
    #           4 : str(end_date + relativedelta(days=-4)),
    #           5 : str(end_date + relativedelta(days=-5)),
    #           6 : str(end_date + relativedelta(days=-6))
    #           }

    

    # last_week_structure_over_ten_mile_goal = {
    # 1 : {0 : goal_distance,
    #     -1 : 3.0,
    #     }
    # 2 : {0 : goal_distance,
    #     -1 : 3.0,
    #     -2 : 0.0,
    #     }
    # 3 : {0 : goal_distance,
    #     -1 : 3.0,
    #     -2 : 0.0,
    #     -3 : quarter_goal,
    #     }
    # 4 : {0 : goal_distance,
    #     -1 : 3.0,
    #     -2 : 0.0,
    #     -3 : quarter_goal,
    #     -4 : 0.0,
    #     }
    # 5 : {0 : goal_distance,
    #     -1 : 3.0,
    #     -2 : 0.0,
    #     -3 : quarter_goal,
    #     -4 : 0.0,
    #     -5 : quarter_goal,
    #     }
    # }

    # last_week_structure_under_ten_mile_goal = {
    # 1 : {0 : goal_distance,
    #     -1 : 1.0,
    #     }
    # 2 : {0 : goal_distance,
    #      -1 : 1.0,
    #      -2 : 0.0,
    #     }
    # 3 : {0 : goal_distance,
    #     -1 : 1.0,
    #     -2 : 0.0,
    #     -3 : quarter_goal
    # }
    # 4 : {0 : goal_distance,
    #     -1 : 1.0,
    #     -2 : 0.0,
    #     -3 : quarter_goal,
    #     -4 : 0.0,
    #     }
    # 5 : {0 : goal_distance,
    #     -1 : 1.0,
    #     -2 : 0.0,
    #     -3 : quarter_goal,
    #     -4 : 0.0,
    #     -5 : quarter_goal,
    #     }


    # weekly_plan[weeks_to_goal + 2] = {}
    # if end_day == 1:
    #     weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
    #     if goal_distance >= 10:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
  
    # elif end_day == 2:
    #     weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
    #     if goal_distance >= 10:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0

    # elif end_day == 3:
    #     weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
    #     if goal_distance >= 10:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)

    # elif end_day == 4:
    #     weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
    #     if goal_distance >= 10:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-4))] = 0

    # elif end_day == 5:
    #     weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
    #     if goal_distance >= 10:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-4))] = 0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/4)

    # elif end_day == 6:
    #     weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
    #     if goal_distance >= 10:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0.0
    #     if goal_distance < 4:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = 1.0 
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-4))] = 0.0
    #     if goal_distance > 20:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/6)
    #     elif goal_distance < 4:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/3)
    #     else:
    #         weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/3)
    #     weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-6))] = round_quarter(goal_distance/4)
    # else:
    #     weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance

    # last_week_over_ten = [goal_distance, 3.0, 0.0, quarter_goal, 0.0, quarter_goal]
    # last_week_under_ten = [goal_distance, 1.0, 0.0, quarter_goal, 0.0, quarter_goal]


def build_plan_with_two_dates(today_date, end_date, current_ability, goal_distance):
    """Generates a running plan that is a dictionary weeks as keys with a dictionary
    of dates:distance key:value pairs as values.

    Long runs are incremented by the increment each week.
    Mid-week runs are 10 percent or 20 percent of the long-run.
    There are two off days with zero mileage.
    """

    start_date = calculate_start_date(today_date)
    start_date_day = start_date.weekday()
    end_day = end_date.weekday()

    weeks_to_goal = calculate_number_of_weeks_to_goal(start_date, end_date)

    weekly_plan = {}
    increment = (goal_distance - current_ability) / float(weeks_to_goal)

    # Create all runs if start date is a Monday
    if start_date_day == 0:
        weekly_plan_start, start_date = generate_middle_weeks_of_plan(weekly_plan, weeks_to_goal, start_date, current_ability, increment, 1)
        weekly_plan_up_to_last_week = generate_second_to_last_week_of_plan(weekly_plan_start, weeks_to_goal, current_ability, start_date)
        weekly_plan_final = generate_last_week_of_plan(weekly_plan_up_to_last_week, weeks_to_goal, goal_distance, current_ability, end_day, end_date)

    # Generate runs if start date is not Monday
    else:
        weekly_plan[1] = generate_first_week_of_runs(start_date_day, start_date, increment, current_ability)

        # Start date for first full week will be the Monday after the start_date
        first_date = start_date+relativedelta(weekday=MO)

        weekly_plan_up_to_second_to_last_week, start_date = generate_middle_weeks_of_plan(weekly_plan, weeks_to_goal, first_date, current_ability, increment, 2)

        second_to_last_week_monday = end_date+relativedelta(weekday=MO(-2))

        # Second to last week will be the same as the first week
        weekly_plan_up_to_last_week = generate_second_to_last_week_of_plan(weekly_plan_up_to_second_to_last_week, weeks_to_goal, current_ability, second_to_last_week_monday)

        # Generate last week of runs based on the number of days in the last week
        weekly_plan_final = generate_last_week_of_plan(weekly_plan_up_to_last_week, weeks_to_goal, goal_distance, current_ability, end_day, end_date)

    # edgecase = handle_edgecases(increment, goal_distance, current_ability)

    # if not edgecase:
    return weekly_plan_final
    # else:
    #     return edgecase


def create_event_source(weekly_plan):
    """Creates objects in correct format to feed into calendar."""

    event_data = []
    for date in weekly_plan:
        if weekly_plan[date]:
            event_source = {}
            event_source['title'] = "%s miles" % weekly_plan[date]
            event_source['allDay'] = True
            event_source['start'] = date
            event_source['eventBackgroundColor'] = 'red'
            event_data.append(event_source)

    return event_data


def create_excel_workbook(weekly_plan, output):
    """Creates a new excel document with the running plan information"""

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('RunningPlan')
    # worksheet.write(row, col, some_data) rows & columns are zero indexed A1 is (0,0)

    # Add bold format
    bold = workbook.add_format({'bold': 1})
    format_header = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#DC0D0D', 'font_size': 14, 'align': 'center'})
    format_table = workbook.add_format({'font_size': 12, 'border': 1, 'border_color': '#c2c2fb'})
    row = 0
    col = 1
    weekdays = calendar.day_name

    for day in weekdays:
        worksheet.write(row, col, day, format_header)
        # worksheet.set_column(row, col, 17)
        col += 1

    row = 1
    col = 0
    for i in range(1, len(weekly_plan) + 1):
        week = "Week %s" % i
        worksheet.write(row, col, week, format_header)
        worksheet.set_column(row, col, 17)
        for day in sorted(weekly_plan[str(i)]):
            if weekly_plan[str(i)][day]:
                worksheet.write(row, col + 1, "%s:   %s miles" % (day[5:10], weekly_plan[str(i)][day]), format_table)
                col += 1
            else:
                worksheet.write(row, col + 1, "%s:   %s" % (day[5:10], 'Off day!'), format_table)
                col += 1
        row += 1
        col = 0

    workbook.set_properties({
    'title':    'Running Plan',
    'author':   'Run Holmes',
    'keywords': 'Run, Plan, Workout',
    })

    workbook.close()


def create_excel_text(weekly_plan):
    # Creates an instance of the StringIO class - a string object that holds a file in the form of a string buffer
    output = StringIO.StringIO()

    # Create_excel_workbook writes the information to the output instance of StringIO
    create_excel_workbook(weekly_plan, output)

    # Retrieves the entire contents of the "File"
    return output.getvalue()


def create_excel_doc(weekly_plan):
    filename = 'RunningPlan9.xlsx'
    create_excel_workbook(weekly_plan, filename)


def handle_edgecases(increment, goal_distance, current_ability):
    """Handles any edge cases that the user might encounter."""

    if increment > 1:
        return """We're sorry, but it will be very difficult for you to achieve 
        your goal in the time that you have. Please consider a race that 
        will provide you with more weeks for training."""

    elif (goal_distance * .8) <= current_ability:
        return """We believe that you already have the ability to achieve your goal. 
        If you would like to try a longer race or goal, we would be happy to assist you!"""

    else:
        return None
