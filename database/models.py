import sqlite3

class Database:
    def __init__(self, db_name="clinic.db"):
        self.db_name = db_name
        self.create_tables()

    def get_connection(self):
        """Get a connection to the database."""
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        """Create all necessary tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Patients table
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
                emergency_contact TEXT
            )
        ''')

        # Doctors table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                specialization TEXT,
                phone TEXT,
                email TEXT,
                commission_rate REAL
            )
        ''')

        # Treatments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS treatments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                base_price REAL,
                commission_rate REAL,
                notes TEXT
            )
        ''')

        # Appointments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER,
                doctor_id INTEGER,
                appointment_date DATE,
                appointment_time TEXT,
                status TEXT,
                total_cost REAL,
                commission_rate REAL,
                notes TEXT,
                FOREIGN KEY (patient_id) REFERENCES patients(id),
                FOREIGN KEY (doctor_id) REFERENCES doctors(id)
            )
        ''')

        # Appointment-Treatments junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointment_treatments (
                appointment_id INTEGER,
                treatment_id INTEGER,
                PRIMARY KEY (appointment_id, treatment_id),
                FOREIGN KEY (appointment_id) REFERENCES appointments(id),
                FOREIGN KEY (treatment_id) REFERENCES treatments(id)
            )
        ''')

        # Expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                description TEXT,
                amount REAL,
                expense_date DATE,
                payment_method TEXT,
                receipt_number TEXT,
                notes TEXT
            )
        ''')

        # Payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                appointment_id INTEGER,
                patient_id INTEGER,
                amount REAL,
                payment_method TEXT,
                payment_date DATE,
                status TEXT,
                notes TEXT,
                FOREIGN KEY (appointment_id) REFERENCES appointments(id),
                FOREIGN KEY (patient_id) REFERENCES patients(id)
            )
        ''')

        # Inventory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name TEXT NOT NULL,
                quantity INTEGER,
                min_stock_level INTEGER,
                unit_price REAL,
                supplier_id INTEGER,
                notes TEXT,
                FOREIGN KEY (supplier_id) REFERENCES suppliers(id)
            )
        ''')

        # Suppliers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                contact_person TEXT,
                phone TEXT,
                email TEXT,
                address TEXT,
                notes TEXT
            )
        ''')

        conn.commit()
        conn.close()
