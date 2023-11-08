from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint, Table, Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import uuid
from .import db

# Association tables for many-to-many relationships
user_ambiance = Table('user_ambiance', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('ambiance_id', Integer, ForeignKey('ambiances.id'))
)

user_cuisine = Table('user_cuisine', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('cuisine_id', Integer, ForeignKey('cuisines.id'))
)

user_dietary = Table('user_dietary', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('dietary_id', Integer, ForeignKey('dietary_restrictions.id'))
)

user_budget = Table('user_budget', db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('budget_id', Integer, ForeignKey('budget_preferences.id'))
)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(128))
    email = Column(String(120), unique=True, nullable=True)
    phone_number = Column(String(20), unique=True, nullable=True)
    address = Column(String(255), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    group_memberships = relationship('GroupMember', back_populates='user', cascade="all, delete-orphan")
    ambiances = relationship('Ambiance', secondary=user_ambiance, back_populates='users')
    cuisines = relationship('Cuisine', secondary=user_cuisine, back_populates='users')
    dietary_restrictions = relationship('DietaryRestriction', secondary=user_dietary, back_populates='users')
    budget_preferences = relationship('BudgetPreference', secondary=user_budget, back_populates='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.id} {self.username}>'
    def set_profile_picture(self, filename):
        self.profile_picture = secure_filename(filename)

class GroupMember(db.Model):
    __tablename__ = 'group_members'

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship('User', back_populates='group_memberships')
    group = relationship('Group', back_populates='members')

    __table_args__ = (UniqueConstraint('group_id', 'user_id', name='_group_user_uc'),)

    def __repr__(self):
        return f'<GroupMember {self.user_id} in Group {self.group_id}>'

class Group(db.Model):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    image_path = Column(String(256), nullable=True)  # Path to the image file
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False, onupdate=datetime.utcnow)
    members = relationship('GroupMember', back_populates='group', cascade="all, delete-orphan")
    invite_tokens = relationship('InviteToken', back_populates='group', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Group {self.id} {self.name}>'

class InviteToken(db.Model):
    __tablename__ = 'invite_tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(256), nullable=False, unique=True)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    group = relationship('Group', back_populates='invite_tokens')

    def __init__(self, group_id, expires_in=48):
        self.token = str(uuid.uuid4())
        self.group_id = group_id
        self.expires_at = datetime.utcnow() + timedelta(hours=expires_in)

    def is_valid(self):
        return datetime.utcnow() < self.expires_at

    def __repr__(self):
        return f'<InviteToken {self.token} for Group {self.group_id}>'


# Ambiance model
class Ambiance(db.Model):
    __tablename__ = 'ambiances'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    # Relationship with User
    users = relationship('User', secondary=user_ambiance, back_populates='ambiances')

# Cuisine model
class Cuisine(db.Model):
    __tablename__ = 'cuisines'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    # Relationship with User
    users = relationship('User', secondary=user_cuisine, back_populates='cuisines')

# DietaryRestriction model
class DietaryRestriction(db.Model):
    __tablename__ = 'dietary_restrictions'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    # Relationship with User
    users = relationship('User', secondary=user_dietary, back_populates='dietary_restrictions')

# BudgetPreference model
class BudgetPreference(db.Model):
    __tablename__ = 'budget_preferences'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    # Relationship with User
    users = relationship('User', secondary=user_budget, back_populates='budget_preferences')

# Remember to create the tables in the database if they don't exist
# db.create_all()

class Event(db.Model):
    __tablename__ = 'events'
    id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String(128), nullable=False)
    time = db.Column(db.Time, nullable=False)
    date = db.Column(db.Date, nullable=False) 
    duration = db.Column(db.String(20), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'))  # Link to the group

    # Relationships
    group = db.relationship('Group', backref=db.backref('events', lazy='dynamic'))  # Back-reference to allow group.events access

    def __repr__(self):
        return f'<Event {self.id} {self.activity_type}>'