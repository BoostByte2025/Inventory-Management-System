import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import os

# Database setup
def setup_database():
    conn = sqlite3.connect('employee_performance.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        date TEXT,
        metric TEXT,
        score INTEGER,
        period TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Add performance data to the database
def add_performance_data(name, date, metric, score, period):
    conn = sqlite3.connect('employee_performance.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO performance (name, date, metric, score, period) VALUES (?, ?, ?, ?, ?)
    ''', (name, date, metric, score, period))
    conn.commit()
    conn.close()
    messagebox.showinfo('Data Added', 'Performance data has been added successfully.')

# Fetch performance data from the database
def fetch_performance_data():
    conn = sqlite3.connect('employee_performance.db')
    df = pd.read_sql_query('SELECT * FROM performance', conn)
    conn.close()
    return df

# Update performance data
def update_performance_data(id, name, date, metric, score, period):
    conn = sqlite3.connect('employee_performance.db')
    cursor = conn.cursor()
    cursor.execute('''
    UPDATE performance SET name=?, date=?, metric=?, score=?, period=? WHERE id=?
    ''', (name, date, metric, score, period, id))
    conn.commit()
    conn.close()
    messagebox.showinfo('Data Updated', 'Performance data has been updated successfully.')

# Delete performance data
def delete_performance_data(id):
    conn = sqlite3.connect('employee_performance.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM performance WHERE id=?', (id,))
    conn.commit()
    conn.close()
    messagebox.showinfo('Data Deleted', 'Performance data has been deleted successfully.')

# Visualize performance data
def visualize_performance(name, chart_type, period):
    df = fetch_performance_data()
    employee_data = df[(df['name'] == name) & (df['period'] == period)]

    if employee_data.empty:
        messagebox.showerror('No Data', f'No performance data found for {name} for {period} period.')
        return

    employee_data['date'] = pd.to_datetime(employee_data['date'])
    metrics = employee_data['metric'].unique()

    fig, ax = plt.subplots(figsize=(10, 6))

    if chart_type == 'Line':
        for metric in metrics:
            metric_data = employee_data[employee_data['metric'] == metric]
            ax.plot(metric_data['date'], metric_data['score'], marker='o', label=metric)
    elif chart_type == 'Bar':
        for metric in metrics:
            metric_data = employee_data[employee_data['metric'] == metric]
            ax.bar(metric_data['date'], metric_data['score'], label=metric)
    elif chart_type == 'Scatter':
        for metric in metrics:
            metric_data = employee_data[employee_data['metric'] == metric]
            ax.scatter(metric_data['date'], metric_data['score'], label=metric)

    ax.set_title(f'Performance Metrics for {name}')
    ax.set_xlabel('Date')
    ax.set_ylabel('Score')
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

# Search performance data
def search_performance_data(name):
    df = fetch_performance_data()
    employee_data = df[df['name'] == name]

    if employee_data.empty:
        messagebox.showerror('No Data', f'No performance data found for {name}.')
        return

    for index, row in employee_data.iterrows():
        tree.insert('', 'end', values=(row['id'], row['name'], row['date'], row['metric'], row['score'], row['period']))

# Export data to CSV, Excel, or PDF
def export_data(format):
    df = fetch_performance_data()
    if df.empty:
        messagebox.showerror('No Data', 'No performance data to export.')
        return

    filename = filedialog.asksaveasfilename(defaultextension=f".{format}", filetypes=[(f"{format.upper()} files", f"*.{format}")])
    if not filename:
        return

    if format == 'csv':
        df.to_csv(filename, index=False)
    elif format == 'xlsx':
        df.to_excel(filename, index=False)
    elif format == 'pdf':
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for i in range(len(df)):
            pdf.cell(200, 10, txt=df.iloc[i].to_string(), ln=True)
        pdf.output(filename)

    messagebox.showinfo('Export Successful', f'Data exported to {filename}')

# GUI setup
def setup_gui():
    root = tk.Tk()
    root.title("Employee Performance Tracker")
    root.geometry("800x600")

    frame = ttk.Frame(root, padding=10)
    frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    # Add performance data
    ttk.Label(frame, text="Employee Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    name_entry = ttk.Entry(frame)
    name_entry.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
    date_entry = ttk.Entry(frame)
    date_entry.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Performance Metric:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
    metric_entry = ttk.Entry(frame)
    metric_entry.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Score:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
    score_entry = ttk.Entry(frame)
    score_entry.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Period:").grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
    period_var = tk.StringVar(value='Daily')
    ttk.Radiobutton(frame, text="Daily", variable=period_var, value='Daily').grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
    ttk.Radiobutton(frame, text="Weekly", variable=period_var, value='Weekly').grid(row=4, column=2, padx=5, pady=5, sticky=tk.W)
    ttk.Radiobutton(frame, text="Monthly", variable=period_var, value='Monthly').grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)

    add_button = ttk.Button(frame, text="Add Data", command=lambda: add_performance_data(name_entry.get(), date_entry.get(), metric_entry.get(), score_entry.get(), period_var.get()))
    add_button.grid(row=5, column=0, columnspan=4, pady=10)

    # Visualization options
    ttk.Label(frame, text="Employee Name for Visualization:").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
    visualize_name_entry = ttk.Entry(frame)
    visualize_name_entry.grid(row=6, column=1, padx=5, pady=5)

    ttk.Label(frame, text="Chart Type:").grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
    chart_type_var = tk.StringVar(value='Line')
    ttk.Radiobutton(frame, text="Line Chart", variable=chart_type_var, value='Line').grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)
    ttk.Radiobutton(frame, text="Bar Chart", variable=chart_type_var, value='Bar').grid(row=7, column=2, padx=5, pady=5, sticky=tk.W)
    ttk.Radiobutton(frame, text="Scatter Plot", variable=chart_type_var, value='Scatter').grid(row=7, column=3, padx=5, pady=5, sticky=tk.W)

    visualize_button = ttk.Button(frame, text="Visualize Performance", command=lambda: visualize_performance(visualize_name_entry.get(), chart_type_var.get(), period_var.get()))
    visualize_button.grid(row=8, column=0, columnspan=4, pady=10)

    # Search functionality
    ttk.Label(frame, text="Search Employee Performance:").grid(row=9, column=0, padx=5, pady=5, sticky=tk.W)
    search_name_entry = ttk.Entry(frame)
    search_name_entry.grid(row=9, column=1, padx=5, pady=5)

    search_button = ttk.Button(frame, text="Search", command=lambda: search_performance_data(search_name_entry.get()))
    search_button.grid(row=9, column=2, padx=5, pady=5)

    # Treeview for displaying data
    global tree
    tree = ttk.Treeview(frame, columns=('ID', 'Name', 'Date', 'Metric', 'Score', 'Period'), show='headings')
    tree.heading('ID', text='ID')
    tree.heading('Name', text='Name')
    tree.heading('Date', text='Date')
    tree.heading('Metric', text='Metric')
    tree.heading('Score', text='Score')
    tree.heading('Period', text='Period')
    tree.grid(row=10, column=0, columnspan=4, pady=10)

    # Export options
    export_frame = ttk.Frame(frame)
    export_frame.grid(row=11, column=0, columnspan=4, pady=10)
    ttk.Label(export_frame, text="Export Data:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Button(export_frame, text="CSV", command=lambda: export_data('csv')).grid(row=0, column=1, padx=5, pady=5)
    ttk.Button(export_frame, text="Excel", command=lambda: export_data('xlsx')).grid(row=0, column=2, padx=5, pady=5)
    ttk.Button(export_frame, text="PDF", command=lambda: export_data('pdf')).grid(row=0, column=3, padx=5, pady=5)

    root.mainloop()

if __name__ == "__main__":
    setup_database()
    setup_gui()
