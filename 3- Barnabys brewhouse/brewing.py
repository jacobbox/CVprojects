"""This module implements process and inventory management, future demand and
product stock predictions as well as a method to suggest what actions need to
be performed soon. Suggested actions include adding new beers to be brewed and
performing upkeep on existing brews.

Useful functions summary (type: help(func_name) for more detailed info):
    predict_week_demand:
        Used to predict the demand for a specific year and week
    generate_usage_summary:
        useful to quickly check the internal state of the tanks
    edit_stock:
        used to change stock
    tank_empty:
        purges a tanks contents
    tank_add_hot_brew:
        Add the hot brew to a tank and begins fermenting
    tank_transfer_to_condition:
        Begins conditioning in a tank using the beer from any specified ready tank
    tank_bottle:
        Bottles the contents of a tank
    predict_remaining_stocks:
        Gives a massive summary dictionary encapsulating most prediction and state information
    beer_stocks_zero_at:
        Informs the user how long until they run out of a given beer
    find_when_tanks_free:
        Tells the user when it predicts the tanks will next be free
    best_next_action:
        Generates a list of actions that need performing in the immediate future
    begin_flask:
        Call this to begin the flask server and allow browser access to
        the user interface on  http://127.0.0.1:5000/
        (this is auto called when the module is ran (not imported))


final notes:
    In other docstrings when expressing the form of a variable the following notation is used:
        the use of ,... should be read as 'and this pattern repeats'
        the use of *# where * is any variable looking thing means this variable
            looking thing is a number (only used where no other defined method of indication)
        the use of "*" where * is a word means a string containing the meaning of *
        A simple example  would be the form: {"name":(height#,age#,["friend_name",...]),...}
            This would translate to a dictionary keyed with a persons name linking to a tuple
            which contains the height age and a list of their friends. It laso tells you that
            there can be many friends and many entries in the dictionary but the tuple will
            always be length 3.
    Many functions below have arguments that at first look very simmilar except
        for an 's' on the end (e.g week_summary vs week_summarys) these are actually
        different data structures and care should be taken to use correct arguments
        with such functions.

"""
from os import path, system, listdir
from datetime import date, datetime
from math import floor as math_floor, ceil as math_ceil, log as math_log
from json import load as json_load, dump as json_write
from time import time as ttime
from typing import Tuple, List, Union
from threading import Thread
from socket import gethostbyname as socket_gethostbyname, gethostname as socket_gethostname
from logging import basicConfig, getLogger, DEBUG as LOGGING_DEBUG
from flask import Flask, request, abort, redirect




#Sweeping developer notes:
#All quantity's are in liters as continual switching
#may increase the chance of errors.

###Constants:
PATH = path.dirname(path.abspath(__file__))+"\\"
MONTH_TO_NUMBER = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                   "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
with open(PATH+"static_data.json", "r") as file:
    STATIC_DATA = json_load(file)
WEEK_TO_SECOND = 604800
FLASK_APP = Flask(__name__)
PAGES = {}
for loop_read_page in listdir(PATH+"pages"):
    if loop_read_page[-5:] == ".html":
        with open(PATH+"pages\\"+loop_read_page) as file:
            PAGES[loop_read_page[:-5]] = file.read()
LOG_FORMAT = "%(levelname)s|%(asctime)s||%(message)s"
###Config constants:
SALES_DATA_FILE = "Barnabys_sales_fabriacted_data"
GROWTH_IMPORTANCE = 0.09
MEAN_BEER_FERMENT_TIME = 28 # 28 days
MEAN_BEER_CONDITION_TIME = 14 # 14 days
FULL_MEAN_TIME = MEAN_BEER_FERMENT_TIME+MEAN_BEER_CONDITION_TIME
FULL_MEAN_TIME_WEEKS = round(FULL_MEAN_TIME/7)
PRIORITY_THRESHHOLD = 3 # number of weeks leeway before a task becomes a 'Priority' to perform
IMPORTANCE_THRESHHOLD = 3 # number of additional weeks leeway before a task becomes important
# number of days before the expected end date the task will show up
DAYS_BEFORE_OPERATION_REMINDER = 3
TANKS_ON_ONE_LINE = 5
WEEKS_TO_SHOW_PREDICTIONS_FOR = 25
PREDICTION_COLOURS = ["#ff0000", "#00ff00", "#0000ff", "#00ffff"]
###init LOGGER:
basicConfig(filename=PATH+"brew_log.log", level=LOGGING_DEBUG, format=LOG_FORMAT)
LOGGER = getLogger()


###Sales Functions start:

def read_sales_data() -> dict:
    """Read the sales data, and return it as a list of dictionaries

    Reads the sales data from the file specified in the config constants then
    ensures that there are no commas in entries before parsing it into summary
    dictionaries.

    Returns:
        A list of dictionaries containing the data from the csv file.
    """
    LOGGER.debug("reading sales data")
    with open(PATH+"sales_data\\"+SALES_DATA_FILE+".csv", mode="r") as file:
        lines = file.readlines()
    lines = sanitize_input_csv(lines)#deal with the entries with commas in them
    sales = []
    for line in lines[1:]:
        line_data = line.split(",")
        #quantity ordered is divided by 2 so that it is in liters not bottles
        sales.append({"Invoice Number":line_data[0], "customer":line_data[1],
                      "date required":line_data[2], "recipe":line_data[3].lower(),
                      "gyle Number":line_data[4],
                      "quantity ordered":round(int(line_data[5])/2, 1)})
    return sales

def sanitize_input_csv(csv_line_list: List[str]) -> List[str]:
    """helper: Takes in a csv file that has just been .readlines()'ed and removes , form entries

    iterates through every line of the given csv file marking its state as inside/outside
    quotes as it meets them.  if it is inside quotes and hits a comma then replace it with
    a semi colon.

    Arguments:
        csv_line_list: A list of strings representing a csv file

    Returns:
        The same list of strings form the input except now entries do not contain commas
    """
    safe_lines = []
    for line in csv_line_list:
        if not line.count(",") == 5:
            index = 0
            in_quotes = False
            safe_line = ""
            while index < len(line):
                if line[index] == "," and in_quotes:#if the ',' should be escaped
                    safe_line += ";"
                else:#normal chars and unescaped ','
                    safe_line += line[index]
                if line[index] == '"':#if we need to start or stop escaping
                    if in_quotes:#toggle quotes or not
                        in_quotes = False
                    else:
                        in_quotes = True
                index += 1
            line = safe_line
        safe_lines.append(line)
    return safe_lines

def date_to_week_number(year: int, month: int, day: int) -> str:
    """Helper function: turn a date into the number of weeks into the year it is.

    Please note: the last week of every year will be 8 or 9 days to soak up extras.
    note to future developers on this point:
    Functions elsewhere in this program have been designed to account for this long week
    either by ignoring duplicates in the case of prediction functions or by it just not
    affecting anything significantly like in growth calculations.  Future functions should
    also consider if this will be an issue as the year does not split nicely into weeks and
    this is a best fit solution.

    Arguments:
        year: An integer representing the year
        month: An integer representing the month
        day: An integer representing day of the month

    Returns:
        A string: pre-padded with 0's to length 2 representing the number of weeks into
            the year a given date is
    """
    day_into_year = date(year, month, day).timetuple().tm_yday
    week_into_year = min(math_ceil((day_into_year)/7), 52)
    return ("00"+str(week_into_year))[-2:]

def month_to_number(month: str) -> int:
    """Helper function: turns a month written as 3 chars into it's integer form"""
    try:
        return MONTH_TO_NUMBER[month[:3].lower()]
    except KeyError:#month is not an acual month code
        LOGGER.error("Month '"+month+"' is not a recognised month")
        raise ValueError("Month '"+month+"' is not a recognised month\nMust be in: "+\
            list(MONTH_TO_NUMBER).__str__())

def timestamp_to_date_tuple(timestamp: str) -> Tuple[int, int, int]:
    """Convert a timestamp as found in sales docs to a tuple-date

    Arguments:
        timestamp: A string in the form DD-MMM-YY where MMM is a months 3-letter code

    Returns:
        A tuple: of length 3 containing the date in the order (YYYY,MM,DD)
    """
    day, month, year = timestamp.split("-")
    return (int("20"+year), int(month_to_number(month)), int(day))

def split_datestamp(datestamp: str) -> Tuple[int, int]:
    """Helper: Split a datestamp in the form YYYY_WW into a tuple of the same form"""
    year, week = datestamp.split("-")
    return int(year), int(week)

def unix_to_time(sec: int)-> Tuple[str, str, str, str, str, str]:
    """Takes in a unix time and expresses it in years month days etc."""
    return (datetime.utcfromtimestamp(sec).strftime('%Y-%m-%d-%H-%M')+"-00").split("-")

def unix_to_yearweek(unix_time: float) -> Tuple[str, str]:
    """Takes a unix time and converts it to a year and number of weeks into year"""
    date = unix_to_time(unix_time)[:3]
    return date[0], date_to_week_number(int(date[0]), int(date[1]), int(date[2]))

def sales_to_week_summarys(sales: List[dict]) -> dict:
    """turns sales data into a summary for each week

    Iterates through every sale in the argument sales and adds it's data to the
    relevant week summary (thus putting the data in a more usable format)

    Arguments:
        sales: A list of dictionarys where each dictionary is keyed with:
            Invoice Number,Customer,Date Required,Recipe,Gyle Number,Quantity ordered

    Returns:
        A dictionary: keyed with beer_type linking to dictionaries which
            in turn are keyed with year-week codes linking to a list of length 2 containing
            a list of all transactions for that week for that beer and the sum volume they
            have bought.
            Potentially clearer- it is of the form:
            {"beer":{"YYYY-WW":[sum#,[{past_sale_dict},...]],...},...}
    """
    LOGGER.debug("generating week summaries")
    week_summarys = {}
    for sale in sales:
        date = timestamp_to_date_tuple(sale["date required"])
        date_stamp = str(date[0])+"-"+str(date_to_week_number(*date))
        if not sale["recipe"] in week_summarys:
            week_summarys[sale["recipe"]] = {}

        try:
            week_summarys[sale["recipe"]][date_stamp][0] += sale["quantity ordered"]
            week_summarys[sale["recipe"]][date_stamp][1].append(sale)
        except KeyError:#week_summarys[sale["recipe"]][date_stamp] does not exist:
            week_summarys[sale["recipe"]][date_stamp] = [0, []]
            week_summarys[sale["recipe"]][date_stamp][0] += sale["quantity ordered"]
            week_summarys[sale["recipe"]][date_stamp][1].append(sale)

    return week_summarys

def generate_missing_weeks(week_summary: dict):
    """Operates on the input week summary dictionary generating blank weeks where no week exists

    week_summary is keyed with 'YYYY-WW' strings.  This function finds the earliest
    such date and the latest and then checks that all the intervening year-week keys exist.
    Where such keys do not exist this function adds them in with blank data sets showing no
    sales for that week.

    Arguments:
        week_summary: A dictionary keyed with 'YYYY-WW' strings

    Side Effects:
        The argument week_summary will be manipulated IN PLACE not returned.
    """
    weeks = list(week_summary.keys())[:]
    #Find the last and first weeks we have data for:
    first_week = 10000
    last_week = 0
    for week in weeks:
        week_number = float(week.replace("-", "."))
        if week_number < first_week:
            first_week = week_number
        if week_number > last_week:
            last_week = week_number
    #Between the first and last weeks found generate all missing entries
    for year in range(math_floor(first_week), math_ceil(last_week)):
        if year == math_floor(first_week):
            start_week = int(str(first_week).split(".")[1][:2])
            end_week = 52
        elif year == math_floor(last_week):
            start_week = 1
            end_week = int(str(last_week).split(".")[1][:2])
        else:
            start_week = 1
            end_week = 52
        for week in range(start_week, end_week+1):
            date_stamp = str(year)+"-"+("00"+str(week))[-2:]
            if not date_stamp in week_summary:
                week_summary[date_stamp] = [0, []]

def find_regression_line_coefficient(data_set: list) -> float:
    """Find the coefficient of the regression line of least squares for the data_set.

    Formula used: B = [Sum(xy)-{Sum(x)Sum(y)}/n] / [Sum(x**2)-{sum(x)**2}/n]
    Where:
        B is the regression line coefficient
        x is an indexed x-value
        y is an indexed y-value
        n is the number of indexed value-pairs

    Arguments:
        data_set: either a list of length 2 tuples in the form (x,y)
            OR a list of numbers representing the 'y' component of the above.
    Returns:
        A number representing the best-fit, by least squares, gradient for a line of linear growth
    """
    LOGGER.debug("finding regression line for %s" % (data_set))
    #if the data set has no x value assume that the x value starts at 0 and increments by 1
    if type(data_set[0]) == int or type(data_set[0]) == float:
        new_data_set = []
        for data in data_set:
            new_data_set.append((len(new_data_set), data))
        data_set = new_data_set
    #Generate part values
    sum_x = sum(map(lambda c: c[0], data_set))
    sum_y = sum(map(lambda c: c[1], data_set))
    sum_xx = sum(map(lambda c: c[0]**2, data_set))
    sum_xy = sum(map(lambda c: c[0]*c[1], data_set))
    count = len(data_set)
    #compute and return final coefficient
    return (sum_xy-((sum_x*sum_y)/count)) / (sum_xx-((sum_x**2)/count))


def generate_quarterly_growth_rate(quarterly_production: List[float],
                                   max_quarters: int = 12) -> int:
    """Helper: Find the coefficient from the regression line of least squares.

    A simple function included to make the use more readable later. Takes the
    quarterly_production and for the latest 'max_quarters' quarters and return the
    regression line of least squares coefficient.

    Arguments:
        quarterly_production: A list of numbers
        max_quarters: A positive integer (default: 12) representing the number
            of quarters to use if available.

    Returns:
        An integer: representing the quarterly growth rate for the data
    """
    return round(find_regression_line_coefficient(quarterly_production[-max_quarters:]))


def find_quarterly_demand(week_summary: dict) -> List[int]:
    """Calculates the total amount of this beer brewed for the quarters.

    Arguments:
        week_summary: A dictionary keyed with 'YYYY-WW' strings representing the
            weekly sales for a past time.

    Returns:
        A list: of integers equaling the sum of weekly demands for each quarter
    """
    weeks = sorted(list(week_summary.keys())[:])
    #in case of accidental passing of week_summarys not week_summary:
    assert weeks[0][4] == "-", "the week_summary has incorrect week structure"
    quarters = []
    week_count = 0
    quarter_demand = 0
    for week in weeks:
        quarter_demand += week_summary[week][0]
        week_count += 1
        if week_count == 13:
            week_count = 0
            quarters.append(quarter_demand)
            quarter_demand = 0
    #if when we ran out of data we were more than half way to the next quarter
    if week_count > 6:
        #assume that the rest of the quarter will go
        #similarly to the fist section and estimate missing data
        quarter_demand *= (13/week_count)
        quarters.append(quarter_demand)
    return quarters

def valid_week_number(week: int) -> str:
    """Helper: Turns an integer week into a string pre-pended with 0's to length 2"""
    if week > 52:
        week -= 52
    elif week < 1:
        week += 52
    return ("00"+str(week))[-2:]

def generate_relevant_keys(week: int, past_weeks_summary: dict) -> List[str]:
    """Finds the keys in past_weeks_summary that are within 2 weeks of week

    Arguments:
        week: An integer containing the week of the year for which keys should be generated
        past_weeks_summary: A dictionary keyed with 'YYYY-WW' strings representing the
            weekly sales for a past time

    Returns:
        A list: containing all keys from past_weeks_summary who's week component
            was within 2 weeks of week
    """
    keys = past_weeks_summary.keys()
    relevance = (valid_week_number(week-2), valid_week_number(week-1),
                 valid_week_number(week), valid_week_number(week+1),
                 valid_week_number(week+2))
    time_valid_keys = filter(lambda k: k[-2:] in relevance, keys)
    return list(time_valid_keys)

def delta_weeks(year1: int, week1: int, year2: int, week2: int) -> int:
    """Helper: Find the time difference between 2 integer year-week """
    assert year1 <= year2, "Year1 cannot be later than year2"
    assert week1 <= week2 if year1 == year2 else True, "week1 cannot be later"+\
        "than week2 if the years are the same"

    if year1 == year2:
        return week2-week1
    return (52-week1)+(((year2-year1)-1)*52)+(week2)



def predict_week_demand(year: int, week: int, past_weeks_summary: dict,
                        growth_factor: float = GROWTH_IMPORTANCE,
                        quarterly_growth: float = None) -> Tuple[float, list]:
    """Predict the demand of the beer past_weeks_summary is about for a given year-week

    Find the quarterly growth apply the growth_factor convert to weekly growth.  Then
    for all relevant year-weeks in past_weeks_summary find the growth that should
    have occurred.  Then average this information into a prediction and return it along
    with a list of sources. (sources included to allow user to interrogate why a given
    prediction was made)

    Arguments:
        year: An integer giving the relevant year.
        week: An integer giving the week into the year specified previously.
        past_weeks_summary: A dictionary keyed with 'YYYY-WW' strings representing the
            weekly sales for a past time.
        growth_factor: A float - How much growth matters, Generally low (0.1ish) when number
            of quarters it was generated from is less than 10 as with so little data seasonal
            flux will be causing it wild inaccuracies. (Defaults to GROWTH_IMPORTANCE)
        quarterly_growth: A numbers - Allows the caller to specify the quarterly
            growth. Useful if predict_week_demand is being called a lot as it saves each call
            finding it themselves. (default: None -- meaning generate it at when called)

    Returns:
        A tuple: of length 2.  The first item in the tuple is the predicted demand in that week.
            The second item is a list of demand sources breaking down how the first value
            was generated. Sources form:
            [("YYYY-WW",(prediction_value#,growth_value#,past_sum#),[who_dict]),...]
    """
    assert 0 < week < 53, "week must be in the inclusive range 1-52"
    if quarterly_growth is None:
        quarterly_demand = find_quarterly_demand(past_weeks_summary)
        quarterly_growth = generate_quarterly_growth_rate(quarterly_demand)
    weekly_growth = (quarterly_growth/13)*growth_factor

    sources = []
    relevant_keys = generate_relevant_keys(week, past_weeks_summary)
    for key in relevant_keys:
        past_sum = past_weeks_summary[key][0]
        growth = delta_weeks(*split_datestamp(key), year, week)*weekly_growth
        sources.append((key, (growth+past_sum, growth, past_sum), past_weeks_summary[key][1]))
    prediction = sum(map(lambda source: source[1][0], sources))/len(sources)
    return (round(prediction, 1), sources)


###Sales Functions end
###Inventory and processing start:

def read_dynamic_data() -> dict:
    """A small function that reads dynamic_data.json and returns the contents as a dictionary"""
    LOGGER.info("Dynamic data read")
    with open(PATH+"dynamic_data.json", "r") as file:
        data = json_load(file)
    LOGGER.debug("Dynamic data read successful")
    return data

def generate_usage_summary(dynamic_data: dict = None) -> Tuple[str, str, str, int]:
    """compile a list of important tank data to show the user graphically

    Arguments:
        dynamic_data: A dictionary representing the dynamic_data.json file
            (default: None -- meaning generate it when called)

    Return:
        A list: of tuples of length 4. The tuples have the form:
            ("tank_name","beer_type","process_stage",time_til_done#)
    """
    if dynamic_data is None:
        dynamic_data = read_dynamic_data()
    tanks = dynamic_data["equipment_state"]
    summarys = []#in the form (name,type,state,time_left(seconds))
    for name in list(tanks.keys())[:]:
        summary = []
        summary.append(name)
        summary.append(tanks[name]["type"])
        if tanks[name]["active"]:
            state = tanks[name]["stage"]
        else:
            state = "inactive"
        summary.append(state)
        summary.append(round(tanks[name]["unix_time_started"]+tanks[name]["run_length"]-ttime()))
        summarys.append(tuple(summary))
    return summarys

def edit_tank_info(name: str, active: bool, stage: str, run_length: int, time_started: int,
                   type_: str, volume: float, gyle_number: int):
    """Check all the arguments are safe to write then, write the input data to dynamic_data.json

    Checks every input to the greatest extent possible to try and ensure that if data is written
    to the file it is safe to do so.  If any discrepancy is found: error based on type or value
    with a human understandable error code.
    Note: Generally this function should not be called directly as other more specific
    functions exist for almost any sensible task you may wish to perform.

    Arguments:
        name: A string referring to the name of the tank to edit
        active: A Boolean referring to whether the edited tank is to be turned on
        stage: A string referring to the current process going on in the tank
        run_length: An integer referring to the number of seconds for which this stage should last
        time_started: An integer referring to the unix time that this tank began this process
        type_: A string referring to the type of beer to produce
        volume: A number referring to the amount of beer that should be in the tank (in liters)
        gyle_number: An integer referring to the batch number

    Side effects:
        This function changes the file dynamic_data.json when run successfully

    Exceptions:
        ValueError: This will be raised in 9 cases where the type is right but
            the value entered is not allowed.  The specific error message will tell
            you what is wrong.
        TypeError: This will be raised in 6 cases where the type is not allowed for
            an argument.  The specific error message will tell you what is wrong.
    """
    LOGGER.debug("edit_tank_info: called for data ["+str(name)+"|"+str(active)+"|"+str(stage)+\
                 "|"+str(run_length)+"|"+str(time_started)+"|"+str(type_)+"|"+str(volume)+"|"+\
                 str(gyle_number)+"|"+"]")
    data = read_dynamic_data()
    if not name in data["equipment_state"].keys():
        raise ValueError("the equipment name '"+name+"' does not exist")
    if not type(active) == bool:
        raise TypeError("active must be a boolean (NOT: "+str(type(active))+")")
    if not stage in ["Fermenting", "Conditioning", "None"]:
        raise ValueError("stage must be one of [fermenting, conditioning, None] (NOT: "+
                         str(stage)+")")
    if stage == "Fermenting" and not STATIC_DATA["equipment"][name]["fermenter"]:
        raise ValueError("The tank '"+str(name)+"' cannot ferment")
    if stage == "Conditioning" and not STATIC_DATA["equipment"][name]["conditioner"]:
        raise ValueError("The tank '"+str(name)+"' cannot condition")
    if not type(run_length) == int:
        raise TypeError("run_length must be an integer (NOT: "+run_length.__class__.__name__+")")
    if not run_length >= 0:
        raise ValueError("run_length must be positive")
    if not type(time_started) == int:
        raise TypeError("time_started must be an integer (NOT: "+\
                        time_started.__class__.__name__+")")
    if not time_started >= 0:
        raise ValueError("time_started must be positive")
    if not type(type_) == str:
        raise TypeError("type_ Must be a string")
    if not type_ in data["liters_of_bottled_beer"] and type_ != "None":
        raise ValueError("type is not recognized must be one of:\n"+\
                         str(list(data["liters_of_bottled_beer"].keys())))
    if (not type(volume) == float) and (not type(volume) == int):
        raise TypeError("volume must be number")
    if volume < 0 or volume > STATIC_DATA["equipment"][name]["volume"]:
        raise ValueError("Volume must be between 0 and tank max")
    if type(gyle_number) != int:
        raise TypeError("gyle_number must be an integer")
    if gyle_number < 0:
        raise ValueError("gyle_number must be positive")
    LOGGER.debug("edit_tank_info: inputs safe!")
    replacement_info = {'active': active, 'stage': stage, 'run_length': run_length,
                        'unix_time_started': time_started, 'type': type_, 'volume':volume,
                        'gyle_number':gyle_number}
    data["equipment_state"][name] = replacement_info
    LOGGER.debug("edit_tank_info: writing")
    with open(PATH+"dynamic_data.json", "w") as file:
        json_write(data, file)
    LOGGER.debug("edit_tank_info: complete")

def edit_stock(beer_type: str, amount: float):
    """Check all the arguments are safe to write then, write the input data to dynamic_data.json

    Arguments:
        beer_type: A string containing the name of a beer
        amount: A number referring to the amount of beer to change the stock by

    Side effects:
        This function changes the file dynamic_data.json when run successfully

    Exceptions:
        ValueError: This exception is raised if either the beer_type does not exist OR
            if the amount is both negative and would make the stock negative. (as negative
            beer stock cannot exist)
        TypeError: This exception occurs if amount is not a number
    """
    LOGGER.debug("edit_stock called")
    data = read_dynamic_data()
    #due to the highly negative consequences if the write fails for the
    #dynamic_data file,  every arguments is ensured to be within correct ranges
    if not beer_type in data["liters_of_bottled_beer"].keys():
        return ValueError("beer_type: "+str(beer_type)+" is not a valid beer type\n"+\
                          "Valid beer types: "+\
                          str(list(data["liters_of_bottled_beer"].keys())[:]))
    try:
        amount = round(float(amount), 3)
    except ValueError:
        raise TypeError("amount must be a number")
    stock = data["liters_of_bottled_beer"][beer_type]
    if not (amount >= 0 or (-amount) >= stock):
        ValueError("amount must either be greater than 0 or negative and less than stock")
    replacement_value = stock+amount
    data["liters_of_bottled_beer"][beer_type] = replacement_value

    with open(PATH+"dynamic_data.json", "w") as file:
        json_write(data, file)
    return None


def tank_empty(name: str) -> Tuple[float, str]:
    """Empty the tank specified in name without bottling returning the contents"""
    dynamic_data = read_dynamic_data()
    return_val = (dynamic_data["equipment_state"][name]["volume"],
                  dynamic_data["equipment_state"][name]["type"])
    edit_tank_info(name, False, "None", 0, 0, "None", 0, 0)
    return return_val

def next_gyle_number() -> int:
    """Read the gyle number from file return it after incrementing the file's current_number"""
    data = read_dynamic_data()
    current_gyle_number = data["current_gyle_number"]
    data["current_gyle_number"] += 1
    with open(PATH+"dynamic_data.json", "w") as file:
        json_write(data, file)
    return current_gyle_number

def tank_ferment(name: str, beer_type: str, gyle_number: int = -1, volume: float = -1,
                 days_to_run: int = MEAN_BEER_FERMENT_TIME, start_date: int = -1):
    """A fairly unabstracted function for adding the hot brew

    Arguments:
        name: A string referring to the name of the tank to edit
        beer_type: A string referring to the type of beer to produce
        gyle_number: An integer referring to the batch number
            (default: -1 -- meaning auto generate when called)
        volume: A number referring to the amount of beer that should be in the tank (in liters)
            (default: -1 -- meaning fill to tank max)
        run_length: An integer referring to the number of days for which this stage should last
            (default: MEAN_BEER_FERMENT_TIME constant)
        start_date: An integer allowing deferred starts and if the user forgets to run this at the
            right time they can add in the missing entries. (default: -1 meaning 'starting now')
            start_date is in unix time.
    Side effects:
        This function changes the file dynamic_data.json when run successfully
    """
    if start_date == -1:
        start_date = round(ttime())
    if volume == -1:
        volume = STATIC_DATA["equipment"][name]["volume"]
    if gyle_number == -1:
        gyle_number = next_gyle_number()
    edit_tank_info(name, True, "Fermenting", days_to_run*86400, start_date,
                   beer_type, volume, gyle_number)

def tank_condition(name: str, beer_type: str, gyle_number: int, volume: float,
                   days_to_run: int = MEAN_BEER_CONDITION_TIME, start_date: int = -1):
    """A fairly unabstracted function for beginning conditioning

    Arguments:
        name: A string referring to the name of the tank to edit
        beer_type: A string referring to the type of beer to produce
        gyle_number: An integer referring to the batch number
        volume: A number referring to the amount of beer that should be in the tank (in liters)
        run_length: An integer referring to the number of days for which this stage should last
            (default: MEAN_BEER_CONDITION_TIME constant)
        start_date: An integer allowing deferred starts and if the user forgets to run this at the
            right time they can add in the missing entry's. (default: -1 meaning 'starting now')
            start_date is in unix time.

    Side effects:
        This function changes the file dynamic_data.json when run successfully
    """
    if start_date == -1:
        start_date = round(ttime())
    edit_tank_info(name, True, "Conditioning", days_to_run*86400, start_date,
                   beer_type, volume, gyle_number)


def tank_add_hot_brew(name: str, beer_type: str, gyle_number: int = -1, volume: float = -1,
                      days_to_run: int = MEAN_BEER_FERMENT_TIME, start_date: int = -1):
    """Add the hot brew to tank name and begin fermenting

    Arguments:
        name: A string referring to the name of the tank to begin brewing in
        beer_type: A string referring to the type of beer to produce
        gyle_number: An integer referring to the batch number
            (default: -1 -- meaning auto generate when called)
        volume: A number referring to the amount of beer that should be in the tank (in liters)
            (default: -1 -- meaning fill to tank max)
        run_length: An integer referring to the number of days for which this stage should last
            (default: MEAN_BEER_FERMENT_TIME constant)
        start_date: An integer allowing deferred starts and if the user forgets to run this at the
            right time they can add in the missing entry's. (default: -1 meaning 'starting now')
            start_date is in unix time.

    Side effects:
        This function changes the file dynamic_data.json when run successfully

    Exceptions:
        ValueError: raised if:
            tank name is not empty
            requested volume is larger than the max possible for tank name
    """
    state = read_dynamic_data()["equipment_state"][name]
    if state["active"] or state["volume"] != 0:
        raise ValueError(str(name)+" is not empty, cannot add hot brew")
    if volume > STATIC_DATA["equipment"][name]["volume"]:
        raise ValueError("volume is larger than this tanks max ("+str(volume)+\
                         ">"+str(STATIC_DATA["equipment"][name]["volume"])+")")

    tank_ferment(name, beer_type, gyle_number, volume, days_to_run, start_date)


def tank_transfer_to_condition(name1: str, name2: str,
                               days_to_run: int = MEAN_BEER_CONDITION_TIME,
                               start_date: int = -1, ignore_warnings=False):
    """Begins conditioning in tank name2 with the beer in tank name1 (name1 can equal name2)

    Arguments:
        name1: A string referring to the tank to take the fermented beer from
        name2: A string referring to the tank to put the fermented beer in
        days_to_run: An integer referring to the number of days for which this stage should last
            (default: MEAN_BEER_CONDITION_TIME)
        start_date: An integer allowing deferred starts and if the user forgets to run this at the
            right time they can add in the missing entry's. (default: -1  meaning 'starting now')
            start_date is in unix time.
        ignore_warnings: A boolean Stating whether warning about proximity to end date
            should be ignored. (default: False)

    Side effects:
        This function changes the file dynamic_data.json when run successfully

    Exceptions:
        ValueError: raised if:
            tank name1 is not fermenting currently
            tank name2 is not empty currently
            more beer is in tank name1 than can fit in tank name2
        Warning: raised if ignore_warnings is False and the tank name1 is not
            within 4 days of it's end date
    """
    data = read_dynamic_data()
    name1_state = data["equipment_state"][name1]
    name2_state = data["equipment_state"][name2]
    if ((not name1_state["active"]) or (name1_state["stage"] != "Fermenting") or
            (name1_state["volume"] == 0)):
        raise ValueError("name1 is not fermenting currently")
    if (name2_state["active"] or name2_state["volume"] > 0) and name1 != name2:
        raise ValueError("name2 is not empty currently")
    if name1_state["volume"] > STATIC_DATA["equipment"][name2]["volume"]:
        raise ValueError("more beer in tank1 than can fit in tank2")
    if ((name1_state["unix_time_started"]+name1_state["run_length"] > round(ttime())+345600) and
            (not ignore_warnings)):
        raise Warning(str(name1)+" is not within 4 days of designated completion date,"+\
                      "\nAre you sure you want to proceed?")

    condition_data = (name2, name1_state["type"], name1_state["gyle_number"],
                      name1_state["volume"], days_to_run, start_date)
    tank_condition(*condition_data)
    if name1 != name2:
        tank_empty(name1)

def tank_bottle(name: str, ignore_warnings: bool = False) -> Tuple[str, float, int]:
    """Bottle the contents of tank name and add it to stock

    Arguments:
        name: A string referring to the tank to take the conditioned beer from
        ignore_warnings: A boolean Stating whether warning about proximity to end date
            should be ignored. (default: False)

    Returns:
        A tuple: of length 3 containing beer_type,volume and
            gyle_number for the batch just bottled

    Side effects:
        This function changes the file dynamic_data.json when run successfully

    Exceptions:
        ValueError: the beer in tank name is not conditioning currently
        Warning: raised if ignore_warnings is False and the tank name1 is not
            within 4 days of it's end date
    """
    state = read_dynamic_data()["equipment_state"][name]
    if state["stage"] != "Conditioning":
        raise ValueError("Beer is not conditioning, you cannot bottle it")
    if ((state["unix_time_started"]+state["run_length"] > round(ttime())+345600) and
            (not ignore_warnings)):
        raise Warning(str(name)+" is not within 4 days of designated completion date,"+\
                      "\nAre you sure you want to proceed?")
    gyle_number = state["gyle_number"]
    volume, type_ = tank_empty(name)
    edit_stock(type_, volume)
    return type_, volume, gyle_number

###Inventory and processing end
###Prediction and suggestion start:


def generate_inventory_summary(weeks_to_predict_for: int = 12) -> dict:
    """Finds the expected stock of different beers with no usage

    First find the current stocks then generate a list of tanks and when they finish.
    Then iterate through all of the weeks rolling over stocks from the week prior
    and adding new ones when a tank finishes

    Arguments:
        weeks_to_predict_for: A integer referring to the number of weeks the inventory
            should be summarized for.  (default: 12)

    Returns:
        A dictionary: keyed with week integers linking to tuples of length 2 for which
            the first item is a dictionary keyed with beer types linking to expected amount
            of that beer and the second item is (with exception to week-0) a dictionary
            keyed with beers linking to a list of tanks that will end during that week.
            The second elements purpose is to allow users to work out why a given value
            was returned.

    Exceptions:
        TypeError: if week_to_predict_for is not an integer
        ValueError: is week_to_predict_for is less than 1
    """
    if type(weeks_to_predict_for) != int:
        raise TypeError("week_to_predict_for must be an integer")
    if weeks_to_predict_for < 1:
        raise ValueError("week_to_predict_for must be greater than 0")
    data = read_dynamic_data()
    weeks_summary = {}
    #Load initial values into loop with source as stock
    weeks_summary[0] = (data["liters_of_bottled_beer"].copy(), (0, "STOCK", None))
    #Find a list of tanks due to finish (tanks_remaining)
    tanks_data = data["equipment_state"]
    tanks_remaining = []
    for tank_name, tank in tanks_data.items():
        if not tank["active"]:
            continue
        time_done = tank["unix_time_started"]+tank["run_length"]
        current_time = ttime()
        if time_done <= current_time:
            week = 0
        else:
            week = round((time_done-current_time)/WEEK_TO_SECOND, 1)
            if tank["stage"] == "Fermenting":
                week += round(MEAN_BEER_CONDITION_TIME/7, 1)
            week = math_ceil(week)
        tanks_remaining.append((week, tank_name, tank))
    #construct a base beer dictionary from which the weeks_summary entrys will be derived
    base_expain_dict = {}
    for beer in weeks_summary[0][0].keys():
        base_expain_dict[beer] = []
    #iterate over weeks rolling over stocks and generating week summary
    for week in range(1, weeks_to_predict_for+1):
        week_sum = (weeks_summary[week-1][0].copy(), base_expain_dict.copy())
        for tank_sum in filter(lambda x: x[0] == week, tanks_remaining):
            type_ = tank_sum[2]["type"]
            week_sum[0][type_] += tank_sum[2]["volume"]
            if len(week_sum[1][type_]) == 0:
                week_sum[1][type_] = [tank_sum,]#force create new list
            else:
                week_sum[1][type_].append(tank_sum)
        weeks_summary[week] = week_sum
    return weeks_summary

def generate_demand_for_next_weeks(weeks_to_predict_for: int = 12) -> dict:
    """generate a summary of expected demand by calling predict_week_demand on each week upcoming

    obtain a summary of the past weeks then for each week in each beer predict demand.
    Then re-iterate through structuring the output correctly and return it.

    Arguments:
        weeks_to_predict_for: A integer referring to the number of weeks the demand
            should be predicted for.  (default: 12)

    Return:
        A dictionary: keyed with weeks from 1 to week_to_predict_for and linking
            to a tuple of length 2.  Within the tuple the first item is a dictionary
            keyed with beer name linking to predicted volumes and the second item is
            a dictionary keyed with beer name linking to a list of secondary_tuples.
            these secondary tuples are of length 3 and contain data about previous
            sales from which the prediction was made. A summary of the form is below:
            {week#:({"beer":volume#,...},("beer":[
                ("YYYY-WW",(sum#,growth#,sales#),[past_sales_dictionarys]),...
            ],...)),...}

    Exceptions:
        TypeError: if week_to_predict_for is not an integer
        ValueError: is week_to_predict_for is less than 1
    """
    if type(weeks_to_predict_for) != int:
        raise TypeError("week_to_predict_for must be an integer")
    if weeks_to_predict_for < 1:
        raise ValueError("week_to_predict_for must be greater than 0")
    #create the predictions in a easy to make way
    past_weeks_summarys = sales_to_week_summarys(read_sales_data())
    beer_week_summary = {}
    for beer, beer_summary in past_weeks_summarys.items():
        past_growth = generate_quarterly_growth_rate(find_quarterly_demand(beer_summary))
        beer_week_summary[beer] = {}
        for relitive_week in range(1, weeks_to_predict_for+1):
            year, week = unix_to_yearweek(ttime()+relitive_week*WEEK_TO_SECOND)
            mini_prediction = predict_week_demand(int(year), int(week), beer_summary,
                                                  quarterly_growth=past_growth)
            beer_week_summary[beer][relitive_week] = mini_prediction
    #format the predicitons found earlier correctly
    future_weeks_summary = {}
    for relitive_week in range(1, weeks_to_predict_for+1):
        future_weeks_summary[relitive_week] = ({}, {})
        for beer, week_to_beer_sum in beer_week_summary.items():
            future_weeks_summary[relitive_week][0][beer] = week_to_beer_sum[relitive_week][0]
            future_weeks_summary[relitive_week][1][beer] = week_to_beer_sum[relitive_week][1]

    return future_weeks_summary

def predict_remaining_stocks(weeks_to_predict_for: int = 10) -> dict:
    """by combining stock information expected brew completions and demand generate expected stock

    For every week up to weeks_to_predict_for find the predicted demand, expected tank finishes
    and roll over stock.  Then combine the information into the expected stock of each beer.

    Arguments:
        weeks_to_predict_for: A integer referring to the number of weeks the stocks
            should be predicted for.  (default: 12)

    Returns:
        A dictionary: keyed with week numbers linking to a secondary dictionary keyed with
        beer types, in turn, linking to a tuple of length 6; the contents of which are
        enumerated below:
            [0] - The expected stock for the indexed week-beer.
            [1] - The expected gain from tanks completing  for the indexed week-beer.
            [2] - The predicted demand  for the indexed week-beer.
            [3] - The sum of all predicted demands thus far  for the indexed week-beer.
            [4] - A list with a summary of the tanks that will finish for the indexed week-beer.
            [5] - A list with a summary of the demand for the indexed week-beer.
        The form is shown below:
            {week#:{"beer_type":
                    (stock#,gain#,predicted_demand#,
                    sum_pred_demand#,[gain_exp_list],[demand_exp_list]),...
                },...}

    Exceptions:
        TypeError: if week_to_predict_for is not an integer
        ValueError: is week_to_predict_for is less than 1
    """
    if type(weeks_to_predict_for) != int:
        raise TypeError("week_to_predict_for must be an integer")
    if weeks_to_predict_for < 1:
        raise ValueError("week_to_predict_for must be greater than 0")
    expected_gains = generate_inventory_summary(weeks_to_predict_for+2)
    expected_demands = generate_demand_for_next_weeks(weeks_to_predict_for+2)
    #create a dictionary to track predicted demand roll over for stock generate
    stocks = {}
    loss_lastweek = {}
    for type_ in list(expected_gains[0][0].keys())[:]:
        loss_lastweek[type_] = 0
    #generate the expected stock summary:
    for week in range(1, weeks_to_predict_for+1):
        stocks[week] = {}
        for type_ in list(expected_gains[0][0].keys())[:]:
            gain = round(expected_gains[week][0][type_], 1)
            demand = round(expected_demands[week][0][type_], 1)
            amount = round((gain-demand)-loss_lastweek[type_], 1)
            gain_reason = expected_gains[week][1][type_]
            demand_reason = expected_demands[week][1][type_]

            loss_lastweek[type_] += demand
            stocks[week][type_] = (amount, gain, demand, loss_lastweek[type_],
                                   gain_reason, demand_reason)

    return stocks

def beer_stocks_zero_at(minimum_responce_time: int = FULL_MEAN_TIME_WEEKS,
                        max_prediction_range: int = 25) -> dict:
    """Checking within the requested range, find the time at which every beers stock runs out

    Arguments:
        minimum_responce_time: An integer referring to when to begin checking for negative stocks.
            (default: FULL_MEAN_TIME_WEEKS)  The minimum_responce_time is set to
            prevent it informing you about stocks running out before you can effect the stocks.
        minimum_responce_time: An integer referring to when to end checking for negative stocks
            (default: 25 (weeks))

    Returns:
        A dictionary: keyed with beer types linking to the number of weeks until the stocks
            run out.  Will show minimum_responce_time if the stocks are already out at it and
            will show max_prediction_range if the stocks do not run out within the selected period

    Exceptions:
        ValueError: raised if minimum_responce_time is bigger than max_prediction_range
    """
    if minimum_responce_time > max_prediction_range:
        raise ValueError("minimum time cannot exceed maximum")
    stocks = predict_remaining_stocks(max_prediction_range)
    zero_time = {}
    for beer in list(stocks[1].keys())[:]:
        for week in range(minimum_responce_time, max_prediction_range):
            if stocks[week][beer][0] <= 0:
                zero_time[beer] = week
                break
        else:
            zero_time[beer] = max_prediction_range
    return zero_time

def can_tank_condition_not_ferment(tank_static_data_row: Tuple[str, dict]) -> bool:
    """Helper: Return True if the tank specified in arguments can condition but not ferment"""
    return tank_static_data_row[1]["conditioner"] and not tank_static_data_row[1]["fermenter"]

def find_tanks_condition_only() -> List[tuple]:
    """Helper: Return a list of tanks that can only condition"""
    return sorted(list(filter(can_tank_condition_not_ferment, STATIC_DATA["equipment"].items())))

def find_tanks_can_condition() -> List[tuple]:
    """Helper: Return a list of tanks that are capable of conditioning"""
    return sorted(list(filter(lambda x: x[1]["conditioner"], STATIC_DATA["equipment"].items())))

def find_when_tanks_free() -> Tuple[dict, list]:
    """For each tank return when it is next unused long enough to start a new brew

    First stage: Every inactive tank is free now, every active tank that is
    conditioning is free when it is finished with the current stage.  Every active tank
    that is Fermenting and can condition is free MEAN_BEER_CONDITION_TIME days after it
    ends it's current stage. If a tank is fermenting and cannot condition then it is added
    to a list of tanks for which a conditioner must be found.
    Second stage: Then for every tank that needs a conditioner attempt to find a suitable one
    first among  ones that cannot ferment (as they get less usage) then within the
    conditioning tanks at large.  Once a tank is found record the expected tank change.
    Final stage: Return when each tank is free and including a list of expected actions to
    keep the prediction correct.

    Returns:
        A tuple: of length 2 the first item being a dictionary keyed with tank names linking to
            the number of weeks before they are free.  The second being a list of expected
            actions that will be performed to keep that prediction accurate. Form:
            ({"tank_name":weeks_until_free#,...},[("tank1","tank2",when#),...])
    """
    tanks_free_at = {}
    #generate base times for finishing
    expected_actions = []
    find_conditioner = []
    data = read_dynamic_data()
    for tank_name, tank_data in data["equipment_state"].items():
        free_at = 0
        if tank_data['active']:#only active tanks can be busy at this stage
            free_at += max(round(tank_data["unix_time_started"]+\
                           tank_data["run_length"]-ttime()), 0)
            if tank_data['stage'] == "Fermenting":
                if STATIC_DATA["equipment"][tank_name]["conditioner"]:
                    free_at += MEAN_BEER_CONDITION_TIME*86400
                else:#If the tank (the fermented stuff is in) cannot condition
                    find_conditioner.append((math_ceil(free_at/WEEK_TO_SECOND),
                                             tank_data, tank_name))

        tanks_free_at[tank_name] = math_ceil(free_at/WEEK_TO_SECOND)
    #Deal with tanks that cannot condition themselves
    for uncondtionalble in find_conditioner:
        for tank_name, _ in find_tanks_condition_only():
            if (tanks_free_at[tank_name] <= uncondtionalble[0] and
                    (STATIC_DATA["equipment"][tank_name]["volume"] >=
                     uncondtionalble[1]["volume"])):
                tanks_free_at[tank_name] = uncondtionalble[0]+\
                                           math_ceil(MEAN_BEER_CONDITION_TIME/7)
                expected_actions.append((uncondtionalble[2], tank_name, uncondtionalble[0]))
                break
        else:#if no tanks that cannot ferment can be found to condition:
            for tank_name, _ in find_tanks_can_condition():
                if (tanks_free_at[tank_name] <= uncondtionalble[0] and
                        (STATIC_DATA["equipment"][tank_name]["volume"] >=
                         uncondtionalble[1]["volume"])):
                    tanks_free_at[tank_name] = uncondtionalble[0]+\
                                               math_ceil(MEAN_BEER_CONDITION_TIME/7)
                    expected_actions.append((uncondtionalble[2], tank_name, uncondtionalble[0]))
                    break

    return tanks_free_at, expected_actions

def find_important_and_priority_beers(zero_at: dict) -> Tuple[list, list]:
    """From the information returned by find_when_tanks_free return any higher priority beers

    Arguments:
        zero_at: A dictionary keyed with beer types linking to the number of
            weeks until the stocks run out.

    Returns:
        A tuple: of length 2 where each item is a list of beers, the first
            of priority 'priority' and the second of priority 'important'.
    """
    prio_beers = []
    impo_beers = []
    for beer, weeks in zero_at.items():
        if weeks < FULL_MEAN_TIME_WEEKS+PRIORITY_THRESHHOLD:
            prio_beers.append(beer)
        elif weeks < FULL_MEAN_TIME_WEEKS+PRIORITY_THRESHHOLD+IMPORTANCE_THRESHHOLD:
            impo_beers.append(beer)
    return prio_beers, impo_beers

def best_next_action() -> dict:
    """Plan the best next actions to be performed based on stock predictions and process state

    First: Pass straight through the required actions devised by find_when_tanks_free as
    these actions must be performed in order to keep the information accurate
    Second: Add actions for all upkeep that must occur such as beginning conditioning or
    bottling a finished beer
    Third: Add an action either instructing the user to add the most in demand beer to the
    tank best suited to fermenting it or an action stating 'take no action' as no
    tanks are available.
    Finally: Return all actions in a dictionary keyed by priority.

    Returns:
        A dictionary: keyed with the priorities (Priority,Important,Upkeep,Surplus)
            linking to lists of tuples detailing actions that should be performed.
            These action tuples have the action code then the tank or tanks involved
            then a user readable description with basic justification.
    """
    data = read_dynamic_data()
    tanks_free = find_when_tanks_free()
    zero_at = beer_stocks_zero_at()
    #find Priority beers:
    prio_beers, impo_beers = find_important_and_priority_beers(zero_at)
    #action's take the form (operation,(effected tanks,...),info)
    actions = {"Priority":[], "Important":[], "Upkeep":[], "Surplus":[]}
    #check for timetable induced expected actions
    for action in tanks_free[1]:
        tank_data = data["equipment_state"][action[0]]
        time_remaining = tank_data["unix_time_started"]+tank_data["run_length"]-ttime()
        if time_remaining < (86400*DAYS_BEFORE_OPERATION_REMINDER):
            instruciton = "Move beer from '"+action[0]+"' to '"+action[1]+\
                          "' and start conditioning as it is "+ \
                          str(round(time_remaining/3600))+" hours until it's end time."
            if data["equipment_state"][action[0]]["type"] in prio_beers:
                actions["Priority"].append(("Move-and-condition",
                                            (action[0], action[1]), instruciton))
            elif data["equipment_state"][action[0]]["type"] in impo_beers:
                actions["Important"].append(("Move-and-condition",
                                             (action[0], action[1]), instruciton))
            else:
                actions["Upkeep"].append(("Move-and-condition",
                                          (action[0], action[1]), instruciton))
    #check for upkeep induced expected actions
    for tank_name, tank_data in data["equipment_state"].items():
        if tank_data["active"]:
            #find priority:
            priority_level = "Upkeep"
            if tank_data["type"] in impo_beers:
                priority_level = "Important"
            if tank_data["type"] in prio_beers:
                priority_level = "Priority"
            #find time remaining and if it finishes soon generate and action
            time_remaining = tank_data["unix_time_started"]+tank_data["run_length"]-ttime()
            if time_remaining < (86400*DAYS_BEFORE_OPERATION_REMINDER):
                if (tank_data["stage"] == "Fermenting" and
                        STATIC_DATA["equipment"][tank_name]["conditioner"]):
                    message = "Begin conditioning on '"+tank_name+"' as it is "+ \
                              str(round(time_remaining/3600))+" hours until it's end time."
                    actions[priority_level].append(
                        ("Condition-in-current-tank", (tank_name), message))

                elif tank_data["stage"] == "Conditioning":
                    message = "Bottle the contents of the tank '"+tank_name+"' as it is "+ \
                              str(round(time_remaining/3600))+" hours until it's end time."
                    actions[priority_level].append(
                        ("Bottle-tank-contents", (tank_name), message))
    #The next new beer to brew
    beer_to_brew, weeks = min(zero_at.items(), key=lambda x: x[1])
    priority_level = "Surplus"
    if beer_to_brew in impo_beers:
        priority_level = "Important"
    if beer_to_brew in prio_beers:
        priority_level = "Priority"
    try:
        tank_name, _ = list(filter(lambda x: x[1] == 0, tanks_free[0].items()))[:][0]
    except IndexError:# there are no free tanks
        actions[priority_level].append("No-action", "no tank", "There are no tanks free so no "+\
                                       "beer should be prepared currently until some tanks clear")
    else:
        message = "Add the hot brew for the beer '"+beer_to_brew+"' to the tank '"+tank_name+\
                  "' as '"+beer_to_brew+"' will run out in "+str(weeks)+" weeks."
        actions[priority_level].append(("Add-hot-brew-to-tank",
                                        (tank_name), message, beer_to_brew))
    return actions


###Prediction and suggestion end
###Flask Interface start:

def find_suggested_action_by_tank(suggested_actions: dict, tank_name: str) -> Union[tuple, bool]:
    """Searches through suggested_actions to find an action involving tank_name

    Arguments:
        suggested_actions: A dictionary keyed with the priorities linking to tuples
            detailing actions that should be performed.
        tank_name: A string - tank name to be searched for.

    Returns:
        Either a tuple detailing an action OR False where no such tuple could be found.
    """
    for priority_level in ['Priority', 'Important', 'Upkeep', 'Surplus']:
        for action in suggested_actions[priority_level]:
            if tank_name == action[1]:
                return action
            if type(action[1]) == tuple:#For the move-and-condition action which involves 2 tanks
                if tank_name == action[1][0]:
                    return action
    return False

def format_sugested_action(sugested_action: tuple) -> str:
    """Helper: Formats sugested_action into a form url's load properly

    Arguments:
        sugested_action: A tuple where the second item may also be
        a tuple and the rest of the items are strings.

    Return:
        A string: equaling the input tuple except the items are joined with | and
            if the second item was a tuple then it is joined with ~
    """
    sugested_action = list(sugested_action)
    if type(sugested_action[1]) == tuple:
        sugested_action[1] = str("~".join(sugested_action[1]))
    return "|".join(sugested_action)

def unformat_sugested_action(sugested_action_formatted: str) -> tuple:
    """Helper: Unformats sugested_action_formatted into a form python can use

    Arguments:
        sugested_action_formatted: A string to be expanded into a tuple with the
            divisions at | and the second item may also need divisioning if so it's
            divisions will be indicated by a ~


    Return:
        A tuple: where the second item may also be a tuple and
            the rest of the items are strings.
    """
    items = sugested_action_formatted.split("|")
    items[1] = items[1].split("~")
    if len(items[1]) == 1:
        items[1] = items[1][0]
    else:
        items[1] = tuple(items[1])
    return tuple(items)

def stocks_to_xy(stocks_in: dict) -> Tuple[dict, dict]:
    """converts a stocks summary into a plot-able form

    Arguments:
        stocks_in: A dictionary keyed with week numbers linking to a
            secondary dictionary keyed with beer types, in turn, linking
            to a tuple of length 6; This tuple containing the expected
            stock at index 0 and the predicted demand at index 2.

    Returns:
        A tuple: of length 2 where the both items are dictionary keyed with beer types
            linking to coordinates; where the x-coord is week number and the y-coord
            is remaining stock or predicted demand respectively.
    """
    stocks = {}
    demand = {}
    for beer, _ in stocks_in[1].items():
        stocks[beer] = []
        demand[beer] = []
    for week, week_data in stocks_in.items():
        for beer, beer_data in week_data.items():
            stocks[beer].append((week, beer_data[0]))
            demand[beer].append((week, beer_data[2]))
    return stocks, demand

def xy_svg_polyline_points(xy_coord: List[Tuple[float, float]], xtop: float, ytop: float, cx1: int,
                           cy1: int, cx2: int, cy2: int) -> Tuple[str, tuple]:
    """Generate some svg polyline plot-able coords based on input

    Arguments:
        xy_coord: a list of tuples containing x,y coords inside
        xtop: the largest x-value that is to be plot-able based on the graph scale
        ytop: the largest y-value that is to be plot-able based on the graph scale
        cx1: The x-coordinate on the svg canvas from which the plot will start
        cy1: The y-coordinate on the svg canvas at with the y axis will be at it's maximum
        cx2: The x-coordinate on the svg canvas at which the plot will end
        cy2: The y-coordinate on the svg canvas at with the y axis will be at it's minimum

    Returns:
        A tuple: of length 2 the first item being a string listing the plot point and the
            second being the coordinate tuple of the last plot point.
    """
    #load the base of the shape in case the points are to be used for a polygon not polyline
    points = str(cx2)+","+str(cy2)+" "+str(cx1)+","+str(cy2)+" "
    #find the pixels per unit for both x and y
    xfact = (cx2-cx1)/xtop
    yfact = (cy2-cy1)/ytop
    #generate and plot a case for 0 (as the data starts at 1)
    _, fcy = min(xy_coord, key=lambda x: x[0])
    points += str(round(cx1))+","+str(min(cy2-round(fcy*yfact), cy2))+" "
    #plot the points
    for x_cd, y_cd in xy_coord:
        points += str(round(x_cd*xfact)+cx1)+","+str(min(cy2-round(y_cd*yfact), cy2))+" "
    last_in = sorted(xy_coord)[-1]
    last_coords = (str(round(last_in[0]*xfact)+cx1), str(min(cy2-round(last_in[1]*yfact), cy2)))
    return points, last_coords

#reference: https://stackoverflow.com/questions/361681/
def best_tick(largest: float, most_ticks: int) -> float:
    """Generate a 'nice' interval for graphs given a max value and most number of intervals

    Arguments:
        largest:A number which represents the greatest amount that needs to be displayed.
        most_ticks: A integer which represents the most number of intervals that
            should be displayed.

    Returns:
        A number: that is the best unit of increment for the input data.
    """
    minimum = largest / most_ticks#minimum increment
    magnitude = 10 ** math_floor(math_log(minimum, 10))
    residual = minimum / magnitude#most significant digit of the minimum increment
    if residual > 5:
        tick = 10 * magnitude
    elif residual > 2:
        tick = 5 * magnitude
    elif residual > 1:
        tick = 2 * magnitude
    else:
        tick = magnitude
    return tick


@FLASK_APP.route('/')
def page_home() -> str:
    """A basic function that returns the homepage loaded earlier."""
    LOGGER.info("Home page requested")
    return PAGES["top_bar"]+PAGES["home"]

@FLASK_APP.route('/process')
def page_process() -> str:
    """A function that returns the Processing page

    This function generates the processing page by:
    first checking if there is a action button that has been pressed and dealing with it
    then loading the svg tanks on the left
    then loading the suggested actions on the right
    then loading the tank_summary below on the right if a tank has been clicked

    Returns:
        A string: containing the web-page HTML to be shown to the user
    """
    LOGGER.info("process page requested")
    #Action request parser
    action_selected = request.args.get("action_selected")
    tank_selected = request.args.get("tank_selected")
    action_output = ""
    action_colour = "black"
    if action_selected == "add_hot_brew":
        LOGGER.debug("action_selected = add_hot_brew")
        beer_selected = request.args.get("beer_selected")
        volume = request.args.get("volume")
        days_to_run = request.args.get("days_to_run")
        try:
            tank_add_hot_brew(tank_selected, beer_selected, -1, int(volume), int(days_to_run))
            action_output = "The fermentation on tank '"+tank_selected+"' has begun for"+\
                            " the beer '"+beer_selected+"'."
        except (ValueError, TypeError) as exc_code:
            LOGGER.warning("user error observed:"+str(exc_code))
            action_colour = "red"
            action_output = str(exc_code)

    elif action_selected == "condition":
        LOGGER.debug("action_selected = condition")
        reciving_tank_selected = request.args.get("rtank_selected")
        days_to_run = request.args.get("days_to_run")
        try:
            tank_transfer_to_condition(tank_selected, reciving_tank_selected,
                                       int(days_to_run), -1, True)
            action_output = "The contents of tank '"+tank_selected+"' are now "+\
                            "conditioning in tank '"+reciving_tank_selected+"'."
        except (ValueError, TypeError) as exc_code:
            LOGGER.warning("user error observed: %s" % (exc_code))
            action_colour = "red"
            action_output = str(exc_code)

    elif action_selected == "bottle":
        LOGGER.debug("action_selected = bottle")
        try:
            tank_bottle(tank_selected, True)
            action_output = "The tank '"+tank_selected+"' has been bottled and added to stock."
        except (ValueError, TypeError) as exc_code:
            LOGGER.warning("user error observed: %s" % (exc_code))
            action_colour = "red"
            action_output = str(exc_code)

    elif action_selected == "purge":
        LOGGER.debug("action_selected = purge")
        try:
            tank_empty(tank_selected)
            action_output = "The tank '"+tank_selected+"' has been purged."
        except (ValueError, TypeError) as exc_code:
            LOGGER.warning("user error observed: %s" % (exc_code))
            action_colour = "red"
            action_output = str(exc_code)



    #Page Construction
    #beginning left column
    LOGGER.debug("beginning page construction")
    page = PAGES["top_bar"]#add top bar
    page += PAGES["blank"].replace("%s", "")
    #find Priority beers:
    zero_at = beer_stocks_zero_at()
    prio_beers, impo_beers = find_important_and_priority_beers(zero_at)
    #get the data to display
    data_to_show = generate_usage_summary()
    dyn_data = read_dynamic_data()
    page_part = ""
    loop_number = 0
    for tank in data_to_show:
        #prepare display data
        if STATIC_DATA["equipment"][tank[0]]["conditioner"]:
            cvis = "visible"
        else:
            cvis = "hidden"
        if STATIC_DATA["equipment"][tank[0]]["fermenter"]:
            tvis = "visible"
        else:
            tvis = "hidden"
        if tank[3] > DAYS_BEFORE_OPERATION_REMINDER*86400:
            col = "#0f0"
        elif tank[1] in prio_beers:
            col = "#f00"
        elif tank[1] in impo_beers:
            col = "#f80"
        else:
            col = "#ff0"
        display_name = tank[0][:9]
        if display_name != tank[0]:
            display_name = display_name[:8]+"…"
        display_brew = tank[1]
        if len(display_brew) > 8:
            if display_brew[:8] == "organic ":
                display_brew = display_brew[8:]
        if len(display_brew) > 8: #still to long
            display_brew = display_brew[:7]+"…"

        #apply display data
        tank_graf = PAGES["tank"]
        if tank[2] == "Fermenting":
            tank_graf = tank_graf.replace("%tcol", col)
            tank_graf = tank_graf.replace("%ccol", "#fff")
        elif tank[2] == "Conditioning":
            tank_graf = tank_graf.replace("%tcol", col)
            tank_graf = tank_graf.replace("%ccol", col)
        else:
            tank_graf = tank_graf.replace("%ccol", "#aaa").replace("%tcol", "#bbb")
        tank_graf = tank_graf.replace("%tvis", tvis)
        tank_graf = tank_graf.replace("%cvis", cvis)
        tank_graf = tank_graf.replace("%name", display_name)
        tank_graf = tank_graf.replace("%what", display_brew)
        tank_graf = tank_graf.replace("%imgid", str(hash(tank[0])))
        page_part += tank_graf

        loop_number += 1
        if loop_number >= TANKS_ON_ONE_LINE:
            loop_number = 0
            page_part += "<p></p>\n"

    page_chunk = PAGES["columns"].replace("%left", page_part)
    #beginning right column
    LOGGER.debug("beginning page-right construction")

    suggested_actions = best_next_action()
    page_part = ""
    rows = ""
    for action in suggested_actions['Priority']:
        rows += PAGES["tablerow"].replace("%import", 'Priority').replace("%action", action[2])
    for action in suggested_actions['Important']:
        rows += PAGES["tablerow"].replace("%import", 'Important').replace("%action", action[2])
    for action in suggested_actions['Upkeep']:
        rows += PAGES["tablerow"].replace("%import", 'Upkeep').replace("%action", action[2])
    for action in suggested_actions['Surplus']:
        rows += PAGES["tablerow"].replace("%import", 'Surplus').replace("%action", action[2])

    page_part += PAGES["table_top"].replace("%s", rows)

    #tank_summary start
    clicked = request.args.get("clicked")
    tank_summary = ""
    if clicked:
        LOGGER.debug("A tank has been clicked:"+str(clicked))
        rel_data = dyn_data['equipment_state'][clicked]#relevant data
        tank_summary = PAGES["tank_summary"]
        tank_summary = tank_summary.replace("%name", clicked)
        tank_summary = tank_summary.replace("%max_vol_poss",
                                            str(STATIC_DATA["equipment"][clicked]["volume"]))
        tank_summary = tank_summary.replace("%default_frun", str(MEAN_BEER_FERMENT_TIME))
        tank_summary = tank_summary.replace("%default_crun", str(MEAN_BEER_CONDITION_TIME))
        sugested_action = find_suggested_action_by_tank(suggested_actions, clicked)
        #Tank states panel
        if rel_data["active"]:
            tank_summary = tank_summary.replace("%contents", rel_data["type"])
            tank_summary = tank_summary.replace("%volume", str(rel_data["volume"]))
            tank_summary = tank_summary.replace("%stage", rel_data["stage"])
            tank_summary = tank_summary.replace("%gyle", str(rel_data["gyle_number"]))
            time_til_dones = list(filter(lambda x: x[0] == clicked, data_to_show))[0][3]
            time_til_doneh = round(time_til_dones/3600)
            time_til_doned = round(time_til_dones/86400)
            tank_summary = tank_summary.replace("%timetilldoned", str(time_til_doned))
            tank_summary = tank_summary.replace("%timetilldoneh", str(time_til_doneh))
            start_date = "/".join(reversed(unix_to_time(rel_data["unix_time_started"])[:3]))
            tank_summary = tank_summary.replace("%start", start_date)
            tank_summary = tank_summary.replace("%runtime",
                                                str(round(rel_data["run_length"]/86400)))
            if sugested_action:
                tank_summary = tank_summary.replace("%suggested_act",
                                                    sugested_action[0].replace("-", " "))
                tank_summary = tank_summary.replace("%show_button", "normbx")
                tank_summary = tank_summary.replace("%suggest_code_name",
                                                    format_sugested_action(sugested_action))
            else:
                tank_summary = tank_summary.replace("%suggested_act", "No action required")
                tank_summary = tank_summary.replace("%show_button", "hidden")
        else:
            tank_summary = tank_summary.replace("%contents", "None")
            tank_summary = tank_summary.replace("%volume", "0")
            tank_summary = tank_summary.replace("%stage", "Inactive")
            tank_summary = tank_summary.replace("%gyle", "---")
            tank_summary = tank_summary.replace("%timetilldoned", "---")
            tank_summary = tank_summary.replace("%timetilldoneh", "---")
            tank_summary = tank_summary.replace("%start", "Never")
            tank_summary = tank_summary.replace("%runtime", "0")
            if sugested_action:
                tank_summary = tank_summary.replace("%suggested_act",
                                                    sugested_action[0].replace("-", " "))
                tank_summary = tank_summary.replace("%show_button", "normbx")
                tank_summary = tank_summary.replace("%suggest_code_name",
                                                    format_sugested_action(sugested_action))
            else:
                tank_summary = tank_summary.replace("%suggested_act", "No action required")
                tank_summary = tank_summary.replace("%show_button", "hidden")

        #tank_buttons panel

        beer_options = ""
        for beer in list(dyn_data['liters_of_bottled_beer'].keys())[:]:
            if sugested_action:
                if sugested_action[0] == "Add-hot-brew-to-tank":
                    #indented not and'ed as not all sugested_action can be indexed at 3
                    if sugested_action[3] == beer:
                        beer_options += '<option value="'+str(beer)+\
                                        '" class=cblue>'+str(beer)+'</option>\n'
                        continue
            beer_options += '<option value="'+str(beer)+'">'+str(beer)+'</option>\n'

        tank_summary = tank_summary.replace("%beer_options", beer_options)

        tanks_free = find_when_tanks_free()
        tank_opt = []
        for tank, weeks in tanks_free[0].items():
            #only consider a tank if it can condition and the beer will fit
            if (STATIC_DATA["equipment"][tank]["conditioner"] and
                    STATIC_DATA["equipment"][tank]["volume"] >=
                    dyn_data["equipment_state"][clicked]["volume"]):
                if tank == clicked:
                    tank_opt.append(tank)
                elif weeks == 0:
                    tank_opt.append(tank)
                elif not dyn_data["equipment_state"][tank]["active"]:
                    tank_opt.append(tank)
        tank_opt_text = ""
        for tank_sel in tank_opt:
            if sugested_action:
                if sugested_action[0] == "Move-and-condition":
                    if sugested_action[1][1] == tank_sel:
                        tank_opt_text += '<option selected value="'+str(tank_sel)+\
                                         '" class=cblue>'+str(tank_sel)+'</option>\n'
                        continue
                elif sugested_action[0] == "Condition-in-current-tank":
                    if sugested_action[1] == tank_sel:
                        tank_opt_text += '<option selected value="'+str(tank_sel)+\
                                         '" class=cblue>'+str(tank_sel)+'</option>\n'
                        continue
            tank_opt_text += '<option value="'+str(tank_sel)+'">'+str(tank_sel)+'</option>\n'

        tank_summary = tank_summary.replace("%tank_options", tank_opt_text)

        tank_summary = tank_summary.replace("%tknm", str(clicked))
        #Show buttons only if clicking them would make sense in the context
        if (STATIC_DATA["equipment"][clicked]["fermenter"] and
                (not dyn_data["equipment_state"][clicked]["active"])):
            tank_summary = tank_summary.replace("%cls_add_hot", "normbx")
        else:
            tank_summary = tank_summary.replace("%cls_add_hot", "hidden")

        if dyn_data["equipment_state"][clicked]["stage"] == "Fermenting":
            tank_summary = tank_summary.replace("%cls_condition", "normbx")
        else:
            tank_summary = tank_summary.replace("%cls_condition", "hidden")

        if dyn_data["equipment_state"][clicked]["stage"] == "Conditioning":
            tank_summary = tank_summary.replace("%cls_bottle", "normbx")
        else:
            tank_summary = tank_summary.replace("%cls_bottle", "hidden")
        #highlight buttons in blue if they are the suggested action
        if sugested_action:
            if sugested_action[0] == "Add-hot-brew-to-tank":
                tank_summary = tank_summary.replace("%imp_add_hot", "cblue")
            else:
                tank_summary = tank_summary.replace("%imp_add_hot", "cnor")
            if sugested_action[0] in ["Condition-in-current-tank", "Move-and-condition"]:
                tank_summary = tank_summary.replace("%imp_condition", "cblue")
            else:
                tank_summary = tank_summary.replace("%imp_condition", "cnor")
            if sugested_action[0] == "Bottle-tank-contents":
                tank_summary = tank_summary.replace("%imp_bottle", "cblue")
            else:
                tank_summary = tank_summary.replace("%imp_bottle", "cnor")


        page_part += tank_summary
        LOGGER.debug("The tank_summary page has been constructed successfully")
    page_part += '<h2><font color="'+action_colour+'">'+action_output+'</font></h2>'

    page_chunk = page_chunk.replace("%right", page_part)

    page += page_chunk
    return page

@FLASK_APP.route('/predict')
def page_predict() -> str:
    """A function that returns the Prediction & Stocks page

    This function generates the Prediction & Stocks page by:
    first checking if there is a stock change request and if so performing it
    After checking and finding a stock change request redirecting
    (to the same page without the request ensure the message is not double sent)
    Then Loading the Left side first svg graph
    Loading the second svg Graph
    Then finally loading the right side

    Returns:
        A string: containing the web-page HTML to be shown to the user
    """
    LOGGER.info("predictions page requested")
    #Has a stock change request just been made?:
    stock_change = request.args.get("stock_change")
    if stock_change:
        if stock_change == "inprogress":
            LOGGER.debug("stock_change in progress")
            beer_selected = request.args.get("beer_selected")
            volume = request.args.get("volume")
            dyn_data = read_dynamic_data()
            try:
                if (dyn_data['liters_of_bottled_beer'][beer_selected]+float(volume)) < 0:
                    return redirect("/predict?stock_change=that+volume+would"+\
                                    "+reduce+the+stock+below+0")
                edit_stock(beer_selected, volume)
            except (TypeError, ValueError) as exc_code:
                abort(400, exc_code)
                return None
            message = "The+stock+for+the+beer+%27"+beer_selected.replace(" ", "+")+\
                      "%27+has+been+changed+by:+"+volume+"+liters."
            LOGGER.debug("stock_change complete redirecting")
            return redirect("/predict?stock_change="+message)


    page = PAGES["top_bar"]+"<p></p>"

    page += PAGES["columns"]
    #left side
    LOGGER.debug("starting first graph")
    #drawing svg graph:
    title = '<br><form action="/why" , style="display: inline-block;">'+\
                '<input type="checkbox" name="stocks" value="general" '+\
                'checked style="display: none">'+\
                '<div>'+\
                '<label style="font-size: 1.17em;margin-top: 1em;margin-bottom:'+\
                '1em;margin-left: 0;margin-right: 0;font-weight: bold;">Stocks:'+\
                '&nbsp&nbsp&nbsp&nbsp </label>'+\
                '<input type="submit" value="why?" style="display: inline-block;">'+\
                '</div>'+\
            '</form><br>'

    lpage = title
    predicted_stocks_full = predict_remaining_stocks(WEEKS_TO_SHOW_PREDICTIONS_FOR)
    graph_able_stocks = stocks_to_xy(predicted_stocks_full)
    max_found = 0
    for beer, plot in graph_able_stocks[0].items():
        max_for_beer = max(plot, key=lambda x: x[1])[1]
        max_found = max(max_found, max_for_beer)
    tick_size = best_tick(max_found, 10)
    carry_over = 0
    number_of_ticks = 0
    while carry_over < max_found:
        carry_over += tick_size
        number_of_ticks += 1
    pixel_per_tick = 360/number_of_ticks
    graph_lines = ""
    for tick in range(1, number_of_ticks+1):
        graph_lines += '<line x1="68" y1="'+str(380-round(tick*pixel_per_tick))+\
                       '" x2="625" y2="'+ str(380-round(tick*pixel_per_tick))+\
                       '" stroke="#888" stroke-width="1"/>'
        graph_lines += '<text x="65" y="'+str(380-round(tick*pixel_per_tick))+\
                       '" text-anchor="end" alignment-baseline="middle" fill="black">'+\
                       str(round(tick*tick_size))+'</text>'

    xtick_size = best_tick(WEEKS_TO_SHOW_PREDICTIONS_FOR, 10)
    xcarry_over = 0
    xnumber_of_ticks = 0
    while xcarry_over+xtick_size <= WEEKS_TO_SHOW_PREDICTIONS_FOR:
        xcarry_over += xtick_size
        xnumber_of_ticks += 1
    xpixel_per_tick = (550/WEEKS_TO_SHOW_PREDICTIONS_FOR)*xtick_size
    graph_xlines = ""
    for tick in range(1, xnumber_of_ticks+1):
        graph_xlines += '<text x="'+str(75+round(tick*xpixel_per_tick))+'" y="382"'+\
                        'text-anchor="middle" alignment-baseline="hanging" fill="black">'+\
                        str(round(xtick_size*tick))+'</text>'


    graph_poly = ""
    count = 0
    for beer, plot in graph_able_stocks[0].items():
        g_able_coord = xy_svg_polyline_points(plot, WEEKS_TO_SHOW_PREDICTIONS_FOR,
                                              tick_size*number_of_ticks, 75, 20, 625, 380)
        colour = PREDICTION_COLOURS[count%len(PREDICTION_COLOURS)]
        count += 1
        graph_poly += '<polyline stroke="'+colour+'" fill-opacity="0"'+\
                      ' stroke-width="2" points="'+g_able_coord[0]+'"/>'
        display_name = beer
        if display_name[:8] == "organic ":
            display_name = display_name[8:]
        graph_poly += '<text x="'+str(int(g_able_coord[1][0])+3)+'" y="'+g_able_coord[1][1]+\
                      '" text-anchor="start" alignment-baseline="middle" fill="'+colour+'">'+\
                      str(display_name)+'</text>'

    graph_svg_elemet = PAGES["graph"]
    graph_svg_elemet = graph_svg_elemet.replace("%graph_polygons", graph_poly)
    graph_svg_elemet = graph_svg_elemet.replace("%graph_increments", graph_lines)
    graph_svg_elemet = graph_svg_elemet.replace("%graph_xincrements", graph_xlines)
    graph_svg_elemet = graph_svg_elemet.replace("%ylabel", "Remaining stocks (liters)")
    graph_svg_elemet = graph_svg_elemet.replace("%xlabel", "Weeks (from now)")
    lpage += graph_svg_elemet
    #second graph
    LOGGER.debug("starting second graph")

    title = '<br><form action="/why" , style="display: inline-block;">'+\
                '<input type="checkbox" name="predict" value="general"'+\
                'checked style="display: none">'+\
                '<div>'+\
                '<label style="font-size: 1.17em;margin-top: 1em;margin-bottom:'+\
                '1em;margin-left: 0;margin-right: 0;font-weight: bold;">Predicted Demand:'+\
                '&nbsp&nbsp&nbsp&nbsp </label>'+\
                '<input type="submit" value="why?" style="display: inline-block;">'+\
                '</div>'+\
            '</form><br>'

    lpage += title


    max_found = 0
    for beer, plot in graph_able_stocks[1].items():
        max_for_beer = max(plot, key=lambda x: x[1])[1]
        max_found = max(max_found, max_for_beer)
    tick_size = best_tick(max_found, 10)
    carry_over = 0
    number_of_ticks = 0
    while carry_over < max_found:
        carry_over += tick_size
        number_of_ticks += 1
    pixel_per_tick = 360/number_of_ticks
    graph_lines = ""
    for tick in range(1, number_of_ticks+1):
        graph_lines += '<line x1="68" y1="'+str(380-round(tick*pixel_per_tick))+\
                       '" x2="625" y2="'+str(380-round(tick*pixel_per_tick))+\
                       '" stroke="#888" stroke-width="1"/>'
        graph_lines += '<text x="65" y="'+str(380-round(tick*pixel_per_tick))+\
                        '" text-anchor="end" alignment-baseline="middle" fill="black">'+\
                        str(round(tick*tick_size))+'</text>'

    xtick_size = best_tick(WEEKS_TO_SHOW_PREDICTIONS_FOR, 10)
    xcarry_over = 0
    xnumber_of_ticks = 0
    while xcarry_over+xtick_size <= WEEKS_TO_SHOW_PREDICTIONS_FOR:
        xcarry_over += xtick_size
        xnumber_of_ticks += 1
    xpixel_per_tick = (550/WEEKS_TO_SHOW_PREDICTIONS_FOR)*xtick_size
    graph_xlines = ""
    for tick in range(1, xnumber_of_ticks+1):
        graph_xlines += '<text x="'+str(75+round(tick*xpixel_per_tick))+'" y="382"'+\
                        'text-anchor="middle" alignment-baseline="hanging" fill="black">'+\
                        str(round(xtick_size*tick))+'</text>'


    graph_poly = ""
    count = 0
    for beer, plot in graph_able_stocks[1].items():
        g_able_coord = xy_svg_polyline_points(plot, WEEKS_TO_SHOW_PREDICTIONS_FOR,
                                              tick_size*number_of_ticks, 75, 20, 625, 380)
        colour = PREDICTION_COLOURS[count%len(PREDICTION_COLOURS)]
        count += 1
        graph_poly += '<polyline stroke="'+colour+'" fill-opacity="0"'+\
                      ' stroke-width="2" points="'+g_able_coord[0]+'"/>'
        display_name = beer
        if display_name[:8] == "organic ":
            display_name = display_name[8:]
        graph_poly += '<text x="'+str(int(g_able_coord[1][0])+3)+'" y="'+g_able_coord[1][1]+\
                      '" text-anchor="start" alignment-baseline="middle" fill="'+colour+'">'+\
                      str(display_name)+'</text>'

    graph_svg_elemet = PAGES["graph"]
    graph_svg_elemet = graph_svg_elemet.replace("%graph_polygons", graph_poly)
    graph_svg_elemet = graph_svg_elemet.replace("%graph_increments", graph_lines)
    graph_svg_elemet = graph_svg_elemet.replace("%graph_xincrements", graph_xlines)
    graph_svg_elemet = graph_svg_elemet.replace("%ylabel", "Predicted demand (liters)")
    graph_svg_elemet = graph_svg_elemet.replace("%xlabel", "Weeks (from now)")
    lpage += graph_svg_elemet

    page = page.replace("%left", lpage)
    #right side
    LOGGER.debug("constructing right hand panel")
    rpage = "<h3>Current stocks (liters):</h3><ul>"
    beers = []
    for beer, amount in read_dynamic_data()["liters_of_bottled_beer"].items():
        rpage += "<li>"+beer+": <b>"+str(round(amount))+"</b></li>"
        beers.append(beer)

    rpage += "</ul>"

    beer_opt = ""
    for beer in beers:
        beer_opt += '<option value="'+str(beer)+'">'+str(beer)+'</option>\n'
    sform = PAGES["stock_change_form"].replace("%beer_options", beer_opt)

    rpage += sform
    if stock_change:
        rpage += "\n"+stock_change+"\n"
    page = page.replace("%right", rpage)
    LOGGER.debug("returning page")
    return page



@FLASK_APP.route('/why')
def page_why() -> str:
    """A function that returns the Why? page

    This function generates the processing page by:
    Working out what the user queried then returning a page customized based on that

    Returns:
        A string: containing the web-page HTML to be shown to the user
    """
    LOGGER.info("WHY??? page requested")
    suggest = request.args.get("suggest")
    if suggest:
        LOGGER.info("A suggestion was queried")
        suggest = unformat_sugested_action(suggest)
        page = PAGES["top_bar"]+"<br>"+PAGES["suggest_exp"]
        page = page.replace("%short_qcode", suggest[0])
        message = "Unknown command ("+suggest[0]+")"
        if suggest[0] == "Bottle-tank-contents":
            message = "You are seeing this suggestion because the tank '"+suggest[1]+\
                      "' is within <b>"+str(DAYS_BEFORE_OPERATION_REMINDER)+\
                      "</b> days of it's end date and it is currently Conditioning."
        if suggest[0] == "Condition-in-current-tank":
            message = "You are seeing this suggestion because:<ul><li> the tank '"+suggest[1]+\
                      "' is within <b>"+str(DAYS_BEFORE_OPERATION_REMINDER)+\
                      "</b> days of it's end date</li><li> it is currently Fermenting</li>"+\
                      "<li>and the tank it is currently in is capable of conditioning</li></ul>"
        if suggest[0] == "Move-and-condition":
            message = "You are seeing this suggestion because:<ul><li> the tank '"+suggest[1][0]+\
                      "' is within <b>"+str(DAYS_BEFORE_OPERATION_REMINDER)+\
                      "</b> days of it's end date</li><li> '"+suggest[1][0]+\
                      "' is currently Fermenting</li>"+\
                      "<li>and the tank it is currently in is not capable of conditioning "+\
                      "it</li></ul>"+"The tank '"+suggest[1][1]+"' was selected as:<ul>"
            if not STATIC_DATA["equipment"][suggest[1][1]]["fermenter"]:
                message += "<li>It has sufficient volume to accept all the beer</li>"+\
                           "<li>It cannot ferment, so gets less use normally</li>"
            else:
                message += "<li>It has sufficient volume to accept all the beer</li><li>"+\
                           "All the tanks that cannot ferment"+\
                           " where either in use or too small</li>"
        if suggest[0] == "Add-hot-brew-to-tank":
            #confirm that the beer to brew is the same and simultaneously obtain data for it
            #This must be done as the user may have waited between loading the page and pressing
            #the button and in such a case the data may have now changes as unlike other simple
            #suggestions Add-hot-brew-to-tank cannot have all it's data in the url easily
            zero_at = beer_stocks_zero_at()
            tanks_free = find_when_tanks_free()
            prio_beers, impo_beers = find_important_and_priority_beers(zero_at)
            beer_to_brew, weeks_zero = min(zero_at.items(), key=lambda x: x[1])
            try:
                tank_name, _ = list(filter(lambda x: x[1] == 0, tanks_free[0].items()))[:][0]
            except IndexError:#A tank became full while the user deliberated
                message = "Something changed, this action is now incorrect please press back"
            else:
                if tank_name == suggest[1]:
                    priority_level = "Surplus"
                    if beer_to_brew in impo_beers:
                        priority_level = "Important"
                    if beer_to_brew in prio_beers:
                        priority_level = "Priority"
                    message = "This has been suggested because:<ul>"+\
                              "<li>Based on predicted demand for <b>"+beer_to_brew+"</b>"+\
                              " offset by current stocks of it and expected production"+\
                              "(from tanks finishing brewing) it will run out the soonest</li>"+\
                              "<li>It has been given priority: <b>"+priority_level+\
                              "</b> because"+\
                              " it will run out in about <b>"+str(weeks_zero)+"</b> weeks</li>"+\
                              "</ul>The tank <b>"+tank_name+"</b> was suggested because:<ul>"+\
                              "<li>The tank <b>"+tank_name+"</b> is not in use</li>"+\
                              "<li>The tank <b>"+tank_name+"</b> can ferment</li>"+\
                              "<li>The tank <b>"+tank_name+"</b> is not reserved</li></ul>"
                else:
                    message = "Something changed, this action is now incorrect please press back"


        page = page.replace("%general_explanation", message)
        page = page.replace("%desc", suggest[2])
        return page

    predict = request.args.get("predict")
    if predict:
        LOGGER.info("A prediction was queried")
        if predict == "general":
            LOGGER.debug("   It was a general prediction")
            page = PAGES["top_bar"]+"<br>"+PAGES["predict_g_exp"]
            page = page.replace("%short_qcode", "Predict-general")
            message = "The prediction over time is generated via predicting each"+\
                      " week on it's own. To find out why a week has the prediction"+\
                      " it does; please click the relevant 'why?' button below."
            page = page.replace("%general_explanation", message)

            demand_pred = generate_demand_for_next_weeks(WEEKS_TO_SHOW_PREDICTIONS_FOR)
            listed_text = ""
            for beer in read_dynamic_data()["liters_of_bottled_beer"].keys():
                listed_text += "<h3>"+str(beer)+"</h3>"
                for week, gdata in demand_pred.items():
                    list_row = PAGES["predict_grow"].replace("%week", str(week))
                    list_row = list_row.replace("%demand", str(round(gdata[0][beer])))
                    list_row = list_row.replace("%beer_type", beer)
                    listed_text += list_row

            page = page.replace("%weeks", listed_text)
            return page

        if predict == "specific":
            LOGGER.debug("   It was a specific prediction")
            qweek = request.args.get("week")
            qbeer = request.args.get("beer")
            try:
                demand_pred = generate_demand_for_next_weeks(WEEKS_TO_SHOW_PREDICTIONS_FOR)
                demand_pred = demand_pred[int(qweek)]
            except KeyError:
                LOGGER.warning("Week Does not exist:"+str(qweek))
                abort(400, 'Week Does not exist')
            except ValueError:
                LOGGER.warning('Week... is not a number?'+str(qweek))
                abort(400, 'Week... is not a number?')#should be unreachable
            page = PAGES["top_bar"]+"<br>"+PAGES["predict_s_exp"]

            page = page.replace("%short_qcode", "Week-"+qweek+"-beer-"+qbeer.replace(" ", "-"))
            page = page.replace("%GROWTH_IMPORTANCE", str(GROWTH_IMPORTANCE))

            message = "For the week <b>"+qweek+"</b> the expected demand is <b>"+\
                      str(demand_pred[0][qbeer])+"</b>.  This is made from an average "+\
                      "of the weeks: <br>&nbsp&nbsp&nbsp&nbsp"
            for week_tuple in demand_pred[1][qbeer]:
                message += week_tuple[0]+", "
            message = message[:-2]
            message += "<p>Below is a list showing those weeks, their total sold for the week,"+\
                       " there growth modifyer and their final value that contributed to the"+\
                       " average. <ul>"
            for week_tuple in demand_pred[1][qbeer]:
                message += (("<li>Week: <b>%s</b>, Total sold: <b>%s</b>,"+\
                           "Growth value: <b>%s</b>, Final effect: <b>%s</b></li>") %
                            (week_tuple[0], str(round(float(week_tuple[1][2]))),
                             str(round(float(week_tuple[1][1]))),
                             str(round(float(week_tuple[1][0])))))
            message += "</ul><br>Finally what follows is a list of the transactions that have"+\
                       " lead to this total sold:<br>"
            for week_tuple in demand_pred[1][qbeer]:
                message += "<h4>"+week_tuple[0]+"</h4><ul>"
                for trans in week_tuple[2]:
                    message += "<li>Invoice Number: <b>"+trans["Invoice Number"]+"</b>"+\
                               " customer: <b>"+trans["customer"]+"</b>"+\
                               " date: <b>"+trans["date required"]+"</b>"+\
                               " recipe: <b>"+trans["recipe"]+"</b>"+\
                               " gyle Number: <b>"+trans["gyle Number"]+"</b>"+\
                               " volume: <b>"+str(trans["quantity ordered"])+"</b></li>"
                message += "</ul>"



            page = page.replace("%specific_data", str(message))

            return page
    stocks = request.args.get("stocks")
    if stocks:
        LOGGER.info("The stocks were queried")
        page = PAGES["top_bar"]+"<br>"+PAGES["stocks_g_exp"]
        #for the tanks that finsh find: when, name and beer type of them
        found_tank_finishes = []
        for week, week_what in generate_inventory_summary().items():
            if type(week_what[1]) == dict:
                for beer in read_dynamic_data()["liters_of_bottled_beer"].keys():
                    if len(week_what[1][beer]) != 0:
                        for tank_finish in week_what[1][beer]:
                            found_tank_finishes.append((tank_finish[0], tank_finish[1], beer))
        tchange = ""
        for tank in found_tank_finishes:
            tchange += "<li> week: "+str(tank[0])+" name:"+str(tank[1])+\
                      " beer type:"+str(tank[2])+"</li>"
        page = page.replace("%tanks", tchange)

        return page
    LOGGER.error("There is no recognized query, aborting.")
    abort(500, 'No recognized query')
    return None




def begin_flask():
    """A function to call FLASK_APP.run() and start the execution.

    This function exists for 2 reasons:
        1. So that the blocking line FLASK_APP.run() can easily be threaded
        2. To deal with the error the IDLE throws up when trying to run FLASK_APP.run()
    """
    try:
        LOGGER.info("Beginning flask")
        FLASK_APP.run(host="0.0.0.0", port=5001)
    except IOError:
        #used as IDLE won't run FLASK_APP.run() and the command line will
        #just calls itself from the command line
        #error otherwise: io.UnsupportedOperation: fileno
        LOGGER.info("Flask begin failed, error caught and trying again")
        system("cmd /k python brewing.py")


###Flask Interface end




if __name__ == '__main__':
    #Begin the threaded Flask call.  It is threaded for developers so that it is easy to add
    #additional functionally in the future as well as allowing testing to be performed easier
    #during development.
    THREAD_FLASK = Thread(target=begin_flask)
    THREAD_FLASK.start()
    LANIP = socket_gethostbyname(socket_gethostname())
    print("Expected Localhost Connection: 127.0.0.1:5001")
    print("Expected LAN Connection: "+LANIP+":5001")
