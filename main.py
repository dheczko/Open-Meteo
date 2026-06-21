import tkinter as tk
from tkinter import colorchooser, messagebox
from datetime import datetime


# Functions

def validate_date(date_str):
    if date_str == "YYYY-MM-DD" or not date_str:
        return False
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def get_title(text):
    return text[0].upper() + text[1:].replace("_", " ")


def toggle_all_days():
    global all_selected

    all_selected = not all_selected

    for var in days_vars.values():
        var.set(all_selected)
    
    toggle_all_button.config(
        text="ALL" if not all_selected else "NONE"
    )


def choose_color1():
    global chart_color1, chart_color_text1

    color = colorchooser.askcolor(title="Choose plot color")

    if color[1]:
        chart_color1.config(
            text=color[1],
            background=color[1]
        )
        chart_color_text1 = color[1]


def choose_color2():
    global chart_color2, chart_color_text2

    color = colorchooser.askcolor(title="Choose plot color")

    if color[1]:
        chart_color2.config(
            text=color[1],
            background=color[1]
        )
        chart_color_text2 = color[1]


def visualize_data():
    # Validate date inputs

    if date_from:
        date_from_value = date_from.get()
        if not validate_date(date_from_value):
            messagebox.showerror("Invalid Date", f"Invalid {"'From' " if date_to else ""}date: {date_from_value}\nPlease use format YYYY-MM-DD")
            return
    else:
        date_from_value = None

    if date_to:
        date_to_value = date_to.get()
        if not validate_date(date_to_value):
            messagebox.showerror("Invalid Date", f"Invalid 'To' date: {date_to_value}\nPlease use format YYYY-MM-DD")
            return
    else:
        date_to_value = None

    # Get data

    selected_days = [
        (idx + 1) % 7 for idx, var in enumerate(days_vars.values()) if var.get()
    ]

    interval_value = interval.get() if interval else None

    statistic2_value = statistic2.get() if statistic2 else None
    chart_type2_value = chart_type2.get() if chart_type2 else None
    color2_value = chart_color2.cget("text") if chart_color2 else None

    data = {
        "interval": interval_value,
        "date_from": date_from_value,
        "date_to": date_to_value,

        "location_id": location_id,

        "week_days": selected_days,

        "temperature_unit": temperature.get(),
        "wind_unit": wind.get(),
        "rain_unit": rain.get(),

        "statistic1": statistic1.get(),
        "chart_type1": chart_type1.get(),
        "color1": chart_color1.cget("text"),

        "statistic2": statistic2_value,
        "chart_type2": chart_type2_value,
        "color2": color2_value,

        "visualization_type": visualization_option
    }

    print(data)


def rerender_all_frames():
    time_frame.destroy()
    location_frame.destroy()
    days_frame.destroy()
    units_frame.destroy()
    chart_frame1.destroy()
    chart_frame2.destroy()
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

    time_frame = tk.LabelFrame(root, text="Time")
    time_frame.pack(padx=15, pady=5, fill="x")

    if "weather_forecast" in visualization_option or "wind_direction" in visualization_option:
        interval = None
        date_to = None
        
        row = tk.Frame(time_frame)
        row.pack(fill="x", pady=3)
        
        tk.Label(row, text="Date", width=15, anchor="w").pack(side="left")
        
        date_from = tk.Entry(row)
        date_from.insert(0, "")
        date_from.pack(side="left")
        
        return

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
    date_from.insert(0, "")
    date_from.pack(side="left")

    # To date

    row2 = tk.Frame(time_frame)
    row2.pack(fill="x", pady=3)

    tk.Label(row2, text="To", width=15, anchor="w").pack(side="left")

    date_to = tk.Entry(row2)
    date_to.insert(0, "")
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
    global statistic1, chart_type1, chart_color1, chart_color_text1, chart_frame1

    chart_frame1 = tk.LabelFrame(root, text=f"Options ({get_title(visualization_option[0])})")
    chart_frame1.pack(padx=15, pady=5, fill="x")

    if "statistic1" not in globals():
        statistic1 = tk.StringVar(value="avg")
    if "chart_type1" not in globals():
        chart_type1 = tk.StringVar(value="Line")

    # Statistic

    if "weather_forecast" not in visualization_option and "wind_direction" not in visualization_option:
        row0 = tk.Frame(chart_frame1)
        row0.pack(fill="x", pady=3)

        tk.Label(row0, text="Statistic", width=12, anchor="w").pack(side="left")

        for opt in ["avg", "max", "min"]:
            tk.Radiobutton(
                row0,
                text=opt,
                variable=statistic1,
                value=opt
            ).pack(side="left", padx=5)

    # Chart type

    if "weather_forecast" not in visualization_option and "wind_direction" not in visualization_option:
        row1 = tk.Frame(chart_frame1)
        row1.pack(fill="x", pady=3)

        tk.Label(row1, text="Chart type", width=12, anchor="w").pack(side="left")

        for opt in ["Line", "Bar", "Scatter"]:
            tk.Radiobutton(
                row1,
                text=opt,
                variable=chart_type1,
                value=opt
            ).pack(side="left", padx=5)

    # Color

    row2 = tk.Frame(chart_frame1)
    row2.pack(fill="x", pady=5)

    tk.Label(row2, text="Color", width=12, anchor="w").pack(side="left")

    tk.Button(
        row2,
        text="Choose color",
        command=choose_color1
    ).pack(side="left", padx=5)

    if "chart_color_text1" not in globals():
        chart_color_text1 = "#ff0000"

    chart_color1 = tk.Label(
        row2,
        text=chart_color_text1,
        background=chart_color_text1,
        width=12
    )
    chart_color1.pack(side="left", padx=10)

    global statistic2, chart_type2, chart_color2, chart_color_text2, chart_frame2

    chart_frame2 = tk.LabelFrame(root, text=f"Options ({get_title(visualization_option[len(visualization_option) > 1])})")
    chart_frame2.pack(padx=15, pady=5, fill="x")

    if len(visualization_option) > 1:
        create_chart_options_section2()
        return
    
    statistic2 = None
    chart_type2 = None
    chart_color2 = None
    chart_color_text2 = None


def create_chart_options_section2():
    global statistic2, chart_type2, chart_color2, chart_color_text2, chart_frame2

    if "statistic2" not in globals() or statistic2 is None:
        statistic2 = tk.StringVar(value="avg")
    if "chart_type2" not in globals() or chart_type2 is None:
        chart_type2 = tk.StringVar(value="Bar")

    # Statistic

    if "weather_forecast" not in visualization_option and "wind_direction" not in visualization_option:
        row0 = tk.Frame(chart_frame2)
        row0.pack(fill="x", pady=3)

        tk.Label(row0, text="Statistic", width=12, anchor="w").pack(side="left")

        for opt in ["avg", "max", "min"]:
            tk.Radiobutton(
                row0,
                text=opt,
                variable=statistic2,
                value=opt
            ).pack(side="left", padx=5)

    # Chart type

    if "weather_forecast" not in visualization_option and "wind_direction" not in visualization_option:
        row1 = tk.Frame(chart_frame2)
        row1.pack(fill="x", pady=3)

        tk.Label(row1, text="Chart type", width=12, anchor="w").pack(side="left")

        for opt in ["Line", "Bar", "Scatter"]:
            tk.Radiobutton(
                row1,
                text=opt,
                variable=chart_type2,
                value=opt
            ).pack(side="left", padx=5)

    # Color

    row2 = tk.Frame(chart_frame2)
    row2.pack(fill="x", pady=5)

    tk.Label(row2, text="Color", width=12, anchor="w").pack(side="left")

    tk.Button(
        row2,
        text="Choose color",
        command=choose_color2
    ).pack(side="left", padx=5)

    if "chart_color_text2" not in globals() or chart_color_text2 is None:
        chart_color_text2 = "#0000ff"

    chart_color2 = tk.Label(
        row2,
        text=chart_color_text2,
        background=chart_color_text2,
        width=12
    )
    chart_color2.pack(side="left", padx=10)


if __name__ == "__main__":
    # Main window

    root = tk.Tk()
    root.title("Open-Meteo Data Visualizer")
    root.geometry("520x800")

    create_dropdown_row(root)
    build_frames()

    root.mainloop()
