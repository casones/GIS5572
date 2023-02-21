import psycopg2
import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def home():
    response = "Carl Sones' API"
    return response

@app.route('/getpolygon')
def get_poly():
    conn = psycopg2.connect(host = "34.135.163.144",
                       database = "lab1",
                       user = "postgres",
                       password = "mgispostgres",
                       port = "5432")

    cursor = conn.cursor()

    query = "SELECT ST_AsGeoJSON(poly) FROM poly"

     try:
        # Execute Query
        cursor.execute(query)
        out = cursor.fetchall() 

        # Close Connection
        connection.close()

        # Convert to GeoJSON
        output = jsonToGeojson(out)

        return output

    # Display Error
    except Exception as e:
        connection.rollback()
        return("Error: " + str(e))

if __name__ == "__main__":
    app.run(
      host='0.0.0.0',
      port=5000)