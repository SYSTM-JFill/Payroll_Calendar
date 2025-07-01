import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import pandas as pd
import holidays
from calendar import monthrange
from ics import Calendar, Event


# === PAY PERIOD GENERATION ===

def generate_pay_periods(start_date, freq, num_periods=26, payday_offset=3):
    periods = []
    current = start_date

    for _ in range(num_periods):
        if freq == "Weekly":
            start = current
            end = current + timedelta(days=6)
            current += timedelta(days=7)

        elif freq == "Bi-weekly":
            start = current
            end = current + timedelta(days=13)
            current += timedelta(days=14)

        elif freq == "Semi-monthly":
            if current.day <= 15:
                start = current.replace(day=1)
                end = current.replace(day=15)
                current = current.replace(day=16)
            else:
                last_day = monthrange(current.year, current.month)[1]
                start = current.replace(day=16)
                end = current.replace(day=last_day)
                next_month = (current.replace(day=1) + timedelta(days=32)).replace(day=1)
                current = next_month

        elif freq == "Monthly":
            year, month = current.year, current.month
            start = current.replace(day=1)
            last_day = monthrange(year, month)[1]
            end = current.replace(day=last_day)
            current = (current.replace(day=1) + timedelta(days=32)).replace(day=1)

        payday = end + timedelta(days=payday_offset)
        periods.append((start, end, payday))

    return periods


# === HOLIDAY CONFLICT CHECK ===

def check_conflicts(periods, region_holidays):
    rows = []
    for start, end, payday in periods:
        is_weekend = payday.weekday() >= 5
        holiday_name = region_holidays.get(payday)
        adjusted_date = payday

        # If payday is on weekend, move back to Friday
        if is_weekend:
            adjusted_date -= timedelta(days=payday.weekday() - 4)  # Friday

        # If holiday, move back one weekday at a time
        if holiday_name:
            while adjusted_date in region_holidays or adjusted_date.weekday() >= 5:
                adjusted_date -= timedelta(days=1)

        note = ""
        if holiday_name and is_weekend:
            note = f"{holiday_name} & Weekend → {adjusted_date.strftime('%Y-%m-%d')}"
        elif holiday_name:
            note = f"{holiday_name} → {adjusted_date.strftime('%Y-%m-%d')}"
        elif is_weekend:
            note = f"Weekend → {adjusted_date.strftime('%Y-%m-%d')}"

        rows.append((
            start.strftime("%Y-%m-%d"),
            end.strftime("%Y-%m-%d"),
            payday.strftime("%Y-%m-%d"),
            payday.strftime("%A"),
            "Yes" if holiday_name else "No",
            "Yes" if is_weekend else "No",
            note
        ))
    return rows



# === GUI ===

class PayrollCalendarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Payroll Calendar Drift Monitor")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self.root, padding=10)
        frm.grid(row=0, column=0, sticky="nsew")

        # Inputs
        ttk.Label(frm, text="Start Date (YYYY-MM-DD):").grid(column=0, row=0)
        self.start_date_entry = ttk.Entry(frm)
        self.start_date_entry.insert(0, datetime.today().strftime("%Y-%m-%d"))
        self.start_date_entry.grid(column=1, row=0)

        ttk.Label(frm, text="Frequency:").grid(column=0, row=1)
        self.freq_cb = ttk.Combobox(frm, values=["Weekly", "Bi-weekly", "Semi-monthly", "Monthly"], state="readonly")
        self.freq_cb.set("Bi-weekly")
        self.freq_cb.grid(column=1, row=1)

        ttk.Label(frm, text="Pay Periods:").grid(column=0, row=2)
        self.num_periods = tk.IntVar(value=26)
        self.periods_spin = ttk.Spinbox(frm, from_=6, to=52, textvariable=self.num_periods)
        self.periods_spin.grid(column=1, row=2)

        ttk.Label(frm, text="Payday Offset (days after period end):").grid(column=0, row=3)
        self.offset_var = tk.IntVar(value=3)
        self.offset_spin = ttk.Spinbox(frm, from_=0, to=10, textvariable=self.offset_var)
        self.offset_spin.grid(column=1, row=3)

        ttk.Label(frm, text="Country:").grid(column=0, row=4)
        self.country_cb = ttk.Combobox(frm, values=["US", "CA", "UK"], state="readonly")
        self.country_cb.set("US")
        self.country_cb.grid(column=1, row=4)

        ttk.Label(frm, text="State/Province:").grid(column=0, row=5)
        self.state_entry = ttk.Entry(frm)
        self.state_entry.insert(0, "CA")
        self.state_entry.grid(column=1, row=5)

        ttk.Button(frm, text="Generate Calendar", command=self.generate_calendar).grid(column=0, row=6, columnspan=2, pady=10)

        # Table
        self.tree = ttk.Treeview(self.root, columns=(
            "Period Start", "Period End", "Pay Date", "Pay Day", "Holiday", "Weekend", "Note"
        ), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=110)

        self.tree.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Export buttons
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=2, column=0, pady=5)

        ttk.Button(button_frame, text="Export to CSV", command=self.export_csv).grid(column=0, row=0, padx=10)
        ttk.Button(button_frame, text="Export to iCal (.ics)", command=self.export_ics).grid(column=1, row=0, padx=10)

    def generate_calendar(self):
        try:
            start = datetime.strptime(self.start_date_entry.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "Invalid start date format. Use YYYY-MM-DD.")
            return

        freq = self.freq_cb.get()
        num = self.num_periods.get()
        offset = self.offset_var.get()
        country = self.country_cb.get()
        state = self.state_entry.get()

        try:
            region_holidays = holidays.country_holidays(country, subdiv=state)
        except Exception:
            region_holidays = holidays.country_holidays(country)

        periods = generate_pay_periods(start, freq, num, payday_offset=offset)
        rows = check_conflicts(periods, region_holidays)

        for row in self.tree.get_children():
            self.tree.delete(row)

        for r in rows:
            self.tree.insert("", "end", values=r)

        self.latest_data = pd.DataFrame(rows, columns=[
            "Period Start", "Period End", "Pay Date", "Pay Day", "Holiday", "Weekend", "Note"
        ])

    def export_csv(self):
        if not hasattr(self, 'latest_data') or self.latest_data.empty:
            messagebox.showwarning("Warning", "No data to export.")
            return

        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file:
            self.latest_data.to_csv(file, index=False)
            messagebox.showinfo("Success", f"Exported to {file}")

    def export_ics(self):
        if not hasattr(self, 'latest_data') or self.latest_data.empty:
            messagebox.showwarning("Warning", "No data to export.")
            return

        file = filedialog.asksaveasfilename(defaultextension=".ics", filetypes=[("iCal files", "*.ics")])
        if not file:
            return

        cal = Calendar()
        for _, row in self.latest_data.iterrows():
            event = Event()
            event.name = f"Payroll: {row['Period Start']} – {row['Period End']}"
            event.begin = row["Pay Date"]
            event.make_all_day()
            cal.events.add(event)

        with open(file, 'w') as f:
            f.writelines(cal)

        messagebox.showinfo("Success", f"Exported iCal to {file}")


# === RUN ===

if __name__ == "__main__":
    root = tk.Tk()
    app = PayrollCalendarApp(root)
    root.mainloop()
