INTRODUCTION:
    This module implements process and inventory management, future demand and
    product stock predictions as well as a method to suggest what actions need to
    be performed soon. Suggested actions include adding new beers to be brewed and
    performing upkeep on existing brews.
    
PREREQUISITES:
    It will be assumed that python is installed and that it's version is compatible
    with the development version (3.7.4).  
    Python can be downloaded here: https://www.python.org/downloads/


INSTALLATION:
    The package will be distributed as a zip file containing all non-python file
    structures already in place however users will need to install some third
    party modules in order for the code to become operational.

    Following is a list consisting of the name of third party modules and a link 
    to the pip page for them along with the pip install command.  This command will
    need to be run via command prompt:
        flask - https://pypi.org/project/Flask/ - pip install Flask
        logging - https://pypi.org/project/logging/ - pip install logging
    Once those are installed you are ready to go!


GETTING STARTED:
  1)
    In order to get the code up and running, enter command prompt and navigate to 
    the file with the brewing.py in via the command 'cd path_to_file'. 
    (or in windows you can hold Ctrl-Shift right click and select Open 'PowerShell
    window here' in the file explorer inside the directory containing brewing.py). 
    Once there, type: 'python brewing.py'
    The following text (or similar) should appear:

     * Serving Flask app "brewing" (lazy loading)
     * Environment: production
       WARNING: This is a development server. Do not use it in a production deployment.
       Use a production WSGI server instead.
     * Debug mode: off
    Expected Localhost Connection: 127.0.0.1:5001
    Expected LAN Connection: 

    Once this has appeared, the server is up and running and you can move on to number 2.
    
  2)
    Next open a browser to view and use the interface. Any should do however it has only been
    Tested on (Chrome Version 78.0.3904.108 https://www.google.co.uk/chrome )
    Once in a browser go to the address bar type:
      If you are on the computer the code is running on:
        127.0.0.1:5001
      If you are on a computer connected to the same LAN router (same Internet connection):
        Whatever came after the : in 'Expected LAN Connection:' on the command prompt
        (Likely 192.168.number.number:5001)
    After you have typed the above address press enter and you should be greeted by a page
    saying (in bold):
      Please click on the above buttons to navigate between pages.
    If you see that, then this stage has worked and you can move on to stage 3
  
  3)
    Now you are on the interface proper.  Please see the relevant section for each page:
    Contents:
        4 - A general overview
        5 - The processing page
        6 - The Prediction and Stocks page
        7 - The why pages
    
    Please note: When the instructions refer to left or right your browser may move 
      items so they are below or above instead - this can be helped by keeping the interface 
      window as big as you can, ideally maximized.
  4)
    A General Overview:
    Use the buttons on the top bar of the page to navigate to each of the tabs.
      * The processing tab contains lots of useful information about what the tanks
        are currently doing as well as a table suggesting what to do next and more specific
        information for the tank currently clicked on.
      * The prediction and stocks tab has 2 graphs showing the change in stocks over time
        and the demand over time.  It also allows you to directly change the stock of
        given beers.
  5)
    The Processing Page:
    The processing page is split into 3 major parts:
      * First, on the left, is a set of images of circles and triangles.  Each image refers 
        to a tank whose name can be seen at the top of the image.  The contents of the tank
        can be seen at the bottom (some of the names may have been shortened to fit in the box)
        The tanks can be clicked on to show the 3rd major element in this list.
      * The second major element is in the table in the top right.  This table shows actions
        that need to be performed soon.  Actions will have a priority ranging from 'Priority'
        to 'Surplus' with 'Priority' being the highest, then 'Important', then 'Upkeep' and
        finally 'Surplus' is the least important.
        If you wish to understand why a given suggestion exists in that list, click on the
        tank it talks about and then the 'Why?' button that shows up (detailed in the next 
        bullet point).
      * Finally when you click a tank a summary section appears on the lower right.  This
        section contains lots of information such as the volume of the tank, the gyle number
        and when the tank will be done.  It also has a line that any relevant suggested tasks
        from the table are written in.  If a task is suggested, a 'Why?' button will show up.
        When clicked this will give a much more detailed explanation of the reasoning behind 
        any decision.  At the bottom there will also appear any relevant button to the current 
        state of the tank.  Filling in the fields as required and clicking the button will do
        the task on the button.  If a task on a button is suggested it will be highlighted in 
        blue to make it easier to spot (as will suggested options on drop downs).  After a button
        is pushed a message will appear in place of the tank summary informing you of its success 
        or reporting an error (such as trying to fill a tank higher than its max) errors will 
        show in red.
  6)
    The Prediction Page:
    The prediction page is in 2 major parts:
      * First on the left are the graphs.  The top graph shows the predicted stocks over
        time and the bottom one shows the predicted demand over time.  If you would like a
        greater explanation of either of the graphs click the 'Why?' button by their title.
      * Second, the Stock readouts and adjustment area is on the right.  Here the current stocks
        of each beer are visible and a form exists below to change the values.  If a beer is
        sold and the stock decreases one need only select from the drop down the beer in
        question and then type the number of liters of beer that have been sold as a negative
        into the volume field.  Pushing the 'Change stocks' button will apply the change and
        give you a message below the form. If anything should go wrong, an error message will be
        displayed informing you.
  7)
    The Why? Page
    If you find yourself questioning a decision the computer seems to have pulled from
    nowhere click on the relevant 'Why?' button to be taken to a specific page for it.  
    These why pages will explain the process the computer went through to return the answer it did.


DEVELOPER DOC:
    Please read the doc-strings and comments in the source code for developer information.


DETAILS:
Author: Jacob Box