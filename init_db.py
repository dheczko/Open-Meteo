import sqlalchemy as sa
from sqlalchemy import create_engine, text

def init_db():
    """
    Tworzy pustą bazę danych, wszystkie tabele ze schematu.
    Jeśli tabele już istnieją, pomija ich tworzenie.
    """
    #UWAGA, ustawić dane do połączenia z db
    engine = create_engine("postgresql://postgres:HasloDoSerwera@localhost:5432/weather_test")

    with engine.connect() as conn: 
        #locations
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS locations (
                id SERIAL PRIMARY KEY,
                city_id INTEGER,
                latitude FLOAT,
                longitude FLOAT
            )
        """))
        #hourly data
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS hourly_data (
                id SERIAL PRIMARY KEY,
                time TIMESTAMP
            )
        """))
        #temperature
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS temperature (
                id SERIAL PRIMARY KEY,
                location_id INTEGER,
                hourly_data_id INTEGER,
                value FLOAT
            )
        """))
        #rain
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS rain (
                id SERIAL PRIMARY KEY,
                location_id INTEGER,
                hourly_data_id INTEGER,
                value FLOAT
            )
        """))
        #wind_speed
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS wind_speed (
                id SERIAL PRIMARY KEY,
                location_id INTEGER,
                hourly_data_id INTEGER,
                value FLOAT
            )
        """))
        #wind_direction
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS wind_direction (
                id SERIAL PRIMARY KEY,
                location_id INTEGER,
                hourly_data_id INTEGER,
                value FLOAT
            )
        """))
        #cities
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS cities (
                id SERIAL PRIMARY KEY,
                name VARCHAR,
                country_id INTEGER
            )
        """))
        #daily_data
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS daily_data (
                id SERIAL PRIMARY KEY,
                time DATE,
                location_id INTEGER,
                weather_id INTEGER
            )
        """))
        #weather_icons
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS weather_icons (
                id SERIAL PRIMARY KEY,
                code INTEGER
            )
        """))

        conn.commit()
        print("Baza danych została zainicjalizowana, tabele utworzone.")