import sqlite3
import pandas as pd
from datetime import datetime, date
# يجب أن يكون ملف crud.py ضمن حزمة (package) لعمل هذا الاستيراد
# ويفترض أن ملف models.py يعرف مثيل قاعدة بيانات باسم 'db'
from .models import db 

class CRUDOperations:
    """
    كلاس مسؤول عن جميع عمليات قاعدة البيانات (إنشاء, قراءة, تحديث, حذف)
    باستخدام SQLite و Pandas.
    """
    
    def __init__(self):
        # الكائن 'db' من ملف models.py يجب أن يوفر دالة get_connection()
        self.db = db
    
    
    # ====================================================================
    #          عمليات الأطباء والموظفين (doctors)
    # ====================================================================
    
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
        """الحصول على جميع الأطباء في DataFrame"""
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

    def update_doctor(self, id, name, specialization, phone, email, address, hire_date, salary, commission_rate):
        """تحديث بيانات طبيب موجود"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE doctors 
            SET name=?, specialization=?, phone=?, email=?, address=?, hire_date=?, salary=?, commission_rate=?
            WHERE id=?
        ''', (name, specialization, phone, email, address, hire_date, salary, commission_rate, id))
        conn.commit()
        conn.close()

    def delete_doctor(self, doctor_id):
        """حذف طبيب"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        conn.commit()
        conn.close()


    # ====================================================================
    #          عمليات المرضى (patients)
    # ====================================================================

    def create_patient(self, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
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
        """الحصول على جميع المرضى في DataFrame"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY name", conn)
        conn.close()
        return df

    def update_patient(self, id, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
        """تحديث بيانات مريض موجود"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE patients 
            SET name=?, phone=?, email=?, address=?, date_of_birth=?, gender=?, medical_history=?, emergency_contact=?
            WHERE id=?
        ''', (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact, id))
        conn.commit()
        conn.close()

    def delete_patient(self, patient_id):
        """حذف مريض"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        conn.close()


    # ====================================================================
    #          عمليات العلاجات (treatments)
    # ====================================================================

    def create_treatment(self, name, description, base_price, duration_minutes, category, is_active=1):
        """إضافة علاج جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO treatments (name, description, base_price, duration_minutes, category, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, base_price, duration_minutes, category, is_active))
        conn.commit()
        conn.close()

    def get_all_treatments(self):
        """الحصول على جميع العلاجات النشطة في DataFrame"""
        conn = self.db.get_connection()
        # جلب is_active=1 (افتراضياً)
        df = pd.read_sql_query("SELECT * FROM treatments WHERE is_active = 1 ORDER BY name", conn)
        conn.close()
        return df
    
    def get_treatment_by_id(self, treatment_id):
        """الحصول على علاج بواسطة ID (مطلوب لعملية التحديث)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM treatments WHERE id = ?", (treatment_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_treatment(self, treatment_id, name, description, base_price, duration_minutes, category, is_active=1):
        """تحديث بيانات علاج موجود"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE treatments 
            SET name=?, description=?, base_price=?, duration_minutes=?, category=?, is_active=?
            WHERE id=?
        ''', (name, description, base_price, duration_minutes, category, is_active, treatment_id))
        conn.commit()
        conn.close()

    def delete_treatment(self, treatment_id):
        """حذف علاج (حذف منطقي بتعيين is_active=0)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE treatments SET is_active = 0 WHERE id = ?", (treatment_id,))
        conn.commit()
        conn.close()


    # ====================================================================
    #          عمليات المواعيد (appointments)
    # ====================================================================
    
    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost, status='مؤكد'):
        """حجز موعد جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost, status))
        
        conn.commit()
        conn.close()
    
    def get_all_appointments(self):
        """الحصول على جميع المواعيد مع أسماء المرضى والأطباء والعلاجات"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.id,
                a.appointment_date,
                a.appointment_time,
                a.total_cost,
                a.status,
                p.name AS patient_name,
                d.name AS doctor_name,
                t.name AS treatment_name,
                a.patient_id,
                a.doctor_id,
                a.treatment_id
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN treatments t ON a.treatment_id = t.id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def update_appointment_status(self, appointment_id, status):
        """تحديث حالة موعد (مؤكد, منتهي, ملغي)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
        conn.commit()
        conn.close()
    
    def get_appointments_by_date(self, target_date):
        """جلب مواعيد ليوم محدد"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.id, a.appointment_time, a.status,
                p.name AS patient_name,
                d.name AS doctor_name,
                t.name AS treatment_name
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            JOIN doctors d ON a.doctor_id = d.id
            JOIN treatments t ON a.treatment_id = t.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        '''
        df = pd.read_sql_query(query, conn, params=(target_date,))
        conn.close()
        return df


    # ====================================================================
    #          عمليات المدفوعات (payments)
    # ====================================================================

    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date):
        """تسجيل دفعة جديدة"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, amount, payment_method, payment_date))
        conn.commit()
        conn.close()

    def get_all_payments(self):
        """الحصول على جميع المدفوعات مع اسم المريض"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                py.id, py.payment_date, py.amount, py.payment_method, 
                p.name AS patient_name,
                py.appointment_id
            FROM payments py
            JOIN patients p ON py.patient_id = p.id
            ORDER BY py.payment_date DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


    # ====================================================================
    #          عمليات المصروفات (expenses)
    # ====================================================================

    def create_expense(self, category, description, amount, expense_date):
        """تسجيل مصروف جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (category, description, amount, expense_date)
            VALUES (?, ?, ?, ?)
        ''', (category, description, amount, expense_date))
        conn.commit()
        conn.close()
    
    def get_all_expenses(self):
        """الحصول على جميع المصروفات في DataFrame"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY expense_date DESC", conn)
        conn.close()
        return df


    # ====================================================================
    #          عمليات المخزون والموردين (inventory & suppliers)
    # ====================================================================

    def create_supplier(self, name, contact_person, phone, email, address, payment_terms):
        """إضافة مورد جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, contact_person, phone, email, address, payment_terms))
        conn.commit()
        conn.close()

    def get_all_suppliers(self):
        """الحصول على جميع الموردين"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY name", conn)
        conn.close()
        return df

    def create_inventory_item(self, item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date=None):
        """إضافة صنف جديد للمخزون"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date))
        conn.commit()
        conn.close()

    def get_all_inventory(self):
        """الحصول على جميع أصناف المخزون مع اسم المورد"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                i.id, i.item_name, i.category, i.quantity, i.unit_price, i.min_stock_level, i.expiry_date,
                s.name AS supplier_name
            FROM inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY i.item_name
        '''
        df = pd.read_sql_query(query, conn)
        # ملء قيم 'supplier_name' الفارغة بـ 'غير محدد'
        df['supplier_name'].fillna('غير محدد', inplace=True)
        conn.close()
        return df

    def get_low_stock_items(self):
        """الحصول على الأصناف التي كميتها أقل من الحد الأدنى"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                i.item_name, i.category, i.quantity, i.min_stock_level,
                s.name AS supplier_name
            FROM inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            WHERE i.quantity < i.min_stock_level
            ORDER BY i.quantity
        '''
        df = pd.read_sql_query(query, conn)
        df['supplier_name'].fillna('غير محدد', inplace=True)
        conn.close()
        return df


    # ====================================================================
    #          تقارير وإحصائيات عامة (Reports)
    # ====================================================================

    def get_financial_summary(self, start_date=None, end_date=None):
        """
        الحصول على ملخص مالي (الإيرادات، المصروفات، صافي الربح)
        للفترة المحددة
        """
        conn = self.db.get_connection()
        
        # إجمالي المدفوعات (الإيرادات)
        payments_query = "SELECT COALESCE(SUM(amount), 0) as total_payments FROM payments"
        if start_date and end_date:
            payments_query += f" WHERE payment_date BETWEEN '{start_date}' AND '{end_date}'"
        
        # إجمالي المصروفات
        expenses_query = "SELECT COALESCE(SUM(amount), 0) as total_expenses FROM expenses"
        if start_date and end_date:
            expenses_query += f" WHERE expense_date BETWEEN '{start_date}' AND '{end_date}'"
        
        total_payments = pd.read_sql_query(payments_query, conn).iloc[0]['total_payments']
        total_expenses = pd.read_sql_query(expenses_query, conn).iloc[0]['total_expenses']
        
        conn.close()
        
        return {
            'total_revenue': float(total_payments),
            'total_expenses': float(total_expenses),
            'net_profit': float(total_payments - total_expenses)
        }

    def get_daily_appointments_count(self):
        """عدد المواعيد اليومية (للشريط الجانبي في app.py)"""
        conn = self.db.get_connection()
        today = date.today().isoformat()
        query = "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ?"
        result = pd.read_sql_query(query, conn, params=(today,)).iloc[0]['count']
        conn.close()
        return int(result)

    def get_all_financial_data(self):
        """
        جلب جميع الإيرادات والمصروفات لاستخدامها في الرسوم البيانية.
        هذه الدالة مطلوبة لصفحة Dashboard.
        """
        conn = self.db.get_connection()
        
        # جلب الإيرادات
        revenue_query = "SELECT payment_date AS date, amount, 'Revenue' AS type FROM payments"
        revenue_df = pd.read_sql_query(revenue_query, conn)
        
        # جلب المصروفات
        expenses_query = "SELECT expense_date AS date, amount, 'Expense' AS type, category FROM expenses"
        expenses_df = pd.read_sql_query(expenses_query, conn)
        
        conn.close()
        
        return revenue_df, expenses_df
