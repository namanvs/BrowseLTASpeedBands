# BrowseLTASpeedBands
Database for storing LTA Datamall API results and flask app for browsing them

## Motivation
I was bored during lockdown and wanted to start applying the RDBMS skills I had to build a dataset by periodically hitting a public API. I then created a rudimentary visual database browser using Flask and Vue.js to learn more about Python and the basics of Web development. I eventually want to run some ML analysis on the data, but the pandemic and ensuing lockdown means that my current data is not representative of "normal" conditions.

## Description
This project collects information for traffic speeds on Singapore's road network. The data is provided by Singapore's Land Transport Authority (LTA) through their [Dynamic Datsets](https://www.mytransport.sg/content/mytransport/home/dataMall/dynamic-data.html#Traffic) on their [DataMall](https://www.mytransport.sg/content/mytransport/home/dataMall.html). I am running this project off a Raspberry Pi. It has more than enough resources for this project, and the simplicity and lightness of this system appeals to me. I'm not deploying this on the cloud because the database can grow large. The API actually updates its values every 5 minutes, so I'm only actually getting half the data. Nevertheless, my database has grown to 50MB in a week.

## Requirements
1. SQLite 3 for the database
2. Python 3, with the following modules
    * PANDAS
    * SciPy
    * Matplotlib
    * SQLAlchemy
    * Flask

## Setup
### 1. Databases
The first thing to set up after pulling this repo is the database. Do this in the root directory of the repo by issuing:
```
sqlite3 trafficmonitor < setupdbs.sql
```
This creates two tables in your database, called "ROADS" and "TRAFFIC".

ROADS Table
|id|name|category|start|end|
|--|----|--------|-----|---|
|INTEGER|STRING|CHARACTER|STRING (a pair of lat, lon)|STRING (a pair of lat, lon)|

I have provided a `Roads.tsv` file you can use to populate the "ROADS" table by doing the following:
```
sqlite3 trafficmonitor 
sqlite> .separator "\t"
sqlite> .import Roads.tsv ROADS
```
I could have put this in the setup script but perhaps my Roads.tsv file will become out-of-date as Singapore continues to grow.

TRAFFIC Table
|road_id|timestamp|speedband|
|--|----|--------|-----|---|
|INTEGER|DATETIME (sqlite3 format, defaults to current timestamp)|INTEGER|

### 2. Data Collection Script
The next task is to collect data to populate the TRAFFIC Table. `ingest.py` does this for you, but you need to supply your own API key, which you can obtain [here](https://www.mytransport.sg/content/mytransport/home/dataMall/request-for-api.html). Place the key LTA sends you in a file named `api_key.txt` in the root of the repo folder.

I run this script every 10 minutes using `crontab` on Linux:
```
crontab -e */10 * * * * ~/.profile; <path to your python> "<path to this repo folder>/ingest.py"
```
### 3. Run Dataset Browser
The dataset browser is a rudimentary visual browser written in Flask. To run it, do:
```
export FLASK_APP=trafficmon.py
flask run
```
in your terminal in the root of the repo. If you're running this on a remote Raspberry Pi, do 
```
flask run --host 0.0.0.0
```
to make the site accessible from a remote machine.

## Browser Functions
The dataset browser offers the following functions:
1. Download the entire dataset as a .mat file. Accessible variables are:
    * matrix of speedbands where the rows are each road in order of increasing road ID, and each column the speedband value in increasing order of timestamp.
    * array of road names.
    * array of road IDs index-matched to the road names array.
    * The sampling interval and the starting timestamp so that you can reconstruct the time vector manually.
2. Browse a table of roads and preview their speedband history for the last 24 hours with an option to download the speedband history for that road.

## TODO
- [] Write a Python script that automates database setup and pre-population of the ROADS table.
- [] Rework the visual interface to dynamically generate interactive graphs with timestamp filtering (I'm new to Web stuff so this will take some time)
- [] Visualize completeness of the dataset. What if the Pi goes down for some time? Is there some way to check if my dataset is still complete? LTA's API is completely real-time and they do not publish complete historical data.
- [] Email LTA and question why data for many other major artery roads are missing. Singapore has 10 major expressways and only 1 of them is reported in this dataset.