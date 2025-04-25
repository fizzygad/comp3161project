from flask import Flask, request, jsonify, make_response
import mysql.connector
import bcrypt
from dotenv import load_dotenv
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)

app.config['PROJECT_URL'] = 'mysql://UWI:Database1@localhost/project'

# def connectDB():
#     return mysql.connector.connect(
#         host='localhost',
#         user='UWI',
#         password='Database1',
#         database='project'
#     )
def connectDB():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='comp3161finalproj '
    )
    
app.config['SECRET_KEY'] = "your_secret_key_string"
    
# Token required decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check if token is in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401
        
        try:
            # Decode the token
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            
            # Get current user info
            cnx = connectDB()
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (data['username'],))
            current_user = cursor.fetchone()
            cursor.close()
            cnx.close()
            
            if not current_user:
                return jsonify({'message': 'User not found!'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Invalid token!'}), 401
            
        return f(current_user, *args, **kwargs)
    
    return decorated

@app.route("/")
def helloworld():
    return "</p>Hello</p>"

@app.route('/register_user', methods=['POST'])
@token_required
def register_user(current_user):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()
        content = request.json

        if not all(key in content for key in ['UserID', 'Email', 'Password', 'Username', 'Role']):
            return make_response({'Error': 'Missing required fields'}, 400)

        user_id = content['UserID']
        email = content['Email']
        password = content['Password']
        username = content['Username']
        role = content['Role']

        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password_bytes, salt)

        add_user = "INSERT INTO users (user_id, email, pswrd, username) VALUES (%s, %s, %s, %s)"
        user_data = (user_id, email, hashed_password, username)
        cursor.execute(add_user, user_data)

        add_role = "INSERT INTO roles (user_id, role) VALUES (%s, %s)"
        role_data = (user_id, role)
        cursor.execute(add_role, role_data)

        cnx.commit()
        return make_response({"Success": "User added"}, 201)

    except mysql.connector.IntegrityError as err:
        cnx.rollback()
        return make_response({'Error': f'Database error: {err}'}, 400)
    except Exception as e:
        cnx.rollback()
        print(f"An unexpected error occurred: {e}")
        return make_response({'Error': 'An unexpected error occurred'}, 500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()
    
@app.route('/login', methods=['POST'])
def login():
    try:
        cnx = connectDB()
        cursor = cnx.cursor(dictionary=True)
        content = request.json
        
        if not all(key in content for key in ['username', 'password']):
            return make_response({'Error': 'Missing username or password'}, 400)
            
        username = content['username']
        password = content['password']
        
        # Get user information
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        # Get user role
        if user:
            cursor.execute("SELECT role FROM roles WHERE user_id = %s", (user['user_id'],))
            role_row = cursor.fetchone()
            user_role = role_row['role'] if role_row else 'unknown'
        else:
            user_role = 'unknown'
        
        # Debug to check data types
        print(f"Password from request: {type(password)}")
        print(f"Stored password type: {type(user['pswrd']) if user else 'No user found'}")
        
        # Verify password - handling different possible types of stored password
        if user:
            stored_password = user['pswrd']
            # If stored password is bytes-like object already, use directly
            if isinstance(stored_password, bytes):
                password_match = bcrypt.checkpw(password.encode('utf-8'), stored_password)
            # If stored password is string, encode it
            else:
                password_match = bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8'))
            
            if password_match:
                # Generate token
                token = jwt.encode({
                    'username': username,
                    'user_id': user['user_id'],
                    'role': user_role,
                    'exp': datetime.utcnow() + timedelta(hours=24)  # Token expires in 24 hours
                }, app.config['SECRET_KEY'], algorithm="HS256")
                
                # Convert token to string if it's in bytes (depends on PyJWT version)
                if isinstance(token, bytes):
                    token = token.decode('utf-8')
                
                return jsonify({
                    'message': f"{username} has been logged in.",
                    'token': token,
                    'user_id': user['user_id'],
                    'role': user_role
                }), 200
        
        # Failed authentication
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        print(f"Login error: {e}")
        return jsonify({'error': 'An error has occurred'}), 500
    finally:
        cursor.close()
        cnx.close()

@app.route('/create_course', methods=['POST'])
@token_required
def create_course(current_user):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()
        
        cursor.execute("SELECT role FROM roles WHERE user_id = %s", (current_user['user_id'],))
        role = cursor.fetchone()
        if not role or role[0] not in ['admin']:
            return make_response({'Error': 'Unauthorized: Only admins can create courses'}, 403)
        
        content = request.json

        # Validate required fields
        if not all(key in content for key in ['CourseID', 'CourseName', 'Description']):
            return make_response({'Error': 'Missing required fields'}, 400)

        course_id = content['CourseID']
        course_name = content['CourseName']
        description = content['Description']

        # Insert into course table
        add_course = "INSERT INTO course (course_id, course_name, description) VALUES (%s, %s, %s)"
        course_data = (course_id, course_name, description)
        cursor.execute(add_course, course_data)

        cnx.commit()
        return make_response({"Success": "Course created"}, 201)

    except mysql.connector.IntegrityError as err:
        cnx.rollback()
        return make_response({'Error': f'Database error: {err}'}, 400)
    except Exception as e:
        cnx.rollback()
        print(f"An unexpected error occurred: {e}")
        return make_response({'Error': 'An unexpected error occurred'}, 500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

@app.route('/courses', methods=['GET'])
@token_required
def get_all_courses(current_user):
    try:
        cnx = connectDB()
        cursor = cnx.cursor(dictionary=True)

        query = "SELECT * FROM course"
        cursor.execute(query)
        courses = cursor.fetchall()

        return make_response({'Courses': courses}, 200)
    except Exception as e:
        print(f"Error retrieving courses: {e}")
        return make_response({'Error': 'Could not retrieve courses'}, 500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

@app.route('/courses/student/<string:user_id>', methods=['GET'])
@token_required
def get_courses_for_student(current_user, user_id):
    try:
        cnx = connectDB()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT c.course_id, c.course_name, c.description, e.enroll_date, e.overall_grade
            FROM course c
            JOIN enroll e ON c.course_id = e.course_id
            WHERE e.user_id = %s
        """
        cursor.execute(query, (user_id,))
        courses = cursor.fetchall()

        return make_response({'StudentCourses': courses}, 200)
    except Exception as e:
        print(f"Error retrieving student courses: {e}")
        return make_response({'Error': 'Could not retrieve student courses'}, 500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

@app.route('/courses/lecturer/<string:user_id>', methods=['GET'])
@token_required
def get_courses_by_lecturer(user_id):
    try:
        cnx = connectDB()
        cursor = cnx.cursor(dictionary=True)

        query = """
            SELECT c.course_id, c.course_name, c.description, t.teach_start_date
            FROM course c
            JOIN teach t ON c.course_id = t.course_id
            WHERE t.user_id = %s
        """
        cursor.execute(query, (user_id,))
        courses = cursor.fetchall()

        return make_response({'LecturerCourses': courses}, 200)
    except Exception as e:
        print(f"Error retrieving lecturer courses: {e}")
        return make_response({'Error': 'Could not retrieve lecturer courses'}, 500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

@app.route('/assign_lecturer', methods=['POST'])
@token_required
def assign_lecturer(current_user):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()
        
        cursor.execute("SELECT role FROM roles WHERE user_id = %s", (current_user['user_id'],))
        role = cursor.fetchone()
        if not role or role[0] not in ['admin']:
            return make_response({'Error': 'Unauthorized: Only admins can create courses'}, 403)
        
        content = request.json
        if not all(k in content for k in ['UserID', 'CourseID', 'TeachStartDate']):
            return make_response({'Error': 'Missing required fields'}, 400)

        user_id = content['UserID']
        course_id = content['CourseID']
        teach_start_date = content['TeachStartDate']

        # Check if this course already has a lecturer
        check_query = "SELECT * FROM teach WHERE course_id = %s"
        cursor.execute(check_query, (course_id,))
        if cursor.fetchone():
            return make_response({'Error': 'This course already has a lecturer assigned'}, 400)

        # Assign lecturer
        insert_query = "INSERT INTO teach (user_id, course_id, teach_start_date) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (user_id, course_id, teach_start_date))

        cnx.commit()
        return make_response({'Success': 'Lecturer assigned to course'}, 201)
    except Exception as e:
        cnx.rollback()
        print(f"Error assigning lecturer: {e}")
        return make_response({'Error': 'Could not assign lecturer'}, 500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

@app.route('/register_student_course', methods=['POST'])
@token_required
def register_student_for_course(current_user):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()

        content = request.json
        if not all(k in content for k in ['UserID', 'CourseID', 'EnrollDate']):
            return make_response({'Error': 'Missing required fields'}, 400)

        user_id = content['UserID']
        course_id = content['CourseID']
        enroll_date = content['EnrollDate']

        # Prevent duplicate enrollment
        check_query = "SELECT * FROM enroll WHERE user_id = %s AND course_id = %s"
        cursor.execute(check_query, (user_id, course_id))
        if cursor.fetchone():
            return make_response({'Error': 'Student already enrolled in this course'}, 400)

        insert_query = """
            INSERT INTO enroll (user_id, course_id, enroll_date, overall_grade)
            VALUES (%s, %s, %s, NULL)
        """
        cursor.execute(insert_query, (user_id, course_id, enroll_date))

        cnx.commit()
        return make_response({'Success': 'Student registered for course'}, 201)
    except Exception as e:
        cnx.rollback()
        print(f"Error registering student: {e}")
        return make_response({'Error': 'Could not register student for course'}, 500)
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()

@app.route('/get_members/<int:course_id>', methods=['GET'])
@token_required
def get_members(current_user, course_id):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()

        # Get students
        cursor.execute("""
            SELECT u.user_id, u.username, 'Student' as role 
            FROM enroll e
            JOIN users u ON e.user_id = u.user_id
            WHERE e.course_id = %s
        """, (course_id,))
        students = cursor.fetchall()

        # Get lecturers
        cursor.execute("""
            SELECT u.user_id, u.username, 'Lecturer' as role 
            FROM teach t
            JOIN users u ON t.user_id = u.user_id
            WHERE t.course_id = %s
        """, (course_id,))
        lecturers = cursor.fetchall()

        members = students + lecturers
        return jsonify({'members': members}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals() and cnx.is_connected(): cnx.close()

@app.route('/calendar_events/course/<int:course_id>', methods=['GET'])
@token_required
def get_calendar_events_for_course(current_user, course_id):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT * FROM CalendarEvent WHERE course_id = %s
        """, (course_id,))
        events = cursor.fetchall()
        return jsonify({'events': events}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals() and cnx.is_connected(): cnx.close()

@app.route('/calendar_events/student', methods=['GET'])
@token_required
def get_calendar_events_for_student_by_date(current_user):
    user_id = request.args.get('user_id')
    date = request.args.get('date')  # Format: YYYY-MM-DD

    try:
        cnx = connectDB()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT ce.* 
            FROM CalendarEvent ce
            JOIN enroll e ON ce.course_id = e.course_id
            WHERE e.user_id = %s 
              AND DATE(ce.start_date) = %s
        """, (user_id, date))
        events = cursor.fetchall()
        return jsonify({'events': events}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals() and cnx.is_connected(): cnx.close()

@app.route('/forums/<int:course_id>', methods=['GET'])
@token_required
def get_forums_by_course(current_user, course_id):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT forum_id, forum_title, forum_desc, time_created 
            FROM forum 
            WHERE course_id = %s
        """, (course_id,))
        forums = cursor.fetchall()
        return jsonify({'forums': forums}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals() and cnx.is_connected(): cnx.close()

@app.route('/forums/create', methods=['POST'])
@token_required
def create_forum(current_user):
    data = request.get_json()
    course_id = data['Course ID']
    forum_title = data['Forum Title']
    forum_desc = data['Forum Description']

    try:
        cnx = connectDB()
        cursor = cnx.cursor()

        cursor.execute("SELECT * FROM course WHERE course_id = %s", (course_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Course not found'}), 404
        
        forum_prefix="F"                            #forum prefix makes forums easily identifiable
        forum_id=0
        cursor.execute("""SELECT COUNT(%s) FROM forum WHERE course_id = %s""", (forum_id, course_id))
        idcount=cursor.fetchone()[0]+1          #course forum number increases by 1 because of insertion
        forum_id= (f"{forum_prefix}{idcount:02d}-{course_id}") #prefix + course forum number + courseid 
        
        cursor.execute("""
            INSERT INTO forum (forum_id, course_id, forum_title, forum_desc, time_created)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (forum_id, course_id, forum_title, forum_desc))
        cnx.commit()
        return jsonify({'message': 'Forum created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals() and cnx.is_connected(): cnx.close()
        
@app.route('/threads/<forum_id>', methods=['GET'])
@token_required
def get_threads_by_forum(current_user, forum_id):
    try:
        cnx = connectDB()
        cursor = cnx.cursor()
        cursor.execute("""
            SELECT *
            FROM thread 
            WHERE forum_id = %s
        """, (forum_id,))
        threads = cursor.fetchall()
        return jsonify({'threads': threads}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals() and cnx.is_connected(): cnx.close()

@app.route('/threads/create', methods=['POST'])
@token_required
def create_thread(current_user):
    data = request.get_json()
    forum_id = data['Forum ID']
    content = data['Thread Content']

    try:
        cnx = connectDB()
        cursor = cnx.cursor()

        cursor.execute("SELECT * FROM forum WHERE forum_id = %s", (forum_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Forum not found'}), 404
        
        thread_prefix="T"                            #thread prefix makes forums easily identifiable
        thread_id=0
        cursor.execute("""SELECT COUNT(%s) FROM thread WHERE forum_id = %s""", (thread_id, forum_id))
        idcount=cursor.fetchone()[0]+1          #course forum number increases by 1 because of insertion
        thread_id= (f"{thread_prefix}{idcount:02d}-{forum_id}") #prefix + course thread number + forumid 
        
        cursor.execute("""
            INSERT INTO thread (thread_id, forum_id, content)
            VALUES (%s, %s, %s)
        """, (thread_id, forum_id, content))
        cnx.commit()
        return jsonify({'message': 'Thread created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'cnx' in locals() and cnx.is_connected(): cnx.close()


if __name__ == '__main__':
    app.run(debug=True, port=5000)