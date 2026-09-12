import sqlite3
import tkinter as tk
from datetime import datetime
from tkinter import ttk, messagebox

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DB_PATH = "bmi_records.db"

COLORS = {
    "Underweight": "#3b82f6",  # blue
    "Normal": "#22c55e",       # green
    "Overweight": "#f59e0b",   # amber
    "Obese": "#ef4444",        # red
}



def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    try:
        conn = get_connection()
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                height_m REAL NOT NULL,
                bmi REAL NOT NULL,
                category TEXT NOT NULL,
                recorded_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not initialize database:\n{e}")


def save_record(username, weight, height, bmi, category):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO records (username, weight_kg, height_m, bmi, category, recorded_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (username, weight, height, bmi, category, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not save record:\n{e}")
        return False


def get_user_history(username):
    try:
        conn = get_connection()
        rows = conn.execute(
            "SELECT bmi, recorded_at FROM records WHERE username = ? ORDER BY recorded_at",
            (username,),
        ).fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        messagebox.showerror("Database Error", f"Could not read history:\n{e}")
        return []


def get_all_usernames():
    try:
        conn = get_connection()
        rows = conn.execute(
            "SELECT DISTINCT username FROM records ORDER BY username"
        ).fetchall()
        conn.close()
        return [r[0] for r in rows]
    except sqlite3.Error:
        return []



def calculate_bmi(weight_kg: float, height_m: float) -> float:
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"



class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator — Advanced")
        self.geometry("480x620")
        self.configure(bg="#0f1117")
        self.resizable(False, False)

        self._build_styles()
        self._build_widgets()

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", background="#0f1117", foreground="#e8e9ee",
                         font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("TEntry", fieldbackground="#1f2330", foreground="#e8e9ee")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=8)
        style.configure("TCombobox", fieldbackground="#1f2330")

    def _build_widgets(self):
        pad = {"padx": 20, "pady": 6}

        ttk.Label(self, text="BMI Calculator", style="Header.TLabel").pack(pady=(20, 4))
        ttk.Label(self, text="Track BMI for multiple users over time").pack(pady=(0, 16))

        form = tk.Frame(self, bg="#0f1117")
        form.pack(**pad)

        ttk.Label(form, text="Name:").grid(row=0, column=0, sticky="w", pady=6)
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Combobox(form, textvariable=self.username_var, width=27)
        self.username_entry["values"] = get_all_usernames()
        self.username_entry.grid(row=0, column=1, pady=6)

        ttk.Label(form, text="Weight (kg):").grid(row=1, column=0, sticky="w", pady=6)
        self.weight_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.weight_var, width=30).grid(row=1, column=1, pady=6)

        ttk.Label(form, text="Height (m):").grid(row=2, column=0, sticky="w", pady=6)
        self.height_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.height_var, width=30).grid(row=2, column=1, pady=6)

        ttk.Button(self, text="Calculate & Save", command=self.on_calculate).pack(pady=16)

      
        self.result_frame = tk.Frame(self, bg="#1f2330", height=90)
        self.result_frame.pack(fill="x", padx=20, pady=4)
        self.result_frame.pack_propagate(False)

        self.result_label = tk.Label(
            self.result_frame, text="Enter your details and calculate.",
            bg="#1f2330", fg="#9598a8", font=("Segoe UI", 12), wraplength=420, justify="center"
        )
        self.result_label.pack(expand=True)

        ttk.Button(self, text="Show BMI Trend for this user", command=self.on_show_trend).pack(pady=10)

        
        self.chart_frame = tk.Frame(self, bg="#0f1117")
        self.chart_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.canvas = None

    def on_calculate(self):
        username = self.username_var.get().strip()
        weight_raw = self.weight_var.get().strip()
        height_raw = self.height_var.get().strip()

        if not username:
            messagebox.showwarning("Missing name", "Please enter a name.")
            return

        try:
            weight = float(weight_raw)
            height = float(height_raw)
        except ValueError:
            messagebox.showwarning("Invalid input", "Weight and height must be numbers.")
            return

        if weight <= 0 or height <= 0:
            messagebox.showwarning("Invalid input", "Weight and height must be positive numbers.")
            return

        bmi = calculate_bmi(weight, height)
        category = classify_bmi(bmi)
        color = COLORS.get(category, "#e8e9ee")

        self.result_frame.configure(bg=color)
        self.result_label.configure(
            bg=color, fg="#0f1117",
            text=f"BMI: {bmi:.2f}   —   {category}",
            font=("Segoe UI", 16, "bold"),
        )

        saved = save_record(username, weight, height, bmi, category)
        if saved:
            values = list(self.username_entry["values"])
            if username not in values:
                values.append(username)
                self.username_entry["values"] = sorted(values)

    def on_show_trend(self):
        username = self.username_var.get().strip()
        if not username:
            messagebox.showwarning("Missing name", "Enter a name first to view their trend.")
            return

        history = get_user_history(username)
        if not history:
            messagebox.showinfo("No data", f"No BMI records found for '{username}' yet.")
            return

        bmis = [row[0] for row in history]
        labels = [row[1][:10] for row in history]  # just the date part

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        fig = Figure(figsize=(4.4, 2.6), dpi=100, facecolor="#0f1117")
        ax = fig.add_subplot(111)
        ax.set_facecolor("#171a23")
        ax.plot(range(len(bmis)), bmis, marker="o", color="#6c8cff", linewidth=2)
        ax.set_title(f"{username}'s BMI Trend", color="#e8e9ee", fontsize=10)
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=7, color="#9598a8")
        ax.tick_params(axis="y", colors="#9598a8", labelsize=7)
        ax.axhline(18.5, color="#3b82f6", linestyle="--", linewidth=0.6)
        ax.axhline(25, color="#f59e0b", linestyle="--", linewidth=0.6)
        ax.axhline(30, color="#ef4444", linestyle="--", linewidth=0.6)
        fig.tight_layout()

        self.canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    init_db()
    app = BMIApp()
    app.mainloop()
