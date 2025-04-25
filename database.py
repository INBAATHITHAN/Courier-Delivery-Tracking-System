import sqlite3
from sqlite3 import Error

class Database:
    def __init__(self, db_file="courier_db.sqlite"):
        self.db_file = db_file
        self.conn = None
        
    def create_connection(self):
        """Create a database connection to SQLite database"""
        try:
            self.conn = sqlite3.connect(self.db_file)
            return self.conn
        except Error as e:
            print(e)
        return None
    
    def initialize_database(self):
        """Initialize database tables"""
        sql_create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        sql_create_customers_table = """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            address TEXT,
            city TEXT,
            state TEXT,
            zip_code TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
        
        sql_create_couriers_table = """
        CREATE TABLE IF NOT EXISTS couriers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            vehicle_type TEXT,
            license_plate TEXT,
            status TEXT DEFAULT 'available',
            FOREIGN KEY (user_id) REFERENCES users (id)
        );
        """
        
        sql_create_packages_table = """
        CREATE TABLE IF NOT EXISTS packages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_number TEXT NOT NULL UNIQUE,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            courier_id INTEGER,
            description TEXT,
            weight REAL,
            dimensions TEXT,
            status TEXT DEFAULT 'pending',
            pickup_address TEXT,
            delivery_address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            estimated_delivery TIMESTAMP,
            actual_delivery TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES customers (id),
            FOREIGN KEY (receiver_id) REFERENCES customers (id),
            FOREIGN KEY (courier_id) REFERENCES couriers (id)
        );
        """
        
        sql_create_tracking_history_table = """
        CREATE TABLE IF NOT EXISTS tracking_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            package_id INTEGER NOT NULL,
            status TEXT NOT NULL,
            location TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,
            FOREIGN KEY (package_id) REFERENCES packages (id)
        );
        """
        
        try:
            conn = self.create_connection()
            cursor = conn.cursor()
            cursor.execute(sql_create_users_table)
            cursor.execute(sql_create_customers_table)
            cursor.execute(sql_create_couriers_table)
            cursor.execute(sql_create_packages_table)
            cursor.execute(sql_create_tracking_history_table)
            conn.commit()
            
            # Create admin user if not exists
            cursor.execute("SELECT * FROM users WHERE username='admin'")
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT INTO users (username, password, role, full_name) VALUES (?, ?, ?, ?)",
                    ('admin', 'admin123', 'admin', 'Admin User')
                )
                conn.commit()
                
        except Error as e:
            print(e)
        finally:
            if conn:
                conn.close()
    
    def get_connection(self):
        """Get a database connection"""
        if not self.conn:
            self.create_connection()
        return self.conn