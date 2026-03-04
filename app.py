from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import init_db, add_record_to_db, get_all_records, delete_record
from database import init_db, add_record_to_db, get_all_records, delete_record as delete_from_db
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Load predefined users
def load_users():
    with open('users.json', 'r') as f:
        return json.load(f)['users']

USERS = load_users()

# Initialize database on startup
init_db()

# Login Required Decorator
def login_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Admin Required Decorator
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if session.get('role') != 'admin':
            flash('Admin access required.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check credentials
        for user in USERS:
            if user['username'] == username and user['password'] == password:
                session['username'] = username
                session['role'] = user['role']
                flash(f'Welcome, {username}!', 'success')
                return redirect(url_for('dashboard'))
        
        flash('Invalid credentials.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    records = get_all_records()
    return render_template('dashboard.html', records=records, username=session['username'], role=session['role'])

@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_record():
    if request.method == 'POST':
        student_name = request.form['student_name']
        offense = request.form['offense']
        student_class = request.form.get('student_class', '')
        
        detention_flag = add_record_to_db(student_name, offense, session['username'], student_class)
        if detention_flag:
            flash(f'⚠️ DETENTION FLAGGED: {student_name} has repeated offences!', 'warning')
        else:
            flash('Record added successfully!', 'success')
        
        return redirect(url_for('dashboard'))
    
    return render_template('add_record.html')

@app.route('/delete/<int:record_id>')
@login_required
@admin_required
def delete_record(record_id):
    delete_from_db(record_id)
    flash('Record deleted.', 'success')
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/api/records')
@login_required
def api_get_records():
    """API endpoint to fetch records as JSON"""
    records = get_all_records()
    return jsonify([{
        'id': record['id'],
        'student_name': record['student_name'],
        'student_class': record['student_class'],
        'offense': record['offense'],
        'teacher': record['teacher'],
        'date': record['date'],
        'detention_flag': record['detention_flag']
    } for record in records])

if __name__ == '__main__':
    app.run(debug=True)