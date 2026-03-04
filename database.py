import sqlite3
from datetime import datetime

DB_NAME = 'disciplinary.db'

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            offense TEXT NOT NULL,
            teacher TEXT NOT NULL,
            student_class TEXT,
            date TEXT NOT NULL,
            detention_flag INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def add_record_to_db(student_name, offense, teacher, student_class=""):
    conn = get_db_connection()
    
    # Check for repeated offences (auto detention flag)
    cursor = conn.execute(
        'SELECT COUNT(*) FROM records WHERE student_name = ?', 
        (student_name,)
    )
    count = cursor.fetchone()[0]
    detention_flag = 1 if count >= 2 else 0
    
    conn.execute(
        '''INSERT INTO records (student_name, offense, teacher, student_class, date, detention_flag)
           VALUES (?, ?, ?, ?, ?, ?)''',
        (student_name, offense, teacher, student_class, datetime.now().strftime("%Y-%m-%d"), detention_flag)
    )
    conn.commit()
    conn.close()
    return detention_flag

def get_all_records():
    conn = get_db_connection()
    records = conn.execute('SELECT * FROM records ORDER BY date DESC').fetchall()
    conn.close()
    return records

def delete_record(record_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM records WHERE id = ?', (record_id,))
    conn.commit()
    conn.close()