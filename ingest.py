import requests as rq
import pandas as pd
import sqlalchemy as db
import json

# API Details
URL = "http://datamall2.mytransport.sg/ltaodataservice/TrafficSpeedBandsv2"
HEADERS = {"AccountKey": "FRBsrUb0SamDTzAlZ41SIA==", "accept":"application/json"}

# Table Names
TRAFFIC = "TRAFFIC"
ROADS = "ROADS"

engine = db.create_engine('sqlite:////mnt/dietpi_userdata/Projects/LTA Traffic Monitor/trafficmonitor')

# Hit API
r = rq.get(url = URL, headers = HEADERS)

# Parse JSON to dataframe
df = pd.DataFrame.from_records(json.loads(r.content.decode("utf-8"))["value"], index="LinkID")

inserted_data = df["SpeedBand"]

inserted_data.to_sql(TRAFFIC, con=engine, if_exists="append", index=True, index_label="road_id")

