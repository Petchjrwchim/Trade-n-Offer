from persistent import Persistent

class TradeItem(Persistent):
    def __init__(self, name, description, price, image, category=None):
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.category = category

    def __repr__(self):
        return f"<TradeItem(name={self.name}, price={self.price}, category={self.category})>"
