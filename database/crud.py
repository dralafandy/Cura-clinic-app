import sqlite3
import pandas as pd
from datetime import date, time, datetime
import os

# اسم ملف قاعدة البيانات
DB_NAME = 'clinic_management.db'

class CRUDOperations:
    """
    فئة متكاملة لإجراء عمليات CRUD على قاعدة بيانات SQLite.
    تتضمن دوال التعامل مع المرضى، الأطباء، العلاجات، والمواعيد.
    """
    def __init__(self):
        """تهيئة الاتصال بقاعدة البيانات وإنشاء الجداول."""
        self.conn = self._get_connection()
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._insert_initial_data()

    def _get_connection(self):
        """إنشاء اتصال بقاعدة بيانات SQLite."""
        try:
            conn = sqlite3.connect(DB_NAME, check_same_thread=False)
            return conn
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
            return None

    def _create_tables(self):
        """إنشاء جميع الجداول المطلوبة إذا لم تكن موجودة."""
        if not self.conn:
            return

        # 1. جدول المرضى
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                date_of_birth DATE,
                gender TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 2. جدول الأطباء
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                phone TEXT,
                email TEXT
            )
        """)

        # 3. جدول العلاجات
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                base_price REAL NOT NULL,
                duration_minutes INTEGER,
                category TEXT
            )
        """)

        # 4. جدول المواعيد
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                treatment_id INTEGER NOT NULL,
                appointment_date DATE NOT NULL,
                appointment_time TIME NOT NULL,
                status TEXT NOT NULL DEFAULT 'مجدول',
                total_cost REAL NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (id),
                FOREIGN KEY (treatment_id) REFERENCES treatments (id)
            )
        """)
        self.conn.commit()

    def _insert_initial_data(self):
        """إدخال بيانات تجريبية لضمان عمل التطبيق."""
        if not self.conn:
            return
            
        # إضافة أطباء
        self.cursor.execute("SELECT COUNT(*) FROM doctors")
        if self.cursor.fetchone()[0] == 0:
            doctors = [
                ('أحمد علي', 'تقويم أسنان', '01012345678', 'ahmed@clinic.com'),
                ('سارة محمد', 'جراحة فم', '01198765432', 'sara@clinic.com'),
                ('خالد سعيد', 'طب أسنان عام', '01255554444', 'khaled@clinic.com')
            ]
            self.cursor.executemany("INSERT INTO doctors (name, specialization, phone, email) VALUES (?, ?, ?, ?)", doctors)

        # إضافة علاجات
        self.cursor.execute("SELECT COUNT(*) FROM treatments")
        if self.cursor.fetchone()[0] == 0:
            treatments = [
                ('تنظيف وتلميع', 300.0, 30, 'وقائي'),
                ('حشو أمامي', 800.0, 60, 'ترميمي'),
                ('خلع ضرس عقل', 1500.0, 90, 'جراحي')
            ]
            self.cursor.executemany("INSERT INTO treatments (name, base_price, duration_minutes, category) VALUES (?, ?, ?, ?)", treatments)
            
        # إضافة مرضى
        self.cursor.execute("SELECT COUNT(*) FROM patients")
        if self.cursor.fetchone()[0] == 0:
            patients = [
                ('ماجد الكناني', '01001001000', 'majed@test.com', 'القاهرة', '1995-05-15', 'ذكر'),
                ('فاطمة الزهراء', '01122334455', 'fatma@test.com', 'الجيزة', '1988-11-20', 'أنثى')
            ]
            self.cursor.executemany("INSERT INTO patients (name, phone, email, address, date_of_birth, gender) VALUES (?, ?, ?, ?, ?, ?)", patients)
            
        # إضافة مواعيد (تجريبي)
        self.cursor.execute("SELECT COUNT(*) FROM appointments")
        if self.cursor.fetchone()[0] == 0:
            today = date.today().strftime('%Y-%m-%d')
            tomorrow = (date.today() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')
            
            appointments = [
                (1, 1, 1, today, '10:00:00', 'مؤكد', 800.0, 'المريض جديد'),
                (2, 2, 2, today, '11:30:00', 'مجدول', 1500.0, 'لإجراء جراحة'),
                (1, 3, 3, tomorrow, '09:30:00', 'في الانتظار', 300.0, 'تنظيف روتيني')
            ]
            self.cursor.executemany("""
                INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, total_cost, notes) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, appointments)

        self.conn.commit()

    def _read_query(self, query, params=()):
        """تنفيذ استعلام قراءة وإرجاع النتائج في شكل DataFrame."""
        if not self.conn:
            return pd.DataFrame()
        try:
            df = pd.read_sql_query(query, self.conn, params=params)
            return df
        except Exception as e:
            print(f"Error in read query: {e}")
            return pd.DataFrame()

    # --- دوال قراءة البيانات المطلوبة في appointments.py ---
    
    def get_all_patients(self):
        """قراءة جميع المرضى."""
        query = "SELECT * FROM patients ORDER BY name"
        return self._read_query(query)

    def get_patient_by_id(self, patient_id):
        """قراءة مريض واحد."""
        query = "SELECT * FROM patients WHERE id = ?"
        df = self._read_query(query, (patient_id,))
        return df.iloc[0].tolist() if not df.empty else None

    def get_all_doctors(self):
        """قراءة جميع الأطباء."""
        query = "SELECT * FROM doctors ORDER BY name"
        return self._read_query(query)

    def get_doctor_by_id(self, doctor_id):
        """قراءة طبيب واحد."""
        query = "SELECT * FROM doctors WHERE id = ?"
        df = self._read_query(query, (doctor_id,))
        return df.iloc[0].tolist() if not df.empty else None

    def get_all_treatments(self):
        """قراءة جميع العلاجات."""
        query = "SELECT * FROM treatments ORDER BY name"
        return self._read_query(query)

    def get_treatment_by_id(self, treatment_id):
        """قراءة علاج واحد."""
        query = "SELECT * FROM treatments WHERE id = ?"
        df = self._read_query(query, (treatment_id,))
        return df.iloc[0].tolist() if not df.empty else None

    def get_all_appointments(self):
        """قراءة جميع المواعيد مع تفاصيل المريض والطبيب والعلاج."""
        query = """
        SELECT 
            a.id, a.appointment_date, a.appointment_time, a.status, a.total_cost, a.notes,
            p.name AS patient_name, p.phone AS patient_phone, 
            d.name AS doctor_name, d.specialization AS doctor_specialization,
            t.name AS treatment_name, t.base_price AS treatment_price
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN treatments t ON a.treatment_id = t.id
        ORDER BY a.appointment_date DESC, a.appointment_time DESC
        """
        return self._read_query(query)

    # --- الدالة المفقودة التي سببت الخطأ ---
    
    def get_appointments_by_date(self, appointment_date):
        """
        [الدالة التي كانت مفقودة]
        استرجاع جميع المواعيد لتاريخ محدد.
        :param appointment_date: التاريخ المراد الفلترة به (datetime.date object).
        :return: DataFrame من المواعيد.
        """
        date_str = appointment_date.strftime('%Y-%m-%d')
        
        query = f"""
        SELECT 
            a.id, a.appointment_date, a.appointment_time, a.status, a.total_cost, a.notes,
            p.name AS patient_name, p.phone AS patient_phone, 
            d.name AS doctor_name, d.specialization AS doctor_specialization,
            t.name AS treatment_name, t.base_price AS treatment_price
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        JOIN treatments t ON a.treatment_id = t.id
        WHERE a.appointment_date = ?
        ORDER BY a.appointment_time ASC
        """
        return self._read_query(query, (date_str,))

    # --- دوال إنشاء وتحديث البيانات المطلوبة في appointments.py ---

    def create_patient(self, name, phone, email=None, address=None, date_of_birth=None, gender=None):
        """إنشاء مريض جديد وإرجاع معرّفه."""
        if not self.conn:
            return None
        try:
            self.cursor.execute("""
                INSERT INTO patients (name, phone, email, address, date_of_birth, gender)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, phone, email, address, date_of_birth, gender))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating patient: {e}")
            return None

    def create_appointment(self, patient_id, doctor_id, treatment_id, appointment_date, appointment_time, notes, total_cost):
        """إنشاء موعد جديد وإرجاع معرّفه."""
        if not self.conn:
            return None
        
        date_str = appointment_date.strftime('%Y-%m-%d')
        time_str = appointment_time.strftime('%H:%M:%S')

        try:
            self.cursor.execute("""
                INSERT INTO appointments (patient_id, doctor_id, treatment_id, appointment_date, appointment_time, status, total_cost, notes)
                VALUES (?, ?, ?, ?, ?, 'مجدول', ?, ?)
            """, (patient_id, doctor_id, treatment_id, date_str, time_str, total_cost, notes))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error creating appointment: {e}")
            return None

    def update_appointment_status(self, appointment_id, new_status):
        """تحديث حالة موعد معين."""
        if not self.conn:
            return False
        try:
            self.cursor.execute("""
                UPDATE appointments SET status = ? WHERE id = ?
            """, (new_status, appointment_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating appointment status: {e}")
            return False
            
# إنشاء نسخة من الفئة ليتم استيرادها واستخدامها في ملفات Streamlit
# (كما هو مستخدم في appointments.py: from database.crud import crud)
crud = CRUDOperations()

