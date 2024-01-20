# Maria Duan, yumengdu@usc.edu
# ITP 216, Fall 2022
# Section: 31883R
# Final Project, db_actions.py
# Description: Create a database

import sqlite3 as sl

db = "BTC.db"
def create(fn):
    # Open the .csv file
    f = open(fn, "r")
    # Clean up the header
    header = f.readline().strip().split(",")
    for i in range(len(header)):
        header[i] = "\'" + header[i] + "\'"
    header = ", ".join(header)
    f.close()

    # Create table using header
    conn = sl.connect(db)
    curs = conn.cursor()
    stmts = ["CREATE TABLE BTC_Price_Volume (" + header + ")"]

    listOfTables = curs.execute(
        """SELECT tbl_name FROM sqlite_master WHERE type='table'
        AND tbl_name='BTC_Price_Volume'; """).fetchall()
    if listOfTables == []:
        for stmt in stmts:
            curs.execute(stmt)
        conn.commit()
    else:
        print('Table found!')

    conn.close()

def store_data(fn, table):
    conn = sl.connect(db)
    curs = conn.cursor()
    # Open the file and ignore the header line
    f = open(fn, "r")
    header = f.readline()

    # Store date into the table
    n = 0
    for line in f:
        line = line.strip()
        line = line.split(",")

        cmd = "INSERT INTO " + table + " VALUES (?, ?, ?, ?, ?) "
        curs.execute(cmd, line)
        n += 1

    # Close
    f.close()
    conn.commit()
    conn.close()

def main():
    fn = "./csv/BTC_Price_Volume.csv"
    table = "BTC_Price_Volume"
    create(fn)
    store_data(fn, table)

if __name__ == "__main__":
    main()
