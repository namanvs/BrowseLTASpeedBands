import requests as rq
import pandas as pd
import sqlalchemy as db
import json
from config import DATABASE
# Table Names
ROADS = "ROADS"
TRAFFIC = "TRAFFIC"
engine = db.create_engine(DATABASE)

# Create Tables
createROADS = db.sql.text("""CREATE TABLE ROADS(id INTEGER PRIMARY KEY,
                                                name TEXT NOT NULL,
                                                category CHARACTER NOT NULL,
                                                start TEXT NOT NULL,
                                                end TEXT NOT NULL)""")
createTRAFFIC = db.sql.text("""CREATE TABLE TRAFFIC(road_id INTEGER NOT NULL,
                                                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                                    speedband INTEGER NOT NULL,
                                                    FOREIGN KEY (road_id) REFERENCES ROADS(id),
                                                    PRIMARY KEY (road_id, timestamp))""")        
with engine.connect() as connection:
    connection.execute(createROADS)
    connection.execute(createTRAFFIC)

#Read API key
with open('api_key.txt', 'r') as file:
    API_KEY = file.read().replace('\n', '')

# API Details
URL = "http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBandsv2"
HEADERS = {"AccountKey": API_KEY, "accept":"application/json"}

# Hit API
r = rq.get(url = URL, headers = HEADERS)

# Parse JSON to dataframe
df = pd.DataFrame.from_records(json.loads(r.content.decode("utf-8"))["value"], index="LinkID")
#Format Start and End coords
df[["SLat", "SLon", "ELat", "ELon"]] = df["Location"].str.split(expand=True)
df["start"] = df["SLat"] + "," + df["SLon"]
df["end"] = df["ELat"][2] + "," + df["ELon"]
# Clean up the dataframe
df.drop(columns = ["SLat", "SLon", "ELat", "ELon", "Location", "MaximumSpeed", "MinimumSpeed", "SpeedBand"], inplace=True)
# Rename columns
df.rename(columns={"RoadCategory":"category", "RoadName":"name"}, inplace=True)
df.index.name = "id"

#Insert Roads
df.to_sql(ROADS, con=engine, if_exists="append", index=True, index_label="id")

