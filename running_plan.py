from datetime import datetime, date, timedelta
import xlsxwriter
import calendar
from dateutil.relativedelta import *
import StringIO

today = datetime.today()
start_date = today+relativedelta(days=-2)
end_date = "2017-05-27"
enddate = datetime.strptime(end_date, "%Y-%m-%d")


def round_quarter(x):
    return round(x * 4) / 4.0

def calculate_days_in_last_week(end_date):
    end_day = end_date.weekday()
    days_in_last_week = end_day + 1
    return days_in_last_week

def calculate_start_date(today_date):
    start_date = today_date+relativedelta(days=+1)
    return start_date

def calculate_days_in_first_week(start_date):
    start_date_day = start_date.weekday()
    days_in_first_week = 7 - start_date_day
    return days_in_first_week

def calculate_number_of_weeks_to_goal(start_date, end_date): 
    days_to_goal = (end_date - start_date).days
    days_in_first_week = calculate_days_in_first_week(start_date)
    days_in_last_week = calculate_days_in_last_week(end_date)
    weeks_to_goal = ((days_to_goal - days_in_first_week - days_in_last_week) / 7) + 1
    return weeks_to_goal

def generate_first_week_of_runs(start_date_day, start_date, increment,current_ability):
    # Create run distances for first week
    long_run = float('%.2f' % (current_ability))
    mid_run = long_run/2
    short_run = long_run/4

    week_one = {}

    # Create runs for first week if start date is something other than a Monday - base week
    if start_date_day == 1:
        week_one[str(start_date+relativedelta(days=-1))] = 0
        week_one[str(start_date)] = short_run
        week_one[str(start_date+relativedelta(days=+1))] = 0
        week_one[str(start_date+relativedelta(days=+2))] = mid_run
        week_one[str(start_date+relativedelta(days=+3))] = 0
        week_one[str(start_date+relativedelta(days=+4))] = short_run
        week_one[str(start_date+relativedelta(days=+5))] = long_run

    elif start_date_day == 2:
        week_one[str(start_date+relativedelta(days=-2))] = 0
        week_one[str(start_date+relativedelta(days=-1))] = 0
        week_one[str(start_date)] = short_run
        week_one[str(start_date+relativedelta(days=+1))] = 0
        week_one[str(start_date+relativedelta(days=+2))] = mid_run
        week_one[str(start_date+relativedelta(days=+3))] = 0
        week_one[str(start_date+relativedelta(days=+4))] = long_run
       
    elif start_date_day == 3:
        week_one[str(start_date+relativedelta(days=-3))] = 0
        week_one[str(start_date+relativedelta(days=-2))] = 0
        week_one[str(start_date+relativedelta(days=-1))] = 0
        week_one[str(start_date)] = short_run
        week_one[str(start_date+relativedelta(days=+1))] = 0
        week_one[str(start_date+relativedelta(days=+2))] = mid_run
        week_one[str(start_date+relativedelta(days=+3))] = long_run
        
    elif start_date_day == 4:
        week_one[str(start_date+relativedelta(days=-4))] = 0
        week_one[str(start_date+relativedelta(days=-3))] = 0
        week_one[str(start_date+relativedelta(days=-2))] = 0
        week_one[str(start_date+relativedelta(days=-1))] = 0
        week_one[str(start_date)] = short_run
        week_one[str(start_date+relativedelta(days=+1))] = 0
        week_one[str(start_date+relativedelta(days=+2))] = mid_run
     
    elif start_date_day == 5:
        week_one[str(start_date+relativedelta(days=-5))] = 0
        week_one[str(start_date+relativedelta(days=-4))] = 0
        week_one[str(start_date+relativedelta(days=-3))] = 0
        week_one[str(start_date+relativedelta(days=-2))] = 0
        week_one[str(start_date+relativedelta(days=-1))] = 0
        week_one[str(start_date)] = short_run
        week_one[str(start_date+relativedelta(days=+1))] = 0
       
    else:
        week_one[str(start_date+relativedelta(days=-6))] = 0
        week_one[str(start_date+relativedelta(days=-5))] = 0
        week_one[str(start_date+relativedelta(days=-4))] = 0
        week_one[str(start_date+relativedelta(days=-3))] = 0
        week_one[str(start_date+relativedelta(days=-2))] = 0
        week_one[str(start_date+relativedelta(days=-1))] = 0
        week_one[str(start_date)] = short_run

    return week_one

def generate_middle_weeks_of_plan(weekly_plan, weeks_to_goal, start_date, current_ability, increment, start_week):

    for week in range(start_week, weeks_to_goal + 1):
        weekly_plan[week] = {}
        long_run = float('%.2f' % (current_ability + ((week - start_week) * increment)))
        typical_week = [long_run/2, 0, long_run/4, long_run/2, 0, long_run/4, long_run]
        for i in range(7):
            weekly_plan[week][str(start_date+relativedelta(days=+i))] = round_quarter(typical_week[i])
        start_date = start_date+relativedelta(weeks=+1)

    return (weekly_plan, start_date)

def generate_second_to_last_week_of_plan(weekly_plan, weeks_to_goal, current_ability, start_date):
    
    weekly_plan[weeks_to_goal + 1] = {}
    for i in range(7):
        long_run = float(current_ability)
        typical_week = [long_run/2, 0, long_run/4, long_run/2, 0, long_run/4, long_run]
        weekly_plan[weeks_to_goal + 1][str(start_date+relativedelta(days=+i))] = round_quarter(typical_week[i]) 

    return weekly_plan


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

        weekly_plan, start_date = generate_middle_weeks_of_plan(weekly_plan, weeks_to_goal, start_date, current_ability, increment, 1)
        weekly_plan = generate_second_to_last_week_of_plan(weekly_plan, weeks_to_goal, current_ability, start_date)
    
    # Generate runs for weeks 2 to # of weeks
    else:
        weekly_plan[1] = generate_first_week_of_runs(start_date_day, start_date, increment,current_ability)
         # Start date for first full week will be the Monday after the start_date
        first_date = start_date+relativedelta(weekday=MO)
        weekly_plan, start_date = generate_middle_weeks_of_plan(weekly_plan, weeks_to_goal, first_date, current_ability, increment, 2)
        second_to_last_week_monday = end_date+relativedelta(weekday=MO(-2))
        # Second to last week will be the same as the first week
        weekly_plan = generate_second_to_last_week_of_plan(weekly_plan, weeks_to_goal, current_ability, second_to_last_week_monday)

    # Generate last week of runs based on the number of days in the last week
    weekly_plan[weeks_to_goal + 2] = {}       
    if end_day == 1:
        weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
        
    elif end_day == 2:
        weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0

    elif end_day == 3:
        weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)

    elif end_day == 4:
        weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-4))] = 0

    elif end_day == 5:
        weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-4))] = 0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/4)

    elif end_day == 6:
        weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-2))] = 0.0
        if goal_distance < 4:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = 1.0 
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-4))] = 0.0
        if goal_distance > 20:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/6)
        elif goal_distance < 4:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/3)
        else:
            weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/3)
        weekly_plan[weeks_to_goal + 2][str(end_date+relativedelta(days=-6))] = round_quarter(goal_distance/4)
    else:
        weekly_plan[weeks_to_goal + 2][str(end_date)] = goal_distance

    return weekly_plan

    # Nice format for test printing
    # for week in sorted(weekly_plan.keys()):
    #     for date in sorted(weekly_plan[week].keys()):
    #         print week, date, weekly_plan[week][date]



def build_plan_no_weeks(today_date, end_date, current_ability, goal_distance):
    """Generates plan using a list of lists, where each internal list includes
    all the runs for the week at that index.

    Long runs are incremented by the increment each week.
    Mid-week runs are 10 percent or 20 percent of the long-run.
    There are two off days with zero mileage. 

    """

    # Number of days from start date to goal
    days_to_goal = (end_date - today_date).days

    # Number of days in first week
    start_date = today_date+relativedelta(days=+1)
    start_date_day = start_date.weekday()
    days_in_first_week = 7 - start_date_day
    end_day = end_date.weekday()
    days_in_last_week = end_day + 1
    weeks = ((days_to_goal - days_in_first_week - days_in_last_week) / 7) + 1

    # Create run distances for first week
    long_run = float('%.2f' % (current_ability))
    mid_run = long_run/2
    short_run = long_run/4

    # Create an empty dictionary to hold the runs each week
    weekly_plan = {}

    # Create all runs if start date is a Monday
    if start_date_day == 0:
        increment = (goal_distance - current_ability) / float(weeks)
        print increment

        for week in range(1, weeks + 1):
            long_run = float('%.2f' % (current_ability + ((week - 1) * increment)))
            typical_week = [long_run/2, 0, long_run/4, long_run/2, 0, long_run/4, long_run]
            for i in range(7):
                weekly_plan[str(start_date+relativedelta(days=i))] = round_quarter(typical_week[i])
            start_date = start_date+relativedelta(weeks=+1)

        # Last full week will be the same as the first week
        for i in range(7):
            long_run = float(current_ability)
            typical_week = [long_run/2, 0, long_run/4, long_run/2, 0, long_run/4, long_run]
            weekly_plan[str(start_date+relativedelta(days=i))] = round_quarter(typical_week[i]) 
    
    # Create runs for first week if start date is something other than a Monday - base week
    else:
        increment = (goal_distance - current_ability) / (weeks)
        if start_date_day == 1:
            weekly_plan[str(start_date+relativedelta(days=-1))] = 0
            weekly_plan[str(start_date)] = short_run
            weekly_plan[str(start_date+relativedelta(days=+1))] = 0
            weekly_plan[str(start_date+relativedelta(days=+2))] = mid_run
            weekly_plan[str(start_date+relativedelta(days=+3))] = 0
            weekly_plan[str(start_date+relativedelta(days=+4))] = short_run
            weekly_plan[str(start_date+relativedelta(days=+5))] = long_run

        elif start_date_day == 2:
            weekly_plan[str(start_date+relativedelta(days=-2))] = 0
            weekly_plan[str(start_date+relativedelta(days=-1))] = 0
            weekly_plan[str(start_date)] = short_run
            weekly_plan[str(start_date+relativedelta(days=+1))] = 0
            weekly_plan[str(start_date+relativedelta(days=+2))] = mid_run
            weekly_plan[str(start_date+relativedelta(days=+3))] = 0
            weekly_plan[str(start_date+relativedelta(days=+4))] = long_run
           
        elif start_date_day == 3:
            weekly_plan[str(start_date+relativedelta(days=-3))] = 0
            weekly_plan[str(start_date+relativedelta(days=-2))] = 0
            weekly_plan[str(start_date+relativedelta(days=-1))] = 0
            weekly_plan[str(start_date)] = short_run
            weekly_plan[str(start_date+relativedelta(days=+1))] = 0
            weekly_plan[str(start_date+relativedelta(days=+2))] = mid_run
            weekly_plan[str(start_date+relativedelta(days=+3))] = long_run
            
        elif start_date_day == 4:
            weekly_plan[str(start_date+relativedelta(days=-4))] = 0
            weekly_plan[str(start_date+relativedelta(days=-3))] = 0
            weekly_plan[str(start_date+relativedelta(days=-2))] = 0
            weekly_plan[str(start_date+relativedelta(days=-1))] = 0
            weekly_plan[str(start_date)] = short_run
            weekly_plan[str(start_date+relativedelta(days=+1))] = 0
            weekly_plan[str(start_date+relativedelta(days=+2))] = mid_run
         
        elif start_date_day == 5:
            weekly_plan[str(start_date+relativedelta(days=-5))] = 0
            weekly_plan[str(start_date+relativedelta(days=-4))] = 0
            weekly_plan[str(start_date+relativedelta(days=-3))] = 0
            weekly_plan[str(start_date+relativedelta(days=-2))] = 0
            weekly_plan[str(start_date+relativedelta(days=-1))] = 0
            weekly_plan[str(start_date)] = short_run
            weekly_plan[str(start_date+relativedelta(days=+1))] = 0
           
        else:
            weekly_plan[str(start_date+relativedelta(days=-6))] = 0
            weekly_plan[str(start_date+relativedelta(days=-5))] = 0
            weekly_plan[str(start_date+relativedelta(days=-4))] = 0
            weekly_plan[str(start_date+relativedelta(days=-3))] = 0
            weekly_plan[str(start_date+relativedelta(days=-2))] = 0
            weekly_plan[str(start_date+relativedelta(days=-1))] = 0
            weekly_plan[str(start_date)] = short_run

        # Start date for first full week will be the Monday after the start_date
        first_date = start_date+relativedelta(weekday=MO)

        # Generate runs for weeks 2 to # of weeks
        for week in range(2, weeks + 2):
            long_run = float('%.2f' % (current_ability + ((week - 2) * increment)))
            typical_week = [long_run/2, 0, long_run/4, long_run/2, 0, long_run/4, long_run]
            for i in range(7):
                weekly_plan[str(first_date+relativedelta(days=i))] = round_quarter(typical_week[i])
            first_date = first_date+relativedelta(weeks=+1)
        
        # Second to last week will be the same as the first week
        second_to_last_week_monday = end_date+relativedelta(weekday=MO(-2))
        for i in range(7):
            long_run = float(current_ability)
            typical_week = [long_run/2, 0, long_run/4, long_run/2, 0, long_run/4, long_run]
            weekly_plan[str(second_to_last_week_monday+relativedelta(days=i))] = round_quarter(typical_week[i]) 


    # Generate last week of runs based on the number of days in the last week    
    if end_day == 1:
        weekly_plan[str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 1.0
        
    elif end_day == 2:
        weekly_plan[str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[weeks + 2][str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[str(end_date+relativedelta(days=-2))] = 0

    elif end_day == 3:
        weekly_plan[str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[str(end_date+relativedelta(days=-2))] = 0
        weekly_plan[str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)

    elif end_day == 4:
        weekly_plan[str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[str(end_date+relativedelta(days=-2))] = 0
        weekly_plan[str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
        weekly_plan[str(end_date+relativedelta(days=-4))] = 0

    elif end_day == 5:
        weekly_plan[str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[str(end_date+relativedelta(days=-2))] = 0
        weekly_plan[str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
        weekly_plan[str(end_date+relativedelta(days=-4))] = 0
        weekly_plan[str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/4)

    elif end_day == 6:
        weekly_plan[str(end_date)] = goal_distance
        if goal_distance >= 10:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 3.0
        else:
            weekly_plan[str(end_date+relativedelta(days=-1))] = 1.0
        weekly_plan[weeks + 2][str(end_date+relativedelta(days=-2))] = 0.0
        if goal_distance < 4:
            weekly_plan[str(end_date+relativedelta(days=-3))] = 1.0 
        else:
            weekly_plan[str(end_date+relativedelta(days=-3))] = round_quarter(goal_distance/4)
        weekly_plan[str(end_date+relativedelta(days=-4))] = 0.0
        if goal_distance > 20:
            weekly_plan[str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/6)
        elif goal_distance < 4:
            weekly_plan[str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/3)
        else:
            weekly_plan[str(end_date+relativedelta(days=-5))] = round_quarter(goal_distance/3)
        weekly_plan[str(end_date+relativedelta(days=-6))] = round_quarter(goal_distance/4)
    else:
        weekly_plan[str(end_date)] = goal_distance

    return weekly_plan

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

    row = 0
    col = 1
    weekdays = calendar.day_abbr

    for day in weekdays:
        worksheet.write(row, col, day)
        col += 1

    row = 1
    col = 0
    for i in range(1, len(weekly_plan) + 1):
        week = "Week %s" % i
        worksheet.write(row, col, week)
        print i
        for day in sorted(weekly_plan[str(i)]):
            worksheet.write(row, col + 1, "%s: %s" % (day[5:10], weekly_plan[str(i)][day]))
            col +=1
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
        print """We're sorry, but it will be very difficult for you to achieve 
        your goal in the time that you have. Please consider a race that 
        will provide you with more weeks for training."""

    if (goal_distance * .8) <= current_ability:
        print """We believe that you already have the ability to achieve your goal. 
        If you would like to try a longer race or goal, we would be happy to assist you!"""




