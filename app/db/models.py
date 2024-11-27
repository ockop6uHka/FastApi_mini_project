from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    traffic = relationship("Traffic", back_populates="customer")

class Traffic(Base):
    __tablename__ = "traffic"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    ip = Column(String, nullable=False)
    date = Column(DateTime, nullable=False)
    received_traffic = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="traffic")
