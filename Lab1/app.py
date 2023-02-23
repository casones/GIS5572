import psycopg2
from flask import Flask, jsonify
from psycopg2 import sql
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

@app.route('/get_polygon', methods=['GET'])
def get_polygon():
    connection= psycopg2.connect(host = '34.135.163.144',
                             database = 'lab1',
                             user = 'postgres',
                             password = 'mgispostgres')

    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(sql.SQL("SELECT poly, ST_AsGeoJSON(polygon)::json AS geometry FROM poly"), (1,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()
    return jsonify(result)