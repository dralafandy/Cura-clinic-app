import sqlite3
import hashlib
from datetime import datetime, date
import os

class Database:
    def __init__(self, db_path="clinic.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """إنشاء قاعدة البيانات والجداول"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # جدول الأطباء
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                hire_date DATE,
                salary REAL,
                commission_rate REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المرضى
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                date_of_birth DATE,
                gender TEXT,
                medical_history TEXT,
                emergency_contact TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول العلاجات مع نسبة العمولة
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                base_price REAL NOT NULL,
                duration_minutes INTEGER,
                category TEXT,
                commission_rate REAL DEFAULT 0.0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المواعيد
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                treatment_id INTEGER,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status TEXT DEFAULT 'مجدول',
                notes TEXT,
                total_cost REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                FOREIGN KEY (treatment_id) REFERENCES treatments (id)
            )
        ''')
        
        # جدول المدفوعات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                patient_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                payment_method TEXT NOT NULL,
                payment_date DATE NOT NULL,
                status TEXT DEFAULT 'مكتمل',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (appointment_id) REFERENCES appointments (id),
                FOREIGN KEY (patient_id) REFERENCES patients (id)
            )
        ''')
        
        # جدول المخزون
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                category TEXT,
                quantity INTEGER NOT NULL DEFAULT 0,
                unit_price REAL,
                min_stock_level INTEGER DEFAULT 10,
                supplier_id INTEGER,
                expiry_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id)
            )
        ''')
        
        # جدول الموردين
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                payment_terms TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المصروفات
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                expense_date DATE NOT NULL,
                payment_method TEXT,
                receipt_number TEXT,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول استخدام المخزون
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inventory_id INTEGER NOT NULL,
                appointment_id INTEGER,
                quantity_used INTEGER NOT NULL,
                usage_date DATE NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (inventory_id) REFERENCES inventory (id),
                FOREIGN KEY (appointment_id) REFERENCES appointments (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.add_sample_data()
    
    def add_sample_data(self):
        """إضافة بيانات تجريبية"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM doctors")
        if cursor.fetchone()[0] == 0:
            sample_doctors = [
                ("د. أحمد محمد", "طب الأسنان العام", "01234567890", "ahmed@clinic.com", "القاهرة", "2023-01-01", 15000.0, 10.0),
                ("د. فاطمة علي", "تقويم الأسنان", "01234567891", "fatma@clinic.com", "الجيزة", "2023-02-01", 18000.0, 15.0),
                ("د. محمد حسن", "جراحة الفم والوجه", "01234567892", "mohamed@clinic.com", "الإسكندرية", "2023-03-01", 20000.0, 20.0)
            ]
            cursor.executemany('''
                INSERT INTO doctors (name, specialization, phone, email, address, hire_date, salary, commission_rate)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_doctors)
            
            sample_patients = [
                ("محمد علي", "01112345678", "mohamed.ali@email.com", "القاهرة", "1990-05-15", "ذكر", "لا يوجد", "01234567899"),
                ("سارة أحمد", "01187654321", "sara.ahmed@email.com", "الجيزة", "1985-08-22", "أنثى", "حساسية من البنسلين", "01234567888"),
                ("علي محمود", "01098765432", "ali.mahmoud@email.com", "الإسكندرية", "2000-03-10", "ذكر", "لا يوجد", "01234567877")
            ]
            cursor.executemany('''
                INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_patients)
            
            sample_treatments = [
                ("فحص وتنظيف", "فحص شامل وتنظيف الأسنان", 200.0, 60, "وقائي", 10.0),
                ("حشو عادي", "حشو الأسنان بالحشو الأبيض", 300.0, 45, "علاجي", 15.0),
                ("حشو عصب", "علاج عصب السن", 800.0, 120, "علاجي", 20.0),
                ("خلع سن", "خلع السن", 150.0, 30, "جراحي", 25.0),
                ("تركيب تقويم", "تركيب جهاز تقويم الأسنان", 5000.0, 90, "تقويمي", 30.0)
            ]
            cursor.executemany('''
                INSERT INTO treatments (name, description, base_price, duration_minutes, category, commission_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_treatments)
            
            sample_inventory = [
                ("قفازات طبية", "مستهلكات", 100, 0.5, 20, None, None),
                ("كمامات طبية", "مستهلكات", 200, 0.3, 50, None, None),
                ("حقن التخدير", "أدوية", 50, 15.0, 10, None, "2025-12-31"),
                ("حشوات بيضاء", "مواد علاجية", 30, 25.0, 5, None, "2025-06-30"),
                ("خيوط جراحية", "أدوات جراحية", 20, 8.0, 5, None, None)
            ]
            cursor.executemany('''
                INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_inventory)
            
            sample_suppliers = [
                ("مورد طبي 1", "أحمد خالد", "01122334455", "supplier1@email.com", "القاهرة", "30 يوم"),
                ("مورد طبي 2", "محمد سمير", "01233445566", "supplier2@email.com", "الجيزة", "15 يوم")
            ]
            cursor.executemany('''
                INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', sample_suppliers)
            
            sample_appointments = [
                (1, 1, 1, "2023-10-01", "10:00", "مكتمل", "فحص روتيني", 200.0),
                (2, 2, 2, "2023-10-02", "11:30", "مجدول", "حشو أسنان", 300.0),
                (3, 3, 3, "2023-10-03", "14:00", "ملغى", "إلغاء المريض", 800.0)
            ]
            cursor.executemany('''
                INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_appointments)
            
            sample_payments = [
                (1, 1, 200.0, "نقداً", "2023-10-01", "مكتمل", "دفع كامل"),
                (2, 2, 100.0, "بطاقة", "2023-10-02", "معلق", "دفع جزئي")
            ]
            cursor.executemany('''
                INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_payments)
            
            sample_expenses = [
                ("إيجار", "إيجار العيادة الشهري", 5000.0, "2023-10-01", "تحويل بنكي", "REC001", "دفعة شهر أكتوبر"),
                ("مستلزمات طبية", "شراء قفازات وكمامات", 1000.0, "2023-10-02", "نقداً", "REC002", "")
            ]
            cursor.executemany('''
                INSERT INTO expenses (category, description, amount, expense_date, payment_method, receipt_number, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', sample_expenses)
        
        conn.commit()
        conn.close()
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_path)

db = Database()
