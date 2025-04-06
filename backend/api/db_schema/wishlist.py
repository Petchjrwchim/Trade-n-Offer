from pydantic import BaseModel

class WishlistCreate(BaseModel):
    user_id: int
    item_id: int
    