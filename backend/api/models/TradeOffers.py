from sqlalchemy import Column, Integer, String, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db_setup import Base
from sqlalchemy import Boolean

class TradeOffer(Base):
    __tablename__ = "trade_offers"

    ID = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.ID"))
    receiver_id = Column(Integer, ForeignKey("users.ID"))
    sender_item_id = Column(Integer, ForeignKey("items.ID"))
    receiver_item_id = Column(Integer, ForeignKey("items.ID"))
    status = Column(Enum("pending", "accepted", "rejected", name="offer_status"), default="pending")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id])
    receiver = relationship("User", foreign_keys=[receiver_id])
    sender_item = relationship("Item", foreign_keys=[sender_item_id])
    receiver_item = relationship("Item", foreign_keys=[receiver_item_id])

    matches = relationship("Match", back_populates="offer")

class Match(Base):
    __tablename__ = "matches"

    ID = Column(Integer, primary_key=True, index=True)
    offer_id = Column(Integer, ForeignKey("trade_offers.ID"))
    status = Column(Enum("active", "completed", "cancelled", name="match_status"), default="active")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    offer = relationship("TradeOffer", back_populates="matches")

class User(Base):
    __tablename__ = "users"

    ID = Column(Integer, primary_key=True, index=True)
    UserName = Column(String(50), unique=True, nullable=False)
    UserPass = Column(String(255), nullable=False)
    img_url = Column(String(255), nullable=True)

    sent_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.sender_id]", back_populates="sender")
    received_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.receiver_id]", back_populates="receiver")
    items = relationship("Item", back_populates="owner")
    purchase_offers_sent = relationship("PurchaseOffer", foreign_keys="[PurchaseOffer.buyer_id]", back_populates="buyer")
    purchase_offers_received = relationship("PurchaseOffer", foreign_keys="[PurchaseOffer.seller_id]", back_populates="seller")

class Item(Base):
    __tablename__ = "items"

    ID = Column(Integer, primary_key=True, index=True)
    userID = Column(Integer, ForeignKey("users.ID"), nullable=False)
    zodb_id = Column(Integer, nullable=False)
    is_purchasable = Column(Boolean, default=False)
    is_tradeable = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)

    owner = relationship("User", back_populates="items")
    sent_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.sender_item_id]", back_populates="sender_item")
    received_offers = relationship("TradeOffer", foreign_keys="[TradeOffer.receiver_item_id]", back_populates="receiver_item")
    purchase_offers = relationship("PurchaseOffer", back_populates="item")


class Wishlist(Base):
    __tablename__ = "wishlist"

    ID = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.ID", ondelete="CASCADE"))
    item_id = Column(Integer, ForeignKey("items.ID", ondelete="CASCADE"))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User")
    item = relationship("Item")

    
class PurchaseOffer(Base):
    __tablename__ = "purchase_offers"

    ID = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.ID"))
    seller_id = Column(Integer, ForeignKey("users.ID"))
    item_id = Column(Integer, ForeignKey("items.ID"))


    status = Column(Enum("idle", "active", "completed", "cancelled", name="purchase_offer_status"), default="idle")
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    buyer = relationship("User", foreign_keys=[buyer_id], back_populates="purchase_offers_sent")
    seller = relationship("User", foreign_keys=[seller_id], back_populates="purchase_offers_received")
    item = relationship("Item", back_populates="purchase_offers")


