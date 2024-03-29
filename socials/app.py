import requests
from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('user')
parser.add_argument('user1')
parser.add_argument('user2')

app = Flask("socials")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="socials", user="postgres", password="postgres", host="socials_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time
        conn = None

        time.sleep(1)
        print("Retrying DB connection")


def add_friend(user1, user2):
    try:
        cur = conn.cursor()
        # Check if the users exist
        user_exists = requests.get("http://authentication:5000/user", params={'username': user2})
        if not user_exists.ok or not user_exists.json():
            return False
        cur.execute("INSERT INTO friendship (username, friend) VALUES (%s, %s);", (user1, user2))
        conn.commit()
        requests.post("http://activities:5000/activity",
                      params={'user': user1, 'description': f"Just became friends with {user2}"})
        return True
    except psycopg2.IntegrityError:
        return False


class Friends(Resource):
    def get(self):
        args = flask_request.args
        cur = conn.cursor()
        cur.execute("SELECT friend FROM friendship WHERE username = %s;", (args['user'],))
        return [x[0] for x in cur.fetchall()]

    def post(self):
        args = flask_request.args
        return add_friend(args['user1'], args['user2'])


api.add_resource(Friends, '/friends')

