from extensions import db
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def generate_uuid():
    return uuid4()
    

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(), primary_key=True)
    username = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.Text())
    isAdmin = db.Column(db.Boolean())
    isActive = db.Column(db.Boolean())
    createdBy = db.Column(db.String(), nullable=False)

    def __repr__(self):
        return f"<User {self.username}>"

    def set_id(self):
        self.id = str(generate_uuid())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username,isActive=True).first()

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


class TokenBlocklist(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    jti = db.Column(db.String(), nullable=True)
    create_at = db.Column(db.DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Token {self.jti}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()


class Orders(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.String(), primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    another_phone = db.Column(db.String(20), nullable=True)
    price = db.Column(db.Float, nullable=False)
    min_guests = db.Column(db.Integer, nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.String(10), nullable=False)
    end_time = db.Column(db.String(10), nullable=False)
    order_amount = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, nullable=False)
    order_type = db.Column(db.String(50), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    isActive = db.Column(db.Boolean(), nullable=False)
    createdBy = db.Column(db.String(), nullable=False)


    def save(self):
        db.session.add(self)
        db.session.commit()

    def set_id(self):
        self.id = str(generate_uuid())

    def update(self):
        db.session.commit()


class Categories(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    isActive = db.Column(db.Boolean(), nullable=False, default=True)
    createdBy = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Category {self.name}>"

    def set_id(self):
        self.id = str(generate_uuid())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_active(cls):
        return cls.query.filter_by(isActive=True).all()

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name, isActive=True).first()


class SubCategories(db.Model):
    __tablename__ = 'sub_categories'

    id = db.Column(db.String(), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_category_id = db.Column(db.String(), db.ForeignKey('categories.id'), nullable=False)
    isActive = db.Column(db.Boolean(), nullable=False, default=True)
    createdBy = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to parent category
    parent_category = db.relationship('Categories', backref='sub_categories')

    def __repr__(self):
        return f"<SubCategory {self.name}>"

    def set_id(self):
        self.id = str(generate_uuid())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_all_active(cls):
        return cls.query.filter_by(isActive=True).all()

    @classmethod
    def get_by_name_and_parent(cls, name, parent_category_id):
        return cls.query.filter_by(name=name, parent_category_id=parent_category_id, isActive=True).first()

    @classmethod
    def get_by_parent_category(cls, parent_category_id):
        return cls.query.filter_by(parent_category_id=parent_category_id, isActive=True).all()


class OrderMenu(db.Model):
    __tablename__ = 'order_menu'

    id = db.Column(db.String(), primary_key=True)
    order_id = db.Column(db.String(), db.ForeignKey('orders.id'), nullable=False)
    sub_category_id = db.Column(db.String(), db.ForeignKey('sub_categories.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text, nullable=True)
    isActive = db.Column(db.Boolean(), nullable=False, default=True)
    createdBy = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    order = db.relationship('Orders', backref='order_menu_items')
    sub_category = db.relationship('SubCategories', backref='order_menu_items')

    def __repr__(self):
        return f"<OrderMenu {self.order_id} - {self.sub_category_id}>"

    def set_id(self):
        self.id = str(generate_uuid())

    def save(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        self.updated_at = datetime.utcnow()
        db.session.commit()

    def delete(self):
        self.isActive = False
        self.update()

    @classmethod
    def get_by_order_id(cls, order_id):
        return cls.query.filter_by(order_id=order_id, isActive=True).all()

    @classmethod
    def get_by_order_and_subcategory(cls, order_id, sub_category_id):
        return cls.query.filter_by(
            order_id=order_id,
            sub_category_id=sub_category_id,
            isActive=True
        ).first()

    @classmethod
    def delete_by_order_id(cls, order_id):
        """Soft delete all menu items for an order"""
        menu_items = cls.query.filter_by(order_id=order_id, isActive=True).all()
        for item in menu_items:
            item.delete()

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'sub_category_id': self.sub_category_id,
            'sub_category_name': self.sub_category.name if self.sub_category else None,
            'parent_category_name': self.sub_category.parent_category.name if self.sub_category and self.sub_category.parent_category else None,
            'quantity': self.quantity,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class OrderMenuMeta(db.Model):
    __tablename__ = 'order_menu_meta'
    
    id = db.Column(db.String(), primary_key=True)
    order_id = db.Column(db.String(), db.ForeignKey('orders.id'), nullable=False, unique=True)
    general_notes = db.Column(db.Text, nullable=True)
    isActive = db.Column(db.Boolean(), nullable=False, default=True)
    createdBy = db.Column(db.String(), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    order = db.relationship('Orders', backref='order_menu_meta')
    
    def __repr__(self):
        return f"<OrderMenuMeta {self.order_id}>"
    
    def set_id(self):
        self.id = str(generate_uuid())
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    def delete(self):
        self.isActive = False
        self.update()
    
    @classmethod
    def get_by_order_id(cls, order_id):
        return cls.query.filter_by(order_id=order_id, isActive=True).first()
    
    @classmethod
    def delete_by_order_id(cls, order_id):
        """Soft delete menu meta for an order"""
        meta = cls.query.filter_by(order_id=order_id, isActive=True).first()
        if meta:
            meta.delete()
    
    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'general_notes': self.general_notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }