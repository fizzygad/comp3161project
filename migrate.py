import mysql.connector
from dotenv import load_dotenv
import os
import bcrypt

# Load environment variables
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT", 3306))
    )

def create_tables():
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor()
        
        # Create database if not exists (commented out since Railway provides one)
        # cursor.execute("CREATE DATABASE IF NOT EXISTS project")
        # cursor.execute("USE project")
        
        # Users table with password length increased for bcrypt hashes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INT PRIMARY KEY,
            email VARCHAR(50),
            pswrd VARCHAR(255),  -- Increased for bcrypt hashes
            username VARCHAR(50)
        """)
        
        # Roles table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS roles(
            user_id INT PRIMARY KEY,
            role VARCHAR(20),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        """)
        
        # Course table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS course (
            course_id INT PRIMARY KEY,
            course_name VARCHAR(100),
            description TEXT
        )""")
        
        # Enroll table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS enroll (
            user_id INT,
            course_id INT,
            enroll_date DATE,
            overall_grade VARCHAR(3),
            PRIMARY KEY (user_id, course_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (course_id) REFERENCES course(course_id)
        )""")
        
        # Teach table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS teach (
            user_id INT,
            course_id INT,
            teach_start_date DATE,
            PRIMARY KEY (user_id, course_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (course_id) REFERENCES course(course_id)
        )""")
        
        # Section table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS section (
            section_id INT PRIMARY KEY,
            course_id INT,
            section_title VARCHAR(100),
            section_desc TEXT,
            FOREIGN KEY (course_id) REFERENCES course(course_id)
        )""")
        
        # Item table
        cursor.execute("""
        CREATE TABLE if not exists item (
            item_id INT PRIMARY KEY,
            section_id INT,
            item_type VARCHAR(50),
            item_desc TEXT,
            FOREIGN KEY (section_id) REFERENCES section(section_id)
        )""")
        
        # Assignment table
        cursor.execute("""
        CREATE TABLE if not exists assignment (
            assignment_id INT PRIMARY KEY,
            course_id INT,
            title VARCHAR(100),
            max_score DECIMAL(5,2),
            due_date DATE,
            FOREIGN KEY (course_id) REFERENCES course(course_id)
        )""")
        
        # Submission table
        cursor.execute("""
        CREATE TABLE if not exists submission (
            submission_id INT PRIMARY KEY,
            user_id INT,
            file_url TEXT,
            submit_date DATE,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )""")
        
        # Receives table
        cursor.execute("""
        CREATE TABLE if not exists receives (
            submission_id INT,
            assignment_id INT,
            grade DECIMAL(5,2),
            PRIMARY KEY (submission_id, assignment_id),
            FOREIGN KEY (submission_id) REFERENCES submission(submission_id),
            FOREIGN KEY (assignment_id) REFERENCES assignment(assignment_id)
        )""")
        
        # Forum table
        cursor.execute("""
        CREATE TABLE if not exists forum (
            forum_id INT PRIMARY KEY,
            course_id INT,
            forum_title VARCHAR(100),
            forum_desc TEXT,
            time_created TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES course(course_id)
        )""")
        
        # Thread table
        cursor.execute("""
        CREATE TABLE if not exists thread (
            thread_id INT PRIMARY KEY,
            forum_id INT,
            content TEXT,
            FOREIGN KEY (forum_id) REFERENCES Forum(forum_id)
        )""")
        
        # Reply table
        cursor.execute("""
        CREATE TABLE if not exists reply (
            reply_id INT PRIMARY KEY,
            thread_id INT,
            content TEXT,
            FOREIGN KEY (thread_id) REFERENCES thread(thread_id)
        )""")
        
        # Post Thread table
        cursor.execute("""
        CREATE TABLE if not exists post_thread (
            user_id INT,
            thread_id INT,
            time_created TIMESTAMP,
            PRIMARY KEY (user_id, thread_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (thread_id) REFERENCES thread(thread_id)
        )""")
        
        # Post Reply table
        cursor.execute("""
        CREATE TABLE if not exists post_reply (
            user_id INT,
            reply_id INT,
            time_created TIMESTAMP,
            PRIMARY KEY (user_id, reply_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (reply_id) REFERENCES reply(reply_id)
        )""")
        
        # Calendar Event table
        cursor.execute("""
        CREATE TABLE if not exists calendarevent (
            event_id INT PRIMARY KEY,
            course_id INT,
            title VARCHAR(100),
            description TEXT,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            FOREIGN KEY (course_id) REFERENCES course(course_id)
        )""")
        
        # Create default admin user if not exists
        cursor.execute("SELECT * FROM users WHERE user_id = 1")
        if not cursor.fetchone():
            hashed_pw = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            cursor.execute(
                "INSERT INTO users (user_id, email, pswrd, username) VALUES (%s, %s, %s, %s)",
                (1, "admin@example.com", hashed_pw, "admin")
            )
            cursor.execute(
                "INSERT INTO roles (user_id, role) VALUES (%s, %s)",
                (1, "admin")
            )
        
        cnx.commit()
        print("Database tables created successfully")
        
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        if 'cnx' in locals():
            cnx.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnx' in locals() and cnx.is_connected():
            cnx.close()

if __name__ == '__main__':
    print("Initializing database...")
    create_tables()