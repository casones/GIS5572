from flask import Flask, request
from database import Database
import os

db = Database.initialize_from_env()

start_str = """{"type": "FeatureCollection", "features": """
end_str = "}"

app = Flask(__name__)

@app.route("/")
def home():
    return "Carl Sones - ArcGIS II - Lab 3"


@app.route("/weather_point_accuracy")
def weather_point():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(aggmthwx_62022_point_diff)) FROM aggmthwx_62022_point_diff;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


@app.route("/weather_h3")
def weather_h3():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(aggmthwx_62022_h3)) FROM aggmthwx_62022_h3;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


@app.route("/elevation_point_accuracy")
def elevation_point():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(elevation_3km_point_diff)) FROM elevation_3km_point_diff;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


@app.route("/elevation_h3")
def elevation_h3():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(elevation_3km_h3)) FROM elevation_3km_h3;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))