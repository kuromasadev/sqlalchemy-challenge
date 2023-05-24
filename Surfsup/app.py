# Import the dependencies.
import sqlalchemy
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
from datetime import datetime, timedelta


# Database Setup

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup
app = Flask(__name__)

# Flask Routes

# Define the homepage route
@app.route("/")
def home():
    """List all available routes."""
    # Create a dictionary of available routes
    routes = {
        "1. Home": "/",
        "2. Precipitation": "/api/v1.0/precipitation",
        "3. Stations": "/api/v1.0/stations",
        "4. Temperature Observations": "/api/v1.0/tobs",
        "5. Temperature Statistics (Start Date)": "/api/v1.0/<start>",
        "6. Temperature Statistics (Start-End Dates)": "/api/v1.0/<start>/<end>",
    }
    return jsonify(routes)

# Define the precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of precipitation data for the last 12 months."""
    # Query1 code
    query1 = """
    SELECT date, prcp
    FROM measurement
    WHERE date >= (
    SELECT date(MAX(date), '-1 year')
    FROM measurement
    )
    ORDER BY date;
    """
    results = engine.execute(query1).fetchall()
    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

# Define the stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations."""
    # Query2 code
    query2 = """
    SELECT DISTINCT station
    FROM measurement;
    """
    results = engine.execute(query2).fetchall()
    station_data = [row[0] for row in results]
    return jsonify(station_data)


# Define the temperature observations route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year."""
    # Query 5 code
    query5 = """
    SELECT MAX(date) 
    FROM measurement;
    """
    most_recent_date = engine.execute(query5).fetchone()[0]
    one_year_ago = (datetime.strptime(most_recent_date, '%Y-%m-%d') - timedelta(days=365)).date()
    
    query5b = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).all()

    tobs_data = []
    for date, tobs in query5b:
        tobs_data.append({"date": date, "tobs": tobs})
    return jsonify(tobs_data)


# Define the temperature statistics route
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    """
    Return a JSON list of the minimum temperature, average temperature,
    and maximum temperature for a specified start or start-end range.
    """
    # Query 6 code 
    query6 = """
    SELECT MIN(tobs) AS min_temp, 
    AVG(tobs) AS avg_temp, 
    MAX(tobs) AS max_temp
    FROM measurement
    WHERE date >= :start_date
    """

    if end:
        query6 += " AND date <= :end_date"
    
    if end:
        results = engine.execute(query6, start_date=start, end_date=end).fetchall()
    else:
        results = engine.execute(query6, start_date=start).fetchall()

    min_temp, avg_temp, max_temp = results[0]
    
    stats_data = {
        "start_date": start,
        "end_date": end,
        "min_temperature": min_temp,
        "avg_temperature": avg_temp,
        "max_temperature": max_temp
    }

    return jsonify(stats_data)


if __name__ == '__main__':
    app.run(debug=True)
