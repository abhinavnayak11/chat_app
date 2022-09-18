from datetime import time
import sqlite3
from collections import namedtuple
import os
from pydantic import BaseModel
import datetime


class Message(BaseModel):
    message_text: str
    user_id: str
    user_contact_id: str
    message_timestamp: str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class User(BaseModel):
    id: int
    name: str = ""
    number: str
    password: str


class Contact(BaseModel):
    name: str
    contact_number: str


EMPTY_USER = User(id=-1, number="", password="")

# from lib.api import DB_PATH

DB_PATH = "data/db.db"

# check queries
IS_USER_QUERY = "SELECT 1 FROM USER WHERE PHONE_NUMBER = '{number}' and PASSWORD_HASH = '{password}'"
IS_NEW_USER_QUERY = "SELECT 1 FROM USER WHERE PHONE_NUMBER = '{number}'"
IS_NOT_ALREADY_CONTACT_QUERY = """
        select 1 from CONTACT
        where USER_ID = {user_id} and CONTACT_ID = (select id from USER where PHONE_NUMBER = '{contact_number}')
    """

# get queries
GET_USER_ID_QUERY = "SELECT ID FROM USER WHERE PHONE_NUMBER = '{number}'"

GET_NUMBER_QUERY = "SELECT PHONE_NUMBER FROM USER WHERE ID = '{user_id}'"

GET_USER_QUERY = "SELECT * FROM USER WHERE PHONE_NUMBER = '{number}'"

GET_CHATS_ALL_CHATS_USER_ID = """
                select distinct(TO_USER) as user_id from CHAT
                where FROM_USER = '{user_id}' 
                union
                select distinct(FROM_USER) as user_id from CHAT
                where TO_USER = '{user_id}'
    """


GET_CONTACTS_QUERY = """
        select CONTACT_ID, CONTACT_NAME from CONTACT
        where USER_ID = '{user_id}'
    """
GET_CHAT_MESSAGES = """
                select FROM_USER, TO_USER, MESSAGE, MESSAGE_TIME from CHAT
                where FROM_USER = {user_id} and TO_USER = {user_contact_id}
                union
                select FROM_USER, TO_USER, MESSAGE, MESSAGE_TIME from CHAT
                where FROM_USER = {user_contact_id} and TO_USER = {user_id}
                order by MESSAGE_TIME
    """

# insert queries
INSERT_USER_QUERY = "INSERT INTO USER (NAME, PHONE_NUMBER, PASSWORD_HASH) VALUES(?,?,?)"  # CHECK ID & NULL
INSERT_CONTACT_QUERY = (
    "INSERT INTO CONTACT (USER_ID, CONTACT_ID, CONTACT_NAME) VALUES(?,?,?)"
)
INSERT_CHAT_MESSAGE_QUERY = (
    "INSERT INTO CHAT (FROM_USER, TO_USER, MESSAGE, MESSAGE_TIME) VALUES(?,?,?,?)"
)

MessageTuple = namedtuple(
    "Message", ["from_user", "to_user", "message", "message_time"]
)


def delete_db(db_path):
    if os.path.exists(db_path):
        os.remove(db_path)


def get_conn(db_path):
    return sqlite3.connect(db_path, check_same_thread=False)


def create_table(DB):
    DB.execute(
        """
        CREATE TABLE IF NOT EXISTS USER (
        ID INTEGER PRIMARY KEY,
        NAME VARCHAR(30),
        PHONE_NUMBER CHAR(10) NOT NULL UNIQUE,
        PASSWORD_HASH VARCHAR(20) NOT NULL
        );
    """
    )
    DB.execute(
        """
        CREATE TABLE IF NOT EXISTS CONTACT (
        USER_ID INT NOT NULL,
        CONTACT_ID INT NOT NULL,
        CONTACT_NAME VARCHAR(30) NOT NULL,
        PRIMARY KEY (USER_ID, CONTACT_ID),
        FOREIGN KEY (USER_ID)
        REFERENCES USER (Id),
        FOREIGN KEY (CONTACT_ID)
        REFERENCES USER (Id),
        UNIQUE(USER_ID, CONTACT_ID) ON CONFLICT IGNORE
        );
    """
    )
    DB.execute(
        """
        CREATE TABLE IF NOT EXISTS CHAT (
        ID INTEGER PRIMARY KEY,
        FROM_USER INTEGER NOT NULL,
        TO_USER INTEGER NOT NULL,
        MESSAGE VARCHAR(500) NOT NULL,
        MESSAGE_TIME TIMESTAMP NOT NULL,
        FOREIGN KEY (FROM_USER)
        REFERENCES USER (Id),
        FOREIGN KEY (TO_USER)
        REFERENCES USER (Id)
        );
    """
    )


conn = get_conn(DB_PATH)
DB = conn.cursor()


def is_user(number, password) -> bool:
    return bool(
        DB.execute(IS_USER_QUERY.format(number=number, password=password)).fetchone()
    )


def is_new_user(number: int) -> bool:
    return not bool(DB.execute(IS_NEW_USER_QUERY.format(number=number)).fetchone())


def is_not_already_contact(user_id: int, contact_number: str) -> bool:
    DB.execute(f"select id from USER where PHONE_NUMBER = '{contact_number}'")
    print(DB.fetchall())
    return not bool(
        DB.execute(
            IS_NOT_ALREADY_CONTACT_QUERY.format(
                user_id=user_id, contact_number=contact_number
            )
        ).fetchone()
    )


def get_user_id(number: int) -> int:
    return DB.execute(GET_USER_ID_QUERY.format(number=number)).fetchone()[0]


def get_number(user_id: int) -> int:
    return DB.execute(GET_NUMBER_QUERY.format(user_id=user_id)).fetchone()[0]


def get_user(number) -> User:
    values = DB.execute(GET_USER_QUERY.format(number=number)).fetchone()
    return User(id=values[0], name=values[1], number=values[2], password=values[3])


def get_chats(user_id: int):
    # get user ids of all chats
    DB.execute(GET_CHATS_ALL_CHATS_USER_ID.format(user_id=user_id))
    all_chats_user_id = tuple([x[0] for x in DB.fetchall()])
    if len(all_chats_user_id) != 1:
        DB.execute(
            """
    select CONTACT_ID, CONTACT_NAME from CONTACT 
    where CONTACT_ID in {all_chats_user_id} 
    and USER_ID = {user_id}""".format(
                all_chats_user_id=all_chats_user_id, user_id=user_id
            )
        )
    else:
        DB.execute(
            """
    select CONTACT_ID, CONTACT_NAME from CONTACT 
    where CONTACT_ID = {all_chats_user_id} 
    and USER_ID = {user_id}""".format(
                all_chats_user_id=all_chats_user_id[0], user_id=user_id
            )
        )

    # get user ids and names of saved contacts
    result = DB.fetchall()
    chats_user_id_contact_saved = tuple([x[0] for x in result])
    chats_name_contact_saved = tuple([x[1] for x in result])

    # get user ids and names of unsaved contacts
    chats_user_id_contact_not_saved = tuple(
        set(all_chats_user_id) - set(chats_user_id_contact_saved)
    )
    if len(chats_user_id_contact_not_saved) == 1:
        DB.execute(
            "select PHONE_NUMBER from USER WHERE ID = {}".format(
                chats_user_id_contact_not_saved[0]
            )
        )
    else:
        DB.execute(
            "select PHONE_NUMBER from USER WHERE ID in {}".format(
                chats_user_id_contact_not_saved
            )
        )
    chats_number_contact_not_saved = tuple([x[0] for x in DB.fetchall()])

    all_chats_user_id = chats_user_id_contact_saved + chats_user_id_contact_not_saved
    all_chats_number = chats_name_contact_saved + chats_number_contact_not_saved

    return tuple(zip(all_chats_user_id, all_chats_number))


def get_contacts(user_id: int):
    DB.execute(GET_CONTACTS_QUERY.format(user_id=user_id))
    # contact_ids = [x[0] for x in DB.fetchall()]
    # contact_names = [x[1] for x in DB.fetchall()]
    return DB.fetchall()


def get_chat_message(user_id: int, user_contact_id: int):
    DB.execute(
        GET_CHAT_MESSAGES.format(user_id=user_id, user_contact_id=user_contact_id)
    )
    Messages = [MessageTuple(x[0], x[1], x[2], x[3]) for x in DB.fetchall()]
    return Messages


def insert_user(name, number, password):
    DB.execute(INSERT_USER_QUERY, (name, number, password))
    conn.commit()


def insert_contact(user_id, contact_number, contact_name):
    DB.execute(
        INSERT_CONTACT_QUERY, (user_id, get_user_id(contact_number), contact_name)
    )
    conn.commit()


def insert_chat_message(
    user_id: int, user_contact_id: int, message: str, message_time: time
):
    DB.execute(
        INSERT_CHAT_MESSAGE_QUERY, (user_id, user_contact_id, message, message_time)
    )
    conn.commit()


# print(get_chat_message(3,1))
# print(get_contacts(1))

# print(get_user('111'))
# print(is_not_already_contact(1,'444'))

print(get_chats(4))

# new = DB.execute('''
#                 select distinct(TO_USER) as user_id from CHAT
#                 where FROM_USER = '{user_id}'
#                 union
#                 select distinct(FROM_USER) as user_id from CHAT
#                 where TO_USER = '{user_id}'
# '''.format(user_id = 4)).fetchall()
# print([x[0] for x in new])

# print(
#     DB.execute(
#         """
#     select CONTACT_ID, CONTACT_NAME from CONTACT 
#     where CONTACT_ID in {all_chats_user_id} 
#     and USER_ID = {user_id}
#     """.format(
#             all_chats_user_id=tuple([1, 2]), user_id=4
#         )
#     ).fetchall()
# )
