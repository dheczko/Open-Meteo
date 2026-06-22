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