'''
school-notes-maker-json.py
Hussein Esmail
Created: 2021 12 11
Description: This program generates a LaTeX template for School course notes
    based on a given file from
    https://github.com/hussein-esmail7/yorku-class-scraper
    The idea is to have the user input as little as possible.
'''

# Test Command:
# python3 lecture_notes_latex_generator.py -a "Hussein Esmail" -c "EECS 3311" -w "MWF" -l "VC 105" -s "A" -p "Andrew Skelton" -y "2022W" -n "3" -t "Software Design" -f "EECS3311.tex"

# TODO: Account for skipping reading week

from datetime import datetime as date
import configparser     # Used to get configuration file contents
import datetime
import getopt           # Used to get argument information
import json             # Used to parse JSON file to program
import os
import re               # Used to match regex patterns
import sys

# TODO: config-ify this program and move to its own git repo
# TODO: Account for if there are multiple locations for lectures on
#       different days

# ========= VARIABLES ===========
DATA_JSON           = [] # JSON data will go here
PATH_POST_SCRIPT    = "" # Optional script to run afterwards, passes tex file
PATH_CONFIG         = "~/.config/school-notes-maker/config"
PATH_TEMPLATE_FILE  = "~/git/templates/lecture-template.tex"
PATH_JSON           = "" # Location of the JSON file
PROGRAM_NAME        = "school-notes-maker-json" # Used in help message
PROGRAM_HELP_SITE   = "https://github.com/hussein-esmail7/template-maker/"

# ========= COLOR CODES =========
color_end               = '\033[0m'     # Resets color
color_darkgrey          = '\033[90m'
color_red               = '\033[91m'
color_green             = '\033[92m'
color_yellow            = '\033[93m'
color_blue              = '\033[94m'
color_pink              = '\033[95m'
color_cyan              = '\033[96m'
color_white             = '\033[97m'
color_grey              = '\033[98m'

# ========= COLORED STRINGS =========
prefix_q            = f"[{color_pink}Q{color_end}]"         # "[Q]"
prefix_y_n          = f"[{color_pink}y/n{color_end}]"       # "[y/n]"
prefix_ques         = f"{prefix_q}\t "                      # "[Q]  "
prefix_err          = f"[{color_red}ERROR{color_end}]\t "   # "[ERROR]"
prefix_done         = f"[{color_green}DONE{color_end}]\t "  # "[DONE]"
prefix_info         = f"[{color_cyan}INFO{color_end}]\t "   # "[INFO]"
prefix_warn         = f"[{color_yellow}WARN{color_end}]\t " # "[WARN]"


def merge_weekdays(wkdays):
    to_return = ""
    weekday_order = ["M", "T", "W", "R", "F"]
    for i in weekday_order:
        for weekday_type in wkdays:
            if i in weekday_type and i not in to_return:
                to_return = to_return + i
    return to_return


def yes_or_no(str_ask):
    while True:
        y_n = input(f"{prefix_q} {prefix_y_n} {str_ask}").lower()
        if len(y_n) == 0:
            return True
        elif y_n[0] == "y":
            return True
        elif y_n[0] == "n":
            return False
        if y_n[0] == "q":
            sys.exit()
        else:
            print(f"{prefix_err} Your response is neither 'y' or 'n'!")

def require_answer(q1):
    # Keeps asking question until user confirms their response is true
    q1ans = ""
    while True:
        q1ans = input(prefix_ques + " " + q1).strip()
        if len(q1ans) == 0:
            print(prefix_err + " You cannot provide a blank response!")
        elif yes_or_no(f"Is this correct - '{q1ans}'? "):
            break
    return q1ans

def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)

def index_str(list, search_str):
    # Returns first index that contains string
    for num, item in enumerate(list):
        if search_str in item:
            return num
    return -1

def rep_arr_val(list, search_str, str):
    # Replaces all values of a string with a new one within an array
    # list: array to search
    # search_str: String to replace
    # str: New string
    for num, item in enumerate(list): # for every index in the array
        if search_str in item: # If the index contains the string to replace
            # print(f"Replaced: \n\t{item}", end="")
            list[num] = item.replace(search_str, str) # Replace the string
            # print(f"\t{list[num]}")
    return list # Return the new list with changed values

def eu(path):
    # Just a shorter name for expanding home directory path
    return os.path.expanduser(path)

def get_config(PATH_CONFIG):
    PATH_CONFIG = eu(PATH_CONFIG)
    c = configparser.ConfigParser()
    if not os.path.exists(PATH_CONFIG):
        # If the config file does not exist, generate a new ConfigParser object
        FOLDER_CONFIG = "/".join(PATH_CONFIG.split("/")[:-1])
        if not os.path.exists(FOLDER_CONFIG):
            # Make the config folder if it doesn't exist
            os.makedirs(FOLDER_CONFIG)
        open(PATH_CONFIG, 'w').write(c)
        print(f"{strPrefix_info} Your config file does not exist! Wrote to {PATH_CONFIG}")
    c.read(PATH_CONFIG)
    config1 = {
            "author": c.get("Default", "author", fallback="Hussein Esmail"),
            "format_output": c.get("Default", "format_output", fallback="{c}{n}.tex"),
            "insert": c.get("Default", "insert", fallback="\\begin{itemize*}\n\t\\item\n\\end{itemize*}"),
            "json": c.get("Default", "json", fallback=""),
            "post": eu(c.get("Default", "post", fallback="")),
            "quiet": c.get("Default", "quiet", fallback="False"),
            "university": c.get("Default", "university", fallback="York University")
            }
    return config1

def main(argv):
    # Main function
    DATA_CONFIG         = get_config(PATH_CONFIG) # Config info
    PATH_POST_SCRIPT    = eu(DATA_CONFIG["post"])
    PATH_JSON           = eu(DATA_CONFIG["json"])
    BOOL_PRINTS         = not bool(DATA_CONFIG["quiet"]) # Config parameter
    TEXT_INSERT         = DATA_CONFIG["insert"] # Config parameter
    university          = DATA_CONFIG["university"] # Config parameter
    author              = "Hussein Esmail" # Default author of the notes file
    currentDate         = date.now().strftime("%Y %m %d")
    lines_append        = [] # Lines to insert into the template
    types_order         = ["Lecture", "Tutorial", "Lab"]
    types_count         = [0, 0, 0] # Keeps same order as `types_order`
    types_days          = ["", "", ""] # See `types_order` for each meaning
    filename            = "" # File name of the output file
    courseCode          = "" # Course code of the new file
    courseLocation      = "" # Course location of the new file
    courseTitle         = "" # Course title of the new file
    course_section      = "" # Course section of the new file (A, B, Z, etc.)
    prof                = "" # Course prof of the new file
    semester            = "" # Course semester of the new file (ex. 2020F)
    courseCredits       = "" # How many credits the course is worth
    r_cc                = "([A-Za-z]{2,4}) (\d{4}) ([A-Za-z]{1})" # CC Regex
    r_cat               = "(\w{6})$" # Regex for CAT code
    json_query          = ""
    # "JSON Query": What the user will input to find in the
    # JSON file. Possible inputs:
    #   1. XXXX XXXX X (Course code, section)
    #   2. XXXXXX (CAT Code)
    query_meets         = [] # The course meetings that qualify will go here
    # Only the parts that qualify. Ex. Not Lab 3 if you are in Lab 5
    # NOTE: If there is conflicting data between JSON and what the user also
    #       gave, prefer what the user gave

    # Process user arguments
    # https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    try:
        opts, args = getopt.getopt(
                argv,
                "ha:f:c:w:l:s:p:y:n:t:j:qi:",
                [   "author=",
                    "filename=",
                    "course-code=",
                    "weekday=",
                    "location=",
                    "section=",
                    "prof=",
                    "semester=",
                    "title=",
                    "json=",
                    "input="
                ]
            )
    except getopt.GetoptError as e:
        print(f'{PROGRAM_NAME}.py -h')
        print(f"{prefix_err} {e}")
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h': # Help message
            print(f"--- {PROGRAM_NAME} ---\n")
            print(f"For more info, go to {PROGRAM_HELP_SITE}\n")
            print("Arguments:")
            print("\t -a, --author:\t\t Author of the notes file (you)\n\t\tExample:\t -a \"Hussein Esmail\"\n")
            print("\t -c, --course-code:\t Course code\n\t\tExample:\t -c \"EECS 1001\"\n")
            print("\t -f, --filename:\t Output file name\n\t\tExample:\t -f \"EECS1001Notes.tex\"\n")
            print("\t -i, --input:\t Course query\n\t\tExample:\t -i \"EECS 1011 Z\"\n")
            print("\t -j, --json:\t\t JSON file path created by yorku-class-scraper\n\t\tExample:\t -j \"../yorku-class-scraper/json/2022_fw.json\"\n")
            print("\t -l, --location:\t Location of the course\n\t\tExample:\t -l \"CLH I\"\n")
            print("\t -n, --credits:\t\t Number of credits this course has\n\t\tExample:\t -n \"3\"\n")
            print("\t -p, --prof:\t\t Course professor/lecturer\n\t\tExample:\t -p \"Andrew Skelton\"\n")
            print("\t -q, --quiet:\t\t Quiet mode\n\t\tExample:\t -q\n")
            print("\t -s, --section:\t\t Course section\n\t\tExample:\t -s \"A\" for Section A\n")
            print("\t -t, --title:\t\t Course title. \n\t\tExample:\t -t \"Introduction to Computer Science\"\n")
            print("\t -y, --semester:\t Course semester.\n\t\tExample:\t -y \"2020F\" (for Fall 2020)\n")
            sys.exit()
        elif opt in ("-a", "--author"):
            author = arg
        elif opt in ("-f", "--filename"):
            filename = arg
        elif opt in ("-c", "--course-code"):
            courseCode = arg
        elif opt in ("-l", "--location"):
            courseLocation = arg
        elif opt in ("-s", "--section"):
            course_section = arg
        elif opt in ("-p", "--prof"):
            prof = arg
        elif opt in ("-y", "--semester"): # y for year as well
            semester = arg
        elif opt in ("-n", "--credits"): # n for number
            courseCredits = int(arg)
        elif opt in ("-t", "--title"): # Course title
            courseTitle = arg
        elif opt in ("-j", "--json"): # Import JSON file
            PATH_JSON = arg
        elif opt in ("-q", "--quiet"): # Quiet mode
            BOOL_PRINTS = False
        elif opt in ("-i", "--input"): # Query input
            json_query = arg

    # Get JSON data if a file was given
    # See https://github.com/hussein-esmail7/yorku-class-scraper/
    #   -> dict_format.pdf for how the JSON file is formatted
    if os.path.exists(eu(PATH_JSON)):
        # If the JSON file exists
        f = open(PATH_JSON)
        DATA_JSON = json.load(f)
        f.close()
        if BOOL_PRINTS:
            print(f"{prefix_info} Loaded JSON file")
        bool_json_query_valid_input = False
        while not bool_json_query_valid_input:
            json_query = input(f"{prefix_q}\t  Input CAT/Course code and section: ")
            json_query = json_query.strip().upper()
            rm_cc = re.match(r_cc, json_query)
            rm_cat = re.match(r_cat, json_query)
            if json_query == "EXIT":
                sys.exit()
            elif len(json_query) == 0:
                print(f"{prefix_err} You must input a query!")
            elif not rm_cc and not rm_cat:
                print(f"{prefix_err} Your query must match a valid input!")
                print(f"\t  CODE: XXXX #### X")
                print(f"\t  CAT:  XXXXXX")
            else:
                bool_json_query_valid_input = True

        rm_cc = re.match("([A-Za-z]{2,4}) (\d{4}) ([A-Za-z]{1})", json_query)
        # rm_cc: "Regex Match, course code version"
        rm_cat = re.match("(\w{6}$)", json_query)
        # rm_cc: "Regex Match, CAT code version"
        if rm_cc:
            if BOOL_PRINTS:
                print(f"{prefix_info} Course code regex match")
            # query based off of course code and section
            cc_start = rm_cc.group(1)
            cc_end = rm_cc.group(2)
            courseCode = f"{cc_start} {cc_end}"
            course_section = rm_cc.group(3)
            for course in DATA_JSON:
                if course["Code"] == cc_start and course["Num"] == cc_end:
                    courseTitle = course["Title"]
                    for meeting in course["Meetings"]:
                        if meeting["Section"] == course_section:
                            query_meets.append(dict(meeting))
            courseCredits = course["Credits"]
            semester = course["Term"]
            for meeting in query_meets:
                if meeting["Type"] == "LECT":
                    courseLocation = meeting["Location"]
                    prof = meeting["Instructor"]
                    for letter in meeting["Day"]:
                        if letter not in types_days[0]:
                            types_days[0] = types_days[0] + letter
                elif meeting["Type"] == "TUTR":
                    for letter in meeting["Day"]:
                        if letter not in types_days[1]:
                            types_days[1] = types_days[1] + letter
                elif meeting["Type"] == "LAB":
                    for letter in meeting["Day"]:
                        if letter not in types_days[2]:
                            types_days[2] = types_days[2] + letter
        elif rm_cat:
            if BOOL_PRINTS:
                print(f"{prefix_info} CAT code regex match")
            for course in DATA_JSON:
                use_this_course = False
                for meeting in course["Meetings"]:
                    # This loop only finds the course that the CAT belongs to
                    if meeting["CAT"] == rm_cat.group(1):
                        use_this_course = dict(course)
                        course_section = meeting["Section"]
                if use_this_course != False:
                    courseCode = use_this_course["Code"] + " " + use_this_course["Num"]
                    courseTitle = use_this_course["Title"]
                    semester = use_this_course["Term"]
                    courseCredits = use_this_course["Credits"]
                    for meeting2 in use_this_course["Meetings"]:
                        # For the meetings in the course it knows to use
                        if meeting2["CAT"] == json_query or len(meeting2["CAT"]) == 0:
                            if meeting2["Type"] == "LECT":
                                courseLocation = meeting2["Location"]
                                prof = meeting2["Instructor"]
                                for letter in meeting2["Day"]:
                                    if letter not in types_days[0]:
                                        types_days[0] = types_days[0] + letter
                            elif meeting2["Type"] == "TUTR":
                                for letter in meeting2["Day"]:
                                    if letter not in types_days[1]:
                                        types_days[1] = types_days[1] + letter
                            elif meeting2["Type"] == "LAB":
                                for letter in meeting2["Day"]:
                                    if letter not in types_days[2]:
                                        types_days[2] = types_days[2] + letter

    else:
        # If the JSON file does not exist
        print(f"{prefix_err} `{PATH_JSON}` is not a valid JSON path!")

    # Ask user anything that is unanswered and required

    if courseCode == "": # If course code was not given in initial run line
        courseCode = require_answer("Course code (with spaces): ")

    # Asking if this course has Lectures, Tutorials, Labs
    # print(f"{prefix_info} About to ask which weekdays for Lectures, Tutorials, Labs" )

    for weekday_type_num, weekday_type in enumerate(types_days): # Weekday values, all initially ""

        weekday_type_str = types_order[weekday_type_num] # "Lecture", "Tutorials", or "Labs". Used for asking the user to input each type
        if weekday_type == "" and not os.path.exists(eu(PATH_JSON)):
            # If weekdays the course occurs not given and has not used a JSON
            # file. This is because if the JSON file was used, that means that
            # there are no tutorials in that type.
            # Do not use require_answer() because it has to check weekday regex
            while True:
                types_days[weekday_type_num] = input(prefix_ques + " Input weekdays this course happens (MTWRF): ").strip().replace(" ", "")
                if bool(re.match("^[MTWRFmtwrf]+$", types_days)): # Weekday regex
                    break
                else:
                    print(f"{prefix_err} Please only enter only MTWRF characters!")

    if courseLocation == "": # Ask course location if not given before
        courseLocation = require_answer("Location of this course: ")

    if courseTitle == "": # Ask for course title if not given before
        courseTitle = require_answer("Course title: ")

    if course_section == "": # Ask for course section if not given before
        # Does not use require_answer() because it has to check it's 1 char
        while True:
            course_section = input(prefix_ques + " Course Section (1 char): ").strip()
            if len(course_section) != 1:
                print(prefix_err + " The course code has to be 1 character only!")
            elif yes_or_no("Is this correct - Section " + course_section + "? "):
                break

    if prof == "": # Ask for professor if not given before
        prof = require_answer("Professor teaching this section: ")

    if semester == "": # Ask for which semester it takes place in if not given
        # Does not use require_answer() because it has to ckeck regex
        while True:
            semester = input(prefix_ques + " Year and Semester (Ex: 2021F): ")
            if bool(re.match("^[0-9]{4}(W|F|SU|S1|S2)$", semester)):
                # Regex: First 4 chars is year, after is term
                break
            else:
                print("Please only enter in the correct format.")

    if courseCredits == "": # Ask for number of credits if not given
        # Does not use require_answer() because it has to be a number
        while True:
            courseCredits = input(f"{prefix_ques} Course credit amount: ")
            try:
                courseCredits = int(courseCredits.strip())
                if yes_or_no(f"Is this correct - {courseCredits} credits? "):
                    break
            except ValueError:
                print(f"{prefix_err} Your response must be a number!")

    # Determine output file name
    if DATA_CONFIG["format_output"].strip() != "":
        # If the user inputted some sort of filename output
        ret = DATA_CONFIG["format_output"]
        ret = ret.replace("{c}", courseCode.split(" ")[0])
        ret = ret.replace("{n}", courseCode.split(" ")[1]) # "1001" in "EN 1001"
        ret = ret.replace("{a}", course_section) # Section
        ret = ret.replace("{s}", semester) # Semester ("W", "F", etc.)
        # ret = ret.replace("{y}", ) # TODO: Year only
        ret = ret.replace("{p}", prof) # Prof full name
        ret = ret.replace("{f}", prof.split()[0]) # Prof first name
        ret = ret.replace("{l}", prof.split()[-1]) # Prof last name
        if not ret.endswith(".tex"):
            ret += ".tex"
        ret = filename
    else: # Ask for file name if the user didn't give an output format before
        # Don't use require_answer() because it has to check for file ext.
        while True:
            filename = input(prefix_ques + " File name (tex): ").strip()
            if len(filename) > 0:
                if not filename.endswith(".tex"):
                    filename += ".tex"
                if yes_or_no("Is this correct - '" + filename + "'? "):
                    break
            else:
                print(f"{prefix_err} You must provide a file name!")

    # Confirming Week 1's start date
    week1monday = ""
    year_temp = re.findall(r'\d+', semester) # Get all numbers in string as arr
    if len(year_temp) > 0: # If there are numbers in the given string
        year = year_temp[0] # Get the first number
    else:
        year = date.today().year
    partOfYear = re.sub(r'[^a-zA-Z]', '', semester)
    # partOfYear = semester[4:] # W or F of SU (rest of string after 4 characters)
    if partOfYear == "W":
        month = 1 # January
    elif partOfYear == "F":
        month = 9 # September
    elif partOfYear == "SU":
        month = 5 # Summer semester starts in May (2022: May 9)
        # Reading week in 2022: June 21-24
    elif partOfYear == "S1":
        month = 5 # S1 semester starts in May (2022: May 9)
        # Exams week in 2022: June 21-24
    elif partOfYear == "S2":
        month = 6 # S2 semester starts in June (2022: June 27)
    else:
        month = 1
        print(f"{prefix_err} Semester is invalid! ({partOfYear})")

    d = datetime.date(year, month, 1)
    next_monday = next_weekday(d, 0)
    continue_loop = True
    while continue_loop:
        confirm_weekday = yes_or_no(f"Is the start of {semester} {next_monday.strftime('%Y %m %d')} [y/n]? ")
        if confirm_weekday:
            continue_loop = False
        else: # If start date is not correct
            date_correct_input = ""
            date_correct = d
            while True:
                date_correct_input = input(prefix_ques + " Input the date in the form of YYYY MM DD: ")
                date_correct = date.strptime(date_correct_input, "%Y %m %d")
                if yes_or_no("Is this correct: " + date_correct.strftime('%a %b %d, %Y') + "? "):
                    continue_loop = False
                    break
            d = date_correct

    # Ask the user when reading week is
    # TODO
    r_week_start = None
    r_week_end   = None
    # Generate the list of possible options:
    mondays = [next_monday.strftime("%Y %m %d")]
    for week in range(0, 11):
        # 11: The number of weeks (12) minus 1 (11) because `mondays` already
        #       has the first entry before the loop starts
        mondays.append(next_weekday(mondays[-1], 0).strftime("%Y %m %d"))
    while r_week_start == None:
        # Continue until it gets a valid answer
        print("Which week does")




    # Warn user if they have multiple types of something, and ask to choose
    for num, meeting_type in enumerate(types_days[1:]):
        meeting_name = types_order[num+1]
        # All types except for index 0 (lectures)
        # Intended for things a student should only have 1 of: TUTR, LAB, etc.
        if len(meeting_type) > 1:
            # If the user has multiple days of this type
            print(f"{prefix_warn} You have multiple {meeting_name} days selected!")
            weekday_use = input(f"\t  Input the weekday you want to use ('0' for all) -> {meeting_type}: ").strip().upper()
            while len(weekday_use) != 1 and (weekday_use != "0" or weekday_use not in meeting_type):
                weekday_list_str = "\', \'".join(meeting_type)
                print(f"{prefix_err} You must input '{weekday_list_str}', or '0'!")
                weekday_use = input(f"\t  Input the weekday you want to use ('0' for all) -> {meeting_type}: ").strip()
            if weekday_use in meeting_type:
                types_days[num+1] = weekday_use # +1 because we offset in
                # the loop declaration (starting at value 1 of weekdays, not 0)

    # Read template file contents
    lines = open(eu(PATH_TEMPLATE_FILE), "r").readlines()

    # Change values in LaTeX template preamble
    ncmd = "\\def\\" # ncmd = "New Command" prefix string
    lines = rep_arr_val(lines, "[FILENAME]", filename) # File name
    lines = rep_arr_val(lines, "[AUTHOR]", author) # Author of these notes (you)
    lines = rep_arr_val(lines, "[DATE]", currentDate) # Today
    lines = rep_arr_val(lines, "[DESC]", f"Course notes for {courseCode}") # File description (as a comment, mainly)
    lines = rep_arr_val(lines, "[SUBJ]", f"Lecture notes for {courseCode} in {semester}") # Subject
    lines = rep_arr_val(lines, "[KEYWORDS]", f"{courseCode}, {university}")
    lines = rep_arr_val(lines, "[COURSE-CREATED-DATE]", currentDate)
    lines = rep_arr_val(lines, "[COURSE-CREDITS]", str(courseCredits))
    lines = rep_arr_val(lines, "[COURSE-CODE]", courseCode)
    lines = rep_arr_val(lines, "[COURSE-TITLE]", courseTitle)
    lines = rep_arr_val(lines, "[COURSE-PROF]", prof) # Prof's full name
    lines = rep_arr_val(lines, "[COURSE-SEMESTER]", semester) # Prof's full name
    lines = rep_arr_val(lines, "[COURSE-SCHEDULE]", merge_weekdays(types_days))
    lines = rep_arr_val(lines, "[COURSE-SECTION]", course_section)
    lines = rep_arr_val(lines, "[COURSE-LOCATION]", courseLocation)
    lines = rep_arr_val(lines, "[PROF]", prof.split()[0]) # Prof by informal name within notes


    # Print sections by week here
    for weekNum in range(1, 12):
        # For the number of weeks in a semester
        lines_append.append("\n\\section{Week " + str(weekNum) + "}") # Each week section line
        for day in range(0, 5):
            # For every day in the week (Monday to Friday)
            d = next_weekday(d, day) # Update the weekday
            # TODO: while day is not in reading week block
            weekday_short = d.strftime('%A')[0:3] # First 3 letters of weekday
            weekday_let = weekday_short[0]
            if day == 3: # 3 = Thursday = R, not T
                weekday_let = "R"
            for num, meeting_type in enumerate(types_days):
                # Check each meeting type if it happens on that day
                if weekday_let in meeting_type:
                    types_count[num] += 1 # Increase the counter
                    tDateFormatted = d.strftime("%Y %m %d")
                    lines_append.append("\\subsection{" + types_order[num] + " " + str(types_count[num]) + ": " + tDateFormatted + " (" + weekday_short + ")}")
                    lines_append.append(TEXT_INSERT + "\n")

    # Merge arrays + write to file
    line_insert = index_str(lines, "% TODO: Lecture notes here")
    lines[line_insert:line_insert] = [line + "\n" for line in lines_append]
    open(filename, "w").writelines(lines)

    # Run post-script
    if len(PATH_POST_SCRIPT) > 0:
        if BOOL_PRINTS:
            print(f"{prefix_info} Detected post-script. Running...")
        os.system(f"{PATH_POST_SCRIPT} \"{FILENAME_OUTPUT}\"")
    sys.exit() # Exit program with no errors

if __name__ == "__main__":
    if len(sys.argv) > 0:
        main(sys.argv[1:])
    else:
        main()
