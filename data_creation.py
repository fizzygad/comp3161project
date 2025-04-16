from faker import Faker
import mysql.connector
import pandas as pd
import random
import datetime

mydb = mysql.connector.connect(
    host='localhost',
    user='UWI',
    password='Database1',
    database='project'
)

mycursor=mydb.cursor()
mycursor.execute("SHOW TABLES")





Courses=pd.read_excel('courses.xlsx')
Courses=Courses.values.tolist()

random.seed(0)
Faker.seed(0)
fake=Faker()

users = [(fake.bothify('#########'),fake.ascii_free_email(),fake.password(),fake.first_name()+fake.last_name(),) for i in range(100050)]
print(users[0])
print(users[59])

roles=[]
for i in range(len(users)):
  if i<50:
    role="Lecturer"
  else:
    role="Student"
  roles.append((users[i][0],role))

print(roles[0])
print(roles[59])


courses = [(fake.bothify('#######'), Courses[i][0], Courses[i][1]) for i in range(200)]

print(courses[0])

def randomdate(start,end):
    start_date = datetime.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = datetime.datetime.strptime(end, "%Y-%m-%d").date()

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days

    random_number_of_days = random.randrange(days_between_dates + 1)

    random_date = start_date + datetime.timedelta(days=random_number_of_days)

    return(random_date.strftime("%Y-%m-%d"))


enrollments = []

for user in roles:
    if user[1]=="Student":
        enrolled_courses = random.sample(courses, random.randint(3, 5))
        for course in enrolled_courses:
            grade = random.randint(50, 100)
            date=randomdate("2023-7-1","2023-9-30")
            enrollments.append((user[0], course[0], date , grade))

chunks=[enrollments[i:i + 100146] for i in range(0, len(enrollments), 100146)]
enr0=chunks[0]
enr1=chunks[1]
enr2=chunks[2]
enr3=chunks[3]

teaches=[]
for user in roles:
    if user[1]=="Lecturer":
        taught_courses = random.sample(courses, random.randint(1, 4))
        for course in taught_courses:
            date=randomdate("2023-9-1","2023-9-30")
            teaches.append((user[0],course[0],date))

print(teaches[0])



with open("role_insert.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO roles (user_id, role) VALUES\n")
    f.write(",\n".join(f"('{r[0]}', '{r[1]}')" for r in roles) + ";\n\n")

with open("user_insert.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO users (user_id, email, pswrd, username) VALUES\n")
    f.write(",\n".join(f"('{u[0]}', '{u[1]}', '{u[2]}', '{u[3]}')" for u in users) + ";\n\n")

with open("course_insert.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO course (course_id, course_name, description) VALUES\n")
    f.write(",\n".join(f"('{c[0]}', '{c[1]}', '{c[2]}')" for c in courses) + ";\n\n")

with open("enr_insert0.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO enroll (user_id, course_id, enroll_date, overall_grade) VALUES\n")
    f.write(",\n".join(f"('{e[0]}', '{e[1]}', '{e[2]}','{e[3]}')" for e in enr0) + ";\n")

with open("enr_insert1.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO enroll (user_id, course_id, enroll_date, overall_grade) VALUES\n")
    f.write(",\n".join(f"('{e[0]}', '{e[1]}', '{e[2]}','{e[3]}')" for e in enr1) + ";\n")

with open("enr_insert2.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO enroll (user_id, course_id, enroll_date, overall_grade) VALUES\n")
    f.write(",\n".join(f"('{e[0]}', '{e[1]}', '{e[2]}','{e[3]}')" for e in enr2) + ";\n")

with open("enr_insert3.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO enroll (user_id, course_id, enroll_date, overall_grade) VALUES\n")
    f.write(",\n".join(f"('{e[0]}', '{e[1]}', '{e[2]}','{e[3]}')" for e in enr3) + ";\n")


with open("teaches_insert.sql", "w", encoding= "utf-8") as f:
    f.write("INSERT INTO teach (user_id, course_id, teach_start_date) VALUES\n")
    f.write(",\n".join(f"('{t[0]}', '{t[1]}', '{t[2]}')" for t in teaches) + ";\n")


print("SQL file named project_insert.sql generated")
