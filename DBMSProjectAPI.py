from flask import Flask, request, jsonify, make_response
import mysql.connector

app = Flask(__name__)

app.config['CUSTOMERDATABASE_URL'] = 'mysql://sammy:password@localhost/customerdata'

@app.route("/")
def helloworld():
    return "</p>Hello</p>"