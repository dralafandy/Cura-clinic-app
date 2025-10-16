import sqlite3
from datetime import datetime, date, timedelta
import os

class Database:
    _instance = None
    
    def __new__(cls, db_path="clinic.db"):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.db_path = db_path
            cls._instance._initialized = False
        return cls._instance
    
    def initialize(self):
        """إنشاء قاعدة البيانات والجداول إذا لم تكن موجودة"""
        if not self._initialized:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
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
                    
                    # جدول العلاجات والخدمات
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS treatments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            description TEXT,
                            base_price REAL NOT NULL,
                            duration_minutes INTEGER,
                            category TEXT,
                            is_active BOOLEAN DEFAULT 1,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
                    
                    # جدول الموردين - يجب إنشاؤه قبل المخزون
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
                    
                    # إضافة بيانات تجريبية
                    self.add_sample_data(conn, cursor)
                    self._initialized = True
            except sqlite3.Error as e:
                print(f"Database initialization error: {e}")
                raise
    
    def add_sample_data(self, conn, cursor):
        """إضافة بيانات تجريبية - بالترتيب الصحيح"""
        try:
            cursor.execute("SELECT COUNT(*) FROM doctors")
            if cursor.fetchone()[0] == 0:
                
                # 1️⃣ أطباء
                sample_doctors = [
                    ("د. أحمد محمد", "طب الأسنان العام", "01234567890", "ahmed@clinic.com", "القاهرة", "2023-01-01", 15000.0, 10.0),
                    ("د. فاطمة علي", "تقويم الأسنان", "01234567891", "fatma@clinic.com", "الجيزة", "2023-02-01", 18000.0, 15.0),
                    ("د. محمود حسن", "جراحة الفم والأسنان", "01234567892", "mahmoud@clinic.com", "القاهرة", "2023-03-01", 20000.0, 12.0)
                ]
                cursor.executemany('''
                    INSERT INTO doctors (name, specialization, phone, email, address, hire_date, salary, commission_rate) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_doctors)
                
                # 2️⃣ مرضى
                sample_patients = [
                    ("محمد علي", "01234567892", "mohamed@patient.com", "القاهرة، مدينة نصر", "1990-05-15", "ذكر", "لا يوجد", "01012345678"),
                    ("سارة حسن", "01234567893", "sarah@patient.com", "الجيزة، الدقي", "1995-08-20", "أنثى", "حساسية من البنسلين", "01012345679"),
                    ("أحمد كمال", "01234567894", "ahmed@patient.com", "القاهرة، مصر الجديدة", "1988-03-10", "ذكر", "ضغط دم مرتفع", "01012345680"),
                    ("منى إبراهيم", "01234567895", "mona@patient.com", "الجيزة، المهندسين", "1992-11-25", "أنثى", "لا يوجد", "01012345681")
                ]
                cursor.executemany('''
                    INSERT INTO patients (name, phone, email, address, date_of_birth, gender, medical_history, emergency_contact) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_patients)
                
                # 3️⃣ علاجات
                sample_treatments = [
                    ("فحص وتنظيف", "فحص شامل للأسنان وتنظيف بالموجات فوق الصوتية", 200.0, 60, "وقائي"),
                    ("حشو عادي", "حشو الأسنان بالحشو الأبيض", 300.0, 45, "علاجي"),
                    ("حشو عصب", "علاج جذور الأسنان وحشو العصب", 800.0, 90, "علاجي"),
                    ("تبييض الأسنان", "تبييض الأسنان بالليزر", 1500.0, 120, "تجميلي"),
                    ("خلع سن", "خلع الأسنان البسيط", 150.0, 30, "جراحي"),
                    ("تركيب تقويم", "تركيب تقويم الأسنان الثابت", 5000.0, 180, "تجميلي")
                ]
                cursor.executemany('''
                    INSERT INTO treatments (name, description, base_price, duration_minutes, category) 
                    VALUES (?, ?, ?, ?, ?)
                ''', sample_treatments)
                
                # 4️⃣ موردين - يجب قبل المخزون
                sample_suppliers = [
                    ("شركة المستلزمات الطبية", "علي عبدالله", "01234567896", "supplies@medical.com", "القاهرة، وسط البلد", "آجل 30 يوم"),
                    ("مؤسسة الأدوات الطبية", "محمد صلاح", "01234567897", "info@medtools.com", "الجيزة، المهندسين", "نقدي"),
                    ("شركة الأدوية والمستلزمات", "هدى أحمد", "01234567898", "contact@pharmaco.com", "القاهرة، مصر الجديدة", "آجل 60 يوم")
                ]
                cursor.executemany('''
                    INSERT INTO suppliers (name, contact_person, phone, email, address, payment_terms) 
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', sample_suppliers)
                
                # 5️⃣ مواعيد
                today = date.today()
                yesterday = today - timedelta(days=1)
                tomorrow = today + timedelta(days=1)
                next_week = today + timedelta(days=7)
                
                sample_appointments = [
                    (1, 1, 1, yesterday.isoformat(), "09:00", "مكتمل", "فحص دوري", 200.0),
                    (2, 2, 2, yesterday.isoformat(), "11:00", "مكتمل", "", 300.0),
                    (3, 1, 1, today.isoformat(), "10:00", "مؤكد", "", 200.0),
                    (4, 3, 5, today.isoformat(), "14:00", "مجدول", "خلع ضرس العقل", 150.0),
                    (1, 2, 3, tomorrow.isoformat(), "09:30", "مؤكد", "", 800.0),
                    (2, 1, 4, next_week.isoformat(), "15:00", "مجدول", "تبييض كامل", 1500.0)
                ]
                cursor.executemany('''
                    INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, notes, total_cost) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', sample_appointments)
                
                # 6️⃣ مخزون - بعد الموردين
                sample_inventory = [
                    ("قفازات طبية (علبة 100 قطعة)", "مستهلكات", 50, 25.0, 20, 1, "2026-12-31"),
                    ("كمامات طبية (علبة 50 قطعة)", "مستهلكات", 40, 15.0, 15, 1, "2026-06-30"),
                    ("حقن تخدير موضعي", "أدوية", 100, 12.0, 30, 3, "2025-12-31"),
                    ("خيوط جراحية", "مستهلكات", 80, 8.0, 25, 2, "2027-01-31"),
                    ("حشو أبيض (كمبوزيت)", "مواد طبية", 30, 150.0, 10, 2, "2026-08-31"),
                    ("مطهر طبي (ليتر)", "مستهلكات", 25, 45.0, 10, 1, "2025-09-30"),
                    ("إبر حقن", "مستهلكات", 200, 0.5, 50, 1, "2026-03-31"),
                    ("قطن طبي (كيلو)", "مستهلكات", 15, 35.0, 5, 1, "2027-12-31"),
                    ("شاش معقم", "مستهلكات", 60, 5.0, 20, 1, "2026-11-30"),
                    ("معجون أسنان طبي", "منتجات", 100, 25.0, 30, 3, "2026-05-31")
                ]
                cursor.executemany('''
                    INSERT INTO inventory (item_name, category, quantity, unit_price, min_stock_level, supplier_id, expiry_date) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', sample_inventory)
                
                # 7️⃣ مدفوعات
                sample_payments = [
                    (1, 1, 200.0, "نقدي", yesterday.isoformat(), "مكتمل", ""),
                    (2, 2, 300.0, "بطاقة ائتمان", yesterday.isoformat(), "مكتمل", ""),
                    (None, 3, 500.0, "تحويل بنكي", (today - timedelta(days=3)).isoformat(), "مكتمل", "دفعة مقدمة للتقويم")
                ]
                cursor.executemany('''
                    INSERT INTO payments (appointment_id, patient_id, amount, payment_method, payment_date, status, notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', sample_payments)
                
                # 8️⃣ مصروفات
                last_month = today - timedelta(days=30)
                two_weeks_ago = today - timedelta(days=14)
                
                sample_expenses = [
                    ("رواتب", "رواتب الأطباء - شهر سابق", 53000.0, last_month.isoformat(), "تحويل بنكي", "SAL-001", ""),
                    ("إيجار", "إيجار العيادة - شهري", 8000.0, last_month.isoformat(), "تحويل بنكي", "RENT-001", ""),
                    ("كهرباء ومياه", "فواتير الخدمات", 1500.0, two_weeks_ago.isoformat(), "نقدي", "UTIL-001", ""),
                    ("صيانة", "صيانة جهاز الأشعة", 2500.0, two_weeks_ago.isoformat(), "نقدي", "MAINT-001", ""),
                    ("مستلزمات", "شراء مستهلكات طبية", 4500.0, yesterday.isoformat(), "شيك", "SUP-001", "من شركة المستلزمات"),
                    ("تسويق", "إعلانات على السوشيال ميديا", 1000.0, (today - timedelta(days=5)).isoformat(), "بطاقة ائتمان", "MKT-001", "")
                ]
                cursor.executemany('''
                    INSERT INTO expenses (category, description, amount, expense_date, payment_method, receipt_number, notes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', sample_expenses)
                
                # 9️⃣ استخدام المخزون
                sample_usage = [
                    (1, 1, 2, yesterday.isoformat(), "استخدام في فحص المريض"),
                    (7, 2, 1, yesterday.isoformat(), "حقنة تخدير"),
                    (3, 2, 1, yesterday.isoformat(), "تخدير موضعي")
                ]
                cursor.executemany('''
                    INSERT INTO inventory_usage (inventory_id, appointment_id, quantity_used, usage_date, notes) 
                    VALUES (?, ?, ?, ?, ?)
                ''', sample_usage)
                
                # تحديث كميات المخزون بعد الاستخدام
                cursor.execute("UPDATE inventory SET quantity = quantity - 2 WHERE id = 1")
                cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = 7")
                cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE id = 3")
                
                conn.commit()
                print("✅ تم إضافة البيانات التجريبية بنجاح!")
                
        except sqlite3.Error as e:
            print(f"❌ خطأ في إضافة البيانات التجريبية: {e}")
            conn.rollback()
            raise
    
    def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات"""
        return sqlite3.connect(self.db_path)

# إنشاء مثيل واحد من قاعدة البيانات
db = Database()
db.initialize()
