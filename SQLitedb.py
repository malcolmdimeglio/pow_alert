#! /usr/bin/env python

import os
from dotenv import load_dotenv, find_dotenv
import sqlite3
from logger import *

load_dotenv(find_dotenv())
DATABASE = os.environ.get("DATABASE_NAME", "myDB.db")
REGISTER = "register"
UPDATE = "update"
UNREGISTER = "unregister"
REMOVE = "remove"

connect = sqlite3.connect(DATABASE)
curs = connect.cursor()
curs.execute("""CREATE TABLE IF NOT EXISTS Users (id INTEGER PRIMARY KEY, number VARCHAR(15), registered VARCHAR(3))""")
connect.commit()  # Save (commit) the changes
connect.close()


def add(phone_number, register):
    log.debug(f"Add {phone_number} number to the DB")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""INSERT INTO Users VALUES (NULL,?,?)""", (phone_number, register))

    conn.commit()  # Save (commit) the changes
    conn.close()


def remove(phone_number):
    log.debug(f"Remove {phone_number} from the DB")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""DELETE FROM Users WHERE number=?""", (phone_number,))

    conn.commit()  # Save (commit) the changes
    conn.close()


def in_database(phone_number):
    log.debug(f"Check if {phone_number} in DB")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    found = False

    for row in c.execute("""SELECT number FROM Users"""):
        if phone_number in row:
            found = True
            log.debug(f"{phone_number} found")

    if not found:
        log.debug(f"{phone_number} not found")
    conn.close()
    return found


def updtate_register_col(phone_number, register):
    log.debug(f"Update {phone_number} data. Register: {register}")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""UPDATE Users SET registered=? WHERE number=?""", (register, phone_number))

    conn.commit()  # Save (commit) the changes
    conn.close()


def update_database(phone_number, action):
    if action == REGISTER:
        if in_database(phone_number):
            updtate_register_col(phone_number, "yes")
        else:
            add(phone_number, "yes")

    elif action == UPDATE:
        if not in_database(phone_number):
            add(phone_number, "no")

    elif action == UNREGISTER:
        if in_database(phone_number):
            updtate_register_col(phone_number, "no")

    elif action == REMOVE:
        remove(phone_number)


def query_registered_numbers():
    log.debug(f"Querry all phone numbers from DB")
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    number_list = []

    for num in c.execute("""SELECT number FROM Users WHERE registered="yes" """):
        number_list.append(num[0])  # Database return a tuple (num,)

    conn.close()
    return number_list
