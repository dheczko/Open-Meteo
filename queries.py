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