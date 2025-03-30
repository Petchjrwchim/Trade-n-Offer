from persistent import Persistent

class TradeItem(Persistent):
    def __init__(self, name, description, price, image, category=None):
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.category = category
        self.is_available = True

    def set_available(self, available: bool):
        self.is_available = available
        self._p_changed = True

    def __repr__(self):
        return f"<TradeItem(name={self.name}, price={self.price}, category={self.category})>"
