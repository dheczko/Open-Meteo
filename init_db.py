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
        #countries
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS countries (
                id SERIAL PRIMARY KEY,
                name VARCHAR
            )
        """))
        #logs
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS logs (
                id SERIAL PRIMARY KEY,
                time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message VARCHAR(255),
                state VARCHAR(255)
            )
        """))
        #-----------------------------------------------------------------------------------------------------------
        """
        Relacje między tabelami:
        """
        conn.execute(text("""
            ALTER TABLE temperature
            ADD CONSTRAINT fk_temperature_location
            FOREIGN KEY (location_id) REFERENCES locations(id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_temperature_hourly_data
            FOREIGN KEY (hourly_data_id) REFERENCES hourly_data(id)
            ON DELETE CASCADE;
        """))
        conn.execute(text("""
            ALTER TABLE rain
            ADD CONSTRAINT fk_rain_location
            FOREIGN KEY (location_id) REFERENCES locations(id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_rain_hourly_data
            FOREIGN KEY (hourly_data_id) REFERENCES hourly_data(id)
            ON DELETE CASCADE;
        """))
        conn.execute(text("""
            ALTER TABLE wind_speed
            ADD CONSTRAINT fk_wind_speed_location
            FOREIGN KEY (location_id) REFERENCES locations(id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_wind_speed_hourly_data
            FOREIGN KEY (hourly_data_id) REFERENCES hourly_data(id)
            ON DELETE CASCADE;
        """))
        conn.execute(text("""
            ALTER TABLE wind_direction
            ADD CONSTRAINT fk_wind_direction_location
            FOREIGN KEY (location_id) REFERENCES locations(id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_wind_direction_hourly_data
            FOREIGN KEY (hourly_data_id) REFERENCES hourly_data(id)
            ON DELETE CASCADE;
        """))
        conn.execute(text("""
            ALTER TABLE daily_data
            ADD CONSTRAINT fk_daily_data_location
            FOREIGN KEY (location_id) REFERENCES locations(id)
            ON DELETE CASCADE,
            ADD CONSTRAINT fk_daily_data_weather
            FOREIGN KEY (weather_id) REFERENCES weather_icons(id)
            ON DELETE CASCADE;
        """))
        conn.execute(text("""
            ALTER TABLE locations
            ADD CONSTRAINT fk_locations_city
            FOREIGN KEY (city_id) REFERENCES cities(id)
            ON DELETE CASCADE;
        """))
        conn.execute(text("""
            ALTER TABLE cities
            ADD CONSTRAINT fk_cities_country
            FOREIGN KEY (country_id) REFERENCES countries(id)
            ON DELETE CASCADE;
        """))
        #-----------------------------------------------------------------------------------------------------------
        """
        Wstawiamy domyślne lokalizacje, miasta i kraje 
        """

        count_countries = conn.execute(text("SELECT COUNT(*) FROM countries")).scalar()
        if count_countries == 0:
            countries = [
                "Polska",
                "Wielka Brytania",
                "Francja",
                "Japonia",
                "Stany Zjednoczone",
                "Włochy",
                "Finlandia",
                "Brazylia",
                "Egipt",
                "Indie"
            ]
            for name in countries:
                conn.execute(
                    text("INSERT INTO countries (name) VALUES (:name)"),
                    {"name": name}
                )
            conn.commit()
            print("Dodano kraje.")
        
        #sprawdzamy czy tabela cities jest pusta, jeżeli jest to dodajemy miasta 
        count_cities = conn.execute(text("SELECT COUNT(*) FROM cities")).scalar()
        if count_cities == 0:
            cities_data = [
                ("Kraków", "Polska", 50.0647, 19.9450),
                ("Londyn", "Wielka Brytania", 51.5074, -0.1278),
                ("Paryż", "Francja", 48.8566, 2.3522),
                ("Tokio", "Japonia", 35.6895, 139.6917),
                ("Waszyngton", "Stany Zjednoczone", 38.9072, -77.0369),
                ("Rzym", "Włochy", 41.9028, 12.4964),
                ("Helsinki", "Finlandia", 60.1699, 24.9384),
                ("Rio de Janeiro", "Brazylia", -22.9068, -43.1729),
                ("Kair", "Egipt", 30.0444, 31.2357),
                ("New Delhi", "Indie", 28.6139, 77.2090),
            ]
            for city_name, country_name, lat, lon in cities_data:
                result = conn.execute(
                    text("SELECT id FROM countries WHERE name = :name"),
                    {"name": country_name}
                )
                country_id = result.fetchone()[0]

                result = conn.execute(
                    text("INSERT INTO cities (name, country_id) VALUES (:name, :country_id) RETURNING id"),
                    {"name": city_name, "country_id": country_id}
                )
                city_id = result.fetchone()[0]

                conn.execute(
                    text("INSERT INTO locations (city_id, latitude, longitude) VALUES (:city_id, :lat, :lon)"),
                    {"city_id": city_id, "lat": lat, "lon": lon}
                )

        conn.commit()
        print("Baza danych została zainicjalizowana, tabele utworzone.")