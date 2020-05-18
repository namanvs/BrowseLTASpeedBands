from backend import app
from flask import jsonify, render_template, send_file, send_from_directory, safe_join, abort
import sqlalchemy as db
import pandas as pd
import json
import decimal, datetime
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy as np
import scipy.io
import os

def alchemyencoder(obj):
    if isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, decimal.Decimal):
        return float(obj)

engine = db.create_engine(app.config["DATABASE"])

# Get dataset overview
@app.route("/")
def getDatasetOverview():
    output = dict()
    with engine.connect() as connection:
        query = db.sql.text("SELECT MIN(timestamp) FROM TRAFFIC LIMIT 1")
        result = connection.execute(query).fetchone()
        print(result[0])
        output["earliest"] = result[0]
        query = db.sql.text("SELECT MAX(timestamp) FROM TRAFFIC LIMIT 1")
        result = connection.execute(query).fetchone()
        output["latest"] = result[0]
        query = db.sql.text("SELECT COUNT(*) FROM ROADS")
        result = connection.execute(query).fetchone()
        output["numroads"] = result[0]
        return render_template("index.html", data =output)

# Get road ids, names and categories
@app.route("/getAllRoads", methods=["GET"])
def getAllRoads():
    query = db.sql.text("SELECT id, name, category FROM ROADS ORDER BY category ASC")
    with engine.connect() as connection:
        result = connection.execute(query).fetchall()
        tuples = []
        for row in result:
            tuples.append((row["id"], row["name"], row["category"]))
        return render_template("browser.html", data = tuples)

# Get history preview for a particular road
@app.route("/getPreview/<id>")
def getPreview(id):
    name = ""
    cat = ""
    name_query = db.sql.text("SELECT name, category FROM ROADS WHERE id = :p1")
    with engine.connect() as connection:
        result = connection.execute(name_query, p1 = id).fetchone()
        name = result[0]
        cat = result[1]
    
    x = []
    y = []
    history_query = db.sql.text("SELECT timestamp, speedband FROM TRAFFIC WHERE road_id = :p1 ORDER BY timestamp ASC LIMIT 144")
    with engine.connect() as connection:
        result = connection.execute(history_query, p1 = id).fetchall()
        for row in result:
            x.append(row["timestamp"][2:-3]) #truncate seconds
            y.append(row["speedband"])
    img = BytesIO()
    fig = plt.plot(x, y)
    plt.title("Last 24h for " + name + " (" + cat +")")
    plt.xticks(x[0::6], ha="left")
    plt.ylim(1, 8)
    plt.savefig(img, format="png")
    plt.clf()
    img.seek(0)
    return send_file(img, mimetype='image/png')

@app.route("/getRoadHistory/<id>")
def getRoadHistory(id):
    name = ""
    cat = ""
    name_query = db.sql.text("SELECT name, category FROM ROADS WHERE id = :p1")
    with engine.connect() as connection:
        result = connection.execute(name_query, p1 = id).fetchone()
        name = result[0]
        cat = result[1]
    x = []
    y = []
    history_query = db.sql.text("SELECT timestamp, speedband FROM TRAFFIC WHERE road_id = :p1 ORDER BY timestamp ASC")
    with engine.connect() as connection:
        result = connection.execute(history_query, p1 = id).fetchall()
        for row in result:
            x.append(row["timestamp"][2:-3]) #truncate seconds
            y.append(row["speedband"])
    return json.dumps(y)

#Download entire dataset
@app.route("/export")
def export():
    # Get Roads and ids
    rids = []
    road_names = []
    roadsQuery = "SELECT id, name FROM ROADS ORDER BY id ASC"
    with engine.connect() as connection:
        result = connection.execute(roadsQuery).fetchall()
        for r in result:
            rids.append(r[0])
            road_names.append(r[1])

    # Get earliest timestamp in dataset for reconstruction
    earliest = ""
    timeQuery = db.sql.text("SELECT timestamp FROM TRAFFIC ORDER BY timestamp ASC LIMIT 1")
    with engine.connect() as connection:
        result = connection.execute(timeQuery).fetchone();
        earliest = result[0][:-3]
    
    # For Each Road Get it's time series data
    list_data = []
    histQuery = db.sql.text("SELECT speedband FROM TRAFFIC WHERE road_id = :p1 ORDER BY timestamp ASC")
    with engine.connect() as connection:
        for id in rids:
            result = connection.execute(histQuery, p1 = id).fetchall()
            bands = [r[0] for r in result]
            list_data.append(bands)    

    mat = np.asarray(list_data, dtype = np.float32)
    road_ids = np.asarray(rids, dtype = np.int)

    filepath = app.config["UPLOAD_FOLDER"] + "data.mat"
    scipy.io.savemat(filepath, {"data": mat, "road_ids": road_ids, "road_names": road_names, "num_roads": mat.shape[0], "num_samples": mat.shape[1], "sample_time": "10 minutes", "start time": earliest})
    temp = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'])
    try:
        return send_from_directory(app.config["UPLOAD_FOLDER"], filename="data.mat", as_attachment=True)
    except FileNotFoundError:
        abort(404)
    
