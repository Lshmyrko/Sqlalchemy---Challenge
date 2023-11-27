# Import the dependencies.



#################################################
# Database Setup
#################################################


# reflect an existing database into a new model

# reflect the tables


# Save references to each table


# Create our session (link) from Python to the DB


#################################################
# Flask Setup
#################################################
from flask import Flask, jsonify

# Create a Flask app
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    """List all available routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a dictionary and return as JSON."""
    # Calculate the date one year ago from the last date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    one_year_ago = (dt.datetime.strptime(most_recent_date, '%Y-%m-%d') - dt.timedelta(days=365)).strftime('%Y-%m-%d')

    # Query for the last 12 months of precipitation data
    results = session.query(Measurement.date, Measurement.prcp)\
        .filter(Measurement.date >= one_year_ago)\
        .all()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in results}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Query for the stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = [station[0] for station in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query the dates and temperature observations of the most-active station for the previous year of data."""
    # Query for the most active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station).label('station_count'))\
        .group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc())\
        .first()

    # Extract the station ID
    most_active_station_id = most_active_station[0]

    # Query for the last 12 months of temperature observations for the most active station
    results = session.query(Measurement.date, Measurement.tobs)\
        .filter(Measurement.station == most_active_station_id, Measurement.date >= one_year_ago)\
        .all()

    # Convert the query results to a list of dictionaries
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in results]

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return a JSON list of the minimum temperature, average temperature, and maximum temperature for a specified start date."""
    # Query for TMIN, TAVG, and TMAX for all dates greater than or equal to the start date
    results = session.query(func.min(Measurement.tobs).label('min_temp'),
                            func.avg(Measurement.tobs).label('avg_temp'),
                            func.max(Measurement.tobs).label('max_temp'))\
        .filter(Measurement.date >= start)\
        .all()

    # Convert the query results to a dictionary
    temp_data = {
        "min_temp": results[0][0],
        "avg_temp": results[0][1],
        "max_temp": results[0][2]
    }

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    """Return a JSON list of the minimum temperature, average temperature, and maximum temperature for a specified start-end range."""
    # Query for TMIN, TAVG, and TMAX for the specified start-end range
    results = session.query(func.min(Measurement.tobs).label('min_temp'),
                            func.avg(Measurement.tobs).label('avg_temp'),
                            func.max(Measurement.tobs).label('max_temp'))\
        .filter(Measurement.date >= start, Measurement.date <= end)\
        .all()

    # Convert the query results to a dictionary
    temp_data = {
        "min_temp": results[0][0],
        "avg_temp": results[0][1],
        "max_temp": results[0][2]
    }

    return jsonify(temp_data)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)


