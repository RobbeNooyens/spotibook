from flask import Flask, make_response
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('username')
parser.add_argument('email')
parser.add_argument('password')

app = Flask("authentication")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="authentication", user="postgres", password="postgres",
                                host="authentication_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time

        time.sleep(1)
        print("Retrying DB connection")


def login(username, password):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE name = %s AND password = %s;", (username, password))
    return bool(cur.fetchone()[0])  # Either True or False


def user_exists(username):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users WHERE name = %s;", (username,))
    return bool(cur.fetchone()[0])  # Either True or False


def register(username, password):
    if not user_exists(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        return True
    return False


class Register(Resource):
    def post(self):
        args = flask_request.args
        return register(args['username'], args['password'])


class Login(Resource):
    def get(self):
        args = flask_request.args
        return login(args['username'], args['password'])


class User(Resource):
    def get(self):
        args = flask_request.args
        return user_exists(args['username'])


api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(User, '/user')