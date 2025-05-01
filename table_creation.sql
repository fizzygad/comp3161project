create database if not exists project;
use project;

create table if not exists users(
user_id int primary key,
email varchar(50),
pswrd varchar(30),
username varchar(50)
);

create table if not exists roles(
user_id int primary key,
role varchar(20),
FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE if not exists course (
course_id INT PRIMARY KEY,
course_name VARCHAR(100),
description TEXT
);

CREATE TABLE if not exists enroll (
user_id INT,
course_id INT,
enroll_date DATE,
overall_grade varchar(3),
PRIMARY KEY (user_id, course_id),
FOREIGN KEY (user_id) REFERENCES users(user_id),
FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE if not exists teach (
user_id INT,
course_id INT,
teach_start_date DATE,
PRIMARY KEY (user_id, course_id),
FOREIGN KEY (user_id) REFERENCES users(user_id),
FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE if not exists section (
section_id VARCHAR(50) PRIMARY KEY,
course_id INT,
section_title VARCHAR(100),
section_desc TEXT,
FOREIGN KEY (course_id) REFERENCES Course(course_id)
);

CREATE TABLE if not exists item (
item_id VARCHAR(50) PRIMARY KEY,
section_id VARCHAR(50),
item_type VARCHAR(50),
item_desc TEXT,
FOREIGN KEY (section_id) REFERENCES section(section_id)
);

CREATE TABLE if not exists assignment (
assignment_id VARCHAR(50) PRIMARY KEY,
course_id INT,
title VARCHAR(100),
max_score DECIMAL(5,2),
due_date DATE,
FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE if not exists submission (
submission_id VARCHAR(50) PRIMARY KEY,
user_id INT,
file_url TEXT,
submit_date DATE,
FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE if not exists Receives (
submission_id VARCHAR(50),
assignment_id VARCHAR(50),
grade DECIMAL(5,2),
PRIMARY KEY (submission_id, assignment_id),
FOREIGN KEY (submission_id) REFERENCES Submission(submission_id),
FOREIGN KEY (assignment_id) REFERENCES Assignment(assignment_id)
);

CREATE TABLE if not exists forum (
forum_id VARCHAR(50) PRIMARY KEY,
course_id INT,
forum_title VARCHAR(100),
forum_desc TEXT,
time_created TIMESTAMP,
FOREIGN KEY (course_id) REFERENCES course(course_id)
);

CREATE TABLE if not exists Thread (
thread_id VARCHAR(50) PRIMARY KEY,
forum_id VARCHAR(50),
content TEXT,
FOREIGN KEY (forum_id) REFERENCES Forum(forum_id)
);

CREATE TABLE if not exists Reply (
reply_id VARCHAR(50) PRIMARY KEY,
thread_id VARCHAR(50),
content TEXT,
FOREIGN KEY (thread_id) REFERENCES Thread(thread_id)
);

CREATE TABLE if not exists Post_Thread (
user_id INT,
thread_id VARCHAR(50),
time_created TIMESTAMP,
PRIMARY KEY (user_id, thread_id),
FOREIGN KEY (user_id) REFERENCES Users(user_id),
FOREIGN KEY (thread_id) REFERENCES Thread(thread_id)
);

CREATE TABLE if not exists Post_Reply (
user_id INT,
reply_id VARCHAR(50),
time_created TIMESTAMP,
PRIMARY KEY (user_id, reply_id),
FOREIGN KEY (user_id) REFERENCES Users(user_id),
FOREIGN KEY (reply_id) REFERENCES Reply(reply_id)
);

CREATE TABLE if not exists CalendarEvent (
event_id INT PRIMARY KEY,
course_id INT,
title VARCHAR(100),
description TEXT,
start_date TIMESTAMP,
end_date TIMESTAMP,
FOREIGN KEY (course_id) REFERENCES Course(course_id)
);
