from flask import Flask, request, render_template, redirect, session
import mysql.connector
import bcrypt

app = Flask(__name__)
app.secret_key = 'secret_key'

# MySQL connection configuration
db_config = {
    'host': 'python.mysql.database.azure.com',
    'user': 'samiksha',
    'password': 'Sneha@16',  # Replace with your MySQL password
    'database': 'database.db',             # Replace with your database name
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        # Create the 'login' table if it doesn't exist
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL
            )
        """)
        conn.commit()

        # Check if the email already exists in the database
        cursor.execute("SELECT * FROM login WHERE email = %s", (email,))
        existing_user = cursor.fetchone()
        if existing_user:
            error = 'Email is already registered.'
        else:
            # Create a new user and add it to the database
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute("INSERT INTO login (name, email, password) VALUES (%s, %s, %s)",
                           (name, email, hashed_password))
            conn.commit()
            
            return redirect('/login')

    return render_template('signup.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM login WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
            session['email'] = user[2]
            conn.close()
            return redirect('/dashboard')
        else:
            error = 'Please provide valid credentials to login.'

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        email = session['email']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM login WHERE email = %s", (email,))
        user = cursor.fetchall()
        conn.close()
        print("User:", user)  # Add this line for debugging
        return render_template('dashboard.html', user=user)
    
    return redirect('/login')



@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
