from flask import Flask, request, jsonify, make_response
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

if __name__ == '__main__':
    app.run()