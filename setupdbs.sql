CREATE TABLE ROADS(
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category CHARACTER NOT NULL,
    start TEXT NOT NULL,
    end TEXT NOT NULL);

CREATE TABLE TRAFFIC(
    road_id INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    speedband INTEGER NOT NULL,
    FOREIGN KEY (road_id) REFERENCES ROADS(id)
    PRIMARY KEY (road_id, timestamp)
);