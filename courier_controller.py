from models import Package, Courier, TrackingHistory
from database import Database
from datetime import datetime, timedelta
import random
import string

class CourierController:
    def __init__(self):
        self.db = Database()
    
    def generate_tracking_number(self):
        """Generate a unique tracking number"""
        letters = string.ascii_uppercase
        digits = string.digits
        tracking_number = ''.join(random.choice(letters) for _ in range(2))
        tracking_number += ''.join(random.choice(digits) for _ in range(8))
        return tracking_number
    
    def create_package(self, sender_id, receiver_id, description, weight, dimensions, 
                       pickup_address, delivery_address, estimated_delivery_days=3):
        """Create a new package"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            tracking_number = self.generate_tracking_number()
            estimated_delivery = datetime.now() + timedelta(days=estimated_delivery_days)
            
            cursor.execute(
                """INSERT INTO packages 
                (tracking_number, sender_id, receiver_id, description, weight, dimensions, 
                pickup_address, delivery_address, estimated_delivery) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (tracking_number, sender_id, receiver_id, description, weight, dimensions, 
                 pickup_address, delivery_address, estimated_delivery)
            )
            package_id = cursor.lastrowid
            
            # Add initial tracking history
            cursor.execute(
                """INSERT INTO tracking_history 
                (package_id, status, notes) 
                VALUES (?, ?, ?)""",
                (package_id, 'pending', 'Package created and awaiting pickup')
            )
            
            conn.commit()
            return True, package_id
        except Exception as e:
            conn.rollback()
            return False, str(e)
    
    def assign_courier(self, package_id, courier_id):
        """Assign a courier to a package"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update package
            cursor.execute(
                "UPDATE packages SET courier_id=?, status='assigned' WHERE id=?",
                (courier_id, package_id)
            )
            
            # Update courier status
            cursor.execute(
                "UPDATE couriers SET status='assigned' WHERE id=?",
                (courier_id,)
            )
            
            # Add tracking history
            cursor.execute(
                """INSERT INTO tracking_history 
                (package_id, status, notes) 
                VALUES (?, ?, ?)""",
                (package_id, 'assigned', f'Courier #{courier_id} assigned to package')
            )
            
            conn.commit()
            return True, "Courier assigned successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
    
    def update_package_status(self, package_id, status, location=None, notes=None):
        """Update package status and add tracking history"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        try:
            # Update package status
            cursor.execute(
                "UPDATE packages SET status=? WHERE id=?",
                (status, package_id)
            )
            
            # Add tracking history
            cursor.execute(
                """INSERT INTO tracking_history 
                (package_id, status, location, notes) 
                VALUES (?, ?, ?, ?)""",
                (package_id, status, location, notes)
            )
            
            # If delivered, update delivery time
            if status == 'delivered':
                cursor.execute(
                    "UPDATE packages SET actual_delivery=CURRENT_TIMESTAMP WHERE id=?",
                    (package_id,)
                )
                
                # Mark courier as available
                cursor.execute(
                    """UPDATE couriers SET status='available' 
                    WHERE id=(SELECT courier_id FROM packages WHERE id=?)""",
                    (package_id,)
                )
            
            conn.commit()
            return True, "Status updated successfully"
        except Exception as e:
            conn.rollback()
            return False, str(e)
    
    def get_package_by_id(self, package_id):
        """Get package details by ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM packages WHERE id=?", (package_id,))
        package_data = cursor.fetchone()
        
        if package_data:
            return Package(*package_data)
        return None
    
    def get_package_by_tracking_number(self, tracking_number):
        """Get package details by tracking number"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM packages WHERE tracking_number=?", (tracking_number,))
        package_data = cursor.fetchone()
        
        if package_data:
            return Package(*package_data)
        return None
    
    def get_tracking_history(self, package_id):
        """Get tracking history for a package"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tracking_history WHERE package_id=? ORDER BY timestamp DESC", (package_id,))
        history_records = cursor.fetchall()
        
        return [TrackingHistory(*record) for record in history_records]
    
    def get_available_couriers(self):
        """Get list of available couriers"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.id, u.full_name, c.vehicle_type, c.license_plate 
            FROM couriers c
            JOIN users u ON c.user_id = u.id
            WHERE c.status='available'
        """)
        
        return cursor.fetchall()
    
    def get_courier_packages(self, courier_id):
        """Get packages assigned to a courier"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.*, u1.full_name as sender_name, u2.full_name as receiver_name
            FROM packages p
            JOIN customers s ON p.sender_id = s.id
            JOIN customers r ON p.receiver_id = r.id
            JOIN users u1 ON s.user_id = u1.id
            JOIN users u2 ON r.user_id = u2.id
            WHERE p.courier_id=?
            ORDER BY p.created_at DESC
        """, (courier_id,))
        
        packages = []
        for pkg in cursor.fetchall():
            package = {
                'id': pkg[0],
                'tracking_number': pkg[1],
                'sender_name': pkg[16],
                'receiver_name': pkg[17],
                'status': pkg[8],
                'pickup_address': pkg[9],
                'delivery_address': pkg[10],
                'created_at': pkg[11],
                'estimated_delivery': pkg[12]
            }
            packages.append(package)
        
        return packages