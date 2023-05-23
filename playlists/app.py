import requests
from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('owner')
parser.add_argument('playlist_id')
parser.add_argument('song_id')
parser.add_argument('user')

app = Flask("playlists")
api = Api(app)

conn = None

while conn is None:
    try:
        conn = psycopg2.connect(dbname="playlists", user="postgres", password="postgres", host="playlists_persistence")
        print("DB connection succesful")
    except psycopg2.OperationalError:
        import time

        time.sleep(1)
        print("Retrying DB connection")


# The user can create playlists.
class Playlist(Resource):
    def get(self):
        args = flask_request.args
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM playlist WHERE owner = %s;", (args['owner'],))
        return cur.fetchall()

    def post(self):
        args = flask_request.args
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO playlist (name, owner) VALUES (%s, %s);", (args['name'], args['owner']))
            conn.commit()
            # Save the action in the activity log
            requests.post("http://activities:5000/activity", params={'user': args['owner'], 'description': f"Created playlist {args['name']}"})
        except psycopg2.IntegrityError:
            return False


# The user can add songs to a playlist.
class PlaylistSongs(Resource):
    def post(self):
        args = flask_request.args
        playlist_id = args['playlist_id']
        artist = args['artist']
        title = args['title']
        user = args['user']
        # Check if song already exists
        response = requests.get("http://songs:5000/songs/exist", params={'artist': artist, 'title': title})
        if not response.ok or response.json():
            return False
        if not response.json():
            cur = conn.cursor()
            # Add song to songs table
            response = requests.post("http://songs:5000/songs/add", params={'artist': artist, 'title': title})
            if not response.ok:
                return False
            try:
                cur.execute("INSERT INTO playlist_songs (playlist_id, title, artist) VALUES (%s, %s, %s);",
                            (playlist_id, title, artist))
                conn.commit()
            except psycopg2.IntegrityError:
                return False
            requests.post("http://activities:5000/activity", params={'user': user, 'description': f"Added song {title} to playlist {playlist_id}"})

        return True

    def get(self):
        args = flask_request.args
        cur = conn.cursor()
        cur.execute("SELECT title, artist FROM playlist_songs WHERE playlist_id = %s;", (args['playlist_id'],))
        return cur.fetchall()


# The user can share a playlist with another user.
class SharedPlaylists(Resource):
    def post(self):
        args = flask_request.args
        try:
            cur = conn.cursor()
            cur.execute("INSERT INTO playlist_editors (playlist_id, username) VALUES (%s, %s);",
                        (args['playlist_id'], args['user']))
            conn.commit()
            requests.post("http://activities:5000/activity",
                          params={'user': args['owner'], 'description': f"Shared a playlist with {args['user']}"})
            return True
        except psycopg2.IntegrityError:
            return False

    def get(self):
        args = flask_request.args
        cur = conn.cursor()
        cur.execute("""
        SELECT playlist.id, playlist.name 
        FROM playlist LEFT JOIN playlist_editors 
        ON playlist.id = playlist_editors.playlist_id 
        WHERE playlist_editors.username = %s;
        """, (args['user'],))
        return cur.fetchall()

api.add_resource(Playlist, '/playlist')
api.add_resource(PlaylistSongs, '/playlist/songs')
api.add_resource(SharedPlaylists, '/playlist/shared')
