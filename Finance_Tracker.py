import mysql.connector as sqltor
from dotenv import load_dotenv
import os
from decimal import Decimal, InvalidOperation
from datetime import date,datetime
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
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter User ID"))
    cat_type=input("Enter Category Type")
    if cat_type:
        st="""SELECT category_id,category_name,category_type FROM categories WHERE user_id=%s AND category_type=%s ORDER BY category_name ASC;"""
        params=(user_id,cat_type)
        cursor.execute(st,params)
    else:
        sc="""SELECT category_id,category_name,category_type FROM categories WHERE user_id=%s ORDER BY category_type,category_name ASC;"""
        params=(user_id,)
        cursor.execute(sc,params)
    return cursor.fetchall()
def add_transaction_atomic():
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter User ID"))
    account_id=int(input("Enter Account ID"))
    category_id=int(input("Enter Category ID"))
    amount=Decimal(input("Enter Amount"))
    transaction_type=input("Enter The Transaction Type")
    description=input("Enter Description of the transaction")
    trans_date=date
    sc="""INSERT INTO transactions(user_id,account,category_id,amount,transaction_type,description,transaction_date)VALUES(%s,%s,%s,%s,%s,%s,%s);"""
    cursor.execute(sc,(user_id,account_id,category_id,amount,transaction_type,description,trans_date))
    if transaction_type=="expense":
        balance_sql="""UPDATE accounts SET current_balance=current_balance-%s WHERE account_id=%s AND user_id=%s;"""
    else:
        balance_sql="""UPDATE accounts SET current_balance=current_balance-%s WHERE account_id=%s AND user_id=%s;"""
    cursor.execute(balance_sql,(amount,account_id,user_id))
    cursor.commit()
def get_recent_transactions():
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter User ID"))
    limit=10
    st="""Select t.transaction_id,t.transaction_date,a.account_name,c.category_name,t.transaction_type,t.amount,t.description FROM transactions t JOIN accounts a ON t.account_id=a.account_id JOIN categories c ON t.category_id=c.category_id WHERE t.user_id=%s ORDER BY t.transaction_date DESC,t.transaction_id DESC LIMIT %s;"""
    cursor.execute(st,(user_id,limit))
    return cursor.fetchall()
def set_budget():
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter User ID"))
    category_id=int(input("Enter Category ID"))
    month_year=date(input("Enter Month_Year"))
    limit=Decimal(input("Enter Limit"))
    st="""INSERT INTO budgets(user_id,category_id,month_year,monthly_limit)VALUES(%s,%s,%s,%s)ON DUPLICATE KEY UPDATE monthly_limit=VALUES(monthly_limit);"""
    cursor.execute(st,(user_id,category_id,month_year,limit))
    mycon.commit()
def get_budget_vs_actual():
    global mycon
    cursor=mycon.cursor()
    user_id=int(input("Enter User ID"))
    months_start=date(input("Enter Month_Start"))
    month_end=date(input("Enter Month_End"))
    st="""Select c.category_name,b.monthly_limit,COALESCE(SUM(t.amount),0,00) AS total_spent,(b.monthly_limit-COALESCE(SUM(t.amount),0.00)) AS remaining_budget FROM budget b JOIN categories c ON b.category_id=c.category_id LEFT JOIN transactions t ON t.category_id=c.category_id AND t.transaction_date BETWEEN %s AND %s AND t.transaction_type='expense' WHERE b.user_id=%s GROUP BY c.category_id,c.category_name,b.monthly_limit;"""
    cursor.execute(st,(months_start,month_end,user_id,months_start))
    return cursor.fetchall()
def record_transaction():
    global mycon
    user_id=int(input("Enter User ID"))
    cursor=mycon.cursor()
    account_id=int(input("Enter Account ID"))
    category_id=int(input("Enter Category ID"))
    amount=Decimal(input("Enter Amount"))
    transaction_type=input("Enter Transaction Type (income/expense)")
    description=input("Enter Description")
    trans_date=date.today()
    if amount<=0:
        raise ValueError("Amount must be greater than zero.")
        account=get_account_by_id(user_id,account_id)
        if not account:
            raise ValueError("Account not found for the given user.")
        if transaction_type=="expense" and account["account_type"] in ["checking","cash"]:
            if account["current_balance"]<amount:
                raise ValueError("Insufficient funds in the account for this expense.")
        return add_transaction_atomic(user_id,account_id,category_id,amount,transaction_type,description,trans_date)
def ensure_default_user():
    global mycon
    cursor=mycon.cursor()
    cursor.execute("SELECT user_id,usernmae FROM users LIMIT 1:")
    user=cursor.fetchone()
    if user:
        cursor.close()
        return user["user_id"],user["username"]
    cursor.execute("INSERT INTO users(username,email) VALUES(%s,%s)",("Default User","user@example,com"))
    mycon.commit()
    uid=cursor.lastrowid
    return uid,"default_user"
def prompt_decimal():
    prompt_text=input("Enter a decimal value: ")
    while True:
        val=input(prompt_text).strip()
        try:
            dec=Decimal(val)
            if dec<=0:
                print("Amount must be positive.")
                continue
            return dec
        except InvalidOperation:
            print("Invalid decimal value. Please enter a valid decimal number.")
def prompt_date():
    while True:
        val=input("Enter a date (YYYY-MM-DD): ").strip()
        if not val:
            print("Date cannot be empty.")
        try:
            return datetime.strptime(val,"%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Please enter a date in YYYY-MM-DD format.")
def handle_add_account():
    print("\n--- Add New Account ---")
    name=input("Enter Account Name:(e.g.,Chase Checking,Cash): ").strip()
    print("Types:checking,savings,cash,credit")
    acc_type=input("Enter Account Type: ").strip().lower()
    if acc_type not in ["checking","savings","cash","credit"]:
        print("Invalid account type. Please choose from checking, savings, cash, or credit.")
        return
    balance=prompt_decimal("Starting Balance: ")
    try:
        create_account()
        print("Account Successfully Created.")
    except Exception as e:
        print("Error creating account")
def handle_add_category():
    print("\n--- Add New Category ---")
    name=input("Enter Category Name: ").strip()
    cat_type=input("Enter Category Type (income/expense): ").strip().lower()
    if cat_type not in ["income","expense"]:
        print("Invalid category type. Please choose either income or expense.")
        return
    try:
        create_category()
        print("Category Successfully Created.")
    except Exception as e:
        print("Error creating category:",e)
def handle_record_transaction():
    print("\n--- Record New Transaction ---")
    accounts=get_accounts_by_user() 
    if not accounts:
        print("No accounts found. Please create an account first.")
        return
    print("\nAvailable Accounts:")
    for acc in accounts:
        print(f"[{acc['account_id']}] {acc['account_name']} (Balance: {acc['current_balance']} {acc['currency']})")
    try:
        acc_id = int(input("Select Account ID: ").strip())
    except ValueError:
        print("Invalid ID.")
        return
    tx_type = input("Transaction Type (income/expense): ").strip().lower()
    if tx_type not in ['income', 'expense']:
        print("Invalid transaction type.")
        return
    categories=get_categories_by_user()
    if not categories:
        print("No categories found. Please create a category first.")
        return 
    print("\nAvailable Categories:")
    for cat in categories:
        print(f"[{cat['category_id']}] {cat['category_name']} ({cat['category_type']})")
    try:
        cat_id = int(input("Select Category ID: ").strip())
    except ValueError:
        print("Invalid ID.")
        return
    amount=prompt_decimal("Enter Amount: ")
    trans_date=prompt_date()
    description=input("Enter Description: ").strip()
    try:
        record_transaction()
        print("Transaction Recorded Successfully.")
    except Exception as e:
        print("Error recording transaction:",e)
        