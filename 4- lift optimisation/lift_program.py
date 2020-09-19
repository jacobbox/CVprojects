"""A module to implement a lift control system.  It also implements a simulation
system to test the control system.  As well as this it provides a mass testing
function to allow a greater accuracy of testing.

Key functions and classes:
    GraphicalDisplay     ┬ A class used to display the lift data
        update_display   └-- the main GraphicalDisplay function used to update lift
                             data that should be displayed
    planner_basic        - A function to generate the next floor to go to under the
                           base case algorithm.
    simulate             - A function to simulate a single trial of an algorithm
                           for a passed set of starting conditions
    normal_cost_function - A function to return the cost of the current lift data in
                           terms of the amount of time people spent waiting this iteration
    generator_uniform    - A function to generate a uniform distribution of people on
                           random floors with uniform distribution of random destinations.
    generator_skewed     - A function to generate a skewed distribution to simulate either
                           day-start or day-end.
    planner_advanced     - A function to implement my custom algorithm for lift control
    batch                - A function to mass test simulations of different algorithms
    out_bat_to_3d_coord  - Takes the output of the batch function and prepares it for
                           plotting by converting it to 3d coordinates.
    al_coord_shown       - Plot and display 3d coords onto a matplotlib contour plot

Notes on use:
    This code is dependent on the modules:
        scipy
        numpy
        matplotlib
    all of which must be installed (normally via pip) for the code to function.
    Python 3.7.4 was used in production and testing thus python 3.7.4 or later should be used
    Windows 10 was used for testing,  whilst it shouldn't matter it definitely works on windows 10
"""
from tkinter import Tk, Canvas, Label, Entry, Button, StringVar
from math import floor as math_floor, log as math_log
from random import randint as random_randint, random as random_random
from time import sleep, time as ttime
from copy import deepcopy
import scipy.interpolate as sp
import numpy as np
import matplotlib.pyplot as plt


BLANK_LIFT_DATA = {"lift dir":"up", "floor target":0, "lift people":[], "lift max people":6,
                   "floor info":[], "lift floor":0}

#config constants:
GETTING_OFF_IMPORTANCE = 2
TARGETING_IMPORTANCE = 2
DISTANCE_NEGATIVE_IMPORTANCE = 1

SIMULATION_CHECKUP_FREQ = 5#how long between check-in's if a simulation is taking a while



class GraphicalDisplay:
    """A class to construct and control a lift output GUI

    This class creates and manages the gui which data in the form of
    BLANK_LIFT_DATA can be displayed upon.

    Functions: (public only)
        Constructor    - Creates the window and optionally populates it with default data
        update_display - Main command used, call this with a lift data
                         dictionary to display the frame the lift data describes
        safe_sleep     - helper that performs sleep without freezing the interface
        block_stop     - stops until a valid unblock event occurs (from the GUI)
        set_cost_info  - set's the cost info to be displayed
    """

    def __init__(self, starting_data=None):
        """initialize the tkinter window and setup the static display elements

        Arguments:
            starting_data - if provided the dynamic elements will also be drawn
                            for the single from starting data represents (default: None)
        """
        self.tk = Tk()#create the window
        #populate the window with static graphics
        self.canvas = Canvas(self.tk, width=500, height=600)
        self.canvas.grid(row=0, column=0, columnspan=6)
        self.canvas.create_rectangle(50, 50, 200, 550)
        self.cost_text = self.canvas.create_text(25, 25, anchor="w", text="Cost: 0 (+?)",
                                                 font=("Helvetica", 18))
        #initialize variables
        self.floors = 0
        self.floor_pix_numbers = []
        self.pix_per_floor = 0
        self.adv = 0#Whether time should advance
        self.spd = 750#number of milliseconds to wait before advancing time
        self.request_solve = False
        #Construct control bar
        Label(self.tk, text="Speed (auto adv): ").grid(row=1, column=0)
        self._spd_trace_var = StringVar(self.tk)
        self.speed_entry = Entry(self.tk, width=5, textvariable=self._spd_trace_var)
        self.speed_entry.grid(row=1, column=1)
        self._safe_spd_edit = False#prevents trace feedback loops
        self._spd_trace_var.set(self.spd)
        self._spd_trace_var.trace("w", self._gui_spd_write)

        #callback for the control buttons
        def set_slf_adv(num, slf=self, *_):
            slf.adv = num
        def set_solve(slf=self, *_):
            slf.adv = -1
            self._spd_trace_var.set(1)
            slf.request_solve = True

        #Create buttons
        Button(self.tk, text="⏸", font=("Helvetica", 16), command=lambda *e: set_slf_adv(0)
               ).grid(row=1, column=2, sticky="e")
        Button(self.tk, text="▶", font=("Helvetica", 16), command=lambda *e: set_slf_adv(1)
               ).grid(row=1, column=3, sticky="e")
        Button(self.tk, text="⏩", font=("Helvetica", 16), command=lambda *e: set_slf_adv(-1)
               ).grid(row=1, column=4, sticky="e")
        Button(self.tk, text="⏭️", font=("Helvetica", 16), command=lambda *e: set_solve()
               ).grid(row=1, column=5, sticky="e")

        #initialize with starting data if provided
        if starting_data:
            self.update_display(starting_data)
        else:
            self._update_floor_number(5)#As it looks odd with nothing there

    def update_display(self, lift_data):
        """Update the dynamic aspects of the display to reflect the input lift_data

        Arguments:
            lift_data - Should be of the form of the BLANK_LIFT_DATA constant except
                        containing the data to be displayed
        """
        #check valid floor number
        number_of_floors = len(lift_data["floor info"])
        if number_of_floors >= 21:
            print("Cannot display")
            return None
        if number_of_floors == 0:
            raise ValueError("There must be at least 1 floor")
        if number_of_floors != self.floors:# only update floor number if needed
            self._update_floor_number(number_of_floors)
        #delete old lift graphics
        self.canvas.delete("lift")
        #get lift display data
        current_floor_pix = self.floor_pix_numbers[lift_data["lift floor"]]
        people_summary = list(map(lambda x: str(x[0]), lift_data["lift people"]))
        people_summary += ["", "", "", "", "", "", "", ""]
        people_summary = (("%-3s"*8) % tuple(people_summary[:8]))
        #display lift and people in lift
        self.canvas.create_rectangle(53, current_floor_pix-self.pix_per_floor+3, 197,
                                     current_floor_pix-3, tags=["lift"])
        self.canvas.create_text(55, current_floor_pix-(self.pix_per_floor/2),
                                anchor="w", text=people_summary, tags=["lift"])
        #delete people waiting on floors
        self.canvas.delete("person")

        for floor in range(0, number_of_floors):
            #get the pixel to generate people on for the current iteration of floor
            floor_center_pix = self.floor_pix_numbers[floor]-(self.pix_per_floor/2)

            for person in range(0, len(lift_data["floor info"][floor])):
                if person >= 11:#check whether the number of people will display with condensing
                    ptxt = "+"+str(len(lift_data["floor info"][floor])-10)+" more"
                    self.canvas.create_text(210+(person*15), floor_center_pix+5,
                                            anchor="w", font=("Courier", 16), text=ptxt,
                                            tags=["person"])
                    break
                #add people
                if lift_data["floor info"][floor][person][0] > floor:
                    self.canvas.create_text(210+(person*15), floor_center_pix,
                                            font=("Courier", 20), text="↑", tags=["person"])
                else:
                    self.canvas.create_text(210+(person*15), floor_center_pix,
                                            font=("Courier", 20), text="↓", tags=["person"])
        #update display to show changes
        self.tk.update()
        self.tk.update_idletasks()

    def _update_floor_number(self, number):
        """An internal function that should not be directly called to update the number of floors.

        This function changes the number of floors shown,  as it is only called when a change
        is detected if it is called to change the number of floors from outside the
        update_display function graphics may display incorrectly for a while.

        Arguments:
            number - The new number of floors
        """
        #clear old data
        self.canvas.delete("floor")
        self.floor_pix_numbers = []
        #generate new floor data
        self.pix_per_floor = pix_per_floor = 500/number
        for i in range(0, number):
            self.canvas.create_line(200, 550-(i*pix_per_floor), 450, 550-(i*pix_per_floor),
                                    tags=["floor"])
            self.canvas.create_text(452, 550-(i*pix_per_floor), anchor="w", text=str(i),
                                    tags=["floor"])
            self.floor_pix_numbers.append(550-(i*pix_per_floor))
        self.floors = number

    def _gui_spd_write(self, *_):
        """This function should not be called,  it is run by the GUI when the step speed changes

        Arguments:
            *_ - A variable to catch the event info the GUI sends,  it is not used hence the _.
        """
        if self._safe_spd_edit:#prevents trace feedback
            return None
        val = self._spd_trace_var.get()

        #check val is an integer
        try:
            val = int(val)
        except ValueError:
            if val == "":
                val = 0
            else:
                self._safe_spd_edit = True#prevents trace feedback from next statement
                self._spd_trace_var.set(self.spd)
                self._safe_spd_edit = False#end trace feedback safe zone
                return None

        #check val is in the permitted range
        if val < 1:
            val = 1
        elif val > 5000:
            val = 5000

        #update display in case val has changed and update internal constants
        self._safe_spd_edit = True#prevents trace feedback from next statement
        self._spd_trace_var.set(val)
        self._safe_spd_edit = False#end trace feedback safe zone
        self.spd = val

    def safe_sleep(self, time, increment=0.01):
        """Same as time.sleep except the tk window will still respond to user inputs.

        Arguments:
            time      - the time to sleep for in seconds.
            increment - the time to wait between redrawing the output window

        Side Effects:
            Pauses execution (via time.sleep)
        """
        count = time/increment#number of loops required
        while count > 0:
            start = ttime()
            self.tk.update()
            count -= 1
            #sleeps for increment minus GUI processing time this helps keep safe_sleep consistent
            sleep(pos(ttime() - start + increment))

    def block_stop(self):
        """When called it will block until self.adv >= 1 and self.spd milliseconds have elapsed

        Side Effects:
            Pauses execution (via time.sleep)
        """
        if self.adv <= -1:#if auto advancing add pause
            self.safe_sleep(self.spd/1000)
        while self.adv == 0:#sleep until graf.adv != 0
            self.safe_sleep(0.099)
        self.adv -= 1#reduce the number of advances to do by 1

    def set_cost_info(self, total, change):
        """Helper function: changes the GUI cost output widget

        Arguments:
            total  - The total cost to be displayed.
            change - The change in cost over the last step to  be displayed.
        """
        self.canvas.itemconfig(self.cost_text, text="Cost: %s (+%s)" % (total, change))


def planner_basic(lift_data):
    """Return the floor number to go to using a basic algorithm.

    Arguments:
        lift_data - Should be of the form of the BLANK_LIFT_DATA constant except
                    containing data about the current state of the lift from which
                    the algorithm can devise it's plan.

    Returns:
        An integer - Representing the floor to go to next,  this floor will
                     be 1 higher or lower than the current floor.

    Side effects:
        The input lift_data may be altered, particularly the ["lift dir"] entry as this is data
        the lift uses to remember what it was doing last.
    """
    current_floor = lift_data["lift floor"]
    last_floors = len(lift_data["floor info"])-1
    if current_floor == last_floors:
        lift_data["lift dir"] = "down"
    if current_floor == 0:
        lift_data["lift dir"] = "up"
    direction = lift_data["lift dir"]
    if direction == "up":
        return current_floor+1
    else:
        return current_floor-1

def _disembark_current_floor(lift_data):
    """Remove all people at their floor from the lift data editing original data

    Arguments:
        lift_data - Should be of the form of the BLANK_LIFT_DATA constant except
                    containing data about the current state of the lift from which
                    the people in the lift that wish to get off on the current floor
                    are to be deleted.

    Returns:
        lift_data - The updated lift data is returned to so that it can be used on the same
                    line as other functions if needed.

    Side Effects:
        The original lift_data is edited as making a copy would be a waste due to the
        function only ever being called where the original data would not be important.
    """
    current_floor = lift_data["lift floor"]
    new_lift_people = []
    #for every person in the lift check if they want to leave and remove them if they do.
    for person in lift_data["lift people"]:
        if person[0] != current_floor:
            new_lift_people.append(person)
    #update constants and return
    lift_data["lift people"] = new_lift_people
    return lift_data


def _embark_current_floor(lift_data):
    """Add as many people as will fit, on the lift's floor, to the lift editing original data

    Arguments:
        lift_data - Should be of the form of the BLANK_LIFT_DATA constant except
                    containing data about the current state of the lift from which
                    the people in the lift that wish to get on at the current floor
                    are to be moved.

    Returns:
        lift_data - The updated lift data is returned to so that it can be used on the same
                    line as other functions if needed.

    Side Effects:
        The original lift_data is edited as making a copy would be a waste due to the
        function only ever being called where the original data would not be important.
    """
    current_floor = lift_data["lift floor"]
    current_floor_info = lift_data["floor info"][current_floor]
    #While you have space and there are people to add in the floor queue
    while (len(lift_data["lift people"]) < lift_data["lift max people"] and
           len(current_floor_info) != 0):
        person = current_floor_info[0]
        current_floor_info.remove(person)
        lift_data["lift people"].append(person)
    return lift_data

def pos(num):
    """Helper function: Make negative numbers 0, positives left be."""
    if num < 0:
        return 0
    return num

def simulate(planning_function, cost_function, starting_lift_data, mode="step",
             graphical_output=None, silence=False):
    """Runs a simulation of a lift with a given set of conditions

    Arguments:
        planning_function  - The function that should be called to plan the next move for the lift,
                             it will be called via planning_function(lift_data).
        cost_function      - The function to be called the gain the cost of the last step, it will
                             be called via cost_function(lift_data).  Note this function MUST
                             return 0 cost if there are no people.
        starting_lift_data - The initial conditions of the lift - this should include
                             the initial people arrangement.
        mode               - The mode to be used must be 'step' or 'solve'
        graphical_output    - The instance of GraphicalDisplay to output to, only needed if
                             the mode 'step' is used. (Default: None)
        silence            - Whether the check-in messages for long calculations should
                             be silenced. (Default: False)

    Returns:
        An integer - representing the total cost of the given simulation.
    """
    #check arguments are consistent:
    if mode == "step" and graphical_output is None:
        raise LookupError("graphical_output must be supplied for stepping process")
    if mode == "step" and len(starting_lift_data["floor info"]) > 20:
        print("Cannot step display 21+ floors: changing mode to solve")
        mode = "solve"
    if mode not in ("step", "solve"):
        raise ValueError("Unrecognized mode: '%s'" % (mode))

    answer = -1
    total_cost = 0
    cost = "?"#only matters for initial display reasons (during step mode)
    #need deep copy to prevent side effects; as otherwise external lift data will be changed
    lift_data = deepcopy(starting_lift_data)
    if mode == "step":
        graphical_output.update_display(lift_data)
    if not silence:#if check-in messages are requested initialize the constants to do this
        start_time = ttime()
        last_print = start_time
        last_check = start_time
        check_freq = 2
        cheak_count = 0
    while answer == -1:
        planned_floor = planning_function(lift_data)#get the floor to go to
        if mode == "step":
            graphical_output.set_cost_info(total_cost, cost)
            graphical_output.block_stop()
            lift_data["lift floor"] = planned_floor
            graphical_output.update_display(lift_data)
            graphical_output.block_stop()
            _disembark_current_floor(lift_data)
            graphical_output.update_display(lift_data)
            graphical_output.block_stop()
            _embark_current_floor(lift_data)
            graphical_output.update_display(lift_data)

            if graphical_output.request_solve:
                mode = "solve"
        else:#the mode is solve
            # in solve mode the test speed is what matters most so the minimum required is called
            lift_data["lift floor"] = planned_floor
            _disembark_current_floor(lift_data)
            _embark_current_floor(lift_data)
            if not silence:#check if silenced first as this is a single operation
                cheak_count += 1
                #only check in every check_freq to ensure efficient running
                if cheak_count >= check_freq:
                    cheak_count = 0
                    ctime = ttime()
                    td = ctime-last_check

                    if td < SIMULATION_CHECKUP_FREQ*0.05:#if you have checked in too soon
                        check_freq *= 2
                    elif td > SIMULATION_CHECKUP_FREQ*0.5:#if you have checked in too late
                        check_freq /= 2
                    last_check = ctime

                    #if on this check in about the right amount of time has passed
                    if ctime-last_print > SIMULATION_CHECKUP_FREQ*0.90:
                        print("time in: %-6s | lift floor: %-5s | cost_last: %-5s | total: %s" %
                              (round(ctime-start_time, 1), lift_data["lift floor"],
                               cost, total_cost))
                        last_print = ctime

        cost = cost_function(lift_data)
        if cost == 0:
            answer = total_cost
        else:
            total_cost += cost

    return answer



def _increment_all_personal_time(lift_data):
    """Act upon original data structure, and for every person in it add 1 to there personal time.

    Arguments:
        lift_data - Should be of the form of the BLANK_LIFT_DATA constant except
                    containing data about the current state of the lift for which
                    every persons time should be incremented.

    Side Effects:
        The original data is edited as creating a copy would be a waste.
    """
    #increment the time of people in the lift
    new_lift_people = []
    for person in lift_data["lift people"]:
        new_lift_people.append((person[0], person[1]+1))
    lift_data["lift people"] = new_lift_people
    #increment the time of people on the floors
    new_floors = []
    for floor in lift_data["floor info"]:
        new_floor = []
        for person in floor:
            new_floor.append((person[0], person[1]+1))
        new_floors.append(new_floor)
    lift_data["floor info"] = new_floors

def normal_cost_function(lift_data):
    """Returns the 1 cost for every person left in play."""
    cost = len(lift_data["lift people"])#the lift people's cost
    for floor in lift_data["floor info"]:#the floor people's cost
        cost += len(floor)
    return cost

def generator_uniform(floors, number_people, max_in_lift=6):
    """generates a new lift structure with uniform distribution

    Arguments:
        floors        - The number of floors that the people should be generated over.
        number_people - The number of people to generate.
        max_in_lift   - The max number of people who can fit in a lift. (Default: 6)

    Returns:
        A valid lift_data structure - Follows the same structure as the BLANK_LIFT_DATA
                                      constant except it is now populated.
    """
    if floors < 2:
        raise ValueError("Floors must be at least 2")
    lift_struct = deepcopy(BLANK_LIFT_DATA)#deep copy as the blank case contains lists
    #initialize the floors with lists to later put people in
    floor_people = []
    for _ in range(floors):
        floor_people.append([])
    #while you have people to put on a floor do:
    people_left = number_people
    while people_left >= 1:
        person_floor = random_randint(0, floors-1)
        person_want = random_randint(0, floors-1)
        #check the person doesn't want to go to their own floor
        if person_floor == person_want:
            continue
        floor_people[person_floor].append((person_want, 0))
        people_left -= 1

    #populate remaining fields with people and returns
    lift_struct["floor info"] = floor_people
    lift_struct["lift max people"] = max_in_lift
    return lift_struct

def generator_skewed(floors, number_people, max_in_lift=6, skew_type="day-end",
                     skew_weighting=0.8):
    """Generates a new lift structure, skewed for either beginning or end of the day

    At the beginning or end of the day a much greater number of people want to either go
    from ground to their floor (beginning) or from their floor to ground (end).  This function
    acts like its uniform equivalent except some percentage of the people will want to do
    one of the things specified above.

    Arguments:
        floors         - The number of floors that the people should be generated over.
        number_people  - The number of people to generate.
        max_in_lift    - The max number of people who can fit in a lift. (Default: 6)
        skew_type      - Either 'day-end' of 'day-start', Instructs the function how to skew
                         the data. (Default: 'day-end')
        skew_weighting - The percentage chance of people following the skew.

    Returns:
        A valid lift_data structure - Follows the same structure as the BLANK_LIFT_DATA
                                      constant except it is now populated.
    """
    if floors < 2:
        raise ValueError("Floors must be at least 2")
    if skew_type not in ["day-end", "day-start"]:
        raise ValueError("skew_type must be either 'day-end' or 'day-start'")
    lift_struct = deepcopy(BLANK_LIFT_DATA)#deep copy as the black case contains lists
    #initialize the floors with lists to later put people in
    floor_people = []
    for _ in range(floors):
        floor_people.append([])
    #while you have people to put on a floor do:
    people_left = number_people
    while people_left >= 1:
        if skew_type == "day-end" and random_random() <= skew_weighting:
            person_want = 0
            person_floor = random_randint(0, floors-1)
        elif skew_type == "day-start" and random_random() <= skew_weighting:
            person_want = random_randint(0, floors-1)
            person_floor = 0
        else:
            person_want = random_randint(0, floors-1)
            person_floor = random_randint(0, floors-1)
        #check the person doesn't want to go to their own floor
        if person_floor == person_want:
            continue
        floor_people[person_floor].append((person_want, 0))
        people_left -= 1

    #populate remaining fields with people and returns
    lift_struct["floor info"] = floor_people
    lift_struct["lift max people"] = max_in_lift
    return lift_struct

def planner_advanced(lift_data):
    """Return the floor number to go to using a advanced algorithm.

    Arguments:
        lift_data - Should be of the form of the BLANK_LIFT_DATA constant except
                    containing data about the current state of the lift from which
                    the algorithm can devise it's plan.

    Returns:
        An integer - Representing the floor to go to next,  this floor will
                     be 1 higher or lower than the current floor.

    Side effects:
        The input lift_data will be altered, particularly the ["floor target"] which is used so
        the elevator can remember what is was doing.
    """
    #initialize variables for quicker reference
    current_floor = lift_data["lift floor"]
    top_floor = len(lift_data["floor info"])-1
    current_space = lift_data["lift max people"]-len(lift_data["lift people"])

    #generate base priority mapping
    floor_prio = {}
    for floor in range(top_floor+1):
        #people to get off. explanation of coming lines:
        ##get people with correct floor
        ##get the second index of the people (time spent waiting)
        ##sum it for a priority
        correct_floor = list(filter(lambda x, flr=floor: x[0] == flr, lift_data["lift people"]))
        time_correct_floor = list(map(lambda x: x[1]+1, correct_floor))
        get_off_prio = sum(time_correct_floor)

        #people to get on. explanation of coming lines:
        ##get the people on the current floor iteration
        ##sort the list by second number (time waiting):
        ##  (as people with higher time waiting are at the front of the queue)
        ##limited to the top n people in terms of time spent waiting
        ##  where n is the remaining lift space.
        ##  (as no more people than there are space for can get on)
        ##get the second index of the filtered people (time spent waiting)
        ##sum it for a priority
        people_on_floor = lift_data["floor info"][floor]
        sorted_people = sorted(people_on_floor, reverse=True, key=lambda x: x[1])
        limited_people = sorted_people[:current_space]
        time_people = list(map(lambda x: x[1]+1, limited_people))
        get_on_prio = sum(time_people)

        #multiplied by 1000000 as otherwise due to rounding all floors may have 0 priority
        floor_prio[floor] = 1000000*(GETTING_OFF_IMPORTANCE*get_off_prio + get_on_prio)

    #Apply the priority boost to the floor the lift was going to last time
    target_floor = lift_data["floor target"]
    if target_floor != current_floor:
        floor_prio[target_floor] *= TARGETING_IMPORTANCE

    #you can't go to the floor you're on
    floor_prio[current_floor] *= 0

    #divide floors by the distance and thus time to get to them
    for floor in range(top_floor+1):
        try:
            floor_prio[floor] = round((floor_prio[floor] / abs(current_floor-floor))*
                                      DISTANCE_NEGATIVE_IMPORTANCE)
        except ZeroDivisionError:
            continue#only occurs on current floor which is already 0 so no division is needed

    #select wanted floor:
    highest_prio = max(floor_prio.values())

    #If the highest priority is 0 then the algorithm has broken and routing should revert to basic
    #  Note: just a precaution this hasn't ever occurred during testing except when induced.
    if highest_prio == 0:
        print("WARNING: Priority problem - no valid option, lift reverting to basic routing!")
        return planner_basic(lift_data)

    #explanation of upcoming code:
    ##gets all floor summaries with the maximum priority (in case there is a draw)
    ##turns those floor summaries into just the floor number
    ##selects the highest of those floors as a tie breaker -
    ##  it should be rare that there is more than 1 option
    floors_with_max_prio = filter(lambda x, pro=highest_prio: x[1] == pro, floor_prio.items())
    floor_high_num = map(lambda x: x[0], floors_with_max_prio)
    selected_floor = max(floor_high_num)

    #update lift data to correctly represent the floor to go to.
    lift_data["floor target"] = selected_floor

    #finally return the floor either above or below the
    #lift in the direction of the wanted floor. As when you
    #are closer to a floor its priority increases this will
    #never loop 1 up then 1 down forever.
    if selected_floor > current_floor:
        return current_floor+1
    else:
        return current_floor-1

def batch(repeats, floor_range, people_range, algorithums, cost_function,
          gen_function, extra_gen_args=None, silence=False):
    """A function for batch/group testing algorithms

    Arguments:
        repeats        - An integer representing the number of repeats each floor person combo
                         should do to get a useful average.
        floor_range    - A tuple of the form (start,end,step) similar to the range builtin's
                         arguments.  This will express the range of data simulation's should
                         be performed for.
        people_range   - A tuple of the form (start,end,step) similar to the range builtin's
                         arguments.  This will express the range of data simulation's should
                         chose people numbers from.
        algorithums    - A list containing the algorithms to test, entering them here rather
                         than as 2 separate batches will ensure they are tested on
                         comparable people distributions.
        cost_function  - A function that the simulations should use to work out the cost of
                         the current lift data. (See: 'simulate' doc-string)
        gen_function   - A function that the simulations should use to work out a people
                         distribution to test. (See: 'simulate' doc-string)
        extra_gen_args - Any extra arguments that the generator should be passed.
        silence        - Whether the check-in messages for long calculations should
                         be silenced. (Default: False)
    Return:
        A dictionary - of the form {floor#:{people#:[list of algorithms average costs]}}
    """
    if extra_gen_args is None:
        extra_gen_args = ()
    #initialize the output associative array
    data = {}
    #if not silenced initialize the constants and variables required
    if not silence:
        start_time = ttime()
        last_print = start_time
        last_check = start_time
        check_freq = 2
        cheak_count = 0
        floor_worth = 1/((floor_range[1]-floor_range[0])//floor_range[2] + 1)
        person_worth = floor_worth/((people_range[1]-people_range[0])//people_range[2]+1)
        rep_worth = person_worth/repeats
        floor_count = 0
        person_count = 0
    for floor in range(*floor_range):
        data[floor] = {}
        for people in range(*people_range):
            data[floor][people] = []
            middle_data = []
            for _ in range(0, len(algorithums)):
                middle_data.append([])
            for rep in range(0, repeats):
                distribution = gen_function(floor, people, *extra_gen_args)
                for index in range(0, len(algorithums)):
                    solution = simulate(algorithums[index], cost_function, distribution, "solve")
                    middle_data[index].append(solution)

                if not silence:#check if silenced first as this is a single operation
                    cheak_count += 1
                    #only check in every check_freq to ensure efficient running
                    if cheak_count >= check_freq:
                        cheak_count = 0
                        ctime = ttime()
                        td = ctime-last_check
                        if td < SIMULATION_CHECKUP_FREQ*0.05:#if you have checked in too soon
                            check_freq *= 2
                        elif td > SIMULATION_CHECKUP_FREQ*0.5:#if you have checked in too late
                            check_freq /= 2
                        last_check = ctime
                        #if on this check in about the right amount of time has passed:
                        if ctime-last_print > SIMULATION_CHECKUP_FREQ*0.90:
                            percent = 100 * ((floor_count*floor_worth)+
                                             (person_count*person_worth)+(rep_worth*rep))
                            print(("time in: %-6s | floor: %-4s | people: %-4s | repeat: %-4s |" +
                                   " percent: %-5.5s%%") % (round(ctime-start_time, 1),
                                                            floor, people, rep, percent))
                            last_print = ctime
                #end check-in message code
            for index in range(0, len(algorithums)):
                algorithum_average = round(sum(middle_data[index])/repeats)
                data[floor][people].append(algorithum_average)
            #check-in internal percentage code:
            if not silence:
                person_count += 1
        #check-in internal percentage code:
        if not silence:
            floor_count += 1
            person_count = 0

    return data

def tuple_search(tuple_list, values_to_find=(0, 0)):
    """Search a list of tuples for a tuple with the first n elements matching values_to_find

    Example:
        For the tuple list [(1,1,3),(1,0,6),(0,1,9),(0,0,12)] and the values_to_find of (0,1):
        It would look for the tuples with a 0 first >>> [(0,1,9),(0,0,12)]
        Then look for the tuple with a 1 second >>> [(0,1,9)]
        Then return it.
        If none are left it would raise an error.

    Arguments:
        tuple_list     - the list of tuples to be checked
        values_to_find - the tuple expressing the elements to search for

    Returns:
        The found tuple from the tuple list.

    Exceptions:
        ValueError: Will raise a ValueError if the values_to_find is not in the tuple_list
    """
    search_len = len(values_to_find)
    for tuple_ in tuple_list:
        for index in range(0, search_len):
            #if you find an incorrect value at index then break
            if tuple_[index] != values_to_find[index]:
                break
        else:#if you never break, then tuple_ matches and is returned
            return tuple_
    #if the loop finishes then no loop returned a tuple and thus it isn't in the list
    raise ValueError("Value not in tuple-list")

def out_bat_to_3d_coord(data):
    """Takes the data output by the batch function and turns it into plot-able 3d coords

    Arguments:
        data - The output of the batch function. (Which is of the form;)
               {floor#:{people#:[list of algorithms average costs]}}

    Return:
        A list of tuples - containing the same data as entered at the start but now as 3d coords.
    """
    al_coord = []
    #extract number of algorithms
    temp_small = data[list(data.keys())[0]]#removes floors
    temp_smaller = temp_small[list(temp_small.keys())[0]]#removes people
    num_algo = len(temp_smaller)#counts entry's (should be 1 per algorithm)

    for index in range(0, num_algo):
        coords = []
        for floor in list(data.keys())[:]:
            for people in list(data[floor].keys())[:]:
                coords.append((floor, people, data[floor][people][index]))
        al_coord.append(coords)
    return al_coord

def con_plot_3d_coord(coords):
    """Take a list of 3d coords and turn it into something matplotlib can plot

    Arguments:
        coords - The 3d coords to be used.
                 Note: every xy value in range of the axis must have an associated z

    Returns:
        A tuple containing the x,y,z elements required for matplotlib's contour plot to work.

    Exceptions:
        ValueError: Will raise a value error if the input coords do not have
                    a z-value for every coord spot to be plotted.
    """
    #get data bounds (for displaying)
    min_x = min(coords, key=lambda x: x[0])[0]
    max_x = max(coords, key=lambda x: x[0])[0]
    min_y = min(coords, key=lambda x: x[1])[1]
    max_y = max(coords, key=lambda x: x[1])[1]

    #extract x-y data, set is used to remove duplicates
    sorted_xs = sorted(set(list(zip(*coords))[0]))
    sorted_ys = sorted(set(list(zip(*coords))[1]))
    sorted_zs = []
    #extract z data
    for xv in sorted_xs:
        for yv in sorted_ys:
            sorted_zs.append(tuple_search(coords, [xv, yv])[2])

    #create an interpolation function
    funct_inter = sp.interp2d(sorted_xs, sorted_ys, sorted_zs)

    #generate a new list of input x-y coords with 200 x values and 200 y values
    newx = np.arange(min_x, max_x, (max_x-min_x)/200)
    newy = np.arange(min_y, max_y, (max_y-min_y)/200)
    #for those new values using the interpolation function we made earlier find the z values
    newz = funct_inter(newx, newy)

    #return the coordinates as 3 lists with the index corresponding
    return newx, newy, newz

def show_al_comp(xyz_basic, xyz_adv):
    """Plot the given xyz values for the basic and advanced algorithm

    Arguments;
        xyz_basic - The xyz values for direct plotting (normally from con_plot_3d_coord)
                    these should be from the batch testing of the basic planner.
        xyz_adv   - The xyz values for direct plotting (normally from con_plot_3d_coord)
                    these should be from the batch testing of the advanced planner.

    Side Effects:
        Will stop execution until the plot is closed or CTRL-C (keyboard-interrupt) is enacted.
    """
    #create plot
    fig, (ax1, ax2) = plt.subplots(1, 2)

    #generate the data required to produce the scale bar
    largest_z = round(float(max(xyz_basic[2].max(), xyz_adv[2].max()))*1.15)
    tick_size = best_tick(largest_z, 15)
    ticks = np.array(list(range(0, largest_z+1, tick_size)))

    #Create a contour plot of the data
    cp = ax1.contourf(*xyz_basic, levels=ticks)
    cp2 = ax2.contourf(*xyz_adv, levels=ticks)

    #Add the color-bar scale to a plot
    fig.colorbar(cp, ax=[ax1, ax2])

    #Set flair data
    ax1.set_title('Basic algorithm')
    ax2.set_title('Improved algorithm')
    ax1.set_xlabel('# of people')
    ax1.set_ylabel('# of floors')

    #Show the constructed plot.  NOTE: Blocking
    plt.show()

def al_coord_shown(al_coords):
    """Helper function: A function to allow easy calling of show_al_comp from the cmd line"""
    #extract the coordinates structured by algorithm and convert them to 3d
    #coordinates sorted by algorithm in a list
    ncoords = []
    for al in range(len(al_coords)):
        ncoords.append(con_plot_3d_coord(al_coords[al]))
    show_al_comp(*ncoords)

#reference: https://stackoverflow.com/questions/361681/
def best_tick(largest, most_ticks):
    """Generate a 'nice' interval for graphs given a max value and most number of intervals

    Arguments:
        largest:    - A number which represents the greatest amount that needs to be displayed.
        most_ticks: - A integer which represents the most number of intervals that
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


#Examples

#example 1
example_lift_data = generator_uniform(19, 35)
GRAFIX = GraphicalDisplay(example_lift_data)
simulate(planner_advanced, normal_cost_function, example_lift_data, "step", GRAFIX)

#example 2
q = batch(10, [5, 26, 5], [10, 51, 10], [planner_basic, planner_advanced], normal_cost_function, generator_uniform, [6])
q2 = batch(10, [5, 26, 5], [10, 51, 10], [planner_basic, planner_advanced], normal_cost_function, generator_skewed, [6, "day-end", 0.8])

#show example 2b
al_coord_shown(out_bat_to_3d_coord(q2))
