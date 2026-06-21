import tkinter as tk
from tkinter import colorchooser


# Functions

def toggle_all_days():
    global all_selected

    all_selected = not all_selected

    for var in days_vars.values():
        var.set(all_selected)
    
    toggle_all_button.config(
        text="ALL" if not all_selected else "NONE"
    )


def choose_color():
    global chart_color, chart_color_text

    color = colorchooser.askcolor(title="Choose plot color")

    if color[1]:
        chart_color.config(
            text=color[1],
            background=color[1]
        )
        chart_color_text = color[1]


def visualize_data():
    selected_days = [
        (idx + 1) % 7 for idx, var in enumerate(days_vars.values()) if var.get()
    ]

    interval_value = interval.get() if interval else None
    date_from_value = date_from.get() if date_from else None
    date_to_value = date_to.get() if date_to else None

    data = {
        "interval": interval_value,
        "date_from": date_from_value,
        "date_to": date_to_value,

        "location_id": location_id,

        "week_days": selected_days,

        "temperature_unit": temperature.get(),
        "wind_unit": wind.get(),
        "rain_unit": rain.get(),

        "statistic": statistic.get(),
        "chart_type": chart_type.get(),

        "color": chart_color.cget("text"),

        "visualization_type": visualization_option
    }

    print(data)


def rerender_all_frames():
    time_frame.destroy()
    location_frame.destroy()
    days_frame.destroy()
    units_frame.destroy()
    chart_frame.destroy()

    submit_button.destroy()

    build_frames()

def build_frames():
    global submit_button

    create_time_section(root)
    create_location_section(root)
    create_week_days_section(root)
    create_units_section(root)
    create_chart_options_section(root)

    submit_button = tk.Button(
        root,
        text="Visualize data",
        command=visualize_data
    )
    submit_button.pack(pady=15)


# Interface sections

def create_dropdown_row(root):
    global visualization_type, visualization_option

    visualization_options = {
        "🌡 Temperature": ["temperature"],
        "💨 Wind speed": ["wind_speed"],
        "🧭 Wind direction": ["wind_direction"],
        "🌧 Rain": ["rain"],
        "🌡 & 🌧 Temperature & Rain": ["temperature", "rain"],
        "🌤 Weather forecast": ["weather_forecast"]
    }

    options = list(visualization_options.keys())

    visualization_type = tk.StringVar(value=options[0])
    visualization_option = visualization_options[options[0]]

    row = tk.Frame(root)
    row.pack(fill="x", pady=3)

    # Label
    tk.Label(
        row,
        text="Visualization type",
        width=13,
        anchor="w"
    ).pack(side="left")

    # Menubutton
    menu_button = tk.Menubutton(
        row,
        textvariable=visualization_type,
        relief="raised",
        anchor="w",
        width=20
    )
    menu_button.pack(side="left")

    # Dropdown menu
    menu = tk.Menu(menu_button, tearoff=0)
    menu_button.config(menu=menu)

    def set_value(value):
        global visualization_option

        visualization_type.set(value)
        visualization_option = visualization_options[value]
        rerender_all_frames()

    for opt in options:
        menu.add_command(
            label=opt,
            command=lambda v=opt: set_value(v)
        )


def create_time_section(root):
    global interval, date_from, date_to, time_frame

    if "weather_forecast" in visualization_option or "wind_direction" in visualization_option:
        interval = None
        date_from = None
        date_to = None
        return

    time_frame = tk.LabelFrame(root, text="Time")
    time_frame.pack(padx=15, pady=5, fill="x")

    # Time interval

    if "interval" not in globals() or interval is None:
        interval = tk.StringVar(value="Day")

    row0 = tk.Frame(time_frame)
    row0.pack(fill="x", pady=3)

    tk.Label(row0, text="Time interval", width=15, anchor="w").pack(side="left")

    tk.Radiobutton(
        row0,
        text="Year",
        variable=interval,
        value="Year"
    ).pack(side="left", padx=5)

    tk.Radiobutton(
        row0,
        text="Month",
        variable=interval,
        value="Month"
    ).pack(side="left", padx=5)

    tk.Radiobutton(
        row0,
        text="Day",
        variable=interval,
        value="Day"
    ).pack(side="left", padx=5)

    # From date

    row1 = tk.Frame(time_frame)
    row1.pack(fill="x", pady=3)

    tk.Label(row1, text="From", width=15, anchor="w").pack(side="left")

    date_from = tk.Entry(row1)
    date_from.insert(0, "YYYY-MM-DD")
    date_from.pack(side="left")

    # To date

    row2 = tk.Frame(time_frame)
    row2.pack(fill="x", pady=3)

    tk.Label(row2, text="To", width=15, anchor="w").pack(side="left")

    date_to = tk.Entry(row2)
    date_to.insert(0, "YYYY-MM-DD")
    date_to.pack(side="left")


def create_location_section(root):
    global location_id, location_name, location_frame

    if "weather_forecast" in visualization_option or "wind_direction" in visualization_option:
        return

    # Dummy data (TODO: replace with data from Database)
    locations = {
        0: "New York",
        1: "London",
        2: "Tokyo",
        3: "Sydney",
        4: "Paris"
    }

    options = list(locations.keys())

    if "location_id" not in globals():
        location_id = options[0]
    if "location_name" not in globals():
        location_name = tk.StringVar(value=locations[location_id])

    location_frame = tk.LabelFrame(root, text="Location")
    location_frame.pack(padx=15, pady=5, fill="x")

    row = tk.Frame(location_frame)
    row.pack(fill="x", pady=3)

    # Label
    tk.Label(
        row,
        text="Location",
        width=13,
        anchor="w"
    ).pack(side="left")

    # Menubutton
    menu_button = tk.Menubutton(
        row,
        textvariable=location_name,
        relief="raised",
        anchor="w",
        width=20
    )
    menu_button.pack(side="left")

    # Dropdown menu
    menu = tk.Menu(menu_button, tearoff=0)
    menu_button.config(menu=menu)

    def set_value(value):
        global location_id, location_name
        location_id = value
        location_name.set(locations[value])

    for opt in options:
        menu.add_command(
            label=locations[opt],
            command=lambda v=opt: set_value(v)
        )


def create_week_days_section(root):
    global days_vars, all_selected, toggle_all_button, days_frame

    if "weather_forecast" in visualization_option or "wind_direction" in visualization_option:
        days_vars = {}
        return

    days_frame = tk.LabelFrame(root, text="Week days")
    days_frame.pack(padx=15, pady=5, fill="x")

    if "days_vars" not in globals():
        days_vars = {}

    week_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    for col in range(2):
        days_frame.grid_columnconfigure(col, weight=1)

    for i, name in enumerate(week_days):
        set_value = True
        if len(days_vars) > 0 and name in days_vars:
            set_value = days_vars[name].get()
        
        var = tk.BooleanVar(value=set_value)
        days_vars[name] = var

        tk.Checkbutton(
            days_frame,
            text=name,
            variable=var,
            anchor="w",
        ).grid(
            row=i // 2,
            column=i % 2,
            sticky="we",
            padx=10,
            pady=2
        )

    all_selected = any(var.get() for var in days_vars.values())

    toggle_all_button = tk.Button(
        days_frame,
        text="NONE" if all_selected else "ALL",
        width=10,
        command=toggle_all_days
    )
    toggle_all_button.grid(
        row=4,
        column=0,
        columnspan=2,
        padx=10,
        sticky="w"
    )


def create_units_section(root):
    global temperature, wind, rain, units_frame
    
    units_frame = tk.LabelFrame(root, text="Units")
    units_frame.pack(padx=15, pady=5, fill="x")

    if "temperature" not in globals():
        temperature = tk.StringVar(value="C")
    if "wind" not in globals():
        wind = tk.StringVar(value="km/h")
    if "rain" not in globals():
        rain = tk.StringVar(value="mm")

    # Temperature

    if "temperature" in visualization_option:
        row0 = tk.Frame(units_frame)
        row0.pack(fill="x", pady=3)

        tk.Label(row0, text="Temperature", width=15, anchor="w").pack(side="left")

        tk.Radiobutton(
            row0,
            text="°C",
            variable=temperature,
            value="C"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            row0,
            text="°F",
            variable=temperature,
            value="F"
        ).pack(side="left", padx=5)

    # Wind

    if "wind_speed" in visualization_option:
        row1 = tk.Frame(units_frame)
        row1.pack(fill="x", pady=3)

        tk.Label(row1, text="Wind", width=15, anchor="w").pack(side="left")

        tk.Radiobutton(
            row1,
            text="km/h",
            variable=wind,
            value="km/h"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            row1,
            text="knots",
            variable=wind,
            value="knots"
        ).pack(side="left", padx=5)

    # Rain

    if "rain" in visualization_option:
        row2 = tk.Frame(units_frame)
        row2.pack(fill="x", pady=3)

        tk.Label(row2, text="Rain", width=15, anchor="w").pack(side="left")

        tk.Radiobutton(
            row2,
            text="mm",
            variable=rain,
            value="mm"
        ).pack(side="left", padx=5)

        tk.Radiobutton(
            row2,
            text="inch",
            variable=rain,
            value="inch"
        ).pack(side="left", padx=5)


def create_chart_options_section(root):
    global statistic, chart_type, chart_color, chart_color_text, chart_frame
    
    chart_frame = tk.LabelFrame(root, text="Chart options")
    chart_frame.pack(padx=15, pady=5, fill="x")

    if "statistic" not in globals():
        statistic = tk.StringVar(value="avg")
    if "chart_type" not in globals():
        chart_type = tk.StringVar(value="Line")

    # Statistic

    if "weather_forecast" not in visualization_option and "wind_direction" not in visualization_option:
        row0 = tk.Frame(chart_frame)
        row0.pack(fill="x", pady=3)

        tk.Label(row0, text="Statistic", width=12, anchor="w").pack(side="left")

        for opt in ["avg", "max", "min"]:
            tk.Radiobutton(
                row0,
                text=opt,
                variable=statistic,
                value=opt
            ).pack(side="left", padx=5)

    # Chart type

    if "weather_forecast" not in visualization_option and "wind_direction" not in visualization_option:
        row1 = tk.Frame(chart_frame)
        row1.pack(fill="x", pady=3)

        tk.Label(row1, text="Chart type", width=12, anchor="w").pack(side="left")

        for opt in ["Line", "Bar", "Scatter"]:
            tk.Radiobutton(
                row1,
                text=opt,
                variable=chart_type,
                value=opt
            ).pack(side="left", padx=5)

    # Color

    row2 = tk.Frame(chart_frame)
    row2.pack(fill="x", pady=5)

    tk.Label(row2, text="Color", width=12, anchor="w").pack(side="left")

    tk.Button(
        row2,
        text="Choose color",
        command=choose_color
    ).pack(side="left", padx=5)

    if "chart_color_text" not in globals():
        chart_color_text = "#ff0000"

    chart_color = tk.Label(
        row2,
        text=chart_color_text,
        background=chart_color_text,
        width=12
    )
    chart_color.pack(side="left", padx=10)


if __name__ == "__main__":
    # Main window

    root = tk.Tk()
    root.title("Open-Meteo Data Visualizer")
    root.geometry("520x750")

    create_dropdown_row(root)
    build_frames()

    root.mainloop()
