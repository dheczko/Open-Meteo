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
    color = colorchooser.askcolor(title="Choose plot color")

    if color[1]:
        chart_color.config(
            text=color[1],
            background=color[1]
        )


def visualize_data():
    selected_days = [
        day for day, var in days_vars.items() if var.get()
    ]

    data = {
        "interval": interval.get(),
        "date_from": date_from.get(),
        "date_to": date_to.get(),

        "week_days": selected_days,

        "temperature_unit": temperature.get(),
        "wind_unit": wind.get(),
        "rain_unit": rain.get(),

        "statistic": statistic.get(),
        "chart_type": chart_type.get(),

        "color": chart_color.cget("text")
    }

    print(data)


# Interface sections

def create_dropdown_row(root):
    global visualization_type

    options = [
        "Temperature",
        "Wind",
        "Rain"
    ]

    visualization_type = tk.StringVar(value=options[0])

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
        visualization_type.set(value)

    for opt in options:
        menu.add_command(
            label=opt,
            command=lambda v=opt: set_value(v)
        )


def create_time_section(root):
    global interval, date_from, date_to

    time_frame = tk.LabelFrame(root, text="Time")
    time_frame.pack(padx=15, pady=5, fill="x")

    # Time interval

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


def create_week_days_section(root):
    global days_vars, all_selected, toggle_all_button

    days_frame = tk.LabelFrame(root, text="Week days")
    days_frame.pack(padx=15, pady=5, fill="x")

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
        var = tk.BooleanVar(value=True)
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

    all_selected = True

    toggle_all_button = tk.Button(
        days_frame,
        text="NONE",
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
    global temperature, wind, rain
    
    units_frame = tk.LabelFrame(root, text="Units")
    units_frame.pack(padx=15, pady=5, fill="x")

    temperature = tk.StringVar(value="C")
    wind = tk.StringVar(value="km/h")
    rain = tk.StringVar(value="mm")

    # Temperature

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
    global statistic, chart_type, chart_color
    
    chart_frame = tk.LabelFrame(root, text="Chart options")
    chart_frame.pack(padx=15, pady=5, fill="x")

    statistic = tk.StringVar(value="avg")
    chart_type = tk.StringVar(value="Line")

    # Statistic

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

    chart_color = tk.Label(
        row2,
        text="#ff0000",
        background="#ff0000",
        width=12
    )
    chart_color.pack(side="left", padx=10)


if __name__ == "__main__":
    # Main window

    root = tk.Tk()
    root.title("Open-Meteo Data Visualizer")
    root.geometry("520x750")

    # Sections

    create_dropdown_row(root)

    create_time_section(root)
    create_week_days_section(root)
    create_units_section(root)
    create_chart_options_section(root)

    # Submit

    tk.Button(
        root,
        text="Visualize data",
        command=visualize_data
    ).pack(pady=15)


    root.mainloop()
