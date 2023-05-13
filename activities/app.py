from datetime import datetime

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
        cur.execute("INSERT INTO activity (user, date, description) VALUES (%s, %s, %s);",
                    (args['user'], datetime.now(), args['description']))
        conn.commit()
        return True

    def get(self):
        args = flask_request.args
        cur = conn.cursor()
        cur.execute("SELECT * FROM activity WHERE user_id = %s ORDER BY date DESC LIMIT %s;", (args['user'], args['results']))
        return jsonify(cur.fetchall())


api.add_resource(Activity, '/activity')
