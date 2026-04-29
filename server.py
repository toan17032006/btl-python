from flask import Flask,jsonify,request
from flask_cors import CORS 
import sqlite3

app = Flask(__name__)
CORS(app)   

app.json.ensure_ascii = False

def get_db_conections():
    conn = sqlite3.connect('player premier legaue.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
@app.route('/api/stats', methods=['GET'])
def get_al_stats():
    
    player_name = request.args.get('name',' ').strip()
    club_name = request.args.get('club', '').strip()

    conn = get_db_conections()
    cursor = conn.cursor()

    if player_name:
        cursor.execute("SELECT * FROM player_stats WHERE player LIKE ?", (f"%{player_name}%",))
    else:
        cursor.execute("SELECT * FROM player_stats")

    rows = cursor.fetchall()
    conn.close()
    
    data = [dict(row) for row in rows]
    return jsonify({"total": len(data), "players": data})

if __name__ == '__main__':
    app.run(debug=True)


    