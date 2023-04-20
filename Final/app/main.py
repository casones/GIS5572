from flask import Flask, request
from database import Database
import os

db = Database.initialize_from_env()

start_str = """{"type": "FeatureCollection", "features": """
end_str = "}"

app = Flask(__name__)

@app.route("/")
def home():
    return "Carl Sones, Alexander Danielson - ArcGIS II - Final Project"


@app.route("/gdd_point_accuracy")
def gdd_point():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(ndawn_observations_gdd_point_diff)) FROM ndawn_observations_gdd_point_diff;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


@app.route("/gdd_h3")
def gdd_h3():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(ndawn_observations_gdd_h3)) FROM ndawn_observations_gdd_h3;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


@app.route("/evapotranspiration_point_accuracy")
def evapotranspiration_point():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(ndawn_observations_pet_point_diff)) FROM ndawn_observations_pet_point_diff;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


@app.route("/evapotranspiration_h3")
def evapotranspiration_h3():
    db.connect()
    q = "SELECT JSON_AGG(ST_AsGeoJSON(ndawn_observations_pet_h3)) FROM ndawn_observations_pet_h3;"
    q_out = str(db.query(q)[0][0]).replace("'", "")
    db.close()
    return start_str + q_out + end_str


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))