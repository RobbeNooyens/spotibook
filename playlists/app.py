from flask import Flask
from flask import request as flask_request
from flask_restful import Resource, Api, reqparse
import psycopg2

parser = reqparse.RequestParser()
parser.add_argument('name')
parser.add_argument('owner')
parser.add_argument('playlist_id')
parser.add_argument('song_id')

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
            cur = conn.cursor()
            cur.execute("INSERT INTO playlist (name, owner) VALUES (%s, %s);", (args['name'], args['owner']))
            conn.commit()
            return True

    # The user can add songs to a playlist.
    class PlaylistSongs(Resource):
        def post(self):
            args = flask_request.args
            cur = conn.cursor()
            cur.execute("INSERT INTO playlist_songs (playlist_id, song_id) VALUES (%s, %s);", (args['playlist_id'], args['song_id']))
            conn.commit()
            return True

        def get(self):
            args = flask_request.args
            cur = conn.cursor()
            cur.execute("SELECT song_id FROM playlist_songs WHERE playlist_id = %s;", (args['playlist_id'],))
            return [x[0] for x in cur.fetchall()]

    # The user can share a playlist with another user.
    class SharedPlaylists(Resource):
        def post(self):
            args = flask_request.args
            cur = conn.cursor()
            cur.execute("INSERT INTO playlist_editors (playlist_id, user_id) VALUES (%s, %s);", (args['playlist_id'], args['user_id']))
            conn.commit()
            return True

        def get(self):
            args = flask_request.args
            cur = conn.cursor()
            cur.execute("SELECT playlist.id, playlist.name FROM playlist LEFT JOIN playlist_editors ON playlist.id = playlist_editors.playlist_id WHERE playlist_editors.user_id = %s;", (args['user_id'],))
            return [x[0] for x in cur.fetchall()]

api.add_resource(Playlist, '/playlist')
api.add_resource(PlaylistSongs, '/playlist/songs')
api.add_resource(SharedPlaylists, '/playlist/shared')
