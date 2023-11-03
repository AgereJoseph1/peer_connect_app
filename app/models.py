from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import UniqueConstraint, Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

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
    group_memberships = relationship('GroupMember', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.id} {self.username}>'

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
