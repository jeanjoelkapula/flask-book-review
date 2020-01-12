import os
import requests
import json, time
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
        index_start = time.time()
        ratings = []
        offset = (page * 15) -15
        book_count = db.execute("SELECT COUNT(*) FROM book;").first()[0]
        db.commit()
        if (book_count % 15) == 0:
            page_count = book_count / 15 
        else:
            page_count = int(book_count /15) + 1
        books = db.execute("SELECT * FROM book LIMIT 15 OFFSET :offset", {"offset":offset}).fetchall()
        for book in books:
            onsite_average_rating = get_onsite_average_rating(book.bookid)
            '''details = get_goodreads_book_details(book.isbn)
            if details is None:
                goodreads_average_rating = 0
            else:
                goodreads_average_rating = float(details["average_rating"])

            if ((onsite_average_rating != 0) and (goodreads_average_rating != 0)):
                average_rating = round (((onsite_average_rating + goodreads_average_rating) / 2), 1)
            elif ((onsite_average_rating == 0) or (goodreads_average_rating == 0)):
                average_rating = round ((onsite_average_rating + goodreads_average_rating), 1)
            mod = (goodreads_average_rating * 10) % 10'''
            
            ratings.append(onsite_average_rating)
            #if rating is not None:
        pagination = paginate(page_count, page)
        index_end = time.time()
        print('index duration', (index_end - index_start))
        return render_template('index.html', books = books, ratings = ratings, current_page = page, pagination = pagination, page_count = page_count, isSearch = False)
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

@app.route('/book/<int:bookid>')
def book(bookid):
    if 'username' in session:   
        book = db.execute("SELECT * FROM book WHERE bookid = :bookid", {"bookid":bookid}).first()
        db.commit()
        reviews = db.execute("SELECT A.firstname, A.lastname, R.rating, R.review FROM review R INNER JOIN useraccount A ON R.userid = A.userid WHERE bookid = :bookid;", {"bookid":bookid}).fetchall()
        db.commit()
        onsite_average_rating = get_onsite_average_rating(bookid)
        details = get_goodreads_book_details(book.isbn)
        print(onsite_average_rating)
        if details is None:
            goodreads_average_rating = 0
        else:
            goodreads_average_rating = float(details["average_rating"])

        if ((onsite_average_rating != 0) and (goodreads_average_rating != 0)):
            average_rating = round (((onsite_average_rating + goodreads_average_rating) / 2), 1)
        elif ((onsite_average_rating == 0) or (goodreads_average_rating == 0)):
            average_rating = round ((onsite_average_rating + goodreads_average_rating), 1)
        print(f'onsite: {onsite_average_rating} goodreads:{goodreads_average_rating}')
        return render_template('book.html', book = book, reviews = reviews, average_rating = onsite_average_rating, goodreads_reviews = details["work_reviews_count"], goodreads_rating=details["average_rating"]) 
    return redirect(url_for('login'))

@app.route('/review', methods = ["POST"])
def review():
    bookid = request.form.get('bookid')
    rating = int(request.form.get('rating'))
    review = request.form.get('review')

    exists = db.execute('SELECT COUNT(*) FROM review where userid = :userid AND bookid = :bookid', {"userid": session['userid'], "bookid":bookid}).first()[0]
    if exists == 0:
        db.execute('INSERT INTO review (bookid, userid, rating, review) VALUES (:bookid, :userid, :rating, :review);', {"bookid":bookid, "userid":session["userid"], "rating":rating, "review":review})
        db.commit()
        #return render_template('review.html', firstname = session["firstname"], lastname = session["lastname"], rating = rating, review = review) 
        return make_response(jsonify({'message': 'review submission successful', 'path':'/book/' + bookid}),200)
    else:
        return make_response(jsonify({'message': 'You may only submit one review per book'}), 500)

@app.route('/search', methods = ["POST"])
def search():
    search = request.form.get('search-bar')
    dictionary = get_search_result(search, 1)
        
    return render_template('index.html', books = dictionary['books'], ratings = dictionary['ratings'], current_page = 1, pagination = dictionary['pagination'], page_count = dictionary['page_count'], search = search, isSearch = True)

@app.route('/search_result', methods = ["GET"])
def search_result(search, page):
    dictionary = get_search_result(search, page)

    return render_template('index.html', books = dictionary['books'], ratings = dictionary['ratings'], current_page = 1, pagination = dictionary['pagination'], page_count = dictionary['page_count'], search = search, isSearch = True)
def get_search_result(search, page):
    ratings= []
    dictionary = dict()
    if (len(search.strip()) != 0):
        search = '%' + search + '%'
        offset = (page * 15) - 15
        books = db.execute('SELECT * FROM book WHERE (isbn ILIKE :search) OR (author ILIKE :search) OR (title ILIKE :search) LIMIT 15 OFFSET :offset', {"search":search, "offset":offset}).fetchall() 
        if (len(books) % 15) == 0:
            page_count = len(books) / 15 
        else:
            page_count = (len(books) / 15) + 1
        if type(page_count) == float:
            page_count = int(page_count)

        for book in books:
            onsite_average_rating = get_onsite_average_rating(book.bookid)
            details = get_goodreads_book_details(book.isbn)
            if details is None:
                goodreads_average_rating = 0
            else:
                goodreads_average_rating = float(details["average_rating"])

            if ((onsite_average_rating != 0) and (goodreads_average_rating != 0)):
                average_rating = round (((onsite_average_rating + goodreads_average_rating) / 2), 1)
            elif ((onsite_average_rating == 0) or (goodreads_average_rating == 0)):
                average_rating = round ((onsite_average_rating + goodreads_average_rating), 1)
            mod = (goodreads_average_rating * 10) % 10
            
            ratings.append(average_rating)
            #if rating is not None:
        pagination = paginate(page_count, 1)
    else:
        books = []
        page_count = 1
        pagination = paginate(page_count, 1)
    dictionary['books'] = books
    dictionary['ratings'] = ratings
    dictionary['page'] = page
    dictionary['pagination'] = pagination
    dictionary['page_count'] = page_count

    return dictionary

@app.route('/logout')
def logout():
    session.pop('userid', None)
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('username', None)
    return redirect(url_for('welcome'))


@app.route ('/api/<isbn>')
def api(isbn):
    book = db.execute('SELECT * from book WHERE isbn = :isbn', {"isbn":isbn}).first()
    db.commit()

    if book is None:
        return make_response(jsonify({'message': 'The book was not found'}), 404)
    else:
        return make_response(json.dumps(dict(book)), 200)

def get_onsite_average_rating(bookid):
    stars = db.execute("SELECT (SELECT COUNT (rating) from review WHERE bookid =4 and rating = 1) as stars_1," + 
        "(SELECT COUNT (rating) from review WHERE bookid =:bookid and rating = 2) as stars_2," +
        "(SELECT COUNT (rating) from review WHERE bookid =:bookid and rating = 3) as stars_3," + 
        "(SELECT COUNT (rating) from review WHERE bookid =:bookid and rating = 4) as stars_4," + 
        "(SELECT COUNT (rating) from review WHERE bookid =:bookid and rating = 5) as stars_5 " +
        "FROM review Limit 1;", {"bookid":bookid}).first()
                    
    stars_1 = stars.stars_1
    stars_2 = stars.stars_2
    stars_3 = stars.stars_3
    stars_4 = stars.stars_4
    stars_5 = stars.stars_5
    print(f'stars_1: {stars_1} stars_2:{stars_2} stars_3:{stars_3} stars_4:{stars_4} stars_5:{stars_5}')
    sum_result = (stars_1 + stars_2 + stars_3 + stars_4 + stars_4)
    if (sum_result != 0):
        onsite_average_rating = ((5 * stars_5) + (4 * stars_4) + (3 * stars_3) + (2 * stars_2) + (1 * stars_1)) / (stars_1 + stars_2 + stars_3 + stars_4 + stars_5)
    else:
        onsite_average_rating = 0
    return onsite_average_rating

def get_goodreads_book_details(isbn):
    res = requests.get ('https://www.goodreads.com/book/review_counts.json', params = {"key":"bS9TJpeOW8gIGXR4CM9NFA", "isbns":isbn})
    if res.status_code == 200:
        return res.json()["books"][0]
    else:
        return None 

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






