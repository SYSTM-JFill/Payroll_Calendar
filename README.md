# Payroll Calendar Drift Monitor

A **Python Tkinter GUI app** to generate payroll pay period schedules with holiday and weekend awareness, including the ability to export schedules as **CSV** or **Google Calendar-compatible iCal (.ics)** files.

---

## Features

- Supports common payroll frequencies:  
  - Weekly  
  - Bi-weekly  
  - Semi-monthly  
  - Monthly

- Customizable pay periods count and payday offset (days after period end)

- Holiday and weekend detection using the [`holidays`](https://pypi.org/project/holidays/) Python library  
  - Shows if a payday falls on a holiday or weekend  
  - Names the holiday and suggests adjusted pay date if payday conflicts

- Export payroll calendar:  
  - CSV format for spreadsheet use  
  - iCal `.ics` format for calendar apps (Google Calendar, Outlook, Apple Calendar, etc.)

---

## Usage and Output

1. **Start Date:** Enter the date when the payroll schedule should begin (format: YYYY-MM-DD).

2. **Frequency:** Choose the payroll frequency from the dropdown menu — options include Weekly, Bi-weekly, Semi-monthly, and Monthly.

3. **Pay Periods:** Specify the number of pay periods to generate (default is 26).

4. **Payday Offset:** Set how many days after the pay period ends the payday occurs (default is 3 days).

5. **Country/State:** Select the country and enter the state or province to apply accurate regional holidays.

6. Click the **Generate Calendar** button to display the pay periods, pay dates, and notes about holidays or weekends.

7. The table shows the following columns:  
   - **Period Start:** The first day of the pay period  
   - **Period End:** The last day of the pay period  
   - **Pay Date:** The scheduled payday before adjustment  
   - **Pay Day:** The weekday name of the payday  
   - **Holiday:** Indicates if the payday falls on a holiday  
   - **Weekend:** Indicates if the payday falls on a weekend  
   - **Note:** Shows the holiday name and adjusted payday if the original payday conflicts with a holiday or weekend

8. Use the **Export to CSV** button to save the payroll calendar data as a CSV file for reporting or sharing.

9. Use the **Export to iCal** button (if available) to download an iCal (.ics) file compatible with calendar applications like Google Calendar or Outlook, allowing easy import of your payroll schedule.

---

**Example Output Table:**

| Period Start | Period End | Pay Date   | Pay Day  | Holiday | Weekend | Note                                |
|--------------|------------|------------|----------|---------|---------|-----------------------------------|
| 2025-11-01   | 2025-11-15 | 2025-11-18 | Tuesday  | No      | No      |                                   |
| 2025-11-16   | 2025-11-30 | 2025-12-01 | Monday   | Yes     | No      | Thanksgiving Day → 2025-11-28     |
| 2025-12-01   | 2025-12-15 | 2025-12-18 | Thursday | No      | No      |                                   |
| 2025-12-16   | 2025-12-31 | 2026-01-03 | Saturday | No      | Yes     | Weekend → 2026-01-02 (Friday fallback) |

---

## Screenshots

![Sample Payroll Calendar Output](sample_output.png)


This helps payroll teams proactively manage pay dates around holidays and weekends, reducing errors and ensuring timely payments.
