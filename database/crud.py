import sqlite3
import pandas as pd
from datetime import date
from database.models import Database

class CRUDOperations:
    def __init__(self):
        self.db = Database()

    def get_connection(self):
        return self.db.get_connection()

    def create_appointment(self, patient_id, doctor_id, treatment_ids, appointment_date, appointment_time, status, total_cost, commission_rate, notes):
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

    def update_appointment_status(self, appointment_id, status):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE appointments
            SET status = ?
            WHERE id = ?
        ''', (status, appointment_id))
        conn.commit()
        conn.close()

    def update_appointment(self, appointment_id, patient_id, doctor_id, treatment_ids, appointment_date, appointment_time, status, total_cost, commission_rate, notes):
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

    def delete_appointment(self, appointment_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM appointment_treatments WHERE appointment_id = ?', (appointment_id,))
        cursor.execute('DELETE FROM appointments WHERE id = ?', (appointment_id,))
        conn.commit()
        conn.close()

    def get_all_appointments(self):
        conn = self.get_connection()
        query = '''
            SELECT a.id, p.name as patient_name, d.name as doctor_name, t.name as treatment_name, 
                   a.appointment_date, a.appointment_time, a.status, a.total_cost, a.commission_rate, a.notes
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN appointment_treatments at ON a.id = at.appointment_id
            JOIN treatments t ON at.treatment_id = t.id
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_appointments_by_date(self, appointment_date):
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

    def get_appointment_by_id(self, appointment_id):
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

    def get_all_patients(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM patients", conn)
        conn.close()
        return df

    def get_all_doctors(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM doctors", conn)
        conn.close()
        return df

    def get_all_treatments(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM treatments", conn)
        conn.close()
        return df

    def create_patient(self, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
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

    def get_all_inventory(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM inventory", conn)
        conn.close()
        return df

    def get_low_stock_items(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM inventory WHERE quantity <= min_stock_level", conn)
        conn.close()
        return df

    def create_expense(self, category, description, amount, expense_date, payment_method, receipt_number, notes):
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

    def get_all_expenses(self):
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM expenses", conn)
        conn.close()
        return df

    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date, status, notes):
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

    def get_all_payments(self):
        conn = self.get_connection()
        df = pd.read_sql_query('''
            SELECT p.id, pt.name as patient_name, p.amount, p.payment_method, p.payment_date, p.status, p.notes, p.appointment_id
            FROM payments p
            JOIN patients pt ON p.patient_id = pt.id
        ''', conn)
        conn.close()
        return df
