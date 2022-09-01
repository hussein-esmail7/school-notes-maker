# school-notes-maker

## Table of Contents
- [What is this?](#what-is-this)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Program](#running-the-program)
	- [Arguments](#arguments)
- [Program Output](#program-output)
- [Configuration File](#configuration-file)
	- [Entire Default Config](#entire-default-config)
	- [Filename Output Options](#filename-output-options)
	- [Post Script](#post-script)
- [Donate](#donate)

## What is this?
This program generates school notes based on the given CAT code and JSON file generated from [yorku-class-scraper](https://github.com/hussein-esmail7/yorku-class-scraper).

## Requirements
- python3

## Installation
At the moment, you can only `git clone` this repository, but I am hoping to put
it on Homebrew soon.

```
git clone https://github.com/hussein-esmail7/school-notes-maker
```

If you want to run this program in Terminal just by typing the program name,
you would have to add an alias in your `.bashrc` file. If you do this, you
should alias to the `school-notes-maker.py` file. Example:
```
alias snotes='path/to/folder/school-notes-maker/school-notes-maker.py'
```

## Running the program
To use this program, you have to make sure you are in the correct directory.

```
cd school-notes-maker
python3 school-notes-maker.py
```

### Arguments
Here are possible arguments you can call in Terminal:
```
-a, --author --> Author of the notes file (you). Example: -a "Hussein Esmail"
-c, --course-code --> Course code. Example: -c "EECS 1001"
-f, --filename --> Output file name. Example: -f "EECS1001Notes.tex"
-i, --input --> Course query.
	This can be one of 2 formats:
	1.  [Course code (2-4 letters)] [Course code number (4 numbers)] [Section (1 letter)]. Example: "EECS 1011 Z"
	2.  [CAT code (6 characters)]. Example: "Y4FZ01"
-j, --json: --> JSON file path created by yorku-class-scraper. Example: -j "../yorku-class-scraper/json/2022_fw.json"
-l, --location: --> Location of the course. Example: -l "CLH I"
-n, --credits --> Number of credits this course has. Example: -n "3"
-p, --prof --> Course professor/lecturer. Example: -p "Andrew Skelton"
-q, --quiet --> Quiet mode. Example: -q
-s, --section --> Course section. Example: -s "A" for Section A
-t, --title --> Course title. Example: -t "Introduction to Computer Science"
-y, --semester --> Course semester. Example: -y "2020F" (for Fall 2020)
```

Example:
`python3 school-notes-maker.py -j "../yorku-class-scraper/json/su_2022_all.json" -i "Y4FZ01" -f "AAAA0000.tex"`

## Program Output
This program outputs a `.tex` LaTeX file. There are multiple ways of comverting this to PDF:
1. Use an online compiler like [Overleaf](https://overleaf.com/) after the program runs.
2. Make a script that can run right after this program if you pass the file path of it to the `PATH_POST_SCRIPT` variable in your [config](#configuration-fil) file.

## Configuration File
This section is the arguments you can put into your configuration file at
`~/.config/school-notes-maker/config`

### Entire Default Config:
```
[Default]
author=Hussein Esmail
format_output={c}{n}.tex
insert=\\begin{itemize*}\n\t\\item\n\\end{itemize*}
json=
post=
quiet=False
university=York University
```

### Filename Output Options
- `{c}`: Course department ("EECS", "ADMS", etc.)
- `{n}`: Course number ("1001" from "EECS 1001")
- `{a}`: Course section ("A", "B", "Z", etc.)
- `{s}`: Semester ("F", "W", "Y", etc.)
- `{y}`: Year ("2022", "2023", etc.) --WARNING-- Not implemented yet
- `{p}`: Professor full name
- `{f}`: Professor first name
- `{l}`: Professor last name
> :warning: If at any point the specified field isn't available in your JSON
> input file, the program will not add it instead of raising an error.

### Post Script
This part of the configuration file lets you run another script after the
output `.tex` file has been created. Personally, I have this set to my
[`c.sh`](https://github.com/hussein-esmail7/sh/blob/main/c.sh) program that can
be found at my [hussein-esmail7/sh/](https://github.com/hussein-esmail7/sh/)
repository. By default, this field is left empty.

The Python program runs whatever is in the `post` argument, then
lastly the file name of the `.tex` file the program just outputted. Please do
not put quotation marks in this argument even if there are spaces in your
command.

## Donate
[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/husseinesmail)

