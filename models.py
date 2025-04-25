from datetime import datetime

class User:
    def __init__(self, user_id, username, password, role, full_name=None, email=None, phone=None, created_at=None):
        self.id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.created_at = created_at if created_at else datetime.now()
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'created_at': self.created_at
        }

class Customer(User):
    def __init__(self, user_id, username, password, role, full_name=None, email=None, phone=None, 
                 created_at=None, address=None, city=None, state=None, zip_code=None, customer_id=None):
        super().__init__(user_id, username, password, role, full_name, email, phone, created_at)
        self.customer_id = customer_id
        self.address = address
        self.city = city
        self.state = state
        self.zip_code = zip_code
    
    def to_dict(self):
        user_dict = super().to_dict()
        user_dict.update({
            'customer_id': self.customer_id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'zip_code': self.zip_code
        })
        return user_dict

class Courier(User):
    def __init__(self, user_id, username, password, role, full_name=None, email=None, phone=None, 
                 created_at=None, vehicle_type=None, license_plate=None, status=None, courier_id=None):
        super().__init__(user_id, username, password, role, full_name, email, phone, created_at)
        self.courier_id = courier_id
        self.vehicle_type = vehicle_type
        self.license_plate = license_plate
        self.status = status
    
    def to_dict(self):
        user_dict = super().to_dict()
        user_dict.update({
            'courier_id': self.courier_id,
            'vehicle_type': self.vehicle_type,
            'license_plate': self.license_plate,
            'status': self.status
        })
        return user_dict

class Package:
    def __init__(self, package_id, tracking_number, sender_id, receiver_id, courier_id=None, 
                 description=None, weight=None, dimensions=None, status='pending', 
                 pickup_address=None, delivery_address=None, created_at=None, 
                 estimated_delivery=None, actual_delivery=None):
        self.id = package_id
        self.tracking_number = tracking_number
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.courier_id = courier_id
        self.description = description
        self.weight = weight
        self.dimensions = dimensions
        self.status = status
        self.pickup_address = pickup_address
        self.delivery_address = delivery_address
        self.created_at = created_at if created_at else datetime.now()
        self.estimated_delivery = estimated_delivery
        self.actual_delivery = actual_delivery
    
    def to_dict(self):
        return {
            'id': self.id,
            'tracking_number': self.tracking_number,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'courier_id': self.courier_id,
            'description': self.description,
            'weight': self.weight,
            'dimensions': self.dimensions,
            'status': self.status,
            'pickup_address': self.pickup_address,
            'delivery_address': self.delivery_address,
            'created_at': self.created_at,
            'estimated_delivery': self.estimated_delivery,
            'actual_delivery': self.actual_delivery
        }

class TrackingHistory:
    def __init__(self, history_id, package_id, status, location=None, timestamp=None, notes=None):
        self.id = history_id
        self.package_id = package_id
        self.status = status
        self.location = location
        self.timestamp = timestamp if timestamp else datetime.now()
        self.notes = notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'package_id': self.package_id,
            'status': self.status,
            'location': self.location,
            'timestamp': self.timestamp,
            'notes': self.notes
        }