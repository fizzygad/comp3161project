from flask import Flask, request, jsonify, make_response
import mysql.connector
import bcrypt

app = Flask(__name__)

app.config['PROJECT_URL'] = 'mysql://UWI:Database1@localhost/project'

@app.route("/")
def helloworld():
    return "</p>Hello</p>"

def connectDB():
    return mysql.connector.connect(host='localhost', user='root', password='root', database='comp3161finalproj')

@app.route('/register_user', methods=['POST'])
def register_user():
    try:
        # cnx = mysql.connector.connect(host='localhost', user='UWI', password='Database1', database='project')
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

@app.route('/login', methods=['GET'])
def login():
    try:
        cnx = mysql.connector.connect(host='localhost', user='UWI', password='Database1', database='project')
        cursor = cnx.cursor()
        content = request.json
        username=content['Username']
        pswrd=content['Password']
        query = "SELECT username FROM users WHERE username = %s AND pswrd = %s"
        cursor.execute(query, (username, pswrd))
        row = cursor.fetchone()
        cursor.close()
        cnx.close()
        if row:
            return make_response({'message': f"{username} has been logged in."}, 200)
        else:
            return make_response({'error': 'Unable to login'}, 400)
    except:
        return make_response({'error': 'An error has occured'}, 400)
    

@app.route('/create_course', methods=['POST'])
def create_course():
    try:
        cnx = connectDB()
        cursor = cnx.cursor()
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
def get_all_courses():
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
def get_courses_for_student(user_id):
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
def assign_lecturer():
    try:
        cnx = connectDB()
        cursor = cnx.cursor()

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
def register_student_for_course():
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
def get_members(course_id):
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

@app.route('/calendar_events/course/<int:course_id>', methods=['GET'])
def get_calendar_events_for_course(course_id):
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

@app.route('/calendar_events/student', methods=['GET'])
def get_calendar_events_for_student_by_date():
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

@app.route('/forums/<int:course_id>', methods=['GET'])
def get_forums_by_course(course_id):
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

@app.route('/forums/create', methods=['POST'])
def create_forum():
    data = request.get_json()
    course_id = data['course_id']
    forum_title = data['forum_title']
    forum_desc = data['forum_desc']

    try:
        cnx = connectDB()
        cursor = cnx.cursor()

        cursor.execute("SELECT * FROM course WHERE course_id = %s", (course_id,))
        if cursor.fetchone() is None:
            return jsonify({'error': 'Course not found'}), 404

        cursor.execute("""
            INSERT INTO forum (forum_id, course_id, forum_title, forum_desc, time_created)
            VALUES (NULL, %s, %s, %s, CURRENT_TIMESTAMP)
        """, (course_id, forum_title, forum_desc))
        cnx.commit()
        return jsonify({'message': 'Forum created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/threads/<int:forum_id>', methods=['GET'])
def get_threads_by_forum(forum_id):
    try:
        conn = connectDB()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT thread_id, content 
            FROM thread 
            WHERE forum_id = %s
        """, (forum_id,))
        threads = cursor.fetchall()
        return jsonify({'threads': threads}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/threads/create', methods=['POST'])
def create_thread():
    data = request.get_json()
    forum_id = data['forum_id']
    user_id = data['user_id']
    title = data['title']
    post_content = data['content']

    try:
        conn = connectDB()
        cursor = conn.cursor()

        # Insert the thread
        cursor.execute("""
            INSERT INTO thread (thread_id, forum_id, content) 
            VALUES (NULL, %s, %s)
        """, (forum_id, f"Title: {title}\n\n{post_content}"))
        
        thread_id = cursor.lastrowid  # Get inserted thread ID

        # Register the user as the poster
        cursor.execute("""
            INSERT INTO post_thread (user_id, thread_id, time_created) 
            VALUES (%s, %s, CURRENT_TIMESTAMP)
        """, (user_id, thread_id))

        conn.commit()
        return jsonify({'message': 'Thread created successfully', 'thread_id': thread_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/replies/create', methods=['POST'])
def add_reply():
    data = request.get_json()
    user_id = data['user_id']
    content = data['content']
    parent_type = data['parent_type']  # "thread" or "reply"
    parent_id = data['parent_id']

    try:
        conn = connectDB()
        cursor = conn.cursor()

        if parent_type == "thread":
            # Reply to thread
            cursor.execute("""
                INSERT INTO reply (reply_id, thread_id, content) 
                VALUES (NULL, %s, %s)
            """, (parent_id, content))
            reply_id = cursor.lastrowid
        elif parent_type == "reply":
            # Reply to a reply (nested)
            # First get the thread_id of the parent reply
            cursor.execute("""
                SELECT thread_id FROM reply 
                JOIN thread USING(thread_id)
                WHERE reply_id = %s
            """, (parent_id,))
            result = cursor.fetchone()
            if not result:
                return jsonify({'error': 'Parent reply not found'}), 404
            thread_id = result[0]

            cursor.execute("""
                INSERT INTO reply (reply_id, thread_id, content) 
                VALUES (NULL, %s, %s)
            """, (thread_id, content))
            reply_id = cursor.lastrowid
        else:
            return jsonify({'error': 'Invalid parent_type'}), 400

        # Register who made the reply
        cursor.execute("""
            INSERT INTO post_reply (user_id, reply_id, time_created) 
            VALUES (%s, %s, CURRENT_TIMESTAMP)
        """, (user_id, reply_id))

        conn.commit()
        return jsonify({'message': 'Reply posted successfully', 'reply_id': reply_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5000, debug=True)