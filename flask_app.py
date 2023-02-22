import psycopg2
import json
from flask import Flask, request

# Create App Instance
app = Flask(__name__)

# Defining Routes
@app.route('/')
def home():
  response = "GIS 5572 - Carl's Basic API"
  return response

@app.route('/getpolygon')
def getPolygon():
    # Make a Connection to the DB - CHANGE PARAMS TO EXECUTE
    connection = psycopg2.connect(host = "34.135.163.144",
                       database = "lab1",
                       user = "postgres",
                       password = "mgispostgres",
                       port = "5432")
    )

    # Create Cursor
    cursor = connection.cursor()

    # Set Query
    query = "SELECT JSON_AGG(lab1_polygon) FROM poly;" # Oops, could have been easier with 'ST_AsGeoJSON'

    # Try to Execute
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


# Helper Function for Converting JSON to GeoJSON
def jsonToGeojson(raw_json):
    # Set GeoJSON Structure
    geojson = {
        "type":"FeatureCollection",
        "features":[
                {
                        "type":"Feature",
                        "geometry":{
                        "type":"Polygon",
                        "coordinates":[obj[0][0]["geom"]["coordinates"][0][0]],
                },
                        "properties":{"objectid":obj[0][0]["objectid"]},
                } for obj in raw_json
        ]
    }

    # Return GeoJSON
    return str(geojson).replace("'", '"')

# Run App
if __name__ == "__main__":
    app.run(
      host='0.0.0.0',
      port=5000)
