from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact = Column(String, nullable=False)
    company = Column(String, nullable=True)
    last_interaction = Column(Date, nullable=True)
    next_followup = Column(Date, nullable=True)
    status = Column(String, nullable=True)
    interest_level = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    priority_score = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    logs = relationship("FollowUpLog", back_populates="customer", cascade="all, delete-orphan")


class FollowUpLog(Base):
    __tablename__ = "followup_logs"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    message = Column(Text, nullable=False)
    tone = Column(String, nullable=True)
    generated_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="logs")