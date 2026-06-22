import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

engine = create_engine("postgresql://postgres:HasloDoSerwera@localhost:5432/weather_test")


def get_weather_stats(table_name, interval, date_from, date_to, location_id, week_days, statistic):
    """
    Pobiera zagregowane dane pogodowe z bazy danych PostgreSQL.
    
    Argumenty:
    - table_name (str): 'temperature', 'wind_speed' lub 'rain'
    - interval (str): 'Year', 'Month' lub 'Day'
    - date_from (str): Data początkowa w formacie 'YYYY-MM-DD'
    - date_to (str): Data końcowa w formacie 'YYYY-MM-DD'
    - location_id (int): ID lokalizacji
    - week_days (list): Lista cyfr (0-niedziela, 1-poniedziałek, ..., 6-sobota)
    - statistic (str): 'avg', 'max' lub 'min'
    
    Zwraca:
    - pd.DataFrame z kolumnami: 'time' oraz 'value'
    """
    # walidacja nazwy tabeli i funkcji statystycznej
    allowed_tables = ["temperature", "rain", "wind_speed"]
    allowed_stats = ["avg", "max", "min"]
    allowed_intervals = ["Year", "Month", "Day"]
    
    if table_name not in allowed_tables:
        raise ValueError(f"Niepoprawna nazwa tabeli. Wybierz z: {allowed_tables}")
    if statistic.lower() not in allowed_stats:
        raise ValueError(f"Niepoprawna statystyka. Wybierz z: {allowed_stats}")
    if interval not in allowed_intervals:
        raise ValueError(f"Niepoprawny interwał. Wybierz z: {allowed_intervals}")
        
    stat_func = statistic.upper()
    
    # Określenie sposobu grupowania czasu (obcinanie daty do początku roku/miesiąca/dnia)
    # PostgreSQL DATE_TRUNC zwraca TIMESTAMP, rzutujemy na DATE
    if interval == "Year":
        time_grouping = "DATE_TRUNC('year', hd.time)::date"
    elif interval == "Month":
        time_grouping = "DATE_TRUNC('month', hd.time)::date"
    else: # Day
        time_grouping = "hd.time::date"

    # Jeżeli lista jest pusta, zwracamy pusty DataFrame
    if not week_days:
        return pd.DataFrame(columns=["time", "value"])
        
    # Budowanie dynamicznego zapytania SQL
    query_string = f"""
        SELECT 
            {time_grouping} AS time,
            {stat_func}(t.value) AS value
        FROM {table_name} t
        JOIN hourly_data hd ON t.hourly_data_id = hd.id
        WHERE t.location_id = :location_id
          AND hd.time::date BETWEEN :date_from AND :date_to
          AND EXTRACT(DOW FROM hd.time) IN :week_days
        GROUP BY {time_grouping}
        ORDER BY time ASC;
    """
    
    with engine.connect() as conn:
        result = conn.execute(
            text(query_string),
            {
                "location_id": location_id,
                "date_from": date_from,
                "date_to": date_to,
                "week_days": tuple(week_days)
            }
        )
        
        # Pobieramy wyniki jako DataFrame
        df = pd.DataFrame(result.fetchall(), columns=["time", "value"])
        df['time'] = pd.to_datetime(df['time'])

        return df
    
def get_combined_weather_stats(table1, statistic1, table2, statistic2, interval, date_from, date_to, location_id, week_days):
    """
    Pobiera jednocześnie dwie serie danych pogodowych złączone po wspólnej osi czasu.
    
    Argumenty:
    - table1 / table2 (str): 'temperature', 'rain' lub 'wind_speed'
    - statistic1 / statistic2 (str): 'avg', 'max' lub 'min'
    - interval (str): 'Year', 'Month' lub 'Day'
    - date_from / date_to (str): Zakres dat 'YYYY-MM-DD'
    - location_id (int): ID lokalizacji
    - week_days (list): Lista dni tygodnia (0-niedziela, 6-sobota)
    
    Zwraca:
    - pd.DataFrame z kolumnami: 'time', 'value1', 'value2'
    """

    # Walidacja danych wejściowych
    allowed_tables = ["temperature", "rain", "wind_speed"]
    allowed_stats = ["avg", "max", "min"]
    
    if table1 not in allowed_tables or table2 not in allowed_tables:
        raise ValueError(f"Niepoprawna nazwa tabeli. Wybierz z: {allowed_tables}")
    if statistic1.lower() not in allowed_stats or statistic2.lower() not in allowed_stats:
        raise ValueError(f"Niepoprawna statystyka. Wybierz z: {allowed_stats}")

    stat1_func = statistic1.upper()
    stat2_func = statistic2.upper()

    # Określenie agregacji czasu (PostgreSQL DATE_TRUNC)
    if interval == "Year":
        time_grouping = "DATE_TRUNC('year', hd.time)::date"
    elif interval == "Month":
        time_grouping = "DATE_TRUNC('month', hd.time)::date"
    else: # Day
        time_grouping = "hd.time::date"

    if not week_days:
        return pd.DataFrame(columns=["time", "value1", "value2"])

    # Zapytanie SQL: Wyciągamy dane z hourly_data, a następnie dołączamy
    # obie tabele pomiarowe, filtrując je po tej samej lokalizacji.
    query_string = f"""
        SELECT 
            {time_grouping} AS time,
            {stat1_func}(t1.value) AS value1,
            {stat2_func}(t2.value) AS value2
        FROM hourly_data hd
        JOIN {table1} t1 ON t1.hourly_data_id = hd.id AND t1.location_id = :location_id
        JOIN {table2} t2 ON t2.hourly_data_id = hd.id AND t2.location_id = :location_id
        WHERE hd.time::date BETWEEN :date_from AND :date_to
          AND EXTRACT(DOW FROM hd.time) IN :week_days
        GROUP BY {time_grouping}
        ORDER BY time ASC;
    """

    with engine.connect() as conn:
        result = conn.execute(
            text(query_string),
            {
                "location_id": location_id,
                "date_from": date_from,
                "date_to": date_to,
                "week_days": tuple(week_days)
            }
        )
        
        # Tworzymy DataFrame
        df = pd.DataFrame(result.fetchall(), columns=["time", "value1", "value2"])
        df['time'] = pd.to_datetime(df['time'])
        
        return df

def get_dominant_wind_direction(date_from, date_to, week_days):
    """
    Wylicza przeważający kierunek wiatru dla wszystkich lokalizacji w podanym zakresie dat
    i wybranych dniach tygodnia.
    
    Argumenty:
    - date_from (str): Data początkowa w formacie 'YYYY-MM-DD'
    - date_to (str): Data końcowa w formacie 'YYYY-MM-DD'
    - week_days (list): Lista cyfr oznaczających dni tygodnia (0-niedziela, 6-sobota)
    
    Zwraca:
    - pd.DataFrame z kolumnami: 'latitude', 'longitude', 'wind_direction'
    """

    # Zabezpieczenie na wypadek pustej listy dni tygodnia
    if not week_days:
        return pd.DataFrame(columns=["latitude", "longitude", "wind_direction"])

    query = text("""
        SELECT 
            l.latitude,
            l.longitude,
            MODE() WITHIN GROUP (ORDER BY wd.value) AS wind_direction
        FROM wind_direction wd
        JOIN hourly_data hd ON wd.hourly_data_id = hd.id
        JOIN locations l ON wd.location_id = l.id
        WHERE hd.time::date BETWEEN :date_from AND :date_to
          AND EXTRACT(DOW FROM hd.time) IN :week_days
        GROUP BY l.id, l.latitude, l.longitude;
    """)

    with engine.connect() as conn:
        result = conn.execute(
            query, 
            {
                "date_from": date_from,
                "date_to": date_to,
                "week_days": tuple(week_days)
            }
        )
        
        # Tworzymy DataFrame z wynikami
        df = pd.DataFrame(
            result.fetchall(), 
            columns=["latitude", "longitude", "wind_direction"]
        )
        
        # Konwertujemy kierunek wiatru na liczby całkowite (stopnie)
        if not df.empty:
            df["wind_direction"] = df["wind_direction"].astype(int)
            
        return df

def get_weather_codes(target_date):
    """
    Pobiera kody pogodowe dla wszystkich lokalizacji w wybranym dniu.
    
    Argument:
    - target_date (str): Data w formacie 'YYYY-MM-DD'
    
    Zwraca:
    - pd.DataFrame z kolumnami: 'latitude', 'longitude', 'weather_code'
    """

    query = text("""
        SELECT 
            l.latitude,
            l.longitude,
            wi.code AS weather_code
        FROM daily_data dd
        JOIN locations l ON dd.location_id = l.id
        LEFT JOIN weather_icons wi ON dd.weather_id = wi.id
        WHERE dd.time = :target_date;
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"target_date": target_date})
        
        # Tworzymy DataFrame z wynikami
        df = pd.DataFrame(
            result.fetchall(), 
            columns=["latitude", "longitude", "weather_code"]
        )
            
        return df