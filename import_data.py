
import pandas as pd
import requests_cache
from retry_requests import retry
import openmeteo_requests
from sqlalchemy import create_engine, text
import psycopg2

REQUIRED_TABLES = [
    "location",
    "hourly_data",
    "temperature",
    "rain",
    "wind_speed",
    "wind_direction"
]

engine = create_engine("postgresql://postgres:HasloDoSerwera@localhost:5432/weather_test")


cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)
url = "https://api.open-meteo.com/v1/forecast"

def is_complete(conn):
    for table in REQUIRED_TABLES:
        result = conn.execute(
            text("SELECT to_regclass(:t)"),
            {"t": f"public.{table}"}
        ).scalar()
        if result is None:
            return False
    return True


def import_data():
    with engine.connect() as conn:
        #if not is_complete(conn):
            #init_db()

        locations = conn.execute(
            text("SELECT id, latitude, longitude FROM location")
        ).fetchall()

        params = {
            "latitude": [loc[1] for loc in locations],
            "longitude": [loc[2] for loc in locations],
            "hourly": ["temperature_2m", "wind_speed_10m", "wind_direction_10m", "rain"],
            "timezone": "GMT",
            "forecast_days": 1,
        }
        responses = openmeteo.weather_api(url, params=params)

        weather_data = {}
        timestamps = None
        for idx, (loc_id, lat, lon) in enumerate(locations):
            response = responses[idx]
            hourly = response.Hourly()

            if timestamps is None:
                timestamps = pd.date_range(
                    start=pd.to_datetime(hourly.Time(), unit="s", utc=True).tz_convert("UTC"),
                    end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True).tz_convert("UTC"),
                    freq=pd.Timedelta(seconds=hourly.Interval()),
                    inclusive="left"
                )
                timestamps = timestamps.tz_convert("UTC")

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
                     INSERT INTO hourly_data (sample_time)
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

import_data()
