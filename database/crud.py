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
    def create_treatment(self, name, description, base_price, duration_minutes, category):
        """إضافة علاج جديد"""
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
        """الحصول على جميع العلاجات"""
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
    
    def update_treatment(self, treatment_id, name, description, base_price, duration_minutes, category):
        """تحديث علاج"""
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
        """حذف علاج (إلغاء تفعيل)"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE treatments SET is_active = 0 WHERE id = ?", (treatment_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات المواعيد ==========
    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes="", total_cost=0.0):
        """إضافة موعد جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes, total_cost)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes, total_cost))
        
        appointment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return appointment_id
    
    def get_all_appointments(self):
        """الحصول على جميع المواعيد مع تفاصيل المريض والطبيب والعلاج"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.id,
                p.name as patient_name,
                d.name as doctor_name,
                t.name as treatment_name,
                a.appointment_date,
                a.appointment_time,
                a.status,
                a.total_cost,
                a.notes
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            ORDER BY a.appointment_date DESC, a.appointment_time DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_appointments_by_date(self, target_date):
        """الحصول على مواعيد يوم محدد"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.id,
                p.name as patient_name,
                d.name as doctor_name,
                t.name as treatment_name,
                a.appointment_time,
                a.status,
                a.total_cost
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.appointment_date = ?
            ORDER BY a.appointment_time
        '''
        df = pd.read_sql_query(query, conn, params=(target_date,))
        conn.close()
        return df
    
    def update_appointment_status(self, appointment_id, status):
        """تحديث حالة الموعد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
        conn.commit()
        conn.close()
    
    # ========== عمليات المدفوعات ==========
    def create_payment(self, appointment_id, patient_id, amount, payment_method, payment_date, notes=""):
        """إضافة دفعة جديدة"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (appointment_id, patient_id, amount, payment_method, payment_date, notes))
        
        payment_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return payment_id
    
    def get_all_payments(self):
        """الحصول على جميع المدفوعات"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                pay.id,
                p.name as patient_name,
                pay.amount,
                pay.payment_method,
                pay.payment_date,
                pay.status,
                pay.notes
            FROM payments pay
            LEFT JOIN patients p ON pay.patient_id = p.id
            ORDER BY pay.payment_date DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    # ========== عمليات المخزون ==========
    def create_inventory_item(self, item_name, category, quantity, unit_price, min_stock_level, supplier_id=None, expiry_date=None):
        """إضافة عنصر مخزون جديد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return item_id
    
    def get_all_inventory(self):
        """الحصول على جميع عناصر المخزون"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                i.*,
                s.name as supplier_name
            FROM inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY i.item_name
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def get_low_stock_items(self):
        """الحصول على العناصر قليلة المخزون"""
        conn = self.db.get_connection()
        query = "SELECT * FROM inventory WHERE quantity <= min_stock_level ORDER BY quantity"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def update_inventory_quantity(self, item_id, quantity):
        """تحديث كمية المخزون"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE inventory SET quantity = ? WHERE id = ?", (quantity, item_id))
        conn.commit()
        conn.close()
    
    # ========== عمليات الموردين ==========
    def create_supplier(self, name, contact_person, phone, email, address, payment_terms):
        """إضافة مورد جديد"""
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
        """الحصول على جميع الموردين"""
        conn = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers ORDER BY name", conn)
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
        """الحصول على ملخص مالي"""
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
        
        conn.close()
        
        return {
            'total_revenue': total_payments,
            'total_expenses': total_expenses,
            'net_profit': total_payments - total_expenses
        }
    
    def get_daily_appointments_count(self):
        """عدد المواعيد اليومية"""
        conn = self.db.get_connection()
        today = date.today().isoformat()
        query = "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ?"
        result = pd.read_sql_query(query, conn, params=(today,))
        conn.close()
        return result.iloc[0]['count'] if not result.empty else 0
# ========== تقارير متقدمة ==========

def get_revenue_by_period(self, start_date, end_date, group_by='day'):
    """الإيرادات حسب الفترة الزمنية"""
    conn = self.db.get_connection()
    
    if group_by == 'day':
        date_format = '%Y-%m-%d'
    elif group_by == 'month':
        date_format = '%Y-%m'
    elif group_by == 'year':
        date_format = '%Y'
    else:
        date_format = '%Y-%m-%d'
    
    query = f'''
        SELECT 
            strftime('{date_format}', payment_date) as period,
            SUM(amount) as total_revenue,
            COUNT(*) as payment_count
        FROM payments
        WHERE payment_date BETWEEN ? AND ?
        GROUP BY period
        ORDER BY period
    '''
    
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def get_expenses_by_category(self, start_date, end_date):
    """المصروفات حسب الفئة"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            category,
            SUM(amount) as total,
            COUNT(*) as count
        FROM expenses
        WHERE expense_date BETWEEN ? AND ?
        GROUP BY category
        ORDER BY total DESC
    '''
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def get_doctor_performance(self, start_date, end_date):
    """أداء الأطباء"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            d.name as doctor_name,
            d.specialization,
            COUNT(a.id) as total_appointments,
            SUM(CASE WHEN a.status = 'مكتمل' THEN 1 ELSE 0 END) as completed_appointments,
            SUM(a.total_cost) as total_revenue,
            AVG(a.total_cost) as avg_revenue_per_appointment,
            d.commission_rate,
            (SUM(a.total_cost) * d.commission_rate / 100) as total_commission
        FROM doctors d
        LEFT JOIN appointments a ON d.id = a.doctor_id
        WHERE a.appointment_date BETWEEN ? AND ?
        GROUP BY d.id, d.name, d.specialization, d.commission_rate
        ORDER BY total_revenue DESC
    '''
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def get_treatment_popularity(self, start_date, end_date):
    """العلاجات الأكثر طلباً"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            t.name as treatment_name,
            t.category,
            COUNT(a.id) as booking_count,
            SUM(a.total_cost) as total_revenue,
            AVG(a.total_cost) as avg_price
        FROM treatments t
        LEFT JOIN appointments a ON t.id = a.treatment_id
        WHERE a.appointment_date BETWEEN ? AND ?
        GROUP BY t.id, t.name, t.category
        ORDER BY booking_count DESC
    '''
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def get_patient_statistics(self):
    """إحصائيات المرضى"""
    conn = self.db.get_connection()
    
    # إحصائيات حسب الجنس
    gender_query = '''
        SELECT gender, COUNT(*) as count
        FROM patients
        GROUP BY gender
    '''
    gender_df = pd.read_sql_query(gender_query, conn)
    
    # إحصائيات حسب العمر
    age_query = '''
        SELECT 
            CASE 
                WHEN (julianday('now') - julianday(date_of_birth)) / 365 < 18 THEN 'أقل من 18'
                WHEN (julianday('now') - julianday(date_of_birth)) / 365 BETWEEN 18 AND 30 THEN '18-30'
                WHEN (julianday('now') - julianday(date_of_birth)) / 365 BETWEEN 31 AND 50 THEN '31-50'
                ELSE 'أكثر من 50'
            END as age_group,
            COUNT(*) as count
        FROM patients
        WHERE date_of_birth IS NOT NULL
        GROUP BY age_group
    '''
    age_df = pd.read_sql_query(age_query, conn)
    
    conn.close()
    return {'gender': gender_df, 'age': age_df}

def get_appointment_status_stats(self, start_date, end_date):
    """إحصائيات حالة المواعيد"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            status,
            COUNT(*) as count,
            SUM(total_cost) as total_revenue
        FROM appointments
        WHERE appointment_date BETWEEN ? AND ?
        GROUP BY status
        ORDER BY count DESC
    '''
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def get_payment_methods_stats(self, start_date, end_date):
    """إحصائيات طرق الدفع"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            payment_method,
            COUNT(*) as count,
            SUM(amount) as total
        FROM payments
        WHERE payment_date BETWEEN ? AND ?
        GROUP BY payment_method
        ORDER BY total DESC
    '''
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def get_inventory_value(self):
    """قيمة المخزون الإجمالية"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            category,
            SUM(quantity * unit_price) as total_value,
            SUM(quantity) as total_quantity,
            COUNT(*) as item_count
        FROM inventory
        GROUP BY category
        ORDER BY total_value DESC
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_top_patients(self, start_date, end_date, limit=10):
    """أكثر المرضى زيارة"""
    conn = self.db.get_connection()
    query = f'''
        SELECT 
            p.name as patient_name,
            p.phone,
            COUNT(a.id) as visit_count,
            SUM(a.total_cost) as total_spent,
            MAX(a.appointment_date) as last_visit
        FROM patients p
        LEFT JOIN appointments a ON p.id = a.patient_id
        WHERE a.appointment_date BETWEEN ? AND ?
        GROUP BY p.id, p.name, p.phone
        ORDER BY visit_count DESC
        LIMIT {limit}
    '''
    df = pd.read_sql_query(query, conn, params=(start_date, end_date))
    conn.close()
    return df

def get_daily_revenue_comparison(self, days=30):
    """مقارنة الإيرادات اليومية"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            payment_date,
            SUM(amount) as daily_revenue,
            COUNT(*) as payment_count
        FROM payments
        WHERE payment_date >= date('now', ?)
        GROUP BY payment_date
        ORDER BY payment_date
    '''
    df = pd.read_sql_query(query, conn, params=(f'-{days} days',))
    conn.close()
    return df

def get_expiring_inventory(self, days=60):
    """المخزون قريب الانتهاء"""
    conn = self.db.get_connection()
    query = '''
        SELECT 
            i.item_name,
            i.category,
            i.quantity,
            i.expiry_date,
            s.name as supplier_name,
            CAST((julianday(i.expiry_date) - julianday('now')) AS INTEGER) as days_to_expire
        FROM inventory i
        LEFT JOIN suppliers s ON i.supplier_id = s.id
        WHERE i.expiry_date IS NOT NULL
        AND julianday(i.expiry_date) - julianday('now') <= ?
        ORDER BY days_to_expire
    '''
    df = pd.read_sql_query(query, conn, params=(days,))
    conn.close()
    return df
# إنشاء مثيل من عمليات CRUD
crud = CRUDOperations()
