import os
from dotenv import load_dotenv
from flask import (
    Flask, request, render_template, session, flash, redirect, url_for, jsonify
)

# import regular expression
import re

# take environment variables from .env.
load_dotenv()

# import database configs
from db import db_connection

app = Flask(__name__)
app.secret_key = os.environ['SECRET_KEY']  # create the unique one for yourself


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ function to show and process login page """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = db_connection()
        cur = conn.cursor()
        sql = """
            SELECT id, username
            FROM users
            WHERE username = '%s' AND password = '%s'
        """ % (username, password)
        cur.execute(sql)
        user = cur.fetchone()

        error = ''
        if user is None:
            error = 'Wrong credentials. No user found'
        else:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))

        flash(error)
        cur.close()
        conn.close()

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    """ function to show and process login page """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        # check user input validity
        error = checkRegisterError(username, password)

        if error:
            flash(error)
        else:
            # at this point the input is safe tobe inserted into db
            conn = db_connection()
            cur = conn.cursor()
            sql = """
                INSERT INTO users (username, password) VALUES ('%s', '%s')
            """ % (username, password)
            cur.execute(sql)

            # commit to make sure changes are saved
            conn.commit()  

            sql = """
                SELECT id, username
                FROM users
                WHERE username = '%s' AND password = '%s'
            """ % (username, password)
            cur.execute(sql)
            user = cur.fetchone()

            cur.close()
            conn.close()

            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))

    # render when method is GET
    return render_template('register.html')

def checkRegisterError(username, password):
    # check if username is present and not less than 3 chars
    if username is None or len(username) < 3:
        return "username must be at least 3 characters"

    # should check if username is not already exist
    isExist = checkUsername(username)
    if isExist:
        return "username already exists"

    # should check if password is present and at least 5 chars
    if password is None or len(password) < 5:
        return "password must be at least 5 characters"

    # should check if password contain at least 1 uppercase
    isContainUppercase = re.findall("([A-Z])", password) 
    if isContainUppercase is None or len(isContainUppercase) == 0:
        return "password must contain at least 1 uppercase letter"
    
    return None


@app.route('/logout')
def logout():
    """ function to do logout """
    session.clear()  # clear all sessions
    return redirect(url_for('login'))


@app.route('/check-username', methods=['POST'])
def checkUsernameRoute():
    data = request.get_json() or {}
    username = data.get('username')

    # check if there is user with current username
    user = checkUsername(username)

    # return user
    return jsonify({'status': 200, 'user': user})


def checkUsername(username):
    conn = db_connection()
    cur = conn.cursor()
    sql = """
            SELECT username
            FROM users
            WHERE username = '%s'
        """ % (username)
    cur.execute(sql)
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


@app.route('/')
def index():
    conn = db_connection()
    cur = conn.cursor()
    sql = """
        SELECT art.id, art.title, art.body
        FROM articles art
        ORDER BY art.title
    """
    cur.execute(sql)
    # [(1, "Article Title 1", "Art 1 content"), (2, "Title2", "Content 2"), ...]
    articles = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', articles=articles)


@app.route('/article/create', methods=['GET', 'POST'])
def create():
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.get_json() or {}
        # check existence of title and body
        if data.get('title') and data.get('body'):
            title = data.get('title', '')
            body = data.get('body', '')
            user_id = session.get('user_id')

            # strip() is to remove excessive whitespaces before saving
            title = title.strip()
            body = body.strip()

            conn = db_connection()
            cur = conn.cursor()
            # insert with the user_id
            sql = """
                INSERT INTO articles (title, body, user_id) VALUES ('%s', '%s', %d)
            """ % (title, body, user_id)
            cur.execute(sql)
            conn.commit()  # commit to make sure changes are saved
            cur.close()
            conn.close()
            # an example with redirect
            return jsonify({'status': 200, 'message': 'Success', 'redirect': '/'})

        # else will be error
        return jsonify({'status': 500, 'message': 'No Data submitted'})

    return render_template('create.html')


@app.route('/article/<int:article_id>', methods=['GET'])
def read(article_id):
    # find the article with id = article_id, return not found page if error
    conn = db_connection()
    cur = conn.cursor()
    sql = """
        SELECT art.title, art.body, usr.name
        FROM articles art
        JOIN users usr ON usr.id = art.user_id
        WHERE art.id = %s
    """ % article_id
    cur.execute(sql)
    article = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('detail.html', article=article)


@app.route('/article/edit/<int:article_id>', methods=['GET', 'POST'])
def edit(article_id):
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        conn = db_connection()
        cur = conn.cursor()
        title = request.form['title']
        body = request.form['body']
        title = title.strip()
        body = body.strip()

        sql_params = (title, body, article_id)

        sql = "UPDATE articles SET title = '%s', body = '%s' WHERE id = %s" % sql_params
        print(sql)
        cur.execute(sql)
        cur.close()
        conn.commit()
        conn.close()
        # use redirect to go to certain url. url_for function accepts the
        # function name of the URL which is function index() in this case
        return redirect(url_for('index'))

    # find the record first
    conn = db_connection()
    cur = conn.cursor()
    sql = 'SELECT id, title, body FROM articles WHERE id = %s' % article_id
    cur.execute(sql)
    article = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit.html', article=article)


@app.route('/article/delete/<int:article_id>', methods=['GET', 'POST'])
def delete(article_id):
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    conn = db_connection()
    cur = conn.cursor()
    sql = 'DELETE FROM articles WHERE id = %s' % article_id
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    return jsonify({'status': 200, 'redirect': '/'})
