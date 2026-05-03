import sqlite3
from flask import Flask, request
from flask_restful import Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify


# Bai 2.1

app = Flask(__name__)
api = Api(app)

# Return information about a player
class Player (Resource):
    def get(self, player_name):
        conn = sqlite3.connect('player premier legaue.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        query = cursor.execute("select * from player_stats where player = ?", (player_name,)).fetchall()
        result = [dict(row) for row in query]
        conn.close()
        return jsonify(result)

#Return information of players of a club
class Club(Resource):
    def get(self, club_name):
        conn = sqlite3.connect('player premier legaue.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        rows = cursor.execute('select * from player_stats where squad = ?', (club_name,)).fetchall()

        result = [dict(row) for row in rows]
        conn.close()
        return jsonify(result)




api.add_resource(Player, '/players/<string:player_name>')
api.add_resource(Club, '/clubs/<string:club_name>')

if __name__ == '__main__' :
    app.run(debug = True)

