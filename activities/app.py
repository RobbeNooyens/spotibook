import json
from datetime import datetime

import requests
from flask import Flask, jsonify
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

app = Flask("activities")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="activities", user="postgres", password="postgres",
                                host="activities_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time

        time.sleep(1)
        print("Retrying DB connection")


class Activity(Resource):
    def put(self):
        args = flask_request.args
        cur = conn.cursor()
        cur.execute("INSERT INTO activity (username, date, description) VALUES (%s, %s, %s);",
                    (args['user'], datetime.now(), args['description']))
        conn.commit()
        return True

    def get(self):
        args = flask_request.args
        # Get list of friends
        friends = requests.get("http://socials:5000/friends", params={'user': args['user']})
        if friends is None or not friends.ok:
            return []
        cur = conn.cursor()
        app.logger.info(friends.json())
        cur.execute("SELECT id, username, date, description FROM activity WHERE username IN %s ORDER BY date LIMIT %s;",
                    (tuple(friends.json()), args['results']))
        activities = cur.fetchall()

        # Format the activities as a list of dictionaries
        result = []
        for activity in activities:
            activity_dict = (
                activity[0],
                activity[1],
                str(activity[2]),  # Convert date to string
                activity[3]
            )
            result.append(activity_dict)

        return result


api.add_resource(Activity, '/activity')
