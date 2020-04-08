from graphene import Enum

from . import db, Base
from sqlalchemy import Column, ForeignKey, Integer, String, Enum, Date, DateTime, func
from sqlalchemy.orm import relationship
from graphene import Enum


class Gender(Enum):
    """Represents a user gender"""
    MALE = 1
    FEMALE = 2
    UNIDENTIFIED = 0


class UserModel(Base):
    """
    Represents a User on database
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), index=True, nullable=False)
    name = Column(String(255))
    gender = Column(String())
    date_of_birth = Column(Date())
    visits = relationship('VisitModel', backref='user')

    def __repr__(self):
        return '<User %r>' % self.email


class WebsiteModel(Base):
    """"
    Represents a website on database
    """
    __tablename__ = 'websites'

    id = Column(Integer, primary_key=True, unique=True)
    url = Column(String(255), nullable=False)
    topic = Column(String(255))
    visits = relationship('VisitModel', backref='website')


class VisitModel(Base):
    """
    Represents user viits across websites
    """
    __tablename__ = 'visits'

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    website_id = Column(Integer, ForeignKey('websites.id'), nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)
