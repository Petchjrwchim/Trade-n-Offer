from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db_setup import Base

class User(Base):
    __tablename__ = "users"

    ID = Column(Integer, primary_key=True, index=True)
    UserName = Column(String(50), unique=True, nullable=False)
    UserPass = Column(String(255), nullable=False)

    sent_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.sender_id]", back_populates="sender")
    received_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.receiver_id]", back_populates="receiver")
