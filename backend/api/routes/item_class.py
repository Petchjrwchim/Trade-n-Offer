from persistent import Persistent

class TradeItem(Persistent):
    """
    Trade Item stored in ZODB.

    Attributes:
        name (str): Name of the item.
        description (str): Description of the item.
        price (float): Price of the item.
        image (str): Image path or Base64 encoded string.
        category (str): (Optional) Category of the item.
    """

    def __init__(self, name, description, price, image, category=None):
        self.name = name
        self.description = description
        self.price = price
        self.image = image
        self.category = category

    def __repr__(self):
        return f"<TradeItem(name={self.name}, price={self.price}, category={self.category})>"
