from models import User, Customer, Courier
from database import Database
import hashlib

class AuthController:
    def __init__(self):
        self.db = Database()
        self.current_user = None
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self, username, password):
        """Authenticate user"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        hashed_password = self.hash_password(password)
        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, hashed_password)
        )
        user_data = cursor.fetchone()
        
        if user_data:
            user_id, username, password, role, full_name, email, phone, created_at = user_data
            
            if role == 'customer':
                cursor.execute("SELECT * FROM customers WHERE user_id=?", (user_id,))
                customer_data = cursor.fetchone()
                if customer_data:
                    customer_id, user_id, address, city, state, zip_code = customer_data
                    self.current_user = Customer(
                        user_id, username, password, role, full_name, email, phone, 
                        created_at, address, city, state, zip_code, customer_id
                    )
            elif role == 'courier':
                cursor.execute("SELECT * FROM couriers WHERE user_id=?", (user_id,))
                courier_data = cursor.fetchone()
                if courier_data:
                    courier_id, user_id, vehicle_type, license_plate, status = courier_data
                    self.current_user = Courier(
                        user_id, username, password, role, full_name, email, phone, 
                        created_at, vehicle_type, license_plate, status, courier_id
                    )
            else:
                self.current_user = User(
                    user_id, username, password, role, full_name, email, phone, created_at
                )
            return True
        return False
    
    def register_customer(self, username, password, full_name, email, phone, address, city, state, zip_code):
        """Register a new customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Check if username exists
        cursor.execute("SELECT id FROM users WHERE username=?", (username,))
        if cursor.fetchone():
            return False, "Username already exists"
        
        try:
            # Insert user
            hashed_password = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password, role, full_name, email, phone) VALUES (?, ?, ?, ?, ?, ?)",
                (username, hashed_password, 'customer', full_name, email, phone)
            )
            user_id = cursor.lastrowid
            
            # Insert customer
            cursor.execute(
                "INSERT INTO customers (user_id, address, city, state, zip_code) VALUES (?, ?, ?, ?, ?)",
                (user_id, address, city, state, zip_code)
            )
            conn.commit()
            
            return True, "Registration successful"
        except Exception as e:
            conn.rollback()
            return False, str(e)
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
    
    def get_current_user(self):
        """Get current logged in user"""
        return self.current_user