import sqlite3
import pandas as pd
from datetime import datetime, date
from .models import db

class CRUDOperations:
    def __init__(self):
        self.db = db
    
    # ========== عمليات الأطباء ==========
    def create_doctor(self, name, specialization, phone, email, address, hire_date, salary, commission_rate=0.0):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO doctors (name, specialization, phone, email, address, hire_date, salary, commission_rate)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, specialization, phone, email, address, hire_date, salary, commission_rate))
        doctor_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return doctor_id
    
    def get_all_doctors(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM doctors ORDER BY name", conn)
        conn.close()
        return df
    
    def get_doctor_by_id(self, doctor_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_doctor(self, doctor_id, name, specialization, phone, email, address, salary, commission_rate):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE doctors SET name=?, specialization=?, phone=?, email=?, address=?, salary=?, commission_rate=?
            WHERE id=?
        ''', (name, specialization, phone, email, address, salary, commission_rate, doctor_id))
        conn.commit()
        conn.close()
    
    def delete_doctor(self, doctor_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات المرضى ==========
    def create_patient(self, name, phone, email, address, date_of_birth, gender, medical_history="", emergency_contact=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact))
        patient_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return patient_id
    
    def get_all_patients(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY name", conn)
        conn.close()
        return df
    
    def get_patient_by_id(self, patient_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_patient(self, patient_id, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE patients SET name=?, phone=?, email=?, address=?, date_of_birth=?, gender=?, medical_history=?, emergency_contact=?
            WHERE id=?
        ''', (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact, patient_id))
        conn.commit()
        conn.close()
    
    def delete_patient(self, patient_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات المواعيد ==========
    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status="مجدول", notes="", total_cost=None):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost))
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return appointment_id
    
    def get_all_appointments(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("""
            SELECT a.*, p.name AS patient_name, d.name AS doctor_name, t.name AS treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            ORDER BY a.appointment_date, a.appointment_time
        """, conn)
        conn.close()
        return df
    
    def get_appointments_by_date(self, appointment_date):
        conn = self.db.get_connection()
        df = pd.read_sql_query("""
            SELECT a.*, p.name AS patient_name, d.name AS doctor_name, t.name AS treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        """, conn, params=(appointment_date,))
        conn.close()
        return df
    
    def update_appointment(self, appointment_id, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments 
            SET patient_id=?, doctor_id=?, treatment_id=?, appointment_date=?, appointment_time=?, status=?, notes=?, total_cost=?
            WHERE id=?
        ''', (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost, appointment_id))
        conn.commit()
        conn.close()
    
    def delete_appointment(self, appointment_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات العلاجات ==========
    def create_treatment(self, name, description, base_price, duration_minutes, category):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO treatments (name, description, base_price, duration_minutes, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, description, base_price, duration_minutes, category))
        treatment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return treatment_id
    
    def get_all_treatments(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM treatments WHERE is_active = 1 ORDER BY name", conn)
        conn.close()
        return df
    
    def get_treatment_by_id(self, treatment_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM treatments WHERE id = ?", (treatment_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_treatment(self, treatment_id, name, description, base_price, duration_minutes, category):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE treatments 
            SET name=?, description=?, base_price=?, duration_minutes=?, category=?
            WHERE id=?
        ''', (name, description, base_price, duration_minutes, category, treatment_id))
        conn.commit()
        conn.close()
    
    def delete_treatment(self, treatment_id):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE treatments SET is_active = 0 WHERE id = ?", (treatment_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات المدفوعات ==========
    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date, status="مكتمل", notes=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, amount, payment_method, payment_date, status, notes))
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def get_all_payments(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("""
            SELECT p.*, a.patient_id AS appointment_patient_id, pt.name AS patient_name
            FROM payments p
            LEFT JOIN appointments a ON p.appointment_id = a.id
            LEFT JOIN patients pt ON p.patient_id = pt.id
            ORDER BY p.payment_date DESC
        """, conn)
        conn.close()
        return df
    
    # ========== عمليات المخزون ==========
    def create_inventory(self, item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date))
        inventory_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return inventory_id
    
    def get_all_inventory(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("""
            SELECT i.*, s.name AS supplier_name
            FROM inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY i.item_name
        """, conn)
        conn.close()
        return df
    
    def get_low_stock_items(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM inventory WHERE quantity <= min_stock_level ORDER BY quantity", conn)
        conn.close()
        return df
    
    def update_inventory_quantity(self, item_id, quantity):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (quantity, item_id))
        conn.commit()
        conn.close()
    
    # ========== عمليات الموردين ==========
    def create_supplier(self, name, contact_person, phone, email, address, payment_terms):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, contact_person, phone, email, address, payment_terms))
        supplier_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return supplier_id
    
    def get_all_suppliers(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY name", conn)
        conn.close()
        return df
    
    # ========== عمليات المصروفات ==========
    def create_expense(self, category, description, amount, expense_date, payment_method, receipt_number="", notes=""):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (category, description, amount, expense_date, payment_method, receipt_number, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category, description, amount, expense_date, payment_method, receipt_number, notes))
        expense_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return expense_id
    
    def get_all_expenses(self):
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY expense_date DESC", conn)
        conn.close()
        return df
    
    # ========== تقارير وإحصائيات ==========
    def get_financial_summary(self, start_date=None, end_date=None):
        conn = self.db.get_connection()
        payments_query = "SELECT COALESCE(SUM(amount), 0) as total_payments FROM payments"
        expenses_query = "SELECT COALESCE(SUM(amount), 0) as total_expenses FROM expenses"
        if start_date and end_date:
            payments_query += f" WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'"
            expenses_query += f" WHERE expense_date BETWEEN '{start_date}' AND '{end_date}'"
        
        total_payments = pd.read_sql_query(payments_query, conn).iloc[0]['total_payments']
        total_expenses = pd.read_sql_query(expenses_query, conn).iloc[0]['total_expenses']
        conn.close()
        
        return {
            'total_revenue': total_payments,
            'total_expenses': total_expenses,
            'net_profit': total_payments - total_expenses
        }
    
    def get_daily_appointments_count(self):
        conn = self.db.get_connection()
        today = date.today().isoformat()
        query = "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ?"
        result = pd.read_sql_query(query, conn, params=(today,))
        conn.close()
        return result.iloc[0]['count'] if not result.empty else 0

# إنشاء مثيل من عمليات CRUD
crud = CRUDOperations()
