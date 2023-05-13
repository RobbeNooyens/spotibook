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


def user_by_id(user_id):
    cur = conn.cursor()
    cur.execute("SELECT name FROM users WHERE id = %s;", (user_id,))
    return cur.fetchone()[0]  # Either True or False


def user_by_name(username):
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE name = %s;", (username,))
    return cur.fetchone()[0]


def register(username, password):
    if not user_exists(username):
        cur = conn.cursor()
        cur.execute("INSERT INTO users (name, password) VALUES (%s, %s);", (username, password))
        conn.commit()
        return True
    return False


class Register(Resource):
    def put(self):
        args = flask_request.args
        return register(args['username'], args['password'])


class Login(Resource):
    def get(self):
        args = flask_request.args
        return login(args['username'], args['password'])

class User(Resource):
    def get(self):
        args = flask_request.args
        if 'username' in args:
            return user_by_name(args['username'])
        elif 'user_id' in args:
            return user_by_id(args['user_id'])
        else:
            return make_response("Please provide a username or user id", 400)


api.add_resource(Register, '/register')
api.add_resource(Login, '/login')
api.add_resource(User, '/user')
