from flask import Flask, redirect, url_for
from flask import request
from flask import render_template
from flask import jsonify
from flask import g
import bleach
import json
import os
import hashlib
import time
import datetime
from datetime import timedelta
import mysql.connector

app = Flask(__name__, static_folder='static', static_url_path='')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    db = get_mysqldb()
    cursor = db.cursor()
    error = None
    user = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s",(username,password))
        result = cursor.fetchall()
        if len(result) == 0:
            error=True
        else:
            # user = {"username": result[0][1]}
            user = result[0][0]
            print(user)
            return redirect(url_for('.comments',error=error, user=user))
    return render_template('login.html', error=error, user=user)

#-------------------------------------------------------------------------------
@app.route('/comments', methods=['GET', 'POST'])
def comments():
    db = get_mysqldb()
    cursor = db.cursor()
    error = None
    user = None
    typo = None
    weekday={1:'First',2:'Second',3:'Third',4:'Fourth',5:'Fifth',6:'Sixth'}

    if request.method == 'POST':
        username = request.form['username']
        comment1 = request.form.get('comment1')
        comment2 = request.form['comment2']
        comment3 = request.form['comment3']
        print(888888)

        comment = '1 - '+comment1+'\n'+'2 - '+comment2+'\n'+'3 - '+comment3
        # get the hour last time submitted
        cursor.execute("SELECT whichday,time FROM comments WHERE username = %s", (username,) )
        time = cursor.fetchone()
        print(222222)
        print(time)
        today = str(datetime.date.today())
        print(today)
        print('**************')

        try:
            # if it is not the first day
            if time:
                # get the hour of now
                last_submit = time[1]
                whichday = time[0]
                yesterday = str(datetime.date.today() - datetime.timedelta(days=1))

                if yesterday == last_submit:
                    whichday += 1
                    sql = "UPDATE comments SET whichday=%s,time=%s,day{}=%s WHERE username = %s".format(whichday)
                    cursor.execute(sql,(whichday,today,comment,username) )
                    db.commit()
                    # check if it reaches 7 days
                    if whichday == 7:
                        fail = False
                        return render_template('fail.html',fail=fail)
                    have_done = weekday[whichday]
                    still_have = 7-whichday
                    return render_template('home.html',have_done=have_done,still_have=still_have)

                # if it is still the same day
                elif today == last_submit:
                    # in case the completed user to refresh the page.
                    if whichday>=7:
                        fail = False
                        return render_template('fail.html',fail=fail)

                    sameday = True
                    return render_template('home.html',sameday=sameday)
                else:
                    fail = True
                    return render_template('fail.html',fail=fail)
            # for the first day
            else:
                cursor.execute("INSERT into comments (username,whichday,time,day1,day2,day3,day4,day5,day6,day7) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (username,1,today,comment,'','','','','',''))
                db.commit()
                have_done = weekday[1]
                still_have = 6
                return render_template('home.html',have_done=have_done,still_have=still_have)
        except mysql.connector.errors.DatabaseError:
            print('哎呦不错')
            user = {"username": username}
            return render_template('comments.html',user=user,typo=type)

    else:
        user1 = request.args['user']
        user = {"username": user1}
    return render_template('comments.html', error=error, user=user)

#-------------------------------------------------------------------------------

# Simple registration function
@app.route('/register', methods=['POST', 'GET'])
def register():
    # If this is a GET request it is a page load request and just return the template
    db = get_mysqldb()
    if request.method == 'GET':
        return render_template('register.html')

    username = request.form['username']
    password = request.form['password']
    #====================================below============
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",\
                        (bleach.clean(username), password))
        db.commit()
    except Exception as e:
        error = {}
        error['message']="Username not unique"
        return render_template('register.html',error=error)

    # having inserted the user redirect to login page
    return redirect("./login")


# checks if a user id is currently in use
@app.route('/username', methods=['POST'])
def username():
    # get the request contents as JSON object
    req = request.get_json(force=True)
    db=get_mysqldb()
    cursor = db.cursor()
    username = req['username']
    print(username)
    cursor.execute("SELECT username FROM users WHERE username = %s", (username,) )
    user = cursor.fetchone()

    # Check if user exists and return True or False
    if user is None:
        return jsonify(exists=False)
    else:
        return jsonify(exists=True)

#===============================================================================
#                     Utility methods
#
# Code below here can be considered to be safe and is not part of the assignment.
#
#===============================================================================

# Utility function to convert database response into JSON compatiable array
def get_mysqldb():
    mydb=mysql.connector.connect(
        host = 'localhost',
        user = 'ubuntu',
        passwd='db5656576',
        database = 'research'
    )
    print('database connected..')
    return mydb

# Reset database for testing purposes - also useful to see structure of DB
@app.route('/resetdatabase', methods=['GET'])
def resetdb():
#=========================below==================================================================
    db = get_mysqldb()
    cursor = db.cursor()
    print('hahaha')

    # id INTEGER PRIMARY KEY,
    sql1= ['DROP TABLE IF EXISTS users','DROP TABLE IF EXISTS comments','DROP TABLE IF EXISTS colours']
    for statement in sql1:
        cursor.execute(statement)

    sql2 = 'CREATE TABLE users (username VARCHAR(64) PRIMARY KEY NOT NULL UNIQUE,password VARCHAR(64))'
    cursor.execute(sql2)

    sql3 = '''
            CREATE TABLE comments (
            username VARCHAR(64) PRIMARY KEY NOT NULL UNIQUE,
            whichday INT DEFAULT 99,
            time VARCHAR(15) DEFAULT '',
            day1 VARCHAR(200) DEFAULT '',
            day2 VARCHAR(200) DEFAULT '',
            day3 VARCHAR(200) DEFAULT '',
            day4 VARCHAR(200) DEFAULT '',
            day5 VARCHAR(200) DEFAULT '',
            day6 VARCHAR(200) DEFAULT '',
            day7 VARCHAR(200) DEFAULT '')
            '''
    cursor.execute(sql3)

    sql4 ='''
            CREATE TABLE colours (
            username VARCHAR(64) PRIMARY KEY NOT NULL UNIQUE,
            whichday INT DEFAULT 99,
            time VARCHAR(15) DEFAULT '',
            day1 VARCHAR(10) DEFAULT '',
            day2 VARCHAR(10) DEFAULT '',
            day3 VARCHAR(10) DEFAULT '',
            day4 VARCHAR(10) DEFAULT '',
            day5 VARCHAR(10) DEFAULT '',
            day6 VARCHAR(10) DEFAULT '',
            day7 VARCHAR(10) DEFAULT '')
            '''
    cursor.execute(sql4)
    print('sql5')

    sql_insert = [\
                'INSERT INTO comments VALUES ("admin", 1, "2019-08-24","haha today is a good day", "","","","","","")',\
                'INSERT INTO colours VALUES ("admin", 1, "2019-08-24","red", "","","","","","")',\
                'INSERT INTO comments VALUES ("zuotian",1,"2019-08-26", "12345","","","","","","")',\
                'INSERT INTO comments VALUES ("zuihou",6,"2019-08-26", "12345","","","","","","")',\
                'INSERT INTO users VALUES ("zuotian","zuotian")',\
                'INSERT INTO users VALUES ("admin","admin")',\
                'INSERT INTO users VALUES ("zuihou","zuihou")'\
                ]
    for statement in sql_insert:
        cursor.execute(statement)
        print(statement)
    print(7989898)

    # Save (commit) the changes
    db.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    db.close()
    return jsonify(reset=True)

if __name__=='__main__':
    app.run()
