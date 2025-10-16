import sqlite3
import pandas as pd
from datetime import datetime, date
from .models import db

class CRUDOperations:
    def __init__(self):
        self.db = db
    
    # ========== عمليات الأطباء ==========
    def create_doctor(self, name, specialization, phone, email, address, hire_date, salary, commission_rate=0.0):
        """إضافة طبيب جديد"""
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
        """الحصول على جميع الأطباء"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM doctors ORDER BY name", conn)
        conn.close()
        return df
    
    def get_doctor_by_id(self, doctor_id):
        """الحصول على طبيب بواسطة ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_doctor(self, doctor_id, name, specialization, phone, email, address, salary, commission_rate):
        """تحديث بيانات طبيب"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE doctors 
            SET name=?, specialization=?, phone=?, email=?, address=?, salary=?, commission_rate=?
            WHERE id=?
        ''', (name, specialization, phone, email, address, salary, commission_rate, doctor_id))
        
        conn.commit()
        conn.close()
    
    def delete_doctor(self, doctor_id):
        """حذف طبيب"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات المرضى ==========
    def create_patient(self, name, phone, email, address, date_of_birth, gender, medical_history="", emergency_contact=""):
        """إضافة مريض جديد"""
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
        """الحصول على جميع المرضى"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY name", conn)
        conn.close()
        return df
    
    def get_patient_by_id(self, patient_id):
        """الحصول على مريض بواسطة ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_patient(self, patient_id, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
        """تحديث بيانات مريض"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE patients 
            SET name=?, phone=?, email=?, address=?, date_of_birth=?, gender=?, medical_history=?, emergency_contact=?
            WHERE id=?
        ''', (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact, patient_id))
        
        conn.commit()
        conn.close()
    
    def delete_patient(self, patient_id):
        """حذف مريض"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات العلاجات ==========
    def create_treatment(self, name, description, base_price, duration_minutes, category, commission_rate=0.0):
        """إضافة علاج جديد مع نسبة العمولة"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO treatments (name, description, base_price, duration_minutes, category, commission_rate)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, base_price, duration_minutes, category, commission_rate))
        
        treatment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return treatment_id
    
    def get_all_treatments(self):
        """الحصول على جميع العلاجات مع نسبة العمولة"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM treatments WHERE is_active = 1 ORDER BY name", conn)
        conn.close()
        return df
    
    def get_treatment_by_id(self, treatment_id):
        """الحصول على علاج بواسطة ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM treatments WHERE id = ?", (treatment_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_treatment(self, treatment_id, name, description, base_price, duration_minutes, category, commission_rate):
        """تحديث بيانات علاج مع نسبة العمولة"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE treatments 
            SET name=?, description=?, base_price=?, duration_minutes=?, category=?, commission_rate=?
            WHERE id=?
        ''', (name, description, base_price, duration_minutes, category, commission_rate, treatment_id))
        
        conn.commit()
        conn.close()
    
    def delete_treatment(self, treatment_id):
        """تعطيل علاج (soft delete)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE treatments SET is_active = 0 WHERE id = ?", (treatment_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات المواعيد ==========
    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status='مجدول', notes="", total_cost=0.0):
        """إضافة موعد جديد"""
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
        """الحصول على جميع المواعيد مع التفاصيل"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.*,
                p.name as patient_name,
                d.name as doctor_name,
                t.name as treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            ORDER BY a.appointment_date, a.appointment_time
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_appointments_by_date(self, appointment_date):
        """الحصول على المواعيد في تاريخ معين"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.*,
                p.name as patient_name,
                d.name as doctor_name,
                t.name as treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        '''
        df = pd.read_sql_query(query, conn, params=(appointment_date,))
        conn.close()
        return df
    
    def get_appointment_by_id(self, appointment_id):
        """الحصول على موعد بواسطة ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    def update_appointment(self, appointment_id, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost):
        """تحديث موعد"""
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
        """حذف موعد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات المدفوعات ==========
    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date, status='مكتمل', notes=""):
        """إضافة دفعة جديدة"""
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
        """الحصول على جميع المدفوعات مع تفاصيل المريض"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                pay.*,
                p.name as patient_name
            FROM payments pay
            LEFT JOIN patients p ON pay.patient_id = p.id
            ORDER BY pay.payment_date DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    # ========== عمليات المصروفات ==========
    def create_expense(self, category, description, amount, expense_date, payment_method, receipt_number="", notes=""):
        """إضافة مصروف جديد"""
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
        """الحصول على جميع المصروفات"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY expense_date DESC", conn)
        conn.close()
        return df
    
    # ========== تقارير وإحصائيات ==========
    def get_financial_summary(self, start_date=None, end_date=None):
        """الحصول على ملخص مالي مع حصص العيادة والأطباء"""
        conn = self.db.get_connection()
        
        # إجمالي المدفوعات
        payments_query = "SELECT COALESCE(SUM(amount), 0) as total_payments FROM payments"
        if start_date and end_date:
            payments_query += f" WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'"
        
        # إجمالي المصروفات
        expenses_query = "SELECT COALESCE(SUM(amount), 0) as total_expenses FROM expenses"
        if start_date and end_date:
            expenses_query += f" WHERE expense_date BETWEEN '{start_date}' AND '{end_date}'"
        
        total_payments = pd.read_sql_query(payments_query, conn).iloc[0]['total_payments']
        total_expenses = pd.read_sql_query(expenses_query, conn).iloc[0]['total_expenses']
        
        # حساب حصص العيادة والأطباء بناءً على commission_rate في treatments
        appointments_query = '''
            SELECT a.total_cost, t.commission_rate
            FROM appointments a
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.status = 'مكتمل'
        '''
        if start_date and end_date:
            appointments_query += f" AND a.appointment_date BETWEEN '{start_date}' AND '{end_date}'"
        
        appointments_df = pd.read_sql_query(appointments_query, conn)
        doctors_share = (appointments_df['total_cost'] * (appointments_df['commission_rate'] / 100)).sum()
        clinic_share = appointments_df['total_cost'].sum() - doctors_share
        
        conn.close()
        
        return {
            'total_revenue': total_payments,
            'total_expenses': total_expenses,
            'net_profit': total_payments - total_expenses,
            'clinic_share': clinic_share,
            'doctors_share': doctors_share
        }
    
    def get_daily_appointments_count(self):
        """عدد المواعيد اليومية"""
        conn = self.db.get_connection()
        today = date.today().isoformat()
        query = "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ?"
        result = pd.read_sql_query(query, conn, params=(today,))
        conn.close()
        return result.iloc[0]['count'] if not result.empty else 0

# إنشاء مثيل من عمليات CRUD
crud = CRUDOperations()
