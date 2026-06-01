#this the master file 
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
import datetime

# ─────────────────────────── THEME COLORS ───────────────────────────
BG        = "#0f1117"
CARD      = "#1a1d27"
ACCENT    = "#00c9a7"
ACCENT2   = "#007a64"
BTN_DEL   = "#c0392b"
TEXT      = "#e8eaf6"
MUTED     = "#7f8c8d"
ENTRY_BG  = "#22263a"
BORDER    = "#2e3250"
SUCCESS   = "#27ae60"
FONT_MAIN = ("Segoe UI", 10)
FONT_HEAD = ("Segoe UI", 11, "bold")
FONT_TITLE= ("Segoe UI", 14, "bold")

# ─────────────────────────── DATABASE ───────────────────────────────
conn = sqlite3.connect("hospital.db")
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.executescript("""
CREATE TABLE IF NOT EXISTS patients(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, age INTEGER, gender TEXT, phone TEXT, address TEXT
);
CREATE TABLE IF NOT EXISTS doctors(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, specialization TEXT, experience INTEGER, schedule TEXT, fee INTEGER
);
CREATE TABLE IF NOT EXISTS appointments(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER, doctor_id INTEGER, date TEXT, time TEXT, status TEXT,
    FOREIGN KEY(patient_id) REFERENCES patients(id),
    FOREIGN KEY(doctor_id)  REFERENCES doctors(id)
);
""")
conn.commit()

# ─────────────────────────── ROOT WINDOW ────────────────────────────
root = tk.Tk()
root.title("🏥  Hospital Management System")
root.geometry("1100x700")
root.configure(bg=BG)
root.resizable(True, True)

# ─────────────────────────── HELPERS ────────────────────────────────
def set_status(msg, color=ACCENT):
    status_var.set(msg)
    status_label.config(fg=color)

def styled_entry(parent, **kw):
    e = tk.Entry(parent, bg=ENTRY_BG, fg=TEXT, insertbackground=TEXT,
                 relief="flat", font=FONT_MAIN, bd=0, highlightthickness=1,
                 highlightbackground=BORDER, highlightcolor=ACCENT, **kw)
    return e

def styled_label(parent, text, bold=False, **kw):
    font = FONT_HEAD if bold else FONT_MAIN
    return tk.Label(parent, text=text, bg=CARD, fg=TEXT, font=font, **kw)

def styled_btn(parent, text, cmd, color=ACCENT, fg="#000", **kw):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, activebackground=ACCENT2, activeforeground="#fff",
                  font=FONT_MAIN, relief="flat", cursor="hand2",
                  padx=12, pady=6, bd=0, **kw)
    b.bind("<Enter>", lambda e: b.config(bg=ACCENT2, fg="#fff"))
    b.bind("<Leave>", lambda e: b.config(bg=color, fg=fg))
    return b

def make_card(parent, title, row=0, col=0, colspan=1, rowspan=1):
    f = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=1,
                 highlightbackground=BORDER)
    f.grid(row=row, column=col, columnspan=colspan, rowspan=rowspan,
           padx=10, pady=10, sticky="nsew")
    tk.Label(f, text=title, bg=CARD, fg=ACCENT, font=FONT_TITLE).pack(
        anchor="w", padx=14, pady=(10, 6))
    ttk.Separator(f, orient="horizontal").pack(fill="x", padx=10)
    return f

def tree_widget(parent, cols, col_widths=None):
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Custom.Treeview",
                    background=ENTRY_BG, foreground=TEXT,
                    fieldbackground=ENTRY_BG, rowheight=28,
                    font=FONT_MAIN, borderwidth=0)
    style.configure("Custom.Treeview.Heading",
                    background=CARD, foreground=ACCENT,
                    font=FONT_HEAD, relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", ACCENT2)],
              foreground=[("selected", "#fff")])

    frame = tk.Frame(parent, bg=CARD)
    frame.pack(fill="both", expand=True, padx=10, pady=8)

    sb = ttk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")

    tv = ttk.Treeview(frame, columns=cols, show="headings",
                      style="Custom.Treeview", yscrollcommand=sb.set)
    sb.config(command=tv.yview)

    for i, col in enumerate(cols):
        w = col_widths[i] if col_widths else 120
        tv.heading(col, text=col, anchor="w")
        tv.column(col, width=w, anchor="w", minwidth=60)

    tv.pack(fill="both", expand=True)
    return tv

# ─────────────────────────── NOTEBOOK / TABS ────────────────────────
nb_style = ttk.Style()
nb_style.configure("Dark.TNotebook", background=BG, borderwidth=0)
nb_style.configure("Dark.TNotebook.Tab",
                   background=CARD, foreground=MUTED,
                   padding=[16, 8], font=FONT_HEAD)
nb_style.map("Dark.TNotebook.Tab",
             background=[("selected", ACCENT2)],
             foreground=[("selected", "#fff")])

# Header
header = tk.Frame(root, bg=ACCENT2, height=56)
header.pack(fill="x")
tk.Label(header, text="🏥  Hospital Management System",
         bg=ACCENT2, fg="#fff", font=("Segoe UI", 16, "bold")).pack(
    side="left", padx=20, pady=12)

notebook = ttk.Notebook(root, style="Dark.TNotebook")
notebook.pack(fill="both", expand=True, padx=0, pady=0)

# ───────────────────────── TAB 1: PATIENTS ──────────────────────────
tab_patients = tk.Frame(notebook, bg=BG)
notebook.add(tab_patients, text="  👤  Patients  ")

tab_patients.columnconfigure(0, weight=1)
tab_patients.columnconfigure(1, weight=2)
tab_patients.rowconfigure(0, weight=1)

# --- Input Card ---
inp_card = make_card(tab_patients, "Register Patient", row=0, col=0)

fields_p = {}
labels_p = ["Full Name", "Age", "Gender", "Phone", "Address"]
for i, lbl in enumerate(labels_p):
    styled_label(inp_card, lbl).pack(anchor="w", padx=14, pady=(8, 0))
    e = styled_entry(inp_card, width=30)
    e.pack(padx=14, pady=(2, 0), fill="x")
    fields_p[lbl] = e

def register_patient():
    name    = fields_p["Full Name"].get().strip()
    age_s   = fields_p["Age"].get().strip()
    gender  = fields_p["Gender"].get().strip()
    phone   = fields_p["Phone"].get().strip()
    address = fields_p["Address"].get().strip()

    if not name:
        set_status("⚠  Name is required.", BTN_DEL); return
    try:
        age = int(age_s)
        if age <= 0 or age > 130: raise ValueError
    except ValueError:
        set_status("⚠  Enter a valid age (1–130).", BTN_DEL); return

    cursor.execute(
        "INSERT INTO patients (name,age,gender,phone,address) VALUES (?,?,?,?,?)",
        (name, age, gender, phone, address))
    conn.commit()
    for e in fields_p.values(): e.delete(0, tk.END)
    set_status(f"✅  Patient '{name}' registered successfully.")
    load_patients()

def load_patients():
    for row in patient_tree.get_children():
        patient_tree.delete(row)
    cursor.execute("SELECT * FROM patients")
    for row in cursor.fetchall():
        patient_tree.insert("", tk.END, values=row)

def delete_patient():
    sel = patient_tree.selection()
    if not sel:
        set_status("⚠  Select a patient to delete.", BTN_DEL); return
    pid = patient_tree.item(sel[0])["values"][0]
    name = patient_tree.item(sel[0])["values"][1]
    if messagebox.askyesno("Confirm", f"Delete patient '{name}'? Their appointments will also be removed."):
        cursor.execute("DELETE FROM appointments WHERE patient_id=?", (pid,))
        cursor.execute("DELETE FROM patients WHERE id=?", (pid,))
        conn.commit()
        set_status(f"🗑  Patient '{name}' deleted.")
        load_patients()
        load_appointments()

btn_row = tk.Frame(inp_card, bg=CARD)
btn_row.pack(padx=14, pady=12, fill="x")
styled_btn(btn_row, "  ➕  Register", register_patient).pack(side="left", padx=(0, 6))
styled_btn(btn_row, "  🗑  Delete", delete_patient, color=BTN_DEL, fg="#fff").pack(side="left")

# --- Table Card ---
tbl_card = make_card(tab_patients, "Patient List", row=0, col=1)
patient_tree = tree_widget(tbl_card,
    cols=("ID","Name","Age","Gender","Phone","Address"),
    col_widths=[40, 160, 50, 80, 110, 200])

# ───────────────────────── TAB 2: DOCTORS ───────────────────────────
tab_doctors = tk.Frame(notebook, bg=BG)
notebook.add(tab_doctors, text="  🩺  Doctors  ")
tab_doctors.columnconfigure(0, weight=1)
tab_doctors.columnconfigure(1, weight=2)
tab_doctors.rowconfigure(0, weight=1)

inp_card_d = make_card(tab_doctors, "Add Doctor", row=0, col=0)
fields_d = {}
labels_d = ["Full Name", "Specialization", "Experience (yrs)", "Schedule", "Fee (₹)"]
for i, lbl in enumerate(labels_d):
    styled_label(inp_card_d, lbl).pack(anchor="w", padx=14, pady=(8, 0))
    e = styled_entry(inp_card_d, width=30)
    e.pack(padx=14, pady=(2, 0), fill="x")
    fields_d[lbl] = e

# Search bar
styled_label(inp_card_d, "Search by Specialization").pack(anchor="w", padx=14, pady=(14, 0))
search_var = tk.StringVar()
search_entry = styled_entry(inp_card_d, textvariable=search_var, width=30)
search_entry.pack(padx=14, pady=(2, 0), fill="x")

def add_doctor():
    name  = fields_d["Full Name"].get().strip()
    spec  = fields_d["Specialization"].get().strip()
    sched = fields_d["Schedule"].get().strip()
    try:
        exp = int(fields_d["Experience (yrs)"].get().strip())
        fee = int(fields_d["Fee (₹)"].get().strip())
    except ValueError:
        set_status("⚠  Experience and Fee must be numbers.", BTN_DEL); return
    if not name:
        set_status("⚠  Name is required.", BTN_DEL); return

    cursor.execute(
        "INSERT INTO doctors (name,specialization,experience,schedule,fee) VALUES (?,?,?,?,?)",
        (name, spec, exp, sched, fee))
    conn.commit()
    for e in fields_d.values(): e.delete(0, tk.END)
    set_status(f"✅  Dr. {name} added successfully.")
    load_doctors()

def load_doctors(spec_filter=""):
    for row in doctor_tree.get_children():
        doctor_tree.delete(row)
    if spec_filter:
        cursor.execute("SELECT * FROM doctors WHERE specialization LIKE ?", (f"%{spec_filter}%",))
    else:
        cursor.execute("SELECT * FROM doctors")
    for row in cursor.fetchall():
        doctor_tree.insert("", tk.END, values=row)

def search_doctors(*args):
    load_doctors(search_var.get().strip())

search_var.trace_add("write", search_doctors)

def delete_doctor():
    sel = doctor_tree.selection()
    if not sel:
        set_status("⚠  Select a doctor to delete.", BTN_DEL); return
    did  = doctor_tree.item(sel[0])["values"][0]
    name = doctor_tree.item(sel[0])["values"][1]
    if messagebox.askyesno("Confirm", f"Delete Dr. '{name}'? Their appointments will also be removed."):
        cursor.execute("DELETE FROM appointments WHERE doctor_id=?", (did,))
        cursor.execute("DELETE FROM doctors WHERE id=?", (did,))
        conn.commit()
        set_status(f"🗑  Dr. '{name}' deleted.")
        load_doctors()
        load_appointments()

btn_row_d = tk.Frame(inp_card_d, bg=CARD)
btn_row_d.pack(padx=14, pady=12, fill="x")
styled_btn(btn_row_d, "  ➕  Add Doctor", add_doctor).pack(side="left", padx=(0,6))
styled_btn(btn_row_d, "  🗑  Delete", delete_doctor, color=BTN_DEL, fg="#fff").pack(side="left")

tbl_card_d = make_card(tab_doctors, "Doctor List", row=0, col=1)
doctor_tree = tree_widget(tbl_card_d,
    cols=("ID","Name","Specialization","Exp","Schedule","Fee"),
    col_widths=[40, 150, 150, 50, 120, 80])

# ──────────────────────── TAB 3: APPOINTMENTS ───────────────────────
tab_appt = tk.Frame(notebook, bg=BG)
notebook.add(tab_appt, text="  📅  Appointments  ")
tab_appt.columnconfigure(0, weight=1)
tab_appt.columnconfigure(1, weight=2)
tab_appt.rowconfigure(0, weight=1)

inp_card_a = make_card(tab_appt, "Book Appointment", row=0, col=0)

fields_a = {}
labels_a = ["Patient ID", "Doctor ID", "Date (YYYY-MM-DD)", "Time (e.g. 10:30 AM)"]
for lbl in labels_a:
    styled_label(inp_card_a, lbl).pack(anchor="w", padx=14, pady=(8, 0))
    if lbl == "Date (YYYY-MM-DD)":
        e = styled_entry(inp_card_a, width=30)
        e.insert(0, datetime.date.today().strftime("%Y-%m-%d"))
    else:
        e = styled_entry(inp_card_a, width=30)
    e.pack(padx=14, pady=(2, 0), fill="x")
    fields_a[lbl] = e

# Quick-reference panel
ref = tk.Frame(inp_card_a, bg=ENTRY_BG, highlightthickness=1,
               highlightbackground=BORDER)
ref.pack(padx=14, pady=(10, 0), fill="x")
tk.Label(ref, text="💡 Tip: Go to Patients / Doctors tabs to get their IDs",
         bg=ENTRY_BG, fg=MUTED, font=("Segoe UI", 8), wraplength=240,
         justify="left").pack(padx=8, pady=6, anchor="w")

def book_appointment():
    try:
        pid  = int(fields_a["Patient ID"].get().strip())
        did  = int(fields_a["Doctor ID"].get().strip())
    except ValueError:
        set_status("⚠  Patient ID and Doctor ID must be integers.", BTN_DEL); return

    date_s = fields_a["Date (YYYY-MM-DD)"].get().strip()
    time_s = fields_a["Time (e.g. 10:30 AM)"].get().strip()

    try:
        valid_date = datetime.datetime.strptime(date_s, "%Y-%m-%d").date()
    except ValueError:
        set_status("⚠  Date must be YYYY-MM-DD format.", BTN_DEL); return
    if not time_s:
        set_status("⚠  Time is required.", BTN_DEL); return

    # Double-booking check
    cursor.execute(
        "SELECT id FROM appointments WHERE doctor_id=? AND date=? AND time=?",
        (did, valid_date.isoformat(), time_s))
    if cursor.fetchone():
        set_status("⚠  Doctor already booked for that slot!", BTN_DEL); return

    try:
        cursor.execute(
            "INSERT INTO appointments (patient_id,doctor_id,date,time,status) VALUES (?,?,?,?,?)",
            (pid, did, valid_date.isoformat(), time_s, "Booked"))
        conn.commit()
        set_status("✅  Appointment booked successfully.")
        for lbl, e in fields_a.items():
            if lbl != "Date (YYYY-MM-DD)":
                e.delete(0, tk.END)
        load_appointments()
    except sqlite3.IntegrityError:
        set_status("⚠  Patient ID or Doctor ID does not exist.", BTN_DEL)

def cancel_appointment():
    sel = appt_tree.selection()
    if not sel:
        set_status("⚠  Select an appointment to cancel.", BTN_DEL); return
    aid    = appt_tree.item(sel[0])["values"][0]
    patient= appt_tree.item(sel[0])["values"][1]
    if messagebox.askyesno("Confirm", f"Cancel appointment for '{patient}'?"):
        cursor.execute("DELETE FROM appointments WHERE id=?", (aid,))
        conn.commit()
        set_status(f"🗑  Appointment #{aid} cancelled.")
        load_appointments()

def load_appointments():
    for row in appt_tree.get_children():
        appt_tree.delete(row)
    cursor.execute("""
        SELECT a.id, p.name, d.name, d.specialization,
               a.date, a.time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors  d ON a.doctor_id  = d.id
        ORDER BY a.date, a.time
    """)
    for row in cursor.fetchall():
        tag = "booked" if row[6] == "Booked" else "other"
        appt_tree.insert("", tk.END, values=row, tags=(tag,))
    appt_tree.tag_configure("booked", foreground=ACCENT)

btn_row_a = tk.Frame(inp_card_a, bg=CARD)
btn_row_a.pack(padx=14, pady=12, fill="x")
styled_btn(btn_row_a, "  📅  Book", book_appointment).pack(side="left", padx=(0, 6))
styled_btn(btn_row_a, "  ✖  Cancel Appt", cancel_appointment, color=BTN_DEL, fg="#fff").pack(side="left")

tbl_card_a = make_card(tab_appt, "Appointment List", row=0, col=1)
appt_tree = tree_widget(tbl_card_a,
    cols=("ID","Patient","Doctor","Specialization","Date","Time","Status"),
    col_widths=[40, 130, 130, 130, 100, 90, 80])

# ─────────────────────────── STATUS BAR ─────────────────────────────
status_bar = tk.Frame(root, bg="#0d0f18", height=30)
status_bar.pack(fill="x", side="bottom")
status_var = tk.StringVar(value="✅  System ready.")
status_label = tk.Label(status_bar, textvariable=status_var,
                        bg="#0d0f18", fg=ACCENT, font=("Segoe UI", 9),
                        anchor="w", padx=12)
status_label.pack(side="left", fill="x")
tk.Label(status_bar, text="Hospital Management System v2.0",
         bg="#0d0f18", fg=MUTED, font=("Segoe UI", 9)).pack(side="right", padx=12)

# ─────────────────────────── INITIAL LOAD ───────────────────────────
load_patients()
load_doctors()
load_appointments()

# ─────────────────────────── CLOSE HANDLER ──────────────────────────
def on_close():
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()