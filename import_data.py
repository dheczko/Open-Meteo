import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
from sqlalchemy import create_engine, text
import psycopg2
from main import DATABASE_URL

# Lazy import init_db: only loaded if database needs initialization

REQUIRED_TABLES = [
    "countries",
    "cities",
    "locations",
    "hourly_data",
    "temperature",
    "rain",
    "wind_speed",
    "wind_direction",
    "daily_data",
    "weather_icons"
]

engine = create_engine(DATABASE_URL)


cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
url = "https://archive-api.open-meteo.com/v1/archive"

def is_complete(conn):
    for table in REQUIRED_TABLES:
        result = conn.execute(
            text("SELECT to_regclass(:t)"),
            {"t": f"public.{table}"}
        ).scalar()
        if result is None:
            return False
    return True

from datetime import datetime, timedelta

def determine_date_range(conn):
    result = conn.execute(
        text("SELECT MAX(time) FROM hourly_data")
    ).scalar()

    today = datetime.now().date()

    if result is None:
        start_date = today - timedelta(days=5*365)
        end_date = today - timedelta(days=1)
    else:
        last_timestamp = result.date()
        start_date = last_timestamp
        end_date = today - timedelta(days=1)

    if start_date > end_date:
        start_date = end_date
    return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")

def get_locations(conn):
    return conn.execute(
        text("SELECT id, latitude, longitude FROM locations")
    ).fetchall()

def import_hourly_data(conn,locations,start_date,end_date):
    params = {
        "latitude": [loc[1] for loc in locations],
        "longitude": [loc[2] for loc in locations],
        "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "rain"],
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date
    }
    responses = openmeteo.weather_api(url, params=params)

    weather_data = {}
    timestamps = None
    for idx, (loc_id, lat, lon) in enumerate(locations):
        response = responses[idx]
        hourly = response.Hourly()

        if timestamps is None:
            timestamps = pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
            timestamps = timestamps.tz_convert("GMT")

        weather_data[loc_id] = {
            "temperature": hourly.Variables(0).ValuesAsNumpy(),
            "wind_speed": hourly.Variables(1).ValuesAsNumpy(),
            "wind_direction": hourly.Variables(2).ValuesAsNumpy(),
            "rain": hourly.Variables(3).ValuesAsNumpy(),
        }
    print("Dane godzinowe pobrane.")

    for i, ts in enumerate(timestamps):
        result = conn.execute(
            text("""
                INSERT INTO hourly_data (time)
                VALUES (:ts) RETURNING id
                """),
            {"ts": ts.to_pydatetime()}
        )
        hourly_data_id = result.fetchone()[0]

        for loc_id in weather_data:
            conn.execute(
                text("INSERT INTO temperature (hourly_data_id, location_id, value) "
                    "VALUES (:h, :l, :v)"),
                {"h": hourly_data_id, "l": loc_id, "v": float(weather_data[loc_id]["temperature"][i])}
            )

            conn.execute(
                text("INSERT INTO rain (hourly_data_id, location_id, value) "
                    "VALUES (:h, :l, :v)"),
                {"h": hourly_data_id, "l": loc_id, "v": float(weather_data[loc_id]["rain"][i])}
            )

            conn.execute(
                text("INSERT INTO wind_speed (hourly_data_id, location_id, value) "
                    "VALUES (:h, :l, :v)"),
                {"h": hourly_data_id, "l": loc_id, "v": float(weather_data[loc_id]["wind_speed"][i])}
            )
            conn.execute(
                    text("INSERT INTO wind_direction (hourly_data_id, location_id, value) "
                    "VALUES (:h, :l, :v)"),
                {"h": hourly_data_id, "l": loc_id, "v": float(weather_data[loc_id]["wind_direction"][i])}
            )
    conn.commit()

    print("Dane godzinowe zapisane.")

def import_daily_data(conn, locations, start_date, end_date):
    rows = conn.execute(text("SELECT id, code FROM weather_icons")).fetchall()
    weather_map = {row.code: row.id for row in rows}

    params = {
        "latitude": [loc[1] for loc in locations],
        "longitude": [loc[2] for loc in locations],
        "daily": "weather_code",
        "timezone": "GMT",
        "start_date": start_date,
        "end_date": end_date
    }

    responses = openmeteo.weather_api(url, params=params)

    daily_data = {}
    dates = None

    for idx, (loc_id, lat, lon) in enumerate(locations):
        response = responses[idx]
        daily = response.Daily()

        if dates is None:
            dates = pd.date_range(
                start=pd.to_datetime(daily.Time(), unit="s", utc=True),
                end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=daily.Interval()),
                inclusive="left"
            ).tz_convert("GMT")

        daily_data[loc_id] = {
            "weather_code": daily.Variables(0).ValuesAsNumpy()
        }

    print("Dane dzienne pobrane.")

    for i, day in enumerate(dates):
        date_only = day.date()

        for loc_id in daily_data:
            code = int(daily_data[loc_id]["weather_code"][i])

            weather_id = weather_map.get(code)

            if weather_id is None:
                result = conn.execute(
                    text("INSERT INTO weather_icons (code) VALUES (:c) RETURNING id"),
                    {"c": code}
                )
                weather_id = result.fetchone()[0]
                weather_map[code] = weather_id

            conn.execute(
                text("""
                    INSERT INTO daily_data (time, location_id, weather_id)
                    VALUES (:d, :l, :w)
                """),
                {
                    "d": date_only,
                    "l": loc_id,
                    "w": weather_id
                }
            )
    conn.commit()
    print("Dane dzienne zapisane.")


def run_and_log(conn, func):
    try:
        func()
        conn.execute(
            text("INSERT INTO logs (time, state, message) VALUES (:t, :s, :m)"),
            {"t": datetime.now(), "s": "Success", "m": "The import has been successful"}
        )
        conn.commit()
    except Exception as e:
        conn.execute(
            text("INSERT INTO logs (time, state, message) VALUES (:t, :s, :m)"),
            {"t": datetime.now(), "s": "Failure","m": "The import has been successful"}
        )
        conn.commit()
        raise e

def import_data():
    with engine.connect() as conn:
        if not is_complete(conn):
            # Lazy import init_db: only load if database setup needed
            from init_db import init_db
            init_db()
        locations = get_locations(conn)
        start_date, end_date = determine_date_range(conn)

        run_and_log(conn, lambda: import_hourly_data(conn,locations,start_date,end_date))
        run_and_log(conn, lambda: import_daily_data(conn,locations,start_date,end_date))


if __name__ == "__main__":
    import_data()
