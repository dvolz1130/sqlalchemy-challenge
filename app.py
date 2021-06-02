import numpy as np
import pandas as pd

import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#### Setting up database ####################
#### Reference site for connect_args - https://stackoverflow.com/questions/48218065/programmingerror-sqlite-objects-created-in-a-thread-can-only-be-used-in-that-sa
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# Reflecting Tables
Base.prepare(engine, reflect=True)

Base.classes.keys()

measurement = Base.classes.measurement
station = Base.classes.station

session = Session(engine)
############## End setting up database ###############

## Flask setup ################
app = Flask(__name__)

## Global variables #############
ld = dt.date(2017, 8, 23)
one_year_ago = ld - dt.timedelta(days=365)

### Home page and list available routes ######
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return ("Welcome to my Climate Webpage!<br/>"
            f"<br/>"
            f"Available routes:<br/>"
            f"To view precipitation, add below to the home URL<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"<br/>"
            f"To view a list of stations, append below to the home URL<br/>"
            f"/api/v1.0/stations<br/>"
            f"<br/>"
            f"To view the date and temperature of most active station USC00519281, append below to the home URL<br/>"
            f"/api/v1.0/tobs<br/>"
            f"<br/>"
            f"To view the average, max, and min temperture for a given start date, append below to the home URL with a date ""(year-month-day)""<br/>"
            f"/api/v1.0/<start><br>"
            f"<br/>"
            f"Give a start and end date ""(year-month-day)"" to view average, max, and min temperture of a trip range<br/>"
            f"/api/v1.0/<start>/<end>"
    )

## precipitation ###################
@app.route("/api/v1.0/precipitation")
def precipitation():
   
    past_info = session.query(measurement.date,measurement.prcp).filter(measurement.date >= one_year_ago).\
             order_by(measurement.date).all()
       
    precip = {date: p for date, p in past_info}
    
    return jsonify(precip)

## Stations ######################
@app.route("/api/v1.0/stations")
def stations():

    stat = session.query(station.station, station.name).all()

    all_stations = {name: s for name, s in stat}

    return jsonify(all_stations)

## Tob #######################
@app.route("/api/v1.0/tobs")
def tob():

    temp_observ = session.query(measurement.date, measurement.tobs).\
              filter(measurement.station == "USC00519281").\
              filter(measurement.date >= one_year_ago).order_by(measurement.date).all()
    highest_tobs = {date: temp for date, temp in temp_observ}
    return jsonify(highest_tobs)

#### start date only ####################
@app.route("/api/v1.0/<start>")
def trip(start):

    temp_observ = session.query(measurement.tobs).filter(measurement.date.between(start, '2017-08-23')).all()
    
    temp_df = pd.DataFrame(temp_observ, columns=["tobs"])

    tavg = temp_df["tobs"].mean()
    tmax = temp_df["tobs"].max()
    tmin = temp_df["tobs"].min()
    
    return jsonify(tavg, tmax, tmin)

#### start and end date of trip #############
@app.route("/api/v1.0/<start>/<end>")
def trip_dur(start,end):

    temp_observ = session.query(measurement.tobs).filter(measurement.date.between(start, end)).all()
    
    temp_df = pd.DataFrame(temp_observ, columns=["tobs"])

    tavg = temp_df["tobs"].mean()
    tmax = temp_df["tobs"].max()
    tmin = temp_df["tobs"].min()
    
    return jsonify(tavg, tmax, tmin)

if __name__ == '__main__':
    app.run(debug=True)

