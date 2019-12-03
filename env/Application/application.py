import os
import requests
import json
from flask import Flask, render_template, request, jsonify, make_response, session, redirect, escape, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError

engine = create_engine(os.getenv("DATABASE_URL")) 
db = scoped_session(sessionmaker(bind=engine)) 

app = Flask(__name__, static_url_path='/static')
@app.route("/")
def welcome():
    return render_template("welcome.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/index/<int:page>')
def index(page):
    if 'username' in session:
        
        ratings = []
        book_count = db.execute("SELECT COUNT(*) FROM book;").first()[0]
        db.commit()
        page_count = book_count / 15 
        if type(page_count) == float:
            page_count = int(page_count)
        books = db.execute("SELECT * FROM book LIMIT 15 OFFSET :page", {"page":page}).fetchall()
        for book in books:
            stars = db.execute("SELECT COUNT(r1.rating) as stars_1, COUNT(r2.rating) as stars_2, COUNT(r3.rating) as stars_3, COUNT(r4.rating) stars_4, COUNT(r5.rating) as stars_5 FROM review r1 " + 
                    "LEFT OUTER JOIN review r2 ON r1.reviewid = r2.reviewid " + 
                    "LEFT OUTER JOIN review r3 ON r1.reviewid = r3.reviewid " + 
                    "LEFT OUTER JOIN review r4 ON r1.reviewid = r4.reviewid " + 
                    "LEFT OUTER JOIN review r5 ON r1.reviewid = r5.reviewid " + 
                    "WHERE r1.bookid = 2 AND " + 
                    "r1.rating = 1 AND " + 
                    "r2.rating = 2 AND " + 
                    "r3.rating = 4 AND " + 
                    "r4.rating = 4 AND " + 
                    "r5.rating = 5;").first()
            stars_1 = stars.stars_1
            stars_2 = stars.stars_2
            stars_3 = stars.stars_3
            stars_4 = stars.stars_4
            stars_5 = stars.stars_5

            sum_result = (stars_1 + stars_2 + stars_3 + stars_4 + stars_4)
            if (sum_result != 0):
                onsite_average_rating = ((5 * stars_5) + (4 * stars_4) + (3 * stars_3) + (2 * stars_2) + (1 * stars_1)) / (stars_1 + stars_2 + stars_3 + stars_4 + stars_4)
            else:
                onsite_average_rating = 0

            res = requests.get ('https://www.goodreads.com/book/review_counts.json', params = {"key":"bS9TJpeOW8gIGXR4CM9NFA", "isbns":book.isbn})
            if res.status_code == 200:
                goodreads_average_rating = float(res.json()["books"][0]["average_rating"])
            else:
                goodreads_average_rating = 0

            if ((onsite_average_rating != 0) and (goodreads_average_rating != 0)):
                average_rating = round (((onsite_average_rating + goodreads_average_rating) / 2), 1)
            elif ((onsite_average_rating == 0) or (goodreads_average_rating == 0)):
                average_rating = round ((onsite_average_rating + goodreads_average_rating), 1)
            mod = (goodreads_average_rating * 10) % 10
            print(f'ON SITE: {onsite_average_rating}  GOOD READS: {goodreads_average_rating} MOD: {mod}')

            
            ratings.append(average_rating)
            #if rating is not None:
        pagination = paginate(page_count, page)
        return render_template('index.html', books = books, ratings = ratings, current_page = page, pagination = pagination, page_count = page_count)
    return redirect(url_for('login'))

@app.route("/signup")
def signup():
    return render_template("signup.html") 

@app.route("/user_create", methods= ["POST"])
def user_create():
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')
    username = request.form.get('username')
    password = request.form.get('password')

    exists = db.execute ("SELECT * FROM useraccount WHERE username = :username", {"username":username}).first()
    db.commit()
    print(exists)
    if exists:
        return make_response(jsonify({'message':'This username is already taken'}), 500)
    else:
        db.execute("INSERT INTO useraccount (firstname, lastname, username, password) VALUES (:firstname, :lastname, :username, :password)",
                  {"firstname":firstname, "lastname":lastname, "username":username, "password":password})
        db.commit()
        return make_response(jsonify({'message':'Your account has been created'}), 200)

@app.route("/user_login", methods = ["POST"])
def user_login():
    username = request.form.get("username")
    password = request.form.get("password")

    print(username + password)
    exists = db.execute("SELECT * FROM useraccount WHERE username = :username AND password = :password", {"username":username, "password":password}).first()

    if exists:  
        user = exists
        session['userid'] = user.userid
        session['firstname'] = user.firstname
        session['lastname']  = user.lastname
        session['username'] = user.username
        return make_response(jsonify({'message': 'login successful', 'path':'/index/1'}))
    else:
        return make_response(jsonify({'message':'Incorrect credentials'}), 500)

@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('username', None)
    return redirect(url_for('welcome'))

@app.route('/book/<int:bookid>')
def book(bookid):
    return f'{bookid}'

@app.route ('/api')
def api():
    res = requests.get ('https://www.goodreads.com/book/review_counts.json', params = {"key":"bS9TJpeOW8gIGXR4CM9NFA", "isbns":"9781632168146"})
    #print(res.json()["books"][0]["average_rating"])
    if res.status_code == 404:
        print('The book was not found')
    else:
        print(f'The type of rating is {type(float(res.json()["books"][0]["average_rating"]))}')
    return res.text

def paginate(n, page):
    assert(0 < n)
    assert(0 < page <= n)

    # Build set of pages to display
    if n <= 10:
        pages = set(range(1, n + 1))
    else:
        pages = (set(range(1, 4))
                 | set(range(max(1, page - 2), min(page + 3, n + 1)))
                 | set(range(n - 2, n + 1)))

    last_page = 0
    pagination = []
    for p in sorted(pages):
        if p != last_page + 1: 
            pagination.append('...')
        else:
            pagination.append(p)
        last_page = p
    return pagination


app.secret_key = r"b'\xc7\xba\xde>?\x1e\xfd\x10\xc7\xf6\xf0\x11?\xec\xd2S\x9b\xe9\xaby{\x19\xbe-'"
if __name__ == "__main__":
    app.run()






