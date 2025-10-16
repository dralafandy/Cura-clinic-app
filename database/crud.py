import sqlite3
import pandas as pd
from datetime import datetime, date
# الاستيراد من نفس الحزمة
from .models import db 

class CRUDOperations:
    """
    كلاس مسؤول عن جميع عمليات قاعدة البيانات (إنشاء, قراءة, تحديث, حذف)
    باستخدام SQLite و Pandas.
    """
    
    def __init__(self):
        # الكائن 'db' من ملف models.py يوفر دالة get_connection()
        self.db = db
    
    def get_connection(self):
        """دالة مساعدة للحصول على اتصال قاعدة البيانات"""
        return self.db.get_connection()
    
    
    # ====================================================================
    #          عمليات الأطباء والموظفين (doctors)
    # ====================================================================
    
    def create_doctor(self, name, specialization, phone, email, address, hire_date, salary, commission_rate=0.0):
        """إضافة طبيب جديد"""
        conn = self.get_connection()
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
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM doctors ORDER BY name", conn)
        conn.close()
        return df
    
    def get_doctor_by_id(self, doctor_id):
        """الحصول على طبيب بواسطة ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_doctor(self, id, name, specialization, phone, email, address, hire_date, salary, commission_rate):
        """تحديث بيانات طبيب موجود"""
        conn = self.get_connection()
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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        conn.commit()
        conn.close()
        
    def get_doctor_performance_data(self, doctor_id=None, start_date=None, end_date=None):
        """جلب بيانات أداء الأطباء (عدد المواعيد والإيرادات)"""
        conn = self.get_connection()
        query = '''
            SELECT 
                d.name AS doctor_name,
                COUNT(a.id) AS appointment_count,
                COALESCE(SUM(a.total_cost), 0) AS total_revenue
            FROM doctors d
            LEFT JOIN appointments a ON d.id = a.doctor_id
            WHERE 1=1
        '''
        params = []
        if start_date and end_date:
            query += " AND a.appointment_date BETWEEN ? AND ?"
            params.extend([start_date, end_date])
            
        if doctor_id:
            query += " AND d.id = ?"
            params.append(doctor_id)
            
        query += " GROUP BY d.id, d.name ORDER BY total_revenue DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df


    # ====================================================================
    #          عمليات المرضى (patients)
    # ====================================================================

    def create_patient(self, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
        """إضافة مريض جديد"""
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

    def get_all_patients(self):
        """الحصول على جميع المرضى في DataFrame"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY name", conn)
        conn.close()
        return df

    def update_patient(self, id, name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact):
        """تحديث بيانات مريض موجود"""
        conn = self.get_connection()
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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM patients WHERE id = ?", (patient_id,))
        conn.commit()
        conn.close()


    # ====================================================================
    #          عمليات العلاجات (treatments)
    # ====================================================================

    def create_treatment(self, name, description, base_price, duration_minutes, category, is_active=1):
        """إضافة علاج جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO treatments (name, description, base_price, duration_minutes, category, is_active)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, base_price, duration_minutes, category, is_active))
        conn.commit()
        conn.close()

    def get_all_treatments(self):
        """الحصول على جميع العلاجات النشطة في DataFrame"""
        conn = self.get_connection()
        # جلب is_active=1
        df = pd.read_sql_query("SELECT * FROM treatments WHERE is_active = 1 ORDER BY name", conn)
        conn.close()
        return df
    
    def get_treatment_by_id(self, treatment_id):
        """الحصول على علاج بواسطة ID (مطلوب لعملية التحديث)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM treatments WHERE id = ?", (treatment_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def update_treatment(self, treatment_id, name, description, base_price, duration_minutes, category, is_active=1):
        """تحديث بيانات علاج موجود"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE treatments 
            SET name=?, description=?, base_price=?, duration_minutes=?, category=?, is_active=?
            WHERE id=?
        ''', (name, description, base_price, duration_minutes, category, is_active, treatment_id))
        conn.commit()
        conn.close()
    
    def get_treatment_analysis(self):
        """تحليل العلاجات الأكثر طلباً"""
        conn = self.get_connection()
        query = '''
            SELECT 
                t.name AS treatment_name,
                COUNT(a.id) AS booking_count,
                COALESCE(SUM(a.total_cost), 0) AS total_revenue
            FROM treatments t
            LEFT JOIN appointments a ON t.id = a.treatment_id
            GROUP BY t.id, t.name
            ORDER BY booking_count DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


    # ====================================================================
    #          عمليات المواعيد (appointments)
    # ====================================================================
    
    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost, status='مؤكد'):
        """حجز موعد جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, total_cost, status))
        conn.commit()
        conn.close()
    
    def get_all_appointments(self):
        """الحصول على جميع المواعيد مع أسماء المرضى والأطباء والعلاجات"""
        conn = self.get_connection()
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
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
        conn.commit()
        conn.close()


    # ====================================================================
    #          عمليات المدفوعات (payments)
    # ====================================================================

    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date):
        """تسجيل دفعة جديدة"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, amount, payment_method, payment_date))
        conn.commit()
        conn.close()

    def get_all_payments(self):
        """الحصول على جميع المدفوعات مع اسم المريض"""
        conn = self.get_connection()
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
    
    def get_pending_payments(self):
        """جلب المدفوعات المعلقة (يفترض أن تكلفة الموعد > المدفوعات)"""
        conn = self.get_connection()
        query = '''
            SELECT 
                a.id AS appointment_id,
                p.name AS patient_name,
                a.total_cost,
                COALESCE(SUM(py.amount), 0) AS paid_amount,
                (a.total_cost - COALESCE(SUM(py.amount), 0)) AS pending_amount,
                a.appointment_date
            FROM appointments a
            JOIN patients p ON a.patient_id = p.id
            LEFT JOIN payments py ON a.id = py.appointment_id
            WHERE a.status = 'منتهي' 
            GROUP BY a.id, p.name, a.total_cost, a.appointment_date
            HAVING pending_amount > 0
            ORDER BY a.appointment_date DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df


    # ====================================================================
    #          عمليات المصروفات (expenses)
    # ====================================================================

    def create_expense(self, category, description, amount, expense_date):
        """تسجيل مصروف جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO expenses (category, description, amount, expense_date)
            VALUES (?, ?, ?, ?)
        ''', (category, description, amount, expense_date))
        conn.commit()
        conn.close()
    
    def get_all_expenses(self):
        """الحصول على جميع المصروفات في DataFrame"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY expense_date DESC", conn)
        conn.close()
        return df
    
    def get_expenses_by_month_year(self, month, year):
        """جلب المصروفات لشهر وسنة محددين"""
        conn = self.get_connection()
        
        # تنسيق الشهر بحيث يكون مكوناً من رقمين للمقارنة
        month_str = f"{int(month):02d}"
        
        query = '''
            SELECT * FROM expenses 
            WHERE strftime('%Y', expense_date) = ? AND strftime('%m', expense_date) = ?
            ORDER BY expense_date
        '''
        df = pd.read_sql_query(query, conn, params=(str(year), month_str))
        conn.close()
        return df


    # ====================================================================
    #          عمليات المخزون والموردين (inventory & suppliers)
    # ====================================================================

    def create_supplier(self, name, contact_person, phone, email, address, payment_terms):
        """إضافة مورد جديد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, contact_person, phone, email, address, payment_terms))
        conn.commit()
        conn.close()

    def get_all_suppliers(self):
        """الحصول على جميع الموردين"""
        conn = self.get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY name", conn)
        conn.close()
        return df

    def get_supplier_by_id(self, supplier_id):
        """جلب مورد واحد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM suppliers WHERE id = ?", (supplier_id,))
        result = cursor.fetchone()
        conn.close()
        return result

    def create_inventory_item(self, item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date=None):
        """إضافة صنف جديد للمخزون"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date))
        conn.commit()
        conn.close()

    def get_all_inventory(self):
        """الحصول على جميع أصناف المخزون مع اسم المورد"""
        conn = self.get_connection()
        query = '''
            SELECT 
                i.id, i.item_name, i.category, i.quantity, i.unit_price, i.min_stock_level, i.expiry_date,
                s.name AS supplier_name
            FROM inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY i.item_name
        '''
        df = pd.read_sql_query(query, conn)
        df['supplier_name'].fillna('غير محدد', inplace=True)
        conn.close()
        return df

    def get_low_stock_items(self):
        """الحصول على الأصناف التي كميتها أقل من الحد الأدنى (مطلوب لصفحة inventory.py)"""
        conn = self.get_connection()
        query = '''
            SELECT 
                i.item_name, i.category, i.quantity, i.min_stock_level, i.unit_price,
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
        conn = self.get_connection()
        
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
        """عدد المواعيد اليومية (مطلوب لصفحة dashboard.py)"""
        conn = self.get_connection()
        today = date.today().isoformat()
        query = "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ?"
        result = pd.read_sql_query(query, conn, params=(today,)).iloc[0]['count']
        conn.close()
        return int(result)

    def get_all_financial_data(self):
        """
        جلب جميع الإيرادات والمصروفات لاستخدامها في الرسوم البيانية.
        مطلوبة لصفحة dashboard.py.
        """
        conn = self.get_connection()
        
        # جلب الإيرادات
        revenue_query = "SELECT payment_date AS date, amount, 'Revenue' AS type FROM payments"
        revenue_df = pd.read_sql_query(revenue_query, conn)
        
        # جلب المصروفات
        expenses_query = "SELECT expense_date AS date, amount, 'Expense' AS type, category FROM expenses"
        expenses_df = pd.read_sql_query(expenses_query, conn)
        
        conn.close()
        
        return revenue_df, expenses_df


# ====================================================================
# إنشاء مثيل CRUDBOperations ليتناسب مع استيراد صفحاتك
# ====================================================================
# هذا السطر هو الحل المباشر لخطأ 'from database.crud import crud' في صفحاتك
crud = CRUDOperations()
