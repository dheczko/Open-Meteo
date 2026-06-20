import tkinter as tk


# Functions

def toggle_all_days():
    global all_selected

    all_selected = not all_selected

    for var in days_vars.values():
        var.set(all_selected)
    
    toggle_all_button.config(
        text="ALL" if not all_selected else "NONE"
    )


# Interface sections

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


if __name__ == "__main__":
    # Main window

    root = tk.Tk()
    root.title("Open-Meteo Data Visualizer")
    root.geometry("520x750")

    # Sections

    create_time_section(root)
    create_week_days_section(root)

    root.mainloop()
