'''
lecture_notes_latex_generator.py
Hussein Esmail
Created: 2021 12 11
Updated: 2022 05 14
Description: This program generates a LaTeX template for School course notes
'''

# Test Command:
# python3 lecture_notes_latex_generator.py -a "Hussein Esmail" -c "EECS 3311" -w "MWF" -l "VC 105" -s "A" -p "Andrew Skelton" -y "2022W" -n "3" -t "Software Design" -f "EECS3311.tex"

# TODO: Account for skipping reading week
# TODO: Ask for lecture times (during the day)
# TODO: Account for lab dates and times
# TODO: Account for tutorial dates and times

import os
import os.path
import getopt
import sys
import re
from datetime import datetime as date
import datetime

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
str_prefix_q            = f"[{color_pink}Q{color_end}]"         # "[Q]"
str_prefix_y_n          = f"[{color_pink}y/n{color_end}]"       # "[y/n]"
str_prefix_ques         = f"{str_prefix_q}\t "                  # "[Q]  "
str_prefix_err          = f"[{color_red}ERROR{color_end}]\t "   # "[ERROR]"
str_prefix_done         = f"[{color_green}DONE{color_end}]\t "  # "[DONE]"
str_prefix_info         = f"[{color_cyan}INFO{color_end}]\t "   # "[INFO]"

def yes_or_no(str_ask):
    while True:
        y_n = input(f"{str_prefix_q} {str_prefix_y_n} {str_ask}").lower()
        if len(y_n) == 0:
            return True
        elif y_n[0] == "y":
            return True
        elif y_n[0] == "n":
            return False
        if y_n[0] == "q":
            sys.exit()
        else:
            print(f"{str_prefix_err} {error_neither_y_n}")

def require_answer(q1):
    # Keeps asking question until user confirms their response is true
    q1ans = ""
    while True:
        q1ans = input(str_prefix_ques + " " + q1).strip()
        if len(q1ans) == 0:
            print(str_prefix_err + " You cannot provide a blank response!")
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
            print(f"Replaced: \n\t{item}", end="")
            list[num] = item.replace(search_str, str) # Replace the string
            print(f"\t{list[num]}")
    return list # Return the new list with changed values

def main(argv):
    author = "Hussein Esmail"
    filename = ""
    path_template_dir = os.path.expanduser("~/git/templates/")
    path_template_file = "lecture-template.tex"
    currentDate = date.now().strftime("%Y %m %d")
    lines_append = []
    weekdays = ["", "", ""] # [Lecture weekdays, Tutorial weekdays, Lab weekdays]
    weekdays_order = ["Lectures", "Tutorials", "Labs"]
    courseCode = ""
    courseLocation = ""
    courseTitle = ""
    courseSection = ""
    prof = ""
    semester = ""
    courseCredits = ""

    # Process user arguments
    # https://www.tutorialspoint.com/python/python_command_line_arguments.htm
    try:
        opts, args = getopt.getopt(argv,"ha:f:c:w:l:s:p:y:n:t:", ["author=", "filename=", "course-code=", "weekday=", "location=", "section=", "prof=", "semester=", "title="])
    except getopt.GetoptError:
        print('lecture_notes_latex_generator.py -a <author> -f <file name>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h': # Help message
            print("--- lecture_notes_latex_generator.py ---\n")
            print("Arguments:")
            print("\t -a, --author:\t\t Author of the notes file")
            print("\t -f, --filename:\t File name of the document to create")
            print("\t -c, --course-code:\t Course code of the course these notes are for")
            # TODO: Update help message to have separate weekday arguments for lectures, tutorials, labs
            # print("\t -w, --weekday:\t\t Weekdays this course takes place (MTWRF)")
            print("\t -l, --location:\t Location of the course")
            print("\t -s, --section:\t\t Course section")
            print("\t -p, --prof:\t\t Teacher of this course")
            print("\t -y, --semester:\t An example can be 2022F for Fall 2022")
            print("\t -n, --credits:\t\t Number of credits this course has")
            print("\t -t, --title:\t\t Title of the course")
            sys.exit()
        elif opt in ("-a", "--author"):
            author = arg
        elif opt in ("-f", "--filename"):
            filename = arg
        elif opt in ("-c", "--course-code"):
            courseCode = arg
        # TODO: Reformat weekdays argument to be specific to lectures, tutorials, labs
        # elif opt in ("-w", "--weekday"):
        #    weekdays = arg
        elif opt in ("-l", "--location"):
            courseLocation = arg
        elif opt in ("-s", "--section"):
            courseSection = arg
        elif opt in ("-p", "--prof"):
            prof = arg
        elif opt in ("-y", "--semester"): # y for year as well
            semester = arg
        elif opt in ("-n", "--credits"): # n for number
            courseCredits = int(arg)
        elif opt in ("-t", "--title"): # Course title
            courseTitle = arg

    # Ask user anything that is unanswered and required

    if courseCode == "": # If course code was not given in initial run line
        courseCode = require_answer("Course code (with spaces): ")

    # Asking if this course has Lectures, Tutorials, Labs
    print(f"{str_prefix_info} About to ask which weekdays for Lectures, Tutorials, Labs" )
    # TODO: change the hardcoded "Lecture, Tutorials, Labs" for the line above to refer to weekdays_order array later

    for weekday_type, weekday_type_num in enumerate(weekdays): # Weekday values, all initially ""
        weekday_type_str = weekdays_order[weekday_type_num] # "Lecture", "Tutorials", or "Labs". Used for asking the user to input each type
        if weekday_type == "": # If weekdays the course occurs not given
            # Do not use require_answer() because it has to check weekday regex
            while True:
                weekdays[weekday_type_num] = input(str_prefix_ques + " Input weekdays this course happens (MTWRF): ").strip().replace(" ", "")
                if bool(re.match("^[MTWRFmtwrf]+$", weekdays)): # Weekday regex
                    break
                else:
                    print(f"{str_prefix_err} Please only enter only MTWRF characters!")

    if courseLocation == "": # Ask course location if not given before
        courseLocation = require_answer("Location of this course: ")

    if filename == "": # Ask for file name if not given before
        # Does not use require_answer() because it has to check for file ext.
        while True:
            filename = input(str_prefix_ques + " File name (tex): ")
            if not filename.endswith(".tex"):
                filename += ".tex"
            if yes_or_no("Is this correct - '" + filename + "'? "):
                break

    if courseTitle == "": # Ask for course title if not given before
        courseTitle = require_answer("Course title: ")

    if courseSection == "": # Ask for course section if not given before
        # Does not use require_answer() because it has to check it's 1 char
        while True:
            courseSection = input(str_prefix_ques + " Course Section (1 char): ").strip()
            if len(courseSection) != 1:
                print(str_prefix_err + " The course code has to be 1 character only!")
            elif yes_or_no("Is this correct - Section " + courseSection + "? "):
                break

    if prof == "": # Ask for professor if not given before
        prof = require_answer("Professor teaching this section: ")

    if semester == "": # Ask for which semester it takes place in if not given
        # Does not use require_answer() because it has to ckeck regex
        while True:
            semester = input(str_prefix_ques + " Year and Semester (Ex: 2021F): ")
            if bool(re.match("^[0-9]{4}(W|F|SU|S1|S2)$", semester)):
                # Regex: First 4 chars is year, after is term
                break
            else:
                print("Please only enter in the correct format.")

    # Confirming Week 1's start date
    week1monday = ""
    year = int(semester[:4]) # Get inputted year (first 4 characters)
    partOfYear = semester[4:] # W or F of SU (rest of string after 4 characters)
    if partOfYear == "W":
        month = 1 # January
    elif partOfYear == "F":
        month = 9 # September
    elif partOfYear == "SU":
        d = datetime.date(year, 5, 7) # 2nd Monday of May
        next_monday = next_weekday(d, 0)
        month = 5 # Summer semester starts in May (2022: May 9)
        # Reading week in 2022: June 21-24
    elif partOfYear == "S1":
        d = datetime.date(year, 5, 7) # 2nd Monday of May
        next_monday = next_weekday(d, 0)
        month = 5 # S1 semester starts in May (2022: May 9)
        # Exams week in 2022: June 21-24
    elif partOfYear == "S2":
        month = 6 # S2 semester starts in June (2022: June 27)
    # If the current month is after January
    # if date.now().month > 1:
    #     d = datetime.date(year, 1, 7)
    # else:
    #     d = datetime.date(date.now().year, 1, 7)

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
                date_correct_input = input(str_prefix_ques + " Input the date in the form of YYYY MM DD: ")
                date_correct = date.strptime(date_correct_input, "%Y %m %d")
                if yes_or_no("Is this correct: " + date_correct.strftime('%a %b %d, %Y') + "? "):
                    continue_loop = False
                    break
            d = date_correct

    if courseCredits == "": # Ask for number of credits if not given
        # Does not use require_answer() because it has to be a number
        while True:
            try:
                courseCredits = int(input(str_prefix_ques + " Course credit amount: "))
                if yes_or_no("Is this correct - " + str(courseCredits) + " credits? "):
                    break
            except:
                print("Your response caused an error!")

    # Read template file contents
    lines = open(path_template_dir + path_template_file, "r").readlines()

    # Change values in LaTeX template preamble
    ncmd = "\\def\\" # ncmd = "New Command" prefix string
    lines = rep_arr_val(lines, "[FILENAME]", filename) # File name
    lines = rep_arr_val(lines, "[AUTHOR]", author) # Author of these notes (you)
    lines = rep_arr_val(lines, "[DATE]", currentDate) # Today
    lines = rep_arr_val(lines, "[DESC]", f"Course notes for {courseCode}") # File description (as a comment, mainly)
    lines = rep_arr_val(lines, "[SUBJ]", f"Lecture notes for {courseCode} in {semester}") # Subject
    lines = rep_arr_val(lines, "[KEYWORDS]", f"{courseCode}, York University") # TODO: Make the York University part parametric later
    lines = rep_arr_val(lines, "[COURSE-CREATED-DATE]", currentDate)
    lines = rep_arr_val(lines, "[COURSE-CREDITS]", str(courseCredits))
    lines = rep_arr_val(lines, "[COURSE-CODE]", courseCode)
    lines = rep_arr_val(lines, "[COURSE-TITLE]", courseTitle)
    lines = rep_arr_val(lines, "[COURSE-PROF]", prof) # Prof's full name
    lines = rep_arr_val(lines, "[COURSE-SEMESTER]", semester) # Prof's full name
    lines = rep_arr_val(lines, "[COURSE-SCHEDULE]", weekdays)
    lines = rep_arr_val(lines, "[COURSE-SECTION]", courseSection)
    lines = rep_arr_val(lines, "[COURSE-LOCATION]", courseLocation)
    lines = rep_arr_val(lines, "[PROF]", prof.split()[0]) # Prof by informal name within notes

    # lines = rep_arr_val(lines, "[]", )
    # TODO: Continue here before running program

    # Index of where to insert new lines
    line_insert = index_str(lines, "% TODO: Lecture notes here")

    # Print sections by week here
    lectureCount = 1 # Counter since there can be multiple lectures in a week
    for weekNum in range(1, 12): # There are normally 12 weeks in a semester
        lines_append.append("\n\\section{Week " + str(weekNum) + "}") # Each week section line
        for lectureDay in weekdays: # Generating each subsection for every weekday in the week
            if lectureDay == "M":
                d = next_weekday(d, 0) # 0 = Monday
                weekday_short = "Mon"
            elif lectureDay == "T":
                d = next_weekday(d, 1) # 1 = Tuesday
                weekday_short = "Tue"
            elif lectureDay == "W":
                d = next_weekday(d, 2) # 2 = Wednesday
                weekday_short = "Wed"
            elif lectureDay == "R": # R = How York represents Thursday since T is used by Tuesday
                d = next_weekday(d, 3) # 3 = Thursday
                weekday_short = "Thu"
            elif lectureDay == "F":
                d = next_weekday(d, 4) # 4 = Friday
                weekday_short = "Fri"
            tDateFormatted = d.strftime("%Y %m %d")
            lines_append.append("\\subsection{Lecture " + str(lectureCount) + ": " + tDateFormatted + " (" + weekday_short + ")}")
            lines_append.append("\\begin{itemize*}")
            lines_append.append("    \\item ")
            lines_append.append("\\end{itemize*}\n")
            lectureCount += 1 # Increase lecture counter for the subsections

    # Merge arrays + write to file
    lines[line_insert:line_insert] = [line + "\n" for line in lines_append]
    open(filename, "w").writelines(lines)

    sys.exit() # Exit program with no errors

if __name__ == "__main__":
    if len(sys.argv) > 0:
        main(sys.argv[1:])
    else:
        main()
