import mysql.connector as sqltor
from dotenv import load_dotenv
import os
load_dotenv()
DB_CONFIG={"host":os.getenv("DB_HOST"),
           "user":os.getenv("DB_USER"),
           "password":os.getenv("DB_PASSWORD"),
           "database":os.getenv("DB_NAME")}
mycon=sqltor.connect(**DB_CONFIG)
def create_users():
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter User ID"))
    username=(input("Enter UserName"))
    email=input("Enter Email")
    st="""INSERT INTO USERS(user_id,username,email)values(%s,%s,%s)"""
    cursor.execute(st,(user_id,username,email))
def create_account():
    global mycon
    cursor=mycon.cursor()
    user_id=input("Enter user id: ")
    account_name=input("Enter account name: ")
    account_type=input("Enter account type: ")
    current_balance=float(input("Enter current balance: "))
    st="""INSERT INTO ACCOUNTS(user_id,account_name,account_type,current_balance) VALUES(%s,%s,%s,%s)"""
    cursor.execute(st,(user_id,account_name,account_type,current_balance))
    mycon.commit()
def get_accounts_by_user():
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter USER ID"))
    st="""Select account_id,account_name,account_type,current_balance,currency FROM accounts WHERE user_id=%s ORDER BY account_name ASC;"""
    cursor.execute(st,(user_id,))
    return cursor.fetchall()
def get_account_by_id():
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter User Id"))
    account_id=input("Enter Account ID")
    st="""SELECT account_id,account_name,account_type,current_balance,currency FROM accounts WHERE user_id=%s AND account_id=%s;"""
    cursor.execute(st,(user_id,account_id))
    return cursor.fetchall()
def create_category():
    global mycon
    user_id=int(input("Enter User ID"))
    name=input("Enter Username")
    cat_type=(input("Enter Category Type"))
    st="""INSERT INTO Categories(user_id,category_name,category_type)VALUES (%s,%s,%s)"""
    cursor=mycon.cursor()
    cursor.execute(st,(user_id,name,cat_type))
    mycon.commit()
def get_categories_by_user():
    