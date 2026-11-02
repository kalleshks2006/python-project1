# INDUSTRIAL ECU FAULT DETECTION & SELF-DIAGNOSIS DASHBOARD
# Educational simulation | Python + Tkinter + Random Forest
# Install: python -m pip install numpy scikit-learn
# Run: python ecu_dashboard.py

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# -------------------- ML DATA + TRAINING --------------------
np.random.seed(42)

def make_engine_data(n=4000):
    X, y = [], []
    for _ in range(n):
        t = np.random.uniform(70, 120)
        v = np.random.uniform(10.5, 14.5)
        rpm = np.random.uniform(600, 5500)
        if t > 105: label = "ENGINE_OVERHEATING"
        elif v < 11.5: label = "LOW_BATTERY_VOLTAGE"
        elif rpm > 4500: label = "HIGH_ENGINE_RPM"
        else: label = "ENGINE_NORMAL"
        X.append([t, v, rpm]); y.append(label)
    return np.array(X), np.array(y)

def make_abs_data(n=4000):
    X, y = [], []
    for _ in range(n):
        speeds = np.random.uniform(20, 120, 4)
        if min(speeds) < 5: label = "ABS_WHEEL_SENSOR_FAULT"
        elif max(speeds)-min(speeds) > 25: label = "ABS_WHEEL_SPEED_MISMATCH"
        else: label = "ABS_NORMAL"
        X.append(speeds); y.append(label)
    return np.array(X), np.array(y)

def make_injector_data(n=4000):
    X, y = [], []
    for _ in range(n):
        current = np.random.uniform(0, 3)
        pulse = np.random.uniform(2, 20)
        pressure = np.random.uniform(1, 5)
        if current < 0.5: label = "INJECTOR_OPEN_CIRCUIT"
        elif current > 2.5: label = "INJECTOR_OVERCURRENT"
        elif pressure < 2: label = "LOW_FUEL_PRESSURE"
        else: label = "INJECTOR_NORMAL"
        X.append([current, pulse, pressure]); y.append(label)
    return np.array(X), np.array(y)

def train(X, y):
    model = RandomForestClassifier(n_estimators=120, max_depth=12, random_state=42)
    model.fit(X, y)
    return model

engine_model = train(*make_engine_data())
abs_model = train(*make_abs_data())
injector_model = train(*make_injector_data())

# -------------------- DIAGNOSTIC MAPS --------------------
ENGINE_INFO = {
    "ENGINE_NORMAL": ("NORMAL", "—", "No action required", "NORMAL"),
    "ENGINE_OVERHEATING": ("CRITICAL", "P0217*", "Inspect cooling system; stop safely if overheating persists.", "FAULT"),
    "LOW_BATTERY_VOLTAGE": ("HIGH", "P0562*", "Inspect battery and charging system.", "FAULT"),
    "HIGH_ENGINE_RPM": ("HIGH", "P0219*", "Check engine speed and control system.", "FAULT"),
}
ABS_INFO = {
    "ABS_NORMAL": ("NORMAL", "—", "No action required", "NORMAL"),
    "ABS_WHEEL_SENSOR_FAULT": ("HIGH", "C0035*", "Inspect wheel-speed sensor, wiring and connector.", "FAULT"),
    "ABS_WHEEL_SPEED_MISMATCH": ("HIGH", "C0040*", "Inspect wheel-speed signals and sensor mounting.", "FAULT"),
}
INJ_INFO = {
    "INJECTOR_NORMAL": ("NORMAL", "—", "No action required", "NORMAL"),
    "INJECTOR_OPEN_CIRCUIT": ("HIGH", "P0201*", "Inspect injector electrical circuit and connector.", "FAULT"),
    "INJECTOR_OVERCURRENT": ("CRITICAL", "P0203*", "Inspect injector circuit; do not energize repeatedly.", "FAULT"),
    "LOW_FUEL_PRESSURE": ("HIGH", "P0087*", "Inspect fuel supply, pump and pressure sensor.", "FAULT"),
}

# -------------------- GUI --------------------
BG = "#101820"
PANEL = "#1b2836"
PANEL2 = "#2A4522"
TEXT = "#eaf2f8"
MUTED = "#c89fa4"
ACCENT = "#28c7a5"
RED = "#ff5d73"
ORANGE = "#ffb454"

root = tk.Tk()
root.title("ECU | Intelligent Fault Detection & Self-Diagnosis")
root.geometry("1120x760")
root.minsize(980, 680)
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook", background=BG, borderwidth=0)
style.configure("TNotebook.Tab", background=PANEL2, foreground=TEXT, padding=(18, 10), font=("Segoe UI", 10, "bold"))
style.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "#061b18")])
style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=9)
style.configure("TEntry", fieldbackground="#0d141b", foreground=TEXT, padding=8)

# Header
header = tk.Frame(root, bg=BG)
header.pack(fill="x", padx=24, pady=(20, 10))
tk.Label(header, text="ECU DIAGNOSTICS", bg=BG, fg=TEXT,
         font=("Segoe UI", 24, "bold")).pack(side="left")
tk.Label(header, text="RANDOM FOREST  •  ENGINE / ABS / INJECTOR",
         bg=BG, fg=ACCENT, font=("Segoe UI", 10, "bold")).pack(side="right", pady=10)

# Status strip
status_strip = tk.Frame(root, bg=PANEL, padx=16, pady=10)
status_strip.pack(fill="x", padx=24, pady=(0, 12))
overall_var = tk.StringVar(value="SYSTEM READY")
tk.Label(status_strip, text="●", bg=PANEL, fg=ACCENT, font=("Segoe UI", 15)).pack(side="left")
tk.Label(status_strip, textvariable=overall_var, bg=PANEL, fg=TEXT,
         font=("Segoe UI", 11, "bold")).pack(side="left", padx=8)
tk.Label(status_strip, text="Simulation mode • No vehicle connection",
         bg=PANEL, fg=MUTED, font=("Segoe UI", 9)).pack(side="right")

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=24, pady=8)

def make_tab(title, fields):
    tab = tk.Frame(notebook, bg=BG)
    notebook.add(tab, text=title)
    card = tk.Frame(tab, bg=PANEL, padx=24, pady=22)
    card.pack(fill="x", padx=18, pady=18)
    tk.Label(card, text=title.upper()+" INPUTS", bg=PANEL, fg=ACCENT,
             font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 15))
    entries = {}
    grid = tk.Frame(card, bg=PANEL)
    grid.pack(fill="x")
    for i, (key, label, default, unit) in enumerate(fields):
        row, col = divmod(i, 2)
        cell = tk.Frame(grid, bg=PANEL)
        cell.grid(row=row, column=col, sticky="ew", padx=(0, 18), pady=8)
        grid.columnconfigure(col, weight=1)
        tk.Label(cell, text=f"{label}  ({unit})", bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 10)).pack(anchor="w")
        var = tk.StringVar(value=str(default))
        entry = ttk.Entry(cell, textvariable=var, font=("Segoe UI", 12))
        entry.pack(fill="x", pady=(5, 0))
        entries[key] = var
    result = tk.Frame(tab, bg=PANEL, padx=24, pady=18)
    result.pack(fill="both", expand=True, padx=18, pady=(0, 18))
    tk.Label(result, text="DIAGNOSTIC RESULT", bg=PANEL, fg=MUTED,
             font=("Segoe UI", 10, "bold")).pack(anchor="w")
    fault_var = tk.StringVar(value="Awaiting diagnosis")
    tk.Label(result, textvariable=fault_var, bg=PANEL, fg=TEXT,
             font=("Segoe UI", 18, "bold"), wraplength=850).pack(anchor="w", pady=8)
    info_var = tk.StringVar(value="Enter sensor values and select Run Diagnosis.")
    tk.Label(result, textvariable=info_var, bg=PANEL, fg=MUTED,
             font=("Segoe UI", 10), wraplength=850, justify="left").pack(anchor="w")
    return entries, fault_var, info_var

def show_result(system, prediction, info, fault_var, info_var):
    severity, dtc, action, state = info[prediction]
    fault_var.set(prediction.replace("_", " "))
    info_var.set(f"Status: {state}   |   Severity: {severity}   |   DTC: {dtc}\\nRecommended action: {action}\\nModel: Random Forest")
    overall_var.set(f"{system}: {state} — {severity}")
    # display color on result label by updating matching widget
    fault_var_label = fault_var._label if hasattr(fault_var, "_label") else None

# Engine tab
engine_entries, engine_fault, engine_info = make_tab("Engine ECU", [
    ("temp", "Engine temperature", 90, "°C"),
    ("voltage", "Battery voltage", 13.2, "V"),
    ("rpm", "Engine speed", 2500, "RPM"),
])
def run_engine():
    try:
        values = [float(engine_entries[k].get()) for k in ("temp", "voltage", "rpm")]
        pred = engine_model.predict([values])[0]
        show_result("ENGINE ECU", pred, ENGINE_INFO, engine_fault, engine_info)
    except ValueError:
        messagebox.showerror("Invalid input", "Enter numeric values in every Engine field.")
tk.Button(engine_entries["temp"]._root(), text="") if False else None
# Buttons are placed in a dedicated footer on each tab
engine_tab = notebook.nametowidget(notebook.tabs()[0])
tk.Button(engine_tab, text="▶  RUN ENGINE DIAGNOSIS", command=run_engine,
          bg=ACCENT, fg="#06231d", activebackground="#45dfbd",
          relief="flat", font=("Segoe UI", 10, "bold"), padx=18, pady=11).pack(anchor="e", padx=18, pady=(0, 15))

# ABS tab
abs_entries, abs_fault, abs_info = make_tab("ABS ECU", [
    ("fl", "Front-left wheel speed", 80, "km/h"),
    ("fr", "Front-right wheel speed", 82, "km/h"),
    ("rl", "Rear-left wheel speed", 78, "km/h"),
    ("rr", "Rear-right wheel speed", 80, "km/h"),
])
def run_abs():
    try:
        values = [float(abs_entries[k].get()) for k in ("fl", "fr", "rl", "rr")]
        pred = abs_model.predict([values])[0]
        show_result("ABS ECU", pred, ABS_INFO, abs_fault, abs_info)
    except ValueError:
        messagebox.showerror("Invalid input", "Enter numeric values in every ABS field.")
abs_tab = notebook.nametowidget(notebook.tabs()[1])
tk.Button(abs_tab, text="▶  RUN ABS DIAGNOSIS", command=run_abs,
          bg=ACCENT, fg="#06231d", activebackground="#45dfbd",
          relief="flat", font=("Segoe UI", 10, "bold"), padx=18, pady=11).pack(anchor="e", padx=18, pady=(0, 15))

# Injector tab
inj_entries, inj_fault, inj_info = make_tab("Fuel Injector ECU", [
    ("current", "Injector current", 1.2, "A"),
    ("pulse", "Pulse width", 10, "ms"),
    ("pressure", "Fuel pressure", 3.5, "bar"),
])
def run_injector():
    try:
        values = [float(inj_entries[k].get()) for k in ("current", "pulse", "pressure")]
        pred = injector_model.predict([values])[0]
        show_result("FUEL INJECTOR ECU", pred, INJ_INFO, inj_fault, inj_info)
    except ValueError:
        messagebox.showerror("Invalid input", "Enter numeric values in every Injector field.")
inj_tab = notebook.nametowidget(notebook.tabs()[2])
tk.Button(inj_tab, text="▶  RUN INJECTOR DIAGNOSIS", command=run_injector,
          bg=ACCENT, fg="#06231d", activebackground="#45dfbd",
          relief="flat", font=("Segoe UI", 10, "bold"), padx=18, pady=11).pack(anchor="e", padx=18, pady=(0, 15))

# Footer
footer = tk.Frame(root, bg=BG)
footer.pack(fill="x", padx=24, pady=(0, 14))
tk.Label(footer, text="* DTC examples are illustrative, not manufacturer-verified. Educational prototype only.",
         bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left")
tk.Button(footer, text="EXIT", command=root.destroy, bg=PANEL2, fg=TEXT,
          relief="flat", padx=16, pady=7).pack(side="right")

root.mainloop()
