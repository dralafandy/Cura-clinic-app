import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
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
                a.patient_id,
                a.doctor_id,
                a.treatment_id,
                p.name as patient_name,
                p.phone as patient_phone,
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
    
    def get_appointment_by_id(self, appointment_id):
        """الحصول على موعد بواسطة ID مع تفاصيل كاملة"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.*,
                p.name as patient_name,
                p.phone as patient_phone,
                d.name as doctor_name,
                t.name as treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.id = ?
        '''
        cursor = conn.cursor()
        cursor.execute(query, (appointment_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
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
    
    def get_appointments_by_status(self, status):
        """الحصول على المواعيد حسب الحالة"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                a.*,
                p.name as patient_name,
                p.phone as patient_phone,
                d.name as doctor_name,
                t.name as treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.status = ?
            ORDER BY a.appointment_date, a.appointment_time
        '''
        df = pd.read_sql_query(query, conn, params=(status,))
        conn.close()
        return df
    
    def get_upcoming_appointments(self, days=7):
        """الحصول على المواعيد القادمة في الأيام المقبلة"""
        conn = self.db.get_connection()
        start_date = date.today().isoformat()
        end_date = (date.today() + timedelta(days=days)).isoformat()
        
        query = '''
            SELECT 
                a.*,
                p.name as patient_name,
                p.phone as patient_phone,
                d.name as doctor_name,
                t.name as treatment_name
            FROM appointments a
            LEFT JOIN patients p ON a.patient_id = p.id
            LEFT JOIN doctors d ON a.doctor_id = d.id
            LEFT JOIN treatments t ON a.treatment_id = t.id
            WHERE a.appointment_date BETWEEN ? AND ?
            AND a.status IN ('مجدول', 'مؤكد')
            ORDER BY a.appointment_date, a.appointment_time
        '''
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def update_appointment_status(self, appointment_id, status):
        """تحديث حالة الموعد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
        conn.commit()
        conn.close()
    
    def update_appointment(self, appointment_id, patient_id, doctor_id, treatment_id, 
                         appointment_date, appointment_time, notes, total_cost, status):
        """تحديث بيانات الموعد بالكامل"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE appointments 
            SET patient_id=?, doctor_id=?, treatment_id=?, appointment_date=?, 
                appointment_time=?, notes=?, total_cost=?, status=?
            WHERE id=?
        ''', (patient_id, doctor_id, treatment_id, appointment_date, 
              appointment_time, notes, total_cost, status, appointment_id))
        
        conn.commit()
        conn.close()
        return True
    
    def delete_appointment(self, appointment_id):
        """حذف موعد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        return True
    
    def check_appointment_conflict(self, doctor_id, appointment_date, appointment_time):
        """التحقق من تضارب المواعيد"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id FROM appointments 
            WHERE doctor_id = ? AND appointment_date = ? AND appointment_time = ?
            AND status != 'ملغي'
        ''', (doctor_id, appointment_date, appointment_time))
        
        result = cursor.fetchone()
        conn.close()
        return result is not None
    
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
    
    def get_payments_by_date_range(self, start_date, end_date):
        """الحصول على المدفوعات في نطاق تاريخي"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                pay.*,
                p.name as patient_name
            FROM payments pay
            LEFT JOIN patients p ON pay.patient_id = p.id
            WHERE pay.payment_date BETWEEN ? AND ?
            ORDER BY pay.payment_date DESC
        '''
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def get_payments_by_patient(self, patient_id):
        """الحصول على مدفوعات مريض محدد"""
        conn = self.db.get_connection()
        query = '''
            SELECT * FROM payments 
            WHERE patient_id = ?
            ORDER BY payment_date DESC
        '''
        df = pd.read_sql_query(query, conn, params=(patient_id,))
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
    
 return item_id
    
    def    def get_all_inventory get_all_inventory(self):
(self):
        """الحصول        """الحصول على جميع عناصر المخ على جميع عناصر المخزون"""
زون"""
        conn = self        conn = self.db.get.db.get_connection()
        query_connection()
        query = = '''
            SELECT 
                '''
            SELECT 
                i i.*,
                s.name.*,
                s.name as supplier_name as supplier_name
            FROM
            FROM inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY inventory i
            LEFT JOIN suppliers s ON i.supplier_id = s.id
            ORDER BY i.item_name
 i.item_name
        '''
        '''
        df = pd        df = pd.read_s.read_sql_query(query,ql_query(query, conn)
        conn)
        conn.close()
        return df
    
    conn.close()
        return df
    
    def get_inventory_by_id def get_inventory_by_id(self, item_id):
        """الح(self, item_id):
        """الحصول على عنصول على عنصر مخزون بواسطةصر مخزون بواسطة ID"""
        conn ID"""
        conn = self = self.db.get_connection()
       .db.get_connection()
        cursor = conn.c cursor = conn.cursor()
        cursor.execute("SELECT * FROM inventoryursor()
        cursor.execute("SELECT * FROM inventory WHERE id = ? WHERE id = ?", (item_id", (item_id,))
,))
        result = cursor        result = cursor.fetchone.fetchone()
        conn.close()
        conn.close()
       ()
        return result
    
    return result
    
    def get def get_low_stock_low_stock_items(self_items(self):
        """):
        """الحصولالحصول على العناصر قلي على العناصر قليلة المخلة المخزون"""
        connزون"""
        conn = = self.db.get_ self.db.get_connection()
connection()
        query = "SELECT * FROM inventory WHERE quantity        query = "SELECT * FROM inventory WHERE quantity <= <= min_stock_level ORDER BY quantity min_stock_level ORDER BY quantity"
        df = pd"
        df = pd.read_sql_query(query, conn.read_sql_query(query, conn)
       )
        conn.close()
        return df
    
 conn.close()
        return df
    
    def get_exp    def get_expired_itemsired_items(self):
       (self):
        """الحصول على العن """الحصول على العناصر المنتهية الصلاصر المنتهية الصلاحية"""
        conn =احية"""
        conn = self.db.get_ self.db.get_connection()
connection()
        today = date        today = date.t.today().isoformat()
oday().isoformat()
        query        query = "SELECT * = "SELECT * FROM inventory FROM inventory WHERE expiry_date WHERE expiry_date < ? ORDER < ? ORDER BY expiry_date"
 BY expiry_date"
        df        df = pd.read_s = pd.read_sql_queryql_query(query, conn,(query, conn, params=(today params=(today,))
       ,))
        conn.close()
        return conn.close()
        return df
    
    def df
    
    def get_items_exp get_items_expiring_iring_soon(self, dayssoon(self, days=30):
       =30):
        """الح """الحصول على العناصرصول على العناصر التي س التي ستنتهي خلالتنتهي خلال أيام أيام محددة"""
 محددة"""
               conn = self.db.get conn = self.db.get_connection()
_connection()
        expiry_date =        expiry_date = (date.today (date.today() +() + timedelta(days timedelta(days==days)).isoformat()
        todaydays)).isoformat()
        today = date.today().iso = date.today().isoformatformat()
        query = "()
        querySELECT * FROM inventory WHERE expiry = "SELECT * FROM inventory_date BETWEEN ? AND ? ORDER WHERE expiry_date BETWEEN ? AND ? ORDER BY expiry_date"
        df BY expiry_date"
        df = pd.read_sql_query = pd.read_sql_query(query, conn, params=((query, conn, params=(today, expiry_date))
       today, expiry_date))
        conn.close()
        return df conn.close()
        return df
    
    def update_inventory_quantity(self, item_id
    
    def update_inventory_quantity(self, item_id, quantity, quantity):
        """تحديث كمية المخز):
        """تحديث كمية المخزون"""
        conn = selfون"""
        conn = self.db.get_connection()
.db.get_connection()
        cursor = conn.cursor()
        cursor = conn.cursor()
               cursor.execute("UPDATE cursor.execute("UPDATE inventory SET quantity = ? WHERE id inventory SET quantity = ? WHERE id = ? = ?", (quantity, item_id))
        conn.commit()
", (quantity, item_id))
        conn.commit()
               conn.close()
    
    def conn.close()
    
    def update_inventory_item(self, update_inventory_item(self, item_id item_id, item, item_name,_name, category, quantity, unit_price, min_stock category, quantity, unit_price, min_stock_level,_level, supplier_id=None, expiry_date supplier_id=None, expiry_date=None):
=None):
        """ت        """تحديث بياناتحديث بيانات عنصر المخز عنصر المخزون"""
ون"""
        conn = self        conn = self.db.get.db.get_connection()
       _connection()
        cursor = cursor = conn.cursor()
 conn.cursor()
        
               
        cursor.execute('''
 cursor.execute('''
                       UPDATE inventory 
            SET UPDATE inventory 
            SET item item_name=?, category_name=?, category=?, quantity=?, unit_price=?, min_stock_level=?, supplier_id=?, quantity=?, unit_price=?, min_stock_level=?, supplier=?, expiry_date=?
            WHERE id_id=?, expiry_date=?
            WHERE id=?
        ''', (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date, item_id))
        
        conn.commit()
        conn.close()
    
    def delete_inventory_item(self, item_id):
        """حذف عنصر مخزون"""
        conn = self.db.get_connection()
       =?
        ''', (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date, item_id))
        
        conn.commit()
        conn.close()
    
    def delete_inventory_item(self, item_id):
        """حذف عنصر مخزون"""
        conn = self.db.get_connection()
        cursor = conn.c cursor = conn.cursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات الموردين ==========
    def create_supplier(self, name, contact_person, phone, email, address, payment_terms):
        """إضافة مورد جديد"""
        conn = self.db.get_connection()
       ursor()
        cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()
    
    # ========== عمليات الموردين ==========
    def create_supplier(self, name, contact_person, phone, email, address, payment_terms):
        """إضافة مورد جديد"""
        conn = self.db.get_connection()
        cursor = conn.c cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name,ursor()
        
        cursor.execute('''
            INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, contact_person, contact_p phone, email, address, payment_terms))
        
        supplier_id = cursor.lastrowid
erson, phone, email, address, payment_terms))
        
        supplier_id = cursor.lastrow        conn.commit()
        connid
        conn.commit()
        conn.close()
        return.close()
        return supplier_id
    
    def get_all_s supplier_id
    
    def get_all_suppliers(selfuppliers(self):
        """الحصول على جميع الموردين"""
        conn):
        """الحصول على جميع الموردين"""
        conn = self.db.get_connection()
        df = pd.read_s = self.db.get_connection()
        df = pd.read_sql_query("SELECT * FROM suppliers ORDER BYql_query("SELECT * FROM suppliers ORDER BY name", conn)
 name", conn)
        conn        conn.close()
        return.close()
        return df
    
 df
    
    def get_s    def get_supplier_by_id(self, supplier_idupplier_by_id(self,):
        """الحصول على supplier_id):
        """الحصول على مورد بواسطة ID مورد بواسطة ID"""
        conn ="""
        conn = self.db self.db.get_connection()
        cursor = conn.cursor.get_connection()
        cursor = conn.cursor()
        cursor()
        cursor.execute("SELECT.execute("SELECT * FROM suppliers WHERE * FROM suppliers WHERE id = id = ?", (supp ?", (supplier_id,))
        result = cursor.fetchone()
        conn.close()
       lier_id,))
        result = cursor.fetchone()
        conn.close()
        return result return result
    
    # =
    
    # =================== عمليات المصروفات ==========
    def create_exp عمليات المصروفات ==========
    def create_expense(selfense(self, category, description, amount,, category, description, amount, expense_date, payment_method expense_date, payment_method, receipt_number=", receipt_number="", notes=""):
        """إ", notes=""):
        """إضافة مصروف جديد"""
ضافة مصروف جديد"""
        conn =        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        self.db.get_connection()
        cursor = conn.cursor()
 cursor.execute('''
                   
        cursor.execute('' INSERT INTO expenses (category, description, amount, expense_date, payment_method, receipt_number'
            INSERT INTO expenses (category, description, amount, expense_date, payment_method, receipt_number, notes)
            VALUES (, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (category, description, amount,?, ?, ?, ?, ?, ?, ?)
        ''', (category, description, amount, expense_date, payment_method, receipt expense_date, payment_method,_number, notes))
        
 receipt_number, notes))
        
        expense        expense_id = cursor.lastrowid
        conn.commit()
        conn.close_id = cursor.lastrowid
        conn.commit()
        conn.close()
()
        return expense_id
    
    def get_all_exp        return expense_id
    
    def get_all_expenses(self):
       enses(self):
        """الحصول على جميع """الحصول على جميع المصروف المصروفات"""
        connات"""
        conn = self.db.get_connection()
        df = = self.db.get_connection()
        df = pd.read_s pd.read_sql_query("SELECT * FROM expensesql_query("SELECT * FROM expenses ORDER BY expense_date DESC ORDER BY expense_date DESC", conn)
        conn.close()
        return", conn)
        conn.close()
        return df
    
    df
    
    def get_exp def get_expenses_by_date_rangeenses_by_date_range(self, start_date, end_date):
        """الحصول على المصروفات في نطاق تاريخي"""
        conn = self.db.get_connection()
        query = '''
            SELECT * FROM expenses 
            WHERE expense_date BETWEEN ? AND ?
            ORDER BY expense_date DESC
        '''
        df = pd(self, start_date, end_date):
        """الحصول على المصروفات في نطاق تاريخي"""
        conn = self.db.get_connection()
        query = '''
            SELECT * FROM expenses 
            WHERE expense_date BETWEEN ? AND ?
            ORDER BY expense_date DESC
        '''
        df =.read_sql_query(query, conn pd.read_sql_query(query, params=(start_date, end_date))
        conn.close()
        return df
    
   , conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def get_expenses_by_category(self, start_date def get_expenses_by_category(self, start_date, end_date):
, end_date):
        """الحصول        """الحصول على المصروف على المصروفات مصنفة حسب الفئة"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                category,
                SUM(amount) as total_amount,
                COUNT(*) as expense_count
            FROM expenses 
            WHERE expense_date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total_amount DESC
        '''
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def update_expense(self, expense_id, category, description, amount, expense_date, payment_method, receipt_number="", notes=""):
        """تحديث مصروف"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE expenses 
            SET category=?, description=?, amount=?, expense_date=?, payment_method=?, receipt_number=?, notes=?
            WHERE id=?
        ''', (category, description, amount, expense_date, payment_method, receipt_number, notes, expense_id))
        
        conn.commit()
        conn.close()
    
    def delete_expense(self, expense_id):
        """حذف مصروف"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
    
    # ========== دوال المحاسبة والتقارير المالية ==========
    def get_financial_summary(self, start_date=None, end_date=None):
        """الحصول على ملخص مالي"""
        conn = self.db.get_connection()
        
        # إجمالي المدفوعات
        payments_query = "SELECT COALESCE(SUM(amount), 0) as totalات مصنفة حسب الفئة"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                category,
                SUM(amount) as total_amount,
                COUNT(*) as expense_count
            FROM expenses 
            WHERE expense_date BETWEEN ? AND ?
            GROUP BY category
            ORDER BY total_amount DESC
        '''
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def update_expense(self, expense_id, category, description, amount, expense_date, payment_method, receipt_number="", notes=""):
        """تحديث مصروف"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE expenses 
            SET category=?, description=?, amount=?, expense_date=?, payment_method=?, receipt_number=?, notes=?
            WHERE id=?
        ''', (category, description, amount, expense_date, payment_method, receipt_number, notes, expense_id))
        
        conn.commit()
        conn.close()
    
    def delete_expense(self, expense_id):
        """حذف مصروف"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
        conn.close()
    
    # ========== دوال المحاسبة والتقارير المالية ==========
    def get_financial_summary(self, start_date=None, end_date=None):
        """الحصول على ملخص مالي"""
        conn = self.db.get_connection()
        
        # إجمالي المدفوعات
        payments_query = "SELECT COALESCE(SUM(amount), 0) as total_payments FROM payments"
       _payments FROM payments"
        if start_date and end_date:
 if start_date and end_date:
            payments_query += f            payments_query += f" WHERE payment_date BETWEEN '{start_date" WHERE payment_date BETWEEN '{}' AND '{end_date}'start_date}' AND '{end_date"
        
        # إجمالي المصروفات
        expenses_query = "SELECT COALESCE(SUM(}'"
        
        # إجمالي المصروفات
        expenses_query = "SELECT COALESCE(SUM(amount), 0) as totalamount), 0) as total_expenses FROM expenses"
        if start_date_expenses FROM expenses"
        if start_date and end_date and end_date:
            expenses_query +=:
            expenses_query += f f" WHERE expense_date BETWEEN" WHERE expense_date BETWEEN '{ '{start_date}' AND '{start_date}' AND '{endend_date}'"
        
       _date}'"
        
        # # عدد المواعيد عدد المواعيد
       
        appointments_query = "SELECT appointments_query = "SELECT COUNT COUNT(*) as total_appointments(*) as total_appointments FROM FROM appointments"
        if start appointments"
        if start_date and end_date:
            appointments_date and end_date:
            appointments_query += f" WHERE appointment_query += f" WHERE appointment_date BETWEEN '{start_date}'_date BETWEEN '{start_date}' AND '{end_date}'"
 AND '{end_date}'"
        
        total_payments =        
        total_payments = pd.read_sql_query(p pd.read_sql_query(payments_query, conn).ilocayments_query, conn).il[oc[0]['total_payments']
        total_expenses0]['total_payments']
        total_expenses = pd.read_sql_query(exp = pd.read_sql_query(enses_query, conn).ilexpenses_query, conn).iloc[0]['total_expenses']
        total_appointments = pd.read_sql_queryoc[0]['total_expenses']
        total_appointments = pd.read_sql_query(appointments_query, conn).(appointments_query, conn).iloc[0]['totaliloc[0]['total_appointments']
        
        conn.close()
        
        return {
            'total_revenue': total_p_appointments']
        
        conn.close()
        
        return {
            'total_revenue': total_payments,
            'total_expayments,
            'total_expenses':enses': total_expenses,
 total_expenses,
            'net_profit':            'net_profit': total_p total_payments - total_expayments - total_expenses,
enses,
            'total_appointments': total_app            'total_appointments': total_appointments,
            'ointments,
            'revenuerevenue_per_appointment':_per_appointment': total_payments / total_appointments if total_appointments total_payments / total_appointments if total_appointments > > 0 else 0
        }
    
    def get 0 else 0
        }
    
    def get_revenue_by_date_range(self_revenue_by_date_range(self, start_date, end_date, start_date, end_date):
        """الحصول على):
        """الحصول على الإيرادات في نط الإيرادات في نطاق تاريخي"""
        conn = self.db.get_connection()
اق تاريخي"""
        conn = self.db.get_connection()
        query =        query = '''
            SELECT 
 '''
            SELECT 
                payment                payment_date,
                SUM_date,
                SUM(amount(amount) as) as daily daily_revenue,
               _revenue,
                COUNT(*) as transaction_count
 COUNT(*) as transaction_count
            FROM payments 
                       FROM payments 
            WHERE payment_date BETWEEN WHERE payment_date BETWEEN ? AND ?
            ? AND ?
            GROUP BY GROUP BY payment_date
            payment_date
            ORDER BY ORDER BY payment_date
        '''
        df = pd.read payment_date
        '''
        df_sql_query(query, = pd.read_sql_query(query, conn, params=( conn, params=(start_date,start_date, end_date end_date))
        conn.close))
        conn.close()
        return()
        return df
    
    df
    
    def get_doctor def get_doctor_performance_performance_report(self, start_report(self, start_date,_date, end_date):
        end_date):
        """ت """تقرير أداءقرير أداء الأطب الأطباء"""
        connاء"""
        conn = self = self.db.get_connection.db.get_connection()
       ()
        query = '''
            query = '''
            SELECT 
 SELECT 
                d.name as                d.name as doctor_name doctor_name,
                d.s,
                d.specialization,
pecialization,
                d.com                d.commission_rate,
               mission_rate,
                COUNT(a COUNT(a.id) as appointment.id) as appointment_count,
               _count,
                SUM(a.total SUM(a.total_cost) as_cost) as total_revenue total_revenue,
                AV,
                AVG(a.totalG(a.total_cost) as_cost) as avg_revenue avg_revenue_per_appointment,
_per_appointment,
                (                (SUM(a.total_costSUM(a.total_cost) *) * d.commission_rate d.commission_rate / 100) / 100) as commission as commission_amount,
                (SUM(a.total_cost) - (SUM(a.total_cost) *_amount,
                (SUM(a.total_cost) - (SUM(a.total_cost) * d.commission d.commission_rate / _rate / 100)) as100)) as net_revenue
            FROM appointments net_revenue
            FROM appointments a
            a
            JOIN doctors d JOIN doctors d ON a.doctor_id = d.id ON a.doctor_id = d.id
            WHERE a.app
            WHERE a.appointment_dateointment_date BETWEEN ? AND ?
 BETWEEN ? AND ?
            GROUP BY d.id, d.name            GROUP BY d.id, d.name, d.special, d.specialization,ization, d.commission_rate d.commission_rate
           
            ORDER BY total_re ORDER BY total_revenue DESC
        '''
        df =venue DESC
        '''
        df = pd.read_sql pd.read_sql_query(query_query(query, conn, params, conn, params=(start_date,=(start_date, end_date end_date))
        conn.close))
        conn.close()
       ()
        return df
    
    return df
    
    def get def get_patient_f_patient_financial_reportinancial_report(self(self,, start_date, end start_date, end_date):
        """تقرير م_date):
        """تقرير مالي للمرضىالي للمرضى"""
        conn"""
        conn = self.db = self.db.get_connection()
.get_connection()
        query =        query = '''
            SELECT '''
            SELECT 
                p 
                p.name as.name as patient patient_name,
                p.phone_name,
                p.phone,
               ,
                COUNT(a.id) as appointment_count COUNT(a.id) as appointment_count,
                SUM(a.total,
                SUM(a.total_cost) as total_spent,
               _cost) as total_spent,
                AVG(a.total_cost AVG(a.total_cost) as avg_per) as avg_per_appointment_appointment,
                MAX,
                MAX(a(a.appointment_date).appointment_date) as last as last_visit
           _visit
            FROM appointments FROM appointments a
            JOIN a
            JOIN patients p patients p ON a.patient ON a.patient_id =_id = p.id
            p.id
            WHERE a WHERE a.appointment_date BETWEEN.appointment_date BETWEEN ? AND ?
 ? AND ?
            GROUP BY p            GROUP BY p.id, p.id, p.name, p.name, p.phone
.phone
            ORDER BY total            ORDER BY total_spent_spent DESC
        '''
 DESC
        '''
        df        df = pd.read_s = pd.read_sql_queryql_query(query, conn,(query, conn, params=( params=(start_date, endstart_date, end_date))
_date))
        conn.close()
        conn.close()
        return        return df
    
    def df
    
    def get_t get_treatment_rereatment_revenue_report(self,venue_report(self, start_date start_date, end_date):
, end_date):
        """ت        """تقرير إقرير إيرادات العلاجاتيرادات العلاجات"""
        conn = self.db.get_connection()
        query = '''
            SELECT"""
        conn = self.db.get_connection()
        query = '''
            SELECT 
                t.name 
                t.name as treatment as treatment_name,
                t.category,
                COUNT(a.id)_name,
                t.category,
                COUNT(a.id) as as usage_count,
                SUM usage_count,
                SUM(a(a.total_cost) as total_re.total_cost) as total_revenuevenue,
                AVG(a,
                AVG(a.total.total_cost) as avg_re_cost) as avg_revenue
venue
            FROM appointments a
            JOIN treatments t ON            FROM appointments a
            JOIN treatments t ON a.treatment_id = t.id a.treatment_id = t
            WHERE.id
            WHERE a a.appointment_date BETWEEN ? AND ?
.appointment_date BETWEEN ? AND ?
            GROUP BY t.id,            GROUP BY t.id, t t.name, t.category
            ORDER BY.name, t.category
            ORDER total_revenue DESC
        '''
        df BY total_revenue DESC
        '''
        df = pd.read_sql_query = pd.read_sql_query(query, conn, params=(start(query, conn, params=(start_date, end_date))
        conn_date, end_date))
        conn.close()
        return df
    
.close()
        return df    def get_monthly_f
    
    def get_monthly_financial_report(self, yearinancial_report(self, year):
        """تقر):
        """تقرير مالي شهري لير مالي شهري لسنة محددة"""
سنة محددة"""
        conn = self.db.get        conn = self.db.get__connection()
        
        #connection()
        
        # الإ الإيرادات الشهريرادات الشهرية
        monthly_revenueية
        monthly_revenue_query_query = '''
            SELECT 
 = '''
            SELECT 
                strftime('%m                strftime('%m', payment', payment_date) as month_date) as month,
               ,
                SUM(amount) as SUM(amount) as revenue revenue
            FROM payments
            FROM payments 
            
            WHERE strftime('%Y', WHERE strftime('%Y', payment_date) = ?
            payment_date) = ?
            GROUP BY month
            GROUP BY month
            ORDER BY month
        ORDER BY month
        '''
 '''
        
        # المصروفات        
        # المصروفات الشهرية
        monthly الشهرية
        monthly_expenses_query = '''
           _expenses_query = '''
            SELECT 
                strftime('% SELECT 
                strftime('%m', expense_date) as month,
m', expense_date) as                SUM(amount) month,
                SUM(amount as expenses
            FROM expenses 
) as expenses
            FROM expenses 
            WHERE strftime('%Y            WHERE strftime('%Y',', expense_date) = ?
 expense_date) = ?
                       GROUP BY month
            GROUP BY month
            ORDER ORDER BY month
        '''
 BY month
        '''
        
        
        monthly_revenue =        monthly_revenue = pd.read pd.read_sql_query(_sql_query(monthlymonthly_revenue_query,_revenue_query, conn, params=( conn, params=(str(year),))
        monthly_expensesstr(year),))
        monthly_expenses = pd.read_s = pd.read_sql_query(monthly_expensesql_query(monthly_expenses_query, conn_query, conn, params=(str, params=(str(year),))
(year),))
        
        conn        
        conn.close()
        
       .close()
        
        # د # دمج البيانات
       مج البيانات
        months = months = ['01', ' ['01', '02',02', '03 '03', '04', '04', '05', '', '05', '06',06', '07', ' '07', '08', '09',08', '09', '10', '11', ' '10', '11', '12']
        report12']
        report_data_data = []
        
        = []
        
        for month in for month in months:
            months:
            revenue = monthly revenue = monthly_revenue_revenue[monthly_revenue[monthly_revenue['['month'] == month]['month'] == month]['revenuerevenue'].sum()
           '].sum()
            expenses = expenses = monthly_expenses monthly_expenses[monthly_expenses[monthly_expenses['month['month'] == month][''] == month]['expensesexpenses'].sum()
           '].sum()
            profit = profit = revenue - expenses
            
 revenue - expenses
            
            report            report_data.append({
               _data.append({
                'month 'month': month,
               ': month,
                're 'revenue': revenue,
venue': revenue,
                'expenses': expenses,
                'profit': profit
                'expenses': expenses,
                'profit': profit
            })
        
            })
        
        return        return pd.DataFrame(report pd.DataFrame(report_data)
    
   _data)
    
    def get def get_inventory_value_report_inventory_value_report(self):
(self):
        """تقر        """تقريرير قيمة المخزون"""
 قيمة المخزون"""
        conn        conn = self.db.get = self.db.get_connection_connection()
        query =()
        query = '''
            SELECT '''
            SELECT 
                category 
                category,
                COUNT(*),
                COUNT(*) as item as item_count,
_count,
                SUM(quantity                SUM(quantity) as total_) as total_quantity,
                SUM(quantity * unit_pricequantity,
                SUM(quantity * unit_price) as total_value,
) as total_value,
                               AVG(unit_price AVG(unit_price) as) as avg_unit_price
            FROM inventory
            GROUP BY category avg_unit_price
            FROM inventory
            GROUP BY category
            ORDER BY total_value
            ORDER BY total DESC
        '''
       _value DESC
        '''
        df = pd.read_sql_query df = pd.read_sql_query(query, conn)
        conn(query, conn)
        conn.close()
        return df
    
.close()
        return df
    
    def get_payment_method    def get_payment_methods_report(self, start_dates_report(self, start_date, end_date):
        """, end_date):
        """تقرير طرق الدفعتقرير طرق الد"""
        connفع"""
        conn = self.db = self.db.get_.get_connection()
        query = '''
            SELECT 
                payment_method,
connection()
        query = '''
            SELECT 
                payment_method,
                COUNT(*) as transaction_count,
                SUM(                COUNT(*) as transaction_count,
                SUM(amount) as totalamount) as total_amount,
                AV_amount,
               G(amount) as avg_amount AVG(amount) as avg_amount
            FROM payments 
            WHERE payment_date BETWEEN
            FROM payments 
            WHERE payment_date BETWEEN ? AND ?
            GROUP BY payment_method
            ORDER ? AND ?
            GROUP BY payment_method
            ORDER BY total BY total_amount DESC
       _amount DESC
        '''
        df = pd.read_sql '''
        df = pd.read_sql_query(query, conn,_query(query, conn, params params=(start_date, end_date=(start_date, end_date))
))
               conn.close()
        return df
    
    def get conn.close()
        return df
    
    def get_expense_expense_analysis_report_analysis_report(self,(self, start_date, end start_date, end_date):
        """تقرير_date):
        """تقرير تحليل المصروفات تحليل المصروفات"""
"""
        conn = self.db        conn = self.db.get_connection()
        query =.get_connection()
        query = '''
            SELECT 
                category '''
            SELECT 
                category,
,
                COUNT(*) as expense                COUNT(*) as expense_count,
_count,
                SUM(amount                SUM(amount) as) as total_amount,
                total_amount,
                AVG AVG(amount) as(amount) as avg_amount avg_amount,
                MIN(,
                MIN(amount)amount) as min_amount as min_amount,
,
                MAX(amount                MAX(amount) as max_amount) as max_amount

                       FROM expenses 
 FROM expenses 
            WHERE expense_date BETWEEN ? AND ?
                       WHERE expense_date BETWEEN ? AND ?
            GROUP BY category
 GROUP BY category
            ORDER BY total_amount DESC
        '''
            ORDER BY total_amount DESC
        '''
        df = pd.read        df = pd.read_sql_query(query, conn, params_sql_query(query, conn, params=(start_date, end_date))
        conn.close=(start_date, end_date))
        conn.close()
       ()
        return df
    
    return df
    
    def get_daily def get_daily_financial_financial_sn_snapshot(self, targetapshot(self, target_date=None_date=None):
        """ل):
        """لقطة ماليةقطة مالية يومية"""
        يومية"""
        if target if target_date is None:
_date is None:
            target            target_date = date.today_date = date.today()
        
()
        
        conn = self        conn = self.db.get.db.get_connection()
        
_connection()
        
        # إير        # إيراداتادات اليوم
        daily_re اليوم
        daily_revenue_query = '''
            SELECT COALESvenue_query = '''
            SELECT COALESCE(SUM(CE(SUM(amount),amount), 0) as 0) as revenue revenue 
            FROM payments 
 
            FROM payments 
            WHERE payment_date            WHERE payment_date = ?
 = ?
        '''
        
        '''
        
               # مص # مصروفروفات اليوم
        daily_expenses_query =ات اليوم
        daily_expenses_query = '''
 '''
            SELECT COALESCE(            SELECT COALESCE(SUMSUM(amount), (amount), 0) as expenses 
            FROM expenses 
0) as expenses 
            FROM expenses 
            WHERE expense_date =            WHERE expense_date = ?
        ?
        '''
        
        # مواعيد اليوم
        daily_app '''
        
        # مواعيد اليوم
        dailyointments_query = '''
            SELECT_appointments_query = '''
            COUNT(*) as appointments 
            SELECT COUNT(*) as appointments 
            FROM appointments 
            WHERE appointment FROM appointments 
            WHERE appointment_date = ?
        '''
        
_date = ?
        '''
        
        revenue = pd.read_sql        revenue = pd.read_sql_query(daily_revenue_query(daily_revenue_query,_query, conn, params=( conn, params=(target_date,)).iloc[0target_date,)).iloc[0]['revenue']
]['revenue']
               expenses = pd.read_s expenses = pd.read_sql_queryql_query(daily_expenses_query(daily_expenses_query, conn, params=(target_date, conn, params=(target_date,)).iloc[,)).iloc[0]['expenses']
        appointments0]['expenses']
        appointments = pd.read_sql_query = pd.read_sql_query(daily_appointments_query,(daily_appointments_query, conn, params=(target_date conn, params=(target_date,)).iloc[0,)).iloc[0]['appointments']
        
       ]['appointments']
        
        conn.close()
        
        return conn.close()
        
        return {
            'date': target {
            'date': target_date,
            'revenue_date,
            'revenue':': revenue,
            'exp revenue,
            'expenses':enses': expenses,
            ' expenses,
            'net_income': revenuenet_income': revenue - - expenses,
            'appointments expenses,
            'appointments': appointments': appointments,
            'revenue_per_appointment': revenue / appointments if appointments > ,
            'revenue_per_appointment': revenue / appointments if appointments > 0 else0 else 0
        0
        }
 }
    
    def get_yearly    
    def get_yearly_com_comparison_report(selfparison_report(self,, years):
        years):
        """تقرير """تقرير مقارنة سن مقارنة سنويةوية"""
       """
        conn = self.db.get_connection()
 conn = self.db.get_connection()
        
        
        comparison_data =        comparison_data = []
        
 []
        
        for year        for year in years:
 in years:
            # إ            # إيريرادات السنة
            revenueادات السنة
            revenue_query =_query = '''
                SELECT CO '''
                SELECT COALESCEALESCE(SUM(SUM((amount),amount), 0 0) as revenue 
                FROM payments 
                WHERE) as revenue 
                FROM payments 
                WHERE str strftime('%Y',ftime('%Y', payment_date) = payment_date) = ?
            '''
            
            # مصروفات ?
            '''
            
            # مصروفات السنة
            expenses_query = '''
                SELECT COALESCE(SUM(amount), 0) as السنة
            expenses_query = '''
                SELECT COALESCE(SUM(amount), 0) as expenses 
                FROM expenses 
                FROM expenses 
 expenses 
                WHERE strftime                WHERE strftime('%Y('%Y', expense_date)', expense_date) = ?
 = ?
            '''
            
                       '''
            
            # عدد # عدد المواعيد
 المواعيد
            appointments            appointments_query = '''
               _query = '''
                SELECT COUNT SELECT COUNT(*) as appointments 
(*) as appointments 
                FROM                FROM appointments 
                WHERE str appointments 
                WHERE strftimeftime('%Y', appointment_date)('%Y', appointment_date) = = ?
            '''
            
            ?
            '''
            
            revenue = revenue = pd.read_sql pd.read_sql_query(re_query(revenue_queryvenue_query, conn, params, conn, params=(str(year),=(str(year),)).il)).iloc[0]['oc[0]['revenue']
revenue']
            expenses =            expenses = pd.read_sql pd.read_sql_query(_query(expensesexpenses_query, conn,_query, conn, params=( params=(str(year),)).ilstr(year),)).iloc[0oc[0]['expenses']
]['expenses']
            appointments            appointments = pd.read_s = pd.read_sql_queryql_query(appointments_query,(appointments_query, conn, conn, params=(str(year params=(str(year),)).),)).iloc[0iloc[0]['appointments']
            
]['appointments']
            
            comparison_data            comparison_data.append({
                'year':.append({
                'year': year year,
                'revenue,
                'revenue':': revenue,
                'exp revenue,
                'expensesenses': expenses,
                '':net_income': revenue - expenses,
                'net_income': revenue - expenses,
                'appointments': appointments expenses,
                'appointments,
                'revenue_per': appointments,
                're_appointment': revenuevenue_per_appointment': revenue / appointments if appointments > 0 else / appointments if appointments >  0
            })
        
0 else 0
                   conn.close()
        return })
        
        conn.close()
 pd.DataFrame(comparison_data        return pd.DataFrame(compar)
    
    def get_dison_data)
    
    defaily_appointments_count(self):
 get_daily_appointments_count(self        """عدد المواعيد اليوم):
        """عدد المواعيدية"""
        conn = self اليومية"""
        conn =.db.get_connection()
 self.db.get_connection()
               today = date.today().isoformat()
        query = "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ? today = date.today().isoformat()
        query = "SELECT COUNT(*) as count FROM appointments WHERE appointment_date = ?"
        result ="
        result = pd.read pd.read_sql_query(query_sql_query(query, conn, params=(today,))
, conn, params=(today,))
        conn.close()
        conn.close()
        return        return result.iloc result.iloc[0]['count'] if not result.empty[0]['count'] if not result.empty else  else 0

# إن0

# إنشاء مثيل من عملياتشاء مثيل من عمليات CR CRUD
crud =UD
crud = CRUD CRUDOperations()
