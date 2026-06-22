import os
import tkinter as tk
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.dates as mdates
import geopandas as gpd
import numpy as np
from main import resource_path
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

def plot_weather_data(df, chart_type1, label1, color1, chart_type2=None, label2=None, color2=None):
    """
    Rysuje wykres jedno- lub dwu-seriowy na podstawie danych z DataFrame.
    
    Argumenty:
    - df (pd.DataFrame): Zawiera kolumnę 'time' (oś X) oraz 'value' (lub wartości pomiarów).
    - chart_type1 / chart_type2 (str): 'Line', 'Bar', 'Scatter'
    - label1 / label2 (str): Etykieta do legendy (np. 'Temperatura', 'Opad', 'Prędkość wiatru')
    - color1 / color2 (str): Kod HEX koloru (np. '#ff0000', '#0000ff')
    """

    if df is None or df.empty:
        print("Brak danych do wyświetlenia na wykresie.")
        return

    df = df.copy()
    df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
    df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1], errors='coerce')

    if chart_type2 and len(df.columns) > 2:
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2], errors='coerce')

    # Dynamiczny startowy rozmiar okna: im więcej danych, tym szersze okno
    base_width = 10
    if len(df) > 30:
        base_width = min(16, 10 + (len(df) - 30) // 10)

    fig, ax1 = plt.subplots(figsize=(base_width, 6))

    # ---- FUNKCJA POMOCNICZA DO RYSOWANIA ----
    def draw_series(ax, x, y, chart_type, color, label):
        if chart_type == 'Line':
            ax.plot(x, y, color=color, linewidth=2, label=label, marker='o')
        elif chart_type == 'Bar':
            x_numeric = mdates.date2num(x)

            if len(x_numeric) > 1:
                mean_delta = pd.Series(x_numeric).diff().mean()
                bar_width = mean_delta * 0.8
            else:
                bar_width = 0.75

            ax.bar(x, y, color=color, alpha=0.7, label=label, width=bar_width)
        elif chart_type == 'Scatter':
            ax.scatter(x, y, color=color, s=40, label=label, alpha=0.8)

    # ---- PIERWSZA SERIA DANYCH (Oś Y po lewej) ----
    # Jeśli df ma uproszczoną strukturę dwóch kolumn 'time' i 'value'
    y1_data = df.iloc[:, 1] # Druga kolumna jako wartości pierwszej serii
    
    draw_series(ax1, df['time'], y1_data, chart_type1, color1, label1)
    
    ax1.set_xlabel("Date", fontsize=11, labelpad=10)
    ax1.set_ylabel(label1, fontsize=11)
    ax1.tick_params(axis='y')
    ax1.grid(True, linestyle='--', alpha=0.5)

    label1 = label1 if len(df) <= 2 else f"Series 1 ({label1})"

    # ---- DRUGA SERIA DANYCH (Oś Y po prawej – opcjonalna) ----
    # Sprawdzamy czy przekazano parametry dla drugiego wykresu i czy df ma trzecią kolumnę
    if chart_type2 and len(df.columns) > 2:
        ax2 = ax1.twinx()  # Wspólna oś X, nowa oś Y
        y2_data = df.iloc[:, 2] # Trzecia kolumna jako wartości drugiej serii
        
        draw_series(ax2, df['time'], y2_data, chart_type2, color2, label2)
        
        ax2.set_ylabel(label2, fontsize=11)
        ax2.tick_params(axis='y')
        
        label2 = f"Series 2 ({label2})"
        
        # Łączenie legend z obu osi w jedno okienko
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    else:
        ax1.legend(loc='upper left')

    # Formatowanie wyglądu strefy czasu na osi X
    fig.autofmt_xdate()
    plt.title("Weather Data Visualization", fontsize=14, pad=15)
    
    # Wyświetlenie wykresu w osobnym oknie Tkinter
    manager = plt.get_current_fig_manager()
    icon_path = resource_path("img/icon.png")
    img = tk.PhotoImage(file=icon_path, master=manager.window)
    manager.window.iconphoto(False, img)

    plt.tight_layout()
    plt.show()

def plot_wind_map(df, color='#ff0000'):
    """
    Rysuje mapę świata z zaznaczonymi strzałkami kierunku wiatru.
    
    Argumenty:
    - df (pd.DataFrame): DataFrame zawierający kolumny 'latitude', 'longitude', 'wind_direction'
    - color (str): Kolor strzałek (np. nazwa lub kod HEX)
    """

    if df is None or df.empty:
        print("Brak danych wiatru do wyświetlenia na mapie.")
        return

    # 1. Obliczanie składowych wektora (U, V) na podstawie kąta w stopniach
    angles_rad = np.radians(df['wind_direction'])
    
    # Składowa X (wschód-zachód) oraz Y (północ-południe)
    # Mnożymy przez -1, ponieważ strzałka ma pokazywać DOKĄD wiatr wieje, a nie skąd.
    u = -np.sin(angles_rad)
    v = -np.cos(angles_rad)

    # 2. Inicjalizacja wykresu i wczytanie lokalnej mapy świata
    _, ax = plt.subplots(figsize=(14, 8))
    
    # Ładujemy uproszczone granice państw/kontynentów
    local_map_path = resource_path("data/world_map.shp")
    world = gpd.read_file(local_map_path)
    
    # Rysujemy mapę jako tło (jasnoszare kontynenty, białe granice)
    world.plot(ax=ax, color='#e0e0e0', edgecolor='white')

    # 3. Naniesienie strzałek za pomocą funkcji quiver
    # Argumenty: X (long), Y (lat), U (składowa X), V (składowa Y)
    ax.quiver(
        df['longitude'], 
        df['latitude'], 
        u, 
        v, 
        color=color,
        scale=80,           # Skala długości strzałek
        width=0.002,        # Grubość linii strzałki
        headwidth=3,        # Szerokość grotu
        headlength=4,       # Długość grotu
        headaxislength=3.5, # Wcięcie grotu
        pivot='middle'      # Punkt obrotu strzałki ustawiony na jej środku
    )

    # 4. Estetyka wykresu
    ax.set_title("Wind Direction Map", fontsize=14, pad=15)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    
    # Ustawienie limitów mapy na pełny zakres współrzędnych geograficznych
    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    
    # Dodanie delikatnej siatki geograficznej
    ax.grid(True, linestyle=':', alpha=0.5)

    manager = plt.get_current_fig_manager()
    icon_path = resource_path("img/icon.png")
    img = tk.PhotoImage(file=icon_path, master=manager.window)
    manager.window.iconphoto(False, img)

    plt.tight_layout()
    plt.show()

def plot_weather_map(df, color='#ff0000'):
    """
    Rysuje mapę świata z ikonami pogodowymi w odpowiednich lokalizacjach.
    
    Argument:
    - df (pd.DataFrame): Zawiera kolumny 'latitude', 'longitude', 'weather_code'
    - color (str): Kolor kropek (jeśli ikona nie istnieje, np. '#ff0000')
    """

    if df is None or df.empty:
        print("Brak danych pogodowych do wyświetlenia na mapie.")
        return

    # 1. Ładowanie lokalnej mapy świata
    local_map_path = resource_path("data/world_map.shp")
    world = gpd.read_file(local_map_path)

    # 2. Inicjalizacja wykresu
    _, ax = plt.subplots(figsize=(14, 8))
    world.plot(ax=ax, color="#f0f0f0", edgecolor='white')

    # 3. Iteracja po wierszach DataFrame i nanoszenie obrazków
    for _, row in df.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        code = int(row['weather_code']) if not pd.isna(row['weather_code']) else 0

        # Ścieżka do konkretnego obrazka, np. img/icons/3.png
        img_path = resource_path(os.path.join("img", "icons", f"{code}.png"))

        if os.path.exists(img_path):
            try:
                # Wczytanie obrazka i ustalenie jego skali (zoom)
                image = plt.imread(img_path)
                image_box = OffsetImage(image, zoom=0.3) 
                
                # Przypięcie obrazka do współrzędnych (lon, lat)
                ab = AnnotationBbox(
                    image_box, 
                    (lon, lat), 
                    frameon=False,
                    zorder=4
                )
                ax.add_artist(ab)
            except Exception as e:
                print(f"[Wypis] Nie udało się wyrenderować ikony dla kodu {code}: {e}")
        else:
            ax.scatter(lon, lat, color=color, s=20, zorder=3)
            print(f"[Ostrzeżenie] Brak pliku graficznego: {img_path}")

    # 4. Estetyka mapy
    ax.set_title("Weather Map", fontsize=14, pad=15)
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    ax.set_xlim(-180, 180)
    ax.set_ylim(-90, 90)
    ax.grid(True, linestyle=':', alpha=0.5)

    manager = plt.get_current_fig_manager()
    icon_path = resource_path("img/icon.png")
    img = tk.PhotoImage(file=icon_path, master=manager.window)
    manager.window.iconphoto(False, img)

    plt.tight_layout()
    plt.show()