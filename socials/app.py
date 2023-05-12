from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('title')
parser.add_argument('artist')

app = Flask("socials")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="socials", user="postgres", password="postgres", host="socials_persistence")
        print("DB connection succesful")
    except psycopg2.OperationxalError:
        import time
        time.sleep(1)
        print("Retrying DB connection")