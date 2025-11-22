import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

DB_NAME = "medicare.db"

# --------------------- Database Layer ---------------------
class DB:
    def __init__(self, db_name: str = DB_NAME):
        self.conn = sqlite3.connect(db_name)
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.init_schema()

    def init_schema(self):
        cur = self.conn.cursor()
        # Patients
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                pid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER CHECK(age >= 0),
                gender TEXT CHECK(gender IN ('M','F','O')),
                phone TEXT,
                disease TEXT,
                address TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        # Appointments
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pid TEXT NOT NULL,
                doctor TEXT NOT NULL,
                dept TEXT,
                appt_date TEXT NOT NULL,
                appt_time TEXT,
                notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(pid) REFERENCES patients(pid) ON DELETE CASCADE
            )
            """
        )
        # Bills
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pid TEXT NOT NULL,
                consultation REAL DEFAULT 0,
                medicine REAL DEFAULT 0,
                room REAL DEFAULT 0,
                other REAL DEFAULT 0,
                total REAL NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(pid) REFERENCES patients(pid) ON DELETE CASCADE
            )
            """
        )
        self.conn.commit()

    # -------- Patients --------
    def add_patient(self, pid, name, age, gender, phone, disease, address):
        self.conn.execute(
            "INSERT INTO patients(pid, name, age, gender, phone, disease, address, created_at) VALUES (?,?,?,?,?,?,?,?)",
            (pid, name, age, gender, phone, disease, address, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def update_patient(self, pid, name, age, gender, phone, disease, address):
        self.conn.execute(
            "UPDATE patients SET name=?, age=?, gender=?, phone=?, disease=?, address=? WHERE pid=?",
            (name, age, gender, phone, disease, address, pid),
        )
        self.conn.commit()

    def delete_patient(self, pid):
        self.conn.execute("DELETE FROM patients WHERE pid=?", (pid,))
        self.conn.commit()

    def list_patients(self, search: str = ""):
        cur = self.conn.cursor()
        if search:
            like = f"%{search}%"
            cur.execute(
                "SELECT pid, name, age, gender, phone, disease, address, created_at FROM patients "
                "WHERE pid LIKE ? OR name LIKE ? OR phone LIKE ? ORDER BY created_at DESC",
                (like, like, like),
            )
        else:
            cur.execute(
                "SELECT pid, name, age, gender, phone, disease, address, created_at FROM patients ORDER BY created_at DESC"
            )
        return cur.fetchall()

    # -------- Appointments --------
    def add_appointment(self, pid, doctor, dept, appt_date, appt_time,notes):
        self.conn.execute(
            "INSERT INTO appointments(pid, doctor, dept, appt_date, appt_time, notes, created_at) VALUES (?,?,?,?,?,?,?)",
            (pid, doctor, dept, appt_date, appt_time, notes, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def delete_appointment(self, appt_id):
        self.conn.execute("DELETE FROM appointments WHERE id=?", (appt_id,))
        self.conn.commit()

    def list_appointments(self, pid_filter: str = ""):
        cur = self.conn.cursor()
        if pid_filter:
            cur.execute(
                "SELECT id, pid, doctor, dept, appt_date, appt_time, notes, created_at FROM appointments WHERE pid=? ORDER BY appt_date DESC, appt_time DESC",
                (pid_filter,),
            )
        else:
            cur.execute(
                "SELECT id, pid, doctor, dept, appt_date, appt_time, notes, created_at FROM appointments ORDER BY appt_date DESC, appt_time DESC"
            )
        return cur.fetchall()

    # -------- Bills --------
    def add_bill(self, pid, consultation, medicine, room, other):
        total = float(consultation or 0) + float(medicine or 0) + float(room or 0) + float(other or 0)
        self.conn.execute(
            "INSERT INTO bills(pid, consultation, medicine, room, other, total, created_at) VALUES (?,?,?,?,?,?,?)",
            (pid, consultation, medicine, room, other, total, datetime.now().isoformat(timespec="seconds")),
        )
        self.conn.commit()

    def list_bills(self, pid_filter: str = ""):
        cur = self.conn.cursor()
        if pid_filter:
            cur.execute(
                "SELECT id, pid, consultation, medicine, room, other, total, created_at FROM bills WHERE pid=? ORDER BY created_at DESC",
                (pid_filter,),
            )
        else:
            cur.execute(
                "SELECT id, pid, consultation, medicine, room, other, total, created_at FROM bills ORDER BY created_at DESC"
            )
        return cur.fetchall()

# --------------------- UI Helpers ---------------------
PAD = 8

class LabeledEntry(ttk.Frame):
    def __init__(self, master, label, **kwargs):
        super().__init__(master)
        ttk.Label(self, text=label).pack(side=tk.LEFT, padx=(0, 6))
        self.var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.var, **kwargs)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def get(self):
        return self.var.get().strip()

    def set(self, value):
        self.var.set(value or "")

class MoneyEntry(LabeledEntry):
    def get_float(self):
        try:
            return float(self.get() or 0)
        except ValueError:
            return 0.0

# --------------------- Main Application ---------------------
class MedicareApp(tk.Tk):
    DOCTORS = [
        ("Dr. Roy", "General Medicine"),
        ("Dr. Gupta", "Cardiologist"),
        ("Dr. Singh", "Neurologist"),
        ("Dr. Patel", "Orthopedic"),
        ("Dr. Mehta", "Pediatrician"),
        ("Dr. Sharma", "Dermatologist"),
        ("Dr. Anushka", "Gynecologist"),
        ("Dr. Iyer", "ENT Specialist"),
        ("Dr. Das", "Psychiatrist"),
        ("Dr. Rao", "Oncologist"),
        
        
        
        
        

    ]

    def __init__(self):
        super().__init__()
        self.title("Medicare Management System")
        self.geometry("1000x650")
        self.minsize(900, 580)
        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")
        self.db = DB()

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self._build_patients_tab()
        self._build_appointments_tab()
        self._build_billing_tab()

    # ---------------- Patients Tab ----------------
    def _build_patients_tab(self):
        tab = ttk.Frame(self.notebook, padding=PAD)
        self.notebook.add(tab, text="Patients")

        form = ttk.LabelFrame(tab, text="Register / Update Patient", padding=PAD)
        form.pack(fill=tk.X, padx=PAD, pady=PAD)

        row1 = ttk.Frame(form)
        row1.pack(fill=tk.X, pady=4)
        self.pid = LabeledEntry(row1, "Patient ID")
        self.pid.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.name = LabeledEntry(row1, "Name")
        self.name.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(PAD, 0))
        self.age = LabeledEntry(row1, "Age", width=8)
        self.age.pack(side=tk.LEFT, padx=(PAD, 0))
        self.gender = ttk.Frame(row1)
        ttk.Label(self.gender, text="Gender").pack(side=tk.LEFT, padx=(0, 6))
        self.gender_var = tk.StringVar(value="M")
        for val, txt in [("M", "M"), ("F", "F"), ("O", "O")]:
            ttk.Radiobutton(self.gender, text=txt, value=val, variable=self.gender_var).pack(side=tk.LEFT)
        self.gender.pack(side=tk.LEFT, padx=(PAD, 0))

        row2 = ttk.Frame(form)
        row2.pack(fill=tk.X, pady=4)
        self.phone = LabeledEntry(row2, "Phone")
        self.phone.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.disease = LabeledEntry(row2, "Disease/Symptoms")
        self.disease.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(PAD, 0))

        self.address = LabeledEntry(form, "Address")
        self.address.pack(fill=tk.X, pady=4)

        btns = ttk.Frame(form)
        btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Save / Add", command=self.save_patient).pack(side=tk.LEFT)
        ttk.Button(btns, text="Update", command=self.update_patient).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Delete", command=self.delete_patient).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Clear", command=self.clear_patient_form).pack(side=tk.LEFT, padx=6)

        search_row = ttk.Frame(tab)
        search_row.pack(fill=tk.X, padx=PAD)
        ttk.Label(search_row, text="Search (ID/Name/Phone):").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 0))
        search_entry.bind("<KeyRelease>", lambda e: self.refresh_patients())

        # Table
        cols = ("pid", "name", "age", "gender", "phone", "disease", "address", "created_at")
        self.patients_tv = ttk.Treeview(tab, columns=cols, show="headings", height=12)
        for c, w in zip(cols, (100, 160, 50, 70, 100, 160, 220, 140)):
            self.patients_tv.heading(c, text=c.upper())
            self.patients_tv.column(c, width=w, anchor=tk.W)
        self.patients_tv.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(4, PAD))
        self.patients_tv.bind("<<TreeviewSelect>>", self.on_patient_select)

        self.refresh_patients()

    def _validate_patient(self):
        if not self.pid.get():
            messagebox.showerror("Validation", "Patient ID is required")
            return False
        if not self.name.get():
            messagebox.showerror("Validation", "Name is required")
            return False
        try:
            if self.age.get():
                int(self.age.get())
        except ValueError:
            messagebox.showerror("Validation", "Age must be a number")
            return False
        if self.gender_var.get() not in ("M", "F", "O"):
            messagebox.showerror("Validation", "Invalid gender")
            return False
        return True

    def save_patient(self):
        if not self._validate_patient():
            return
        try:
            self.db.add_patient(
                self.pid.get(),
                self.name.get(),
                int(self.age.get() or 0),
                self.gender_var.get(),
                self.phone.get(),
                self.disease.get(),
                self.address.get(),
            )
            messagebox.showinfo("Success", "Patient added")
            self.refresh_patients()
            self.clear_patient_form()
            self.refresh_patient_comboboxes()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Patient ID already exists. Use Update instead.")

    def update_patient(self):
        if not self._validate_patient():
            return
        self.db.update_patient(
            self.pid.get(),
            self.name.get(),
            int(self.age.get() or 0),
            self.gender_var.get(),
            self.phone.get(),
            self.disease.get(),
            self.address.get(),
        )
        messagebox.showinfo("Success", "Patient updated")
        self.refresh_patients()
        self.refresh_patient_comboboxes()

    def delete_patient(self):
        pid = self.pid.get()
        if not pid:
            messagebox.showerror("Error", "Enter Patient ID to delete")
            return
        if messagebox.askyesno("Confirm", f"Delete patient {pid}? This will also remove appointments and bills."):
            self.db.delete_patient(pid)
            self.refresh_patients()
            self.clear_patient_form()
            self.refresh_patient_comboboxes()

    def clear_patient_form(self):
        for w in (self.pid, self.name, self.age, self.phone, self.disease, self.address):
            w.set("")
        self.gender_var.set("M")
        self.patients_tv.selection_remove(*self.patients_tv.selection())

    def refresh_patients(self):
        for i in self.patients_tv.get_children():
            self.patients_tv.delete(i)
        rows = self.db.list_patients(self.search_var.get().strip())
        for r in rows:
            self.patients_tv.insert("", tk.END, values=r)
        self.refresh_patient_comboboxes()

    def on_patient_select(self, _):
        sel = self.patients_tv.selection()
        if not sel:
            return
        vals = self.patients_tv.item(sel[0], "values")
        self.pid.set(vals[0])
        self.name.set(vals[1])
        self.age.set(vals[2])
        self.gender_var.set(vals[3])
        self.phone.set(vals[4])
        self.disease.set(vals[5])
        self.address.set(vals[6])

    # ---------------- Appointments Tab ----------------
    def _build_appointments_tab(self):
        tab = ttk.Frame(self.notebook, padding=PAD)
        self.notebook.add(tab, text="Appointments")

        form = ttk.LabelFrame(tab, text="Book Appointment", padding=PAD)
        form.pack(fill=tk.X, padx=PAD, pady=PAD)

        row = ttk.Frame(form)
        row.pack(fill=tk.X, pady=4)

        ttk.Label(row, text="Patient").pack(side=tk.LEFT)
        self.appt_patient_var = tk.StringVar()
        self.appt_patient_cb = ttk.Combobox(row, textvariable=self.appt_patient_var, width=28, state="readonly")
        self.appt_patient_cb.pack(side=tk.LEFT, padx=(6, PAD))

        ttk.Label(row, text="Doctor").pack(side=tk.LEFT)
        self.doctor_var = tk.StringVar()
        self.doctor_cb = ttk.Combobox(row, textvariable=self.doctor_var, state="readonly")
        self.doctor_cb['values'] = [d[0] for d in self.DOCTORS]
        self.doctor_cb.current(0)
        self.doctor_cb.pack(side=tk.LEFT, padx=(6, PAD))

        ttk.Label(row, text="Dept").pack(side=tk.LEFT)
        self.dept_var = tk.StringVar()
        self.dept_cb = ttk.Combobox(row, textvariable=self.dept_var, state="readonly")
        self.dept_cb['values'] = sorted(list({d[1] for d in self.DOCTORS}))
        self.dept_cb.current(0)
        self.dept_cb.pack(side=tk.LEFT, padx=(6, PAD))

        row2 = ttk.Frame(form)
        row2.pack(fill=tk.X, pady=4)
        self.appt_date = LabeledEntry(row2, "Date (YYYY-MM-DD)")
        self.appt_date.pack(side=tk.LEFT, padx=(0, PAD))
        self.appt_time = LabeledEntry(row2, "Time (HH:MM)")
        self.appt_time.pack(side=tk.LEFT, padx=(0, PAD))
        self.appt_notes = LabeledEntry(row2, "Notes")
        self.appt_notes.pack(side=tk.LEFT, fill=tk.X, expand=True)

        btns = ttk.Frame(form)
        btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Book", command=self.book_appointment).pack(side=tk.LEFT)
        ttk.Button(btns, text="Delete Selected", command=self.delete_selected_appointment).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Refresh", command=self.refresh_appointments).pack(side=tk.LEFT)

        # Table
        cols = ("id", "pid", "doctor", "dept", "appt_date", "appt_time", "notes", "created_at")
        self.appt_tv = ttk.Treeview(tab, columns=cols, show="headings", height=13)
        for c, w in zip(cols, (60, 100, 140, 120, 100, 80, 220, 140)):
            self.appt_tv.heading(c, text=c.upper())
            self.appt_tv.column(c, width=w, anchor=tk.W)
        self.appt_tv.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(4, PAD))

        filter_row = ttk.Frame(tab)
        filter_row.pack(fill=tk.X, padx=PAD, pady=(0, PAD))
        ttk.Label(filter_row, text="Filter by Patient ID:").pack(side=tk.LEFT)
        self.appt_filter_var = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.appt_filter_var, width=20).pack(side=tk.LEFT, padx=(6, 6))
        ttk.Button(filter_row, text="Apply", command=self.refresh_appointments).pack(side=tk.LEFT)

        self.refresh_patient_comboboxes()
        self.refresh_appointments()

    def refresh_patient_comboboxes(self):
        # For appointment & billing dropdowns
        patients = [f"{r[0]} - {r[1]}" for r in self.db.list_patients()]
        if hasattr(self, 'appt_patient_cb'):
            self.appt_patient_cb['values'] = patients
            if patients and not self.appt_patient_var.get():
                self.appt_patient_cb.current(0)
        if hasattr(self, 'bill_patient_cb'):
            self.bill_patient_cb['values'] = patients
            if patients and not self.bill_patient_var.get():
                self.bill_patient_cb.current(0)

    def _extract_pid(self, combo_value: str) -> str:
        # combo format: "PID - Name"
        return (combo_value or "").split(" - ")[0]

    def book_appointment(self):
        pid = self._extract_pid(self.appt_patient_var.get())
        if not pid:
            messagebox.showerror("Validation", "Select a patient")
            return
        date = self.appt_date.get()
        time_ = self.appt_time.get()
        doctor = self.doctor_var.get()
        dept = self.dept_var.get()
        if not date:
            messagebox.showerror("Validation", "Date is required (YYYY-MM-DD)")
            return
        try:
            # light validation
            datetime.strptime(date, "%Y-%m-%d")
            if time_:
                datetime.strptime(time_, "%H:%M")
        except ValueError:
            messagebox.showerror("Validation", "Invalid date/time format")
            return
        self.db.add_appointment(pid, doctor, dept, date, time_, self.appt_notes.get())
        messagebox.showinfo("Success", "Appointment booked")
        self.refresh_appointments()
        self.appt_notes.set("")

    def delete_selected_appointment(self):
        sel = self.appt_tv.selection()
        if not sel:
            messagebox.showerror("Error", "Select an appointment to delete")
            return
        appt_id = self.appt_tv.item(sel[0], "values")[0]
        if messagebox.askyesno("Confirm", f"Delete appointment #{appt_id}?"):
            self.db.delete_appointment(appt_id)
            self.refresh_appointments()

    def refresh_appointments(self):
        for i in self.appt_tv.get_children():
            self.appt_tv.delete(i)
        pid_filter = self.appt_filter_var.get().strip()
        for r in self.db.list_appointments(pid_filter):
            self.appt_tv.insert("", tk.END, values=r)

    # ---------------- Billing Tab ----------------
    def _build_billing_tab(self):
        tab = ttk.Frame(self.notebook, padding=PAD)
        self.notebook.add(tab, text="Billing")

        form = ttk.LabelFrame(tab, text="Generate Bill", padding=PAD)
        form.pack(fill=tk.X, padx=PAD, pady=PAD)

        top = ttk.Frame(form)
        top.pack(fill=tk.X, pady=4)
        ttk.Label(top, text="Patient").pack(side=tk.LEFT)
        self.bill_patient_var = tk.StringVar()
        self.bill_patient_cb = ttk.Combobox(top, textvariable=self.bill_patient_var, width=28, state="readonly")
        self.bill_patient_cb.pack(side=tk.LEFT, padx=(6, PAD))

        charges = ttk.Frame(form)
        charges.pack(fill=tk.X, pady=4)
        self.consult = MoneyEntry(charges, "Consultation")
        self.consult.pack(side=tk.LEFT, padx=(0, PAD))
        self.medicine = MoneyEntry(charges, "Medicine")
        self.medicine.pack(side=tk.LEFT, padx=(0, PAD))
        self.room = MoneyEntry(charges, "Room")
        self.room.pack(side=tk.LEFT, padx=(0, PAD))
        self.other = MoneyEntry(charges, "Other")
        self.other.pack(side=tk.LEFT, padx=(0, PAD))

        btns = ttk.Frame(form)
        btns.pack(fill=tk.X, pady=4)
        ttk.Button(btns, text="Calculate Total", command=self.calc_total).pack(side=tk.LEFT)
        ttk.Button(btns, text="Save Bill", command=self.save_bill).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="Export Selected (TXT)", command=self.export_selected_bill).pack(side=tk.LEFT, padx=6)

        self.total_var = tk.StringVar(value="Total: 0.00")
        ttk.Label(form, textvariable=self.total_var, font=("Segoe UI", 12, "bold")).pack(anchor=tk.W, pady=(4, 0))

        cols = ("id", "pid", "consultation", "medicine", "room", "other", "total", "created_at")
        self.bills_tv = ttk.Treeview(tab, columns=cols, show="headings", height=13)
        for c, w in zip(cols, (60, 100, 110, 110, 90, 90, 100, 140)):
            self.bills_tv.heading(c, text=c.upper())
            self.bills_tv.column(c, width=w, anchor=tk.W)
        self.bills_tv.pack(fill=tk.BOTH, expand=True, padx=PAD, pady=(4, PAD))

        filter_row = ttk.Frame(tab)
        filter_row.pack(fill=tk.X, padx=PAD, pady=(0, PAD))
        ttk.Label(filter_row, text="Filter by Patient ID:").pack(side=tk.LEFT)
        self.bill_filter_var = tk.StringVar()
        ttk.Entry(filter_row, textvariable=self.bill_filter_var, width=20).pack(side=tk.LEFT, padx=(6, 6))
        ttk.Button(filter_row, text="Apply", command=self.refresh_bills).pack(side=tk.LEFT)

        self.refresh_patient_comboboxes()
        self.refresh_bills()

    def calc_total(self):
        total = sum([
            self.consult.get_float(),
            self.medicine.get_float(),
            self.room.get_float(),
            self.other.get_float(),
        ])
        self.total_var.set(f"Total: {total:.2f}")
        return total

    def save_bill(self):
        pid = self._extract_pid(self.bill_patient_var.get())
        if not pid:
            messagebox.showerror("Validation", "Select a patient")
            return
        c, m, r, o = (
            self.consult.get_float(),
            self.medicine.get_float(),
            self.room.get_float(),
            self.other.get_float(),
        )
        total = c + m + r + o
        self.db.add_bill(pid, c, m, r, o)
        messagebox.showinfo("Success", f"Bill saved. Total = {total:.2f}")
        self.refresh_bills()
        self.total_var.set("Total: 0.00")
        for w in (self.consult, self.medicine, self.room, self.other):
            w.set("")

    def refresh_bills(self):
        for i in self.bills_tv.get_children():
            self.bills_tv.delete(i)
        pid_filter = self.bill_filter_var.get().strip()
        for r in self.db.list_bills(pid_filter):
            self.bills_tv.insert("", tk.END, values=r)

    def export_selected_bill(self):
        sel = self.bills_tv.selection()
        if not sel:
            messagebox.showerror("Error", "Select a bill to export")
            return
        vals = self.bills_tv.item(sel[0], "values")
        bill_id, pid, c, m, r, o, total, created = vals
        # Fetch patient name
        rows = self.db.list_patients(pid)
        pname = rows[0][1] if rows else "Unknown"
        content = (
            f"==== Medicare Bill ===\n"
            f"Bill ID: {bill_id}\nDate: {created}\n\n"
            f"Patient ID: {pid}\nName: {pname}\n\n"
            f"Consultation: {c}\nMedicine: {m}\nRoom: {r}\nOther: {o}\n"
            f"---------------------------\nTotal: {total}\n"
        )
        fname = f"bill_{bill_id}.txt"
        with open(fname, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("Exported", f"Saved {fname} in current folder")

# --------------------- Run ---------------------
if __name__ == "__main__":
    app = MedicareApp()
    app.mainloop()
