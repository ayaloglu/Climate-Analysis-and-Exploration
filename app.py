from sqlalchemy import create_engine, func, distinct
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base
import sqlalchemy
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import style
from flask import Flask, jsonify

app = Flask(__name__)

style.use('fivethirtyeight')


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station


@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return("Welcome to my 'Home' page! <br/>"
           f"Available Routes:<br/>"
           f"/api/v1.0/precipitation <br/>"
           f"/api/v1.0/stations <br/>"
           f"/api/v1.0/tobs <br/>"
           f"/api/v1.0/start <br/>"
           f"/api/v1.0//api/v1.0/start/end")


@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for 'Precipitation' page...")

    session = Session(engine)

    one_year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    last_year = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > one_year_ago).all()
    last_year_df = pd.DataFrame(last_year, columns=["Date", "precipitation"])
    last_year_df = last_year_df.set_index("Date")
    last_year_df.sort_index()

    last_year_dict = last_year_df.to_dict()
    session.close()
    return jsonify(last_year_dict)


@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for 'Stations' page...")

    session = Session(engine)
    a = session.query(Station.name).all()
    session.close()
    return jsonify(pd.DataFrame(a).to_dict())


@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for 'tobs' page...")
    session = Session(engine)

    most_active_sta = session.query(Measurement.station, func.count(Measurement.station)).group_by(
        Measurement.station).order_by(func.count(Measurement.station).desc()).first()
    b = session.query(Measurement.tobs).filter(
        Measurement.station == most_active_sta[0]).all()

    session.close()

    return jsonify(pd.DataFrame(b).to_dict())


@app.route("/api/v1.0/<start>")
def start(start):
    print("Server received request for 'start' page...")
    session = Session(engine)

    after_start = session.query(func.min(Measurement.tobs), func.max(
        Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).first()

    session.close()
    return f"Since {start} Min Temprerature: {after_start[0]}, Max Temperature: {after_start[1]}, Avg Temperature: {after_start[2]}."


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print("Server received request for 'start, end' page...")
    session = Session(engine)

    range = session.query(func.min(Measurement.tobs), func.max(
        Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).first()

    session.close()
    return f"Between {start} and {end} Min Temprerature: {range[0]}, Max Temperature: {range[1]}, Avg Temperature: {range[2]}."


if __name__ == "__main__":
    app.run(debug=True)
