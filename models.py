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