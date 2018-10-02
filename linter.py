#!/usr/bin/env python3

import sys
import re
from operator import itemgetter
import sqlite3
import pandas as pd

# Set up database
conn = sqlite3.connect('issue.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

linter_regex = {
    "lll" : r"(?<=line is )(.*)(?= characters)",
    "gocyclo" : r"(?<=complexity )(.*)(?= of)"
}

def close_and_exit(status):
    conn.commit()
    conn.close()
    sys.exit(status)

def string_to_num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def get_linter(line):
    match = re.findall(r"[a-z]+\)$", line)
    if len(match) == 0: 
        return ""
    return match[0][:-1]

def get_path(line):
    pos = line.find(".go")
    if pos == -1:
        return ""
    return line[:pos+3]

def get_package(line):
    match = re.findall(r"[^\/]*", line)
    if len(match) == 0: 
        return ""
    return match[0]

def get_row(line):
    match = re.findall(r"(?<=:)(\d+)(?=:)", line)
    if len(match) == 0: 
        return 0
    return string_to_num(match[0])

def get_value(linter, line):
    if linter in linter_regex:
        match = re.findall(linter_regex[linter], line)
        if len(match) > 0:
            return string_to_num(match[0])
    return 0

def print_usage():
    print("\nLinter PY\n")
    print("Options")
    print("populate, p : Populate the issue.db")
    print("list,     l : List all linters with issue counter")
    print("package, pa : List all package with issue counter")
    print("file,     f : List all file with issue counter")
    print("li lintername : List all issue by lintername")
    close_and_exit(1)

def populate_db():
    c.execute('DROP TABLE IF EXISTS issues')
    c.execute('''CREATE TABLE issues
             (line text, linter text, path text, package text, row int, value int)''')
    for line in sys.stdin:
        linter = get_linter(line)
        c.execute('INSERT INTO issues VALUES (?,?,?,?,?,?)', [line, linter, get_path(line), get_package(line), get_row(line), get_value(linter, line)])
    close_and_exit(0)

def linter_by_count():
    print(pd.read_sql_query("SELECT linter, count(*) FROM issues GROUP BY linter ORDER BY count(*)", conn, index_col="linter"))

def package_by_count():
    print(pd.read_sql_query("SELECT package, count(*) FROM issues GROUP BY package ORDER BY count(*) DESC", conn, index_col="package"))
   
def file_by_count():
    print(pd.read_sql_query("SELECT path, count(*) FROM issues GROUP BY path ORDER BY count(*) DESC", conn, index_col="path"))

def files_by_linter(linter):
    if "verbose" in sys.argv:
        query = 'SELECT linter, package, path, row, value, line FROM issues WHERE linter = ? ORDER BY value DESC'
        for row in c.execute(query, (linter,)):
            print(row[0], row[1], row[2] + ":" +  str(row[3]), row[4])
            print("\t" + row[5])
    else:
        query = 'SELECT linter, package, path, row, value FROM issues WHERE linter = ? ORDER BY value DESC'
        for row in c.execute(query, (linter,)):
            print(row[0], row[1], row[2] + ":" + str(row[3]), row[4])


# Check argv and execute functions accordingly
if len(sys.argv) == 1:
    print_usage()
else:
    if sys.argv[1] in ["p", "-p", "pop", "populate"]:
        populate_db()
    if sys.argv[1] in ["l", "-l", "linters"]:
        linter_by_count()
    if sys.argv[1] in ["pa", "-pa", "package"]:
        package_by_count()
    if sys.argv[1] in ["f", "-f", "file"]:
        file_by_count()
    if sys.argv[1] in ["li", "-li"]:
        files_by_linter(sys.argv[2])

close_and_exit(0)
