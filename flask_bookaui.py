
from flask import Flask, request, session, redirect, url_for, render_template_string
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf.csrf import CSRFProtect, generate_csrf
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Clé secrète sécurisée
csrf = CSRFProtect(app)

DATABASE = 'booksAUI.db'

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL)""")

    c.execute("""CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        content TEXT NOT NULL)""")

    c.execute("SELECT * FROM users WHERE username=?", ('studentaui',))
    if not c.fetchone():
        hashed_pwd = generate_password_hash('welcome')
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", ('studentaui', hashed_pwd))

    c.execute("SELECT * FROM books")
    if not c.fetchone():
        books = [
            ("Pride and Prejudice", "Jane Austen", "Content of Pride and Prejudice..."),
            ("1984", "George Orwell", "Content of 1984..."),
            ("To Kill a Mockingbird", "Harper Lee", "Content of To Kill a Mockingbird...")
        ]
        c.executemany("INSERT INTO books (title, author, content) VALUES (?, ?, ?)", books)

    conn.commit()
    conn.close()

init_db()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    csrf_token = generate_csrf()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password_hash(user[2], password):
            session['username'] = username
            return redirect(url_for('home'))
        else:
            error = "Invalid credentials"

    return render_template_string(login_template, error=error, csrf_token=csrf_token)

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, author FROM books")
    books = cursor.fetchall()
    conn.close()
    return render_template_string(home_template, username=session['username'], books=books)

@app.route('/book/<int:book_id>')
def book(book_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT title, author, content FROM books WHERE id = ?", (book_id,))
    book = cursor.fetchone()
    conn.close()
    if not book:
        return "<h3>Book not found!</h3><a href='/'>Back</a>"
    return render_template_string(book_template, title=book[0], author=book[1], content=book[2])

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


# Template definitions
login_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login | BookAUI</title>
    <style>
        :root {
            --primary: #7F5AF0;
            --primary-dark: #6C4BD1;
            --secondary: #2CB67D;
            --text: #16161A;
            --light: #FFFFFE;
            --gray: #94A1B2;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        body {
            background: linear-gradient(135deg, #0F0E17, #1E1E2E);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 2rem;
        }
        
        .login-card {
            background: var(--light);
            border-radius: 16px;
            padding: 3rem;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.25);
            transition: transform 0.3s ease;
        }
        
        .login-card:hover {
            transform: translateY(-5px);
        }
        
        .logo {
            text-align: center;
            margin-bottom: 2.5rem;
        }
        
        .logo h1 {
            color: var(--primary);
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .logo p {
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        .form-group {
            margin-bottom: 1.5rem;
        }
        
        .form-group label {
            display: block;
            color: var(--text);
            font-size: 0.9rem;
            font-weight: 500;
            margin-bottom: 0.5rem;
        }
        
        .form-control {
            width: 100%;
            padding: 0.75rem 1rem;
            border: 2px solid #E2E8F0;
            border-radius: 8px;
            font-size: 1rem;
            transition: all 0.3s;
        }
        
        .form-control:focus {
            border-color: var(--primary);
            outline: none;
            box-shadow: 0 0 0 3px rgba(127, 90, 240, 0.2);
        }
        
        .btn {
            width: 100%;
            padding: 0.75rem;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .btn:hover {
            background: var(--primary-dark);
        }
        
        .error-message {
            color: #EF4444;
            text-align: center;
            margin-bottom: 1.5rem;
            font-size: 0.9rem;
            padding: 0.75rem;
            background: #FEE2E2;
            border-radius: 8px;
        }
        
        .footer-text {
            text-align: center;
            margin-top: 1.5rem;
            color: var(--gray);
            font-size: 0.85rem;
        }
        
        .footer-text a {
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo">
            <h1>BookAUI</h1>
            <p>Discover your next favorite book</p>
        </div>
        
        {% if error %}
        <div class="error-message">{{ error }}</div>
        {% endif %}
        
           <form method="POST" action="/login">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <div class="form-group">
                <label for="username">Username</label>
                <input class="form-control" type="text" name="username" id="username" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input class="form-control" type="password" name="password" id="password" required>
            </div>
            <button class="btn" type="submit">Login</button>
        </form>
        <p class="footer-text">Don't have an account? <a href="#">Sign up</a></p>
    </div>
</body>
</html>
'''

home_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Books | BookAUI</title>
    <style>
        :root {
            --primary: #7F5AF0;
            --primary-dark: #6C4BD1;
            --secondary: #2CB67D;
            --text: #16161A;
            --light: #FFFFFE;
            --gray: #94A1B2;
            --bg: #F8FAFC;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        body {
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 3rem;
            padding-bottom: 1rem;
            border-bottom: 1px solid #E2E8F0;
        }
        
        .brand {
            display: flex;
            align-items: center;
        }
        
        .brand h1 {
            color: var(--primary);
            font-size: 1.75rem;
        }
        
        .logout-btn {
            padding: 0.5rem 1.25rem;
            background: var(--primary);
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
        }
        
        .logout-btn:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
        
        .welcome-section {
            margin-bottom: 3rem;
        }
        
        .welcome-section h2 {
            font-size: 1.5rem;
            color: var(--text);
            margin-bottom: 0.5rem;
        }
        
        .welcome-section p {
            color: var(--gray);
        }
        
        .books-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        
        .books-header h3 {
            font-size: 1.25rem;
            color: var(--text);
        }
        
        .books-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 1.5rem;
        }
        
        .book-card {
            background: var(--light);
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
            border: 1px solid #E2E8F0;
        }
        
        .book-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            border-color: var(--primary);
        }
        
        .book-title {
            font-size: 1.1rem;
            font-weight: 600;
            color: var(--primary);
            margin-bottom: 0.5rem;
            display: block;
            text-decoration: none;
        }
        
        .book-author {
            color: var(--gray);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .book-meta {
            display: flex;
            align-items: center;
            color: var(--gray);
            font-size: 0.8rem;
            margin-top: 1rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1.5rem;
            }
            
            .books-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <h1>BookAUI</h1>
            </div>
            <a href="{{ url_for('logout') }}" class="logout-btn">Logout</a>
        </header>
        
        <div class="welcome-section">
            <h2>Welcome back!</h2>
            <p>Continue your reading journey with these amazing books</p>
        </div>
        
        <div class="books-header">
            <h3>Your Library</h3>
        </div>
        
        <div class="books-grid">
            {% for id, title, author in books %}
            <div class="book-card">
                <a href="{{ url_for('book', book_id=id) }}" class="book-title">{{ title }}</a>
                <div class="book-author">by {{ author }}</div>
                <div class="book-meta">
                    <span>Available</span>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''

book_template = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} | BookAUI</title>
    <style>
        :root {
            --primary: #7F5AF0;
            --primary-dark: #6C4BD1;
            --secondary: #2CB67D;
            --text: #16161A;
            --light: #FFFFFE;
            --gray: #94A1B2;
            --bg: #F8FAFC;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        body {
            background-color: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .back-link {
            display: inline-flex;
            align-items: center;
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
            margin-bottom: 2rem;
        }
        
        .back-link svg {
            margin-right: 0.5rem;
        }
        
        .back-link:hover {
            text-decoration: underline;
        }
        
        .book-cover {
            width: 100%;
            max-width: 300px;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.1);
            margin: 0 auto 2rem;
            display: block;
        }
        
        .book-header {
            margin-bottom: 2rem;
            text-align: center;
        }
        
        .book-title {
            font-size: 2rem;
            color: var(--text);
            margin-bottom: 0.5rem;
            line-height: 1.2;
        }
        
        .book-author {
            color: var(--primary);
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }
        
        .book-meta {
            display: flex;
            justify-content: center;
            gap: 1.5rem;
            margin-bottom: 2rem;
            color: var(--gray);
            font-size: 0.9rem;
        }
        
        .book-description {
            background: var(--light);
            padding: 2rem;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            margin-bottom: 2rem;
        }
        
        .book-description p {
            margin-bottom: 1rem;
        }
        
        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .btn {
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn-primary {
            background: var(--primary);
            color: white;
            border: none;
        }
        
        .btn-primary:hover {
            background: var(--primary-dark);
            transform: translateY(-2px);
        }
        
        .btn-outline {
            background: transparent;
            color: var(--primary);
            border: 2px solid var(--primary);
        }
        
        .btn-outline:hover {
            background: rgba(127, 90, 240, 0.1);
            transform: translateY(-2px);
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 1.5rem;
            }
            
            .book-title {
                font-size: 1.75rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <a href="{{ url_for('home') }}" class="back-link">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            Back to Books
        </a>
        
        <div class="book-header">
            <h1 class="book-title">{{ title }}</h1>
            <div class="book-author">by {{ author }}</div>
        </div>
        
        <div class="book-description">
            <p>Orgueil et Préjugés (Pride and Prejudice) est un roman de la femme de lettres anglaise Jane Austen paru en 1813. Il est considéré comme l'une de ses œuvres les plus significatives et est aussi la plus connue du grand public.</p>
            
            <p>The news that a wealthy young gentleman named Charles Bingley has rented the manor of Netherfield Park causes a great stir in the nearby village of Longbourn, especially in the Bennet household. The Bennets have five unmarried daughters—from oldest to youngest, Jane, Elizabeth, Mary, Kitty, and Lydia—and Mrs. Bennet is desperate to see them all married.</p>
            
            <p>After Mr. Bennet pays a social visit to Mr. Bingley, the Bennets attend a ball at which Mr. Bingley is present. He is taken with Jane and spends much of the evening dancing with her. His close friend, Mr. Darcy, is less pleased with the evening and haughtily refuses to dance with Elizabeth, which makes everyone view him as arrogant and obnoxious.</p>
        </div>
        
        <div class="action-buttons">
            <a href="#" class="btn btn-primary">Read Now</a>
            <a href="#" class="btn btn-outline">Add to Library</a>
        </div>
    </div>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, port=30083)


