-- Table for purchase offers (buying a single item)
CREATE TABLE purchase_offers (
    ID INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    buyer_id INT NOT NULL,
    seller_id INT NOT NULL,
    item_id INT NOT NULL,
    status ENUM('pending', 'accepted', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    FOREIGN KEY (buyer_id) REFERENCES users(ID),
    FOREIGN KEY (seller_id) REFERENCES users(ID),
    FOREIGN KEY (item_id) REFERENCES items(ID)
);