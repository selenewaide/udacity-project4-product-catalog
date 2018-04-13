#!/usr/bin/env python2.7
"""Database objects for product catalog."""

import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Category(Base):
    """Category object."""

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250))
    user = Column(String(250))


class Product(Base):
    """Product object."""

    __tablename__ = 'product'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    created = Column(DateTime, default=datetime.datetime.utcnow)
    user = Column(String(250))

    @property
    def serialize(self):
        """Data for product API endpoint."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'category_id': self.category_id,
            'user': self.user
        }


# Create SQLite db file
engine = create_engine('sqlite:///product_catalog4.db')


Base.metadata.create_all(engine)
