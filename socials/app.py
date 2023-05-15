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
    # Get userid for user2
    response = requests.get(f"http://authentication:5000/user?username={user2}")
    if not response.ok:
        return False
    user2_id = response.json()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM friendship
                WHERE (user1 = %s AND user2 = %s)
            ) AS entry_exists;
        """, (user1, user2_id))
        exists = cur.fetchone()[0]
        if exists:
            return False
        cur.execute("INSERT INTO friendship (user1, user2) VALUES (%s, %s);", (user1, user2_id))
        conn.commit()
        return True
    except psycopg2.IntegrityError:
        return False
    return False


class Friends(Resource):
    def get(self):
        args = flask_request.args
        cur = conn.cursor()
        cur.execute("SELECT user2 FROM friendship WHERE user1 = %s;", (args['user'],))
        return [x[0] for x in cur.fetchall()]

    def post(self):
        args = flask_request.args
        return add_friend(args['user1'], args['user2'])


api.add_resource(Friends, '/friends')
