from models import Customer, Package
from database import Database

class CustomerController:
    def __init__(self):
        self.db = Database()
    
    def get_customer_packages(self, customer_id):
        """Get packages sent or received by a customer"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, 
                   sender.full_name as sender_name, 
                   receiver.full_name as receiver_name,
                   u.full_name as courier_name
            FROM packages p
            JOIN customers s ON p.sender_id = s.id
            JOIN customers r ON p.receiver_id = r.id
            JOIN users sender ON s.user_id = sender.id
            JOIN users receiver ON r.user_id = receiver.id
            LEFT JOIN couriers c ON p.courier_id = c.id
            LEFT JOIN users u ON c.user_id = u.id
            WHERE p.sender_id=? OR p.receiver_id=?
            ORDER BY p.created_at DESC
        """, (customer_id, customer_id))
        
        packages = []
        for pkg in cursor.fetchall():
            package = {
                'id': pkg[0],
                'tracking_number': pkg[1],
                'sender_name': pkg[16],
                'receiver_name': pkg[17],
                'courier_name': pkg[18],
                'status': pkg[8],
                'pickup_address': pkg[9],
                'delivery_address': pkg[10],
                'created_at': pkg[11],
                'estimated_delivery': pkg[12]
            }
            packages.append(package)
        
        return packages
    
    def get_customer_by_id(self, customer_id):
        """Get customer details by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, u.username, u.password, u.role, u.full_name, u.email, u.phone, u.created_at,
                   c.address, c.city, c.state, c.zip_code
            FROM customers c
            JOIN users u ON c.user_id = u.id
            WHERE c.id=?
        """, (customer_id,))
        
        customer_data = cursor.fetchone()
        if customer_data:
            return Customer(
                customer_data[0], customer_data[1], customer_data[2], customer_data[3],
                customer_data[4], customer_data[5], customer_data[6], customer_data[7],
                customer_data[8], customer_data[9], customer_data[10], customer_data[11],
                customer_data[0]  # customer_id same as id
            )
        return None
    
    def update_customer_profile(self, customer_id, full_name, email, phone, address, city, state, zip_code):
        """Update customer profile information"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get user_id from customer
            cursor.execute("SELECT user_id FROM customers WHERE id=?", (customer_id,))
            user_id = cursor.fetchone()[0]
            
            # Update user table
            cursor.execute(
                "UPDATE users SET full_name=?, email=?, phone=? WHERE id=?",
                (full_name, email, phone, user_id)
            )
            
            # Update customer table
            cursor.execute(
                "UPDATE customers SET address=?, city=?, state=?, zip_code=? WHERE id=?",
                (address, city, state, zip_code, customer_id)
            )
            
            conn.commit()
            return True, "Profile updated successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)