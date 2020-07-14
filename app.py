#################################################
# Import Dependencies
#################################################

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"/api/v1.0/start ... where start is a yyyy-mm-dd<br/><br/>"
        f"/api/v1.0/start/end ... where end is also a yyyy-mm-dd<br/><br/>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of measurement data"""
    # Query all measurements
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary from the row data and append to a list of prcp
    all_prcp = []
    for date, prcp in results:
        all_prcp.append({date: prcp})

    # Return the results
    return jsonify(all_prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all stations
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return the results
    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def most_active_station_tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Determine the date of the last data point and store it as a string
    q_latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first() 
    latest_date_str = q_latest_date[0]
    # return latest_date_str

    # Convert the last data point to a date
    latest_date_dt = dt.datetime.strptime(latest_date_str,"%Y-%m-%d").date()
    
    # Create and store a variable for holding the date one year ago from the last data point
    year_ago_date_dt = latest_date_dt - dt.timedelta(days=365)
    # year_ago_date_str = str(year_ago_date_dt)
    # return year_ago_date_str

    # Create a list of the stations and their count of measurements
    station_groups = session.query(Measurement.station, func.count(Measurement.date)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.date).desc())

    # Grab the station name from the most active station
    most_active_station_name = station_groups.first()[0]

    # Perform a query to retrieve the observed temperature for the most active station's past year
    most_active_latest_year_tobs = session.query(Measurement.tobs).\
    filter(Measurement.date >= year_ago_date_dt).\
    filter(Measurement.station == most_active_station_name).all()
    session.close()
    
    # Convert list of tuples into normal list
    all_tobs = list(np.ravel(most_active_latest_year_tobs))

    # Return the results
    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>/")
@app.route("/api/v1.0/<start>/<end>")
def temp_calc(start=None, end=None):
    """Fetch the minimum temperature, the average temperature, and the max temperature
    for a given start date (and end date, if specified"""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    if end != None:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

        session.close()

        # Return the results
        return jsonify(results)
    
    else:
        results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

        session.close()

        # Return the results
        return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)