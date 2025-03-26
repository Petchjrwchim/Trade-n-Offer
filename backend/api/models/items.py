from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db_setup import Base

class Item(Base):
    __tablename__ = "items"

    ID = Column(Integer, primary_key=True, index=True)
    userID = Column(Integer, ForeignKey("users.ID"), nullable=False)
    zodb_id = Column(Integer, nullable=False)

    owner = relationship("User", back_populates="items")
    sent_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.sender_item_id]", back_populates="sender_item")
    received_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.receiver_item_id]", back_populates="receiver_item")
