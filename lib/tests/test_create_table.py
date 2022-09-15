import sqlite3
import os
from lib.db import create_table

print(os.getcwd())

def create_test_db():
    test_db_path = 'lib/tests/test_db.db'
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    return sqlite3.connect(test_db_path)

# how to check create table has no errors

def test_user_table_insert():
    conn = create_test_db()
    DB = conn.cursor()
    create_table(DB)
    DB.execute('''
    INSERT INTO USER (ID, NAME, PHONE_NUMBER, PASSWORD_HASH)
    VALUES
    (1, 'Abhinav', '123', '1234');
    ''')
    DB.execute("select * from USER")
    assert DB.fetchone() == (1, 'Abhinav', '123', '1234')

def test_user_table_id_autoincrement():
    conn = create_test_db()
    DB = conn.cursor()
    create_table(DB)
    DB.execute('''
    INSERT INTO USER (NAME, PHONE_NUMBER, PASSWORD_HASH)
    VALUES
    ('Abhinav', '123', '1234'),
    ('Ashwany', '222', 'ash')
    ''')
    DB.execute("select ID from User")
    assert [x[0] for x in DB.fetchall()] == [1,2]

def test_user_table_id_unique_contraint():
    conn = create_test_db()
    DB = conn.cursor()
    create_table(DB)
    try:
        DB.execute('''
        INSERT INTO USER (ID, NAME, PHONE_NUMBER, PASSWORD_HASH)
        VALUES
        (1, 'Abhinav', '123', '1234'),
        (1, 'Ashwany', '222', 'ash')
        ''')
    except Exception as e:
        assert type(e) is sqlite3.IntegrityError
        assert e.args[0] == "UNIQUE constraint failed: USER.ID"

def test_user_table_id_not_null_constraint():
    conn = create_test_db()
    DB = conn.cursor()
    create_table(DB)
    try:
        DB.execute('''
        INSERT INTO USER (ID, NAME, PHONE_NUMBER, PASSWORD_HASH)
        VALUES
        (3, 'Abhinav', '123', '1234'),
        (4, 'Ashwany', '222', 'ash'),
        (NULL, 'Shobha', '333', 'password123')
        ''')
        DB.execute("select * from USER")
        print(DB.fetchall())
        assert DB.fetchall() == [1,2]
    except Exception as e:
        assert type(e) is sqlite3.IntegrityError
        assert e.args[0] == "NOT NULL constraint failed: USER.NAME"

def test_user_table_phone_number_not_null_contraint():
    conn = create_test_db()
    DB = conn.cursor()
    create_table(DB)
    try:
        DB.execute('''
        INSERT INTO USER (ID, NAME, PHONE_NUMBER, PASSWORD_HASH)
        VALUES
        (1, 'Abhinav', NULL, '1234')
        ''')
    except Exception as e:
        assert type(e) is sqlite3.IntegrityError
        assert e.args[0] == "NOT NULL constraint failed: USER.PHONE_NUMBER"

def test_user_table_phone_number_unique_contraint():
    conn = create_test_db()
    DB = conn.cursor()
    create_table(DB)
    try:
        DB.execute('''
        INSERT INTO USER (NAME, PHONE_NUMBER, PASSWORD_HASH)
        VALUES
        ('Abhinav', '123', '1234'),
        ('Ashwany', '123', 'ash')
        ''')
    except Exception as e:
        assert type(e) is sqlite3.IntegrityError
        assert e.args[0] == "UNIQUE constraint failed: USER.PHONE_NUMBER"