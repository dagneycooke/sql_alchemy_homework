from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# home page
@app.route("/")
def welcome():

 #   List all available routes
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/YYYY-MM-DD"
        f"/api/v1.0/YYYY-MM-DD/YYYY-MM-DD"

    )

# create route for precipitation data
@app.route("/api/v1.0/precipitation")
def passengers():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of measurement data including the date and prcp"""
    # Query all measurement dates and precipitation
    results = session.query(Measurement.date, Measurement.prcp).all()

    # close sessio
    session.close()

    #Convert the query results to a Dictionary using date as the key and prcp as the value.
    all_dates = []
    for date, prcp in results:
        dates_dict = {}
        dates_dict[date] = prcp
        all_dates.append(dates_dict)

    # return json version of dates/precipitation data
    return jsonify(all_dates)

# display all station names
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(results))

    return jsonify(all_names)


# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    
    last_date_query = session.query(Measurement.date).order_by(Measurement.date.desc()).limit(1).all()

    # get date out of query
    last_date = last_date_query[0][0]

    # convert string to date and calculate one yar ago
    one_year_ago = dt.datetime.strptime(last_date,'%Y-%m-%d').date() - dt.timedelta(days=365)

    results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.tobs != 0).\
        filter(Measurement.date >= one_year_ago).all()
    session.close()

    # turn list of tuples into normal list
    tobs_list = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_list.append(tobs_dict)

    # return json version of dates/precipitation data
    return jsonify(tobs_list)


# take start date and get average info since that date
@app.route("/api/v1.0/<start>")
def start_only(start): #function provided in starter jupyter notebook

    # open session, query date/measurment info, close session
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    session.close()

    # convert to list
    temp_list = list(np.ravel(results))

    # convert to dict
    for temp in temp_list:
        temp_dict = {"Min":temp_list[0],"Avg":temp_list[1],"Max":temp_list[2]}

    return jsonify(temp_dict)

# take start and end date and get average info for date range
@app.route("/api/v1.0/<start>/<end>")
def start_to_end(start,end): #function provided in starter jupyter notebook

    # open session, query measurement info, close session
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    # convert results to list and then read into dict
    temp_list = list(np.ravel(results))

    for temp in temp_list:
        temp_dict = {"Min":temp_list[0],"Avg":temp_list[1],"Max":temp_list[2]}

    # display dict
    return jsonify(temp_dict)


if __name__ == '__main__':
    app.run(debug=True)

