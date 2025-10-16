import sqlite3
import pandas as pd
from datetime import date
from database.models import Database

class CRUDOperations:
    def __init__(self):
        self.db = Database()

    def get_connection(self):
        """Get a database connection."""
        return self.db.get_connection()

    # --- Appointment Operations ---
    def create_appointment(self, patient_id, doctor_id, treatment_ids, appointment_date, appointment_time, status, total_cost, commission_rate, notes):
        """Create a new appointment and link treatments."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, total_cost, commission_rate, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, appointment_date, appointment_time, status, total_cost, commission_rate, notes))
        appointment_id = cursor.lastrowid
        for treatment_id in treatment_ids:
            cursor.execute('''
                INSERT INTO appointment_treatments (appointment_id, treatment_id)
                VALUES (?, ?)
            ''', (appointment_id, treatment_id))
        conn.commit()
        conn.close()
        return appointment_id

    def update_appointment(self, appointment_id, patient_id, doctor_id, treatment_ids, appointment_date, appointment_time, status, total_cost, commission_rate, notes):
        """Update an existing appointment and its treatments."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments
            SET patient_id = ?, doctor_id = ?, appointment_date = ?, appointment_time = ?, status = ?, total_cost = ?, commission_rate = ?, notes = ?
            WHERE id = ?
        ''', (patient_id, doctor_id, appointment_date, appointment_time, status, total_cost, commission_rate, notes, appointment_id))
        cursor.execute('DELETE FROM appointment_treatments WHERE appointment_id = ?', (appointment_id,))
        for treatment_id in treatment_ids:
            cursor.execute('''
                INSERT INTO appointment_treatments (appointment_id, treatment_id)
                VALUES (?, ?)
            ''', (appointment_id, treatment_id))
        conn.commit()
        conn.close()

    def update_appointment_status(self, appointment_id, status):
        """Update the status of an appointment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments
            SET status = ?
            WHERE id = ?
        ''', (status, appointment_id))
        conn.commit()
        conn.close()

    def delete_appointment(self, appointment_id):
        """Delete an appointment and its associated treatments."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM appointment_treatments WHERE appointment_id = ?', (appointment_id,))
        cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
        conn.commit()
        conn.close()

    def get_all_appointments(self):
        """Retrieve all appointments with joined patient, doctor, and treatment data."""
        conn = self.get_connection()
        query = '''
            SELECT a.id, p.name as patient_name, d.name as doctor_name, GROUP_CONCAT(t.name) as treatment_name,
                   a.appointment_date, a.appointment_time, a.status, a.total_cost, a.commission_rate, a.notes, a.doctor_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN appointment_treatments at ON a.id = at.appointment_id
            JOIN treatments t ON at.treatment_id = t.id
            GROUP BY a.id
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_appointment_by_id(self, appointment_id):
        """Retrieve a single appointment by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT a.id, a.patient_id, a.doctor_id, a.appointment_date, a.appointment_time, a.status,
                   a.total_cost, a.commission_rate, a.notes
            FROM appointments a
            WHERE a.id = ?
        ''', (appointment_id,))
        appointment = cursor.fetchone()
        if appointment:
            cursor.execute('SELECT treatment_id FROM appointment_treatments WHERE appointment_id = ?', (appointment_id,))
            treatment_ids = [row[0] for row in cursor.fetchall()]
            appointment_dict = {
                'id': appointment[0],
                'patient_id': appointment[1],
                'doctor_id': appointment[2],
                'appointment_date': appointment[3],
                'appointment_time': appointment[4],
                'status': appointment[5],
                'total_cost': appointment[6],
                'commission_rate': appointment[7],
                'notes': appointment[8],
                'treatment_ids': treatment_ids
            }
            conn.close()
            return appointment_dict
        conn.close()
        return None

    def get_appointments_by_date(self, appointment_date):
        """Retrieve appointments for a specific date."""
        conn = self.get_connection()
        query = '''
            SELECT a.id, a.patient_id, a.doctor_id, p.name as patient_name, d.name as doctor_name,
                   a.appointment_date, a.appointment_time, a.status, a.total_cost, a.commission_rate, a.notes
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            WHERE a.appointment_date = ?
        '''
        df = pd.read_sql_query(query, conn, params=(appointment_date,))
        conn.close()
        return df

    # --- Patient Operations ---
    def create_patient(self, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
        """Create a new patient."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact))
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return patient_id

    def update_patient(self, patient_id, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
        """Update an existing patient."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE patients
            SET name = ?, phone = ?, email = ?, address = ?, date_of_birth = ?, gender = ?, medical_history = ?, emergency_contact = ?
            WHERE id = ?
        ''', (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact, patient_id))
        conn.commit()
        conn.close()

    def delete_patient(self, patient_id):
        """Delete a patient."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
        conn.commit()
        conn.close()

    def get_all_patients(self):
        """Retrieve all patients."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM patients", conn)
        conn.close()
        return df

    def get_patient_by_id(self, patient_id):
        """Retrieve a single patient by ID."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM patients WHERE id = ?", conn, params=(patient_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    # --- Doctor Operations ---
    def create_doctor(self, name, specialization, phone, email, commission_rate):
        """Create a new doctor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO doctors (name, specialization, phone, email, commission_rate)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, specialization, phone, email, commission_rate))
        doctor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doctor_id

    def update_doctor(self, doctor_id, name, specialization, phone, email, commission_rate):
        """Update an existing doctor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE doctors
            SET name = ?, specialization = ?, phone = ?, email = ?, commission_rate = ?
            WHERE id = ?
        ''', (name, specialization, phone, email, commission_rate, doctor_id))
        conn.commit()
        conn.close()

    def delete_doctor(self, doctor_id):
        """Delete a doctor."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM doctors WHERE id = ?', (doctor_id,))
        conn.commit()
        conn.close()

    def get_all_doctors(self):
        """Retrieve all doctors."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM doctors", conn)
        conn.close()
        return df

    def get_doctor_by_id(self, doctor_id):
        """Retrieve a single doctor by ID."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM doctors WHERE id = ?", conn, params=(doctor_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    # --- Treatment Operations ---
    def create_treatment(self, name, base_price, commission_rate, notes):
        """Create a new treatment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO treatments (name, base_price, commission_rate, notes)
            VALUES (?, ?, ?, ?)
        ''', (name, base_price, commission_rate, notes))
        treatment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return treatment_id

    def update_treatment(self, treatment_id, name, base_price, commission_rate, notes):
        """Update an existing treatment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE treatments
            SET name = ?, base_price = ?, commission_rate = ?, notes = ?
            WHERE id = ?
        ''', (name, base_price, commission_rate, notes, treatment_id))
        conn.commit()
        conn.close()

    def delete_treatment(self, treatment_id):
        """Delete a treatment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM appointment_treatments WHERE treatment_id = ?', (treatment_id,))
        cursor.execute('DELETE FROM treatments WHERE id = ?', (treatment_id,))
        conn.commit()
        conn.close()

    def get_all_treatments(self):
        """Retrieve all treatments."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM treatments", conn)
        conn.close()
        return df

    def get_treatment_by_id(self, treatment_id):
        """Retrieve a single treatment by ID."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM treatments WHERE id = ?", conn, params=(treatment_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    # --- Expense Operations ---
    def create_expense(self, category, description, amount, expense_date, payment_method, receipt_number, notes):
        """Create a new expense."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (category, description, amount, expense_date, payment_method, receipt_number, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category, description, amount, expense_date, payment_method, receipt_number, notes))
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return expense_id

    def update_expense(self, expense_id, category, description, amount, expense_date, payment_method, receipt_number, notes):
        """Update an existing expense."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE expenses
            SET category = ?, description = ?, amount = ?, expense_date = ?, payment_method = ?, receipt_number = ?, notes = ?
            WHERE id = ?
        ''', (category, description, amount, expense_date, payment_method, receipt_number, notes, expense_id))
        conn.commit()
        conn.close()

    def delete_expense(self, expense_id):
        """Delete an expense."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.commit()
        conn.close()

    def get_all_expenses(self):
        """Retrieve all expenses."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM expenses", conn)
        conn.close()
        return df

    def get_expense_by_id(self, expense_id):
        """Retrieve a single expense by ID."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM expenses WHERE id = ?", conn, params=(expense_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    # --- Payment Operations ---
    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date, status, notes):
        """Create a new payment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, amount, payment_method, payment_date, status, notes))
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id

    def update_payment(self, payment_id, appointment_id, patient_id, amount, payment_method, payment_date, status, notes):
        """Update an existing payment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE payments
            SET appointment_id = ?, patient_id = ?, amount = ?, payment_method = ?, payment_date = ?, status = ?, notes = ?
            WHERE id = ?
        ''', (appointment_id, patient_id, amount, payment_method, payment_date, status, notes, payment_id))
        conn.commit()
        conn.close()

    def delete_payment(self, payment_id):
        """Delete a payment."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM payments WHERE id = ?', (payment_id,))
        conn.commit()
        conn.close()

    def get_all_payments(self):
        """Retrieve all payments."""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT p.id, pt.name as patient_name, p.amount, p.payment_method, p.payment_date, p.status, p.notes, p.appointment_id
            FROM payments p
            JOIN patients pt ON p.patient_id = pt.id
        ''', conn)
        conn.close()
        return df

    def get_payment_by_id(self, payment_id):
        """Retrieve a single payment by ID."""
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT p.id, pt.name as patient_name, p.amount, p.payment_method, p.payment_date, p.status, p.notes, p.appointment_id
            FROM payments p
            JOIN patients pt ON p.patient_id = pt.id
            WHERE p.id = ?
        ''', conn, params=(payment_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    # --- Inventory Operations ---
    def create_inventory_item(self, item_name, quantity, min_stock_level, unit_price, supplier_id, notes):
        """Create a new inventory item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (item_name, quantity, min_stock_level, unit_price, supplier_id, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (item_name, quantity, min_stock_level, unit_price, supplier_id, notes))
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id

    def update_inventory_item(self, item_id, item_name, quantity, min_stock_level, unit_price, supplier_id, notes):
        """Update an existing inventory item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE inventory
            SET item_name = ?, quantity = ?, min_stock_level = ?, unit_price = ?, supplier_id = ?, notes = ?
            WHERE id = ?
        ''', (item_name, quantity, min_stock_level, unit_price, supplier_id, notes, item_id))
        conn.commit()
        conn.close()

    def delete_inventory_item(self, item_id):
        """Delete an inventory item."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM inventory WHERE id = ?', (item_id,))
        conn.commit()
        conn.close()

    def get_all_inventory(self):
        """Retrieve all inventory items."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        return df

    def get_low_stock_items(self):
        """Retrieve inventory items with low stock."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM inventory WHERE quantity <= min_stock_level", conn)
        conn.close()
        return df

    def get_inventory_item_by_id(self, item_id):
        """Retrieve a single inventory item by ID."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM inventory WHERE id = ?", conn, params=(item_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None

    # --- Supplier Operations ---
    def create_supplier(self, name, contact_person, phone, email, address, notes):
        """Create a new supplier."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO suppliers (name, contact_person, phone, email, address, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, contact_person, phone, email, address, notes))
        supplier_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return supplier_id

    def update_supplier(self, supplier_id, name, contact_person, phone, email, address, notes):
        """Update an existing supplier."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE suppliers
            SET name = ?, contact_person = ?, phone = ?, email = ?, address = ?, notes = ?
            WHERE id = ?
        ''', (name, contact_person, phone, email, address, notes, supplier_id))
        conn.commit()
        conn.close()

    def delete_supplier(self, supplier_id):
        """Delete a supplier."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM suppliers WHERE id = ?', (supplier_id,))
        conn.commit()
        conn.close()

    def get_all_suppliers(self):
        """Retrieve all suppliers."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers", conn)
        conn.close()
        return df

    def get_supplier_by_id(self, supplier_id):
        """Retrieve a single supplier by ID."""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers WHERE id = ?", conn, params=(supplier_id,))
        conn.close()
        return df.iloc[0] if not df.empty else None
