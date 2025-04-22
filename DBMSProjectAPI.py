from flask import Flask, request, jsonify, make_response
from datetime import date
import mysql.connector

app = Flask(__name__)

app.config['PROJECT_URL'] = 'mysql://UWI:Database1@localhost/project'

@app.route("/")
def helloworld():
    return "</p>Hello</p>"

@app.route('/register_user', methods=['POST'])
def register_user():
    try:
        cnx = mysql.connector.connect(host='localhost', user='UWI', password='Database1', database='project')
        cursor = cnx.cursor()
        content = request.json
        user_id = content['UserID']
        email = content['Email']
        pswrd = content['Password']
        username = content['Username']
        role = content['Role']
        cursor.execute(f"INSERT INTO users VALUES('{user_id}','{email}','{pswrd}','{username}')")
        cursor.execute(f"INSERT INTO roles VALUES('{user_id}','{role}')")
        cnx.commit()
        cursor.close()
        cnx.close()
        return make_response({"Success" : "User added"}, 201)
    except Exception as e:
        print(e)
        return make_response({'Error': 'An error has occured'}, 400)

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

@app.route('/create_course/<user_id>', methods=['POST'])
def create_course(user_id):
    try:
        cnx = mysql.connector.connect(host='localhost', user='UWI', password='Database1', database='project')
        cursor = cnx.cursor()
        content = request.json
        course_id=content['Course ID']
        course_name=content['Course Name']
        description=content['Description']
        cursor.execute(f"Select role from roles WHERE user_id={user_id}")
        row=cursor.fetchone()
        if row and row[0].lower()=="admin":
            cursor.execute(f"INSERT INTO course VALUES('{course_id}','{course_name}','{description}')")
            response=make_response({"success" : "Course created"}, 202)
        else:
            response=make_response({"error":"Only authorized personnel can create a course"},403)
        cnx.commit()
        cursor.close()
        return response
    except Exception as e:
        return make_response({'error': str(e)}, 400)
    
@app.route('/retrieve_courses/', defaults={'user_id': None}, methods=['GET'])
@app.route('/retrieve_courses/<user_id>', methods=['GET'])
def retrieve_courses(user_id):
    try:
        cnx = mysql.connector.connect(host='localhost', user='UWI', password='Database1', database='project')
        cursor = cnx.cursor()
        if not user_id:
            cursor.execute('SELECT * FROM course;')
            course_list = []
            for courseid, coursename, description in cursor:
                courses = {}
                courses['Course ID'] = courseid
                courses['Course Name'] = coursename
                courses['Description'] = description
                course_list.append(courses)
            cursor.close()
            cnx.close()
            return make_response(course_list), 200
        elif user_id.isdigit():
            cursor.execute(f"SELECT role FROM roles WHERE user_id = '{user_id}'")
            row=cursor.fetchone()
            if row and row[0].lower()=="student":
                cursor.execute(f"SELECT e1.user_id, e1.course_id, c1.course_name FROM enroll as e1 JOIN course as c1 WHERE e1.course_id=c1.course_id AND e1.user_id='{user_id}';")
                student_courses=[]
                for userid, courseid, coursename in cursor:
                    stuinfo = {}
                    stuinfo['User ID'] = userid
                    stuinfo['Course ID'] = courseid
                    stuinfo['Course Name'] = coursename
                    student_courses.append(stuinfo)
                cursor.close()
                cnx.close()
                return make_response(student_courses), 200
            elif row and row[0].lower()=="lecturer":
                cursor.execute(f"SELECT t1.user_id, t1.course_id, c1.course_name FROM teach as t1 JOIN course as c1 WHERE t1.course_id=c1.course_id AND t1.user_id='{user_id}';")
                lecturer_courses=[]
                for userid, courseid, coursename in cursor:
                    lecinfo = {}
                    lecinfo['User ID'] = userid
                    lecinfo['Course ID'] = courseid
                    lecinfo['Course Name'] = coursename
                    lecturer_courses.append(lecinfo)
                cursor.close()
                cnx.close()
                return make_response(lecturer_courses), 200
        else:
            return make_response({'error': 'User not found'}, 400)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

@app.route('/registerfor_course/<user_id>', methods=['POST'])
def registerfor_course(user_id):
    try:
        cnx = mysql.connector.connect(host='localhost', user='UWI', password='Database1', database='project')
        cursor = cnx.cursor()
        cursor.execute(f"Select role from roles WHERE user_id={user_id}")
        row=cursor.fetchone()
        if row and row[0].lower()=="student":
            content = request.json
            course_id=content['Course ID']
            enroll_date= date.today()
            overall_grade=0
            cursor.execute(f"SELECT course_name FROM course WHERE course_id = '{course_id}'")
            course_name=cursor.fetchone()
            if course_name is None:
                response=make_response({"error": "Course Not Found"}, 403)
            else:
                cursor.execute(f"INSERT INTO enroll VALUES('{user_id}','{course_id}','{enroll_date}','{overall_grade}')")
                course_name=course_name[0]
                response=make_response({"success" : f"You are now a member of the '{course_name}' course"}, 202)
        else:
            response=make_response({"error":"Only students can register for courses"}, 403)
        cnx.commit()
        cursor.close()
        return response
    except Exception as e:
        return make_response({'error': str(e)}, 400)
    
@app.route('/retrieve_members/<course_id>', methods=['GET'])
def retrieve_members(course_id):
    try:
        cnx = mysql.connector.connect(host='localhost', user='UWI', password='Database1', database='project')
        cursor = cnx.cursor()
        if course_id.isdigit():
            cursor.execute(f"SELECT course_name FROM course WHERE course_id = '{course_id}'")
            course_name=cursor.fetchone()
            if course_name is None:
                return make_response({"error": "Course Not Found"}, 403)
            else:
                cursor.execute(f"SELECT e.user_id, r.role FROM enroll e JOIN roles r WHERE e.user_id = r.user_id AND e.course_id = '{course_id}' UNION SELECT t.user_id, r.role FROM teach t JOIN roles r WHERE t.user_id = r.user_id AND t.course_id = '{course_id}'")
                member_list=[]
                for userid, role in cursor:
                    memberinfo = {}
                    memberinfo['User ID'] = userid
                    memberinfo['Role'] = role
                    member_list.append(memberinfo)
                cursor.close()
                cnx.close()
                return make_response(member_list), 200
        else:
            return make_response({'error': 'Invalid Course ID'}, 400)
    except Exception as e:
        return make_response({'error': str(e)}, 400)

if __name__ == '__main__':
    app.run(port=5000, debug=True)