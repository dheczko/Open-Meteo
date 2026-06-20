import tkinter as tk


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


if __name__ == "__main__":
    # Main window

    root = tk.Tk()
    root.title("Open-Meteo Data Visualizer")
    root.geometry("520x750")

    # Sections

    create_time_section(root)

    root.mainloop()
