from js import document, console, window
from pyodide.ffi import create_proxy

# Sample offer data
SAMPLE_OFFERS = [
    {
        "id": 1,
        "from": "camera_trader",
        "image_url": "/static/image_test/camera.jpg",
        "title": "Vintage Camera Trade",
        "description": "I'd like to trade my vintage camera for your guitar. It's in excellent condition.",
        "value": "$150 or equivalent",
        "posted_time": "3h ago"
    },
    {
        "id": 2,
        "from": "music_collector",
        "image_url": "/static/image_test/guitar.jpg",
        "title": "Acoustic Guitar Offer",
        "description": "I'm offering my acoustic guitar plus $50 for your digital piano.",
        "value": "Guitar + $50",
        "posted_time": "5h ago"
    },
    {
        "id": 3,
        "from": "tech_enthusiast",
        "image_url": "/static/image_test/laptop.jpg",
        "title": "Gaming Laptop Trade",
        "description": "Would like to trade my gaming laptop for your camera equipment. Can add cash if needed.",
        "value": "$800 equivalent",
        "posted_time": "1d ago"
    },
    {
        "id": 4,
        "from": "instrument_dealer",
        "image_url": "/static/image_test/piano.jpg",
        "title": "Digital Piano Exchange",
        "description": "Offering my digital piano for your guitar collection. Barely used, perfect condition.",
        "value": "$400 value",
        "posted_time": "2d ago"
    }
]

class OfferStack:
    def __init__(self):
        self.offers = []
        self.current_index = 0
        self.container = document.getElementById('offerStackContainer')
        self.cards_wrapper = document.getElementById('offerCardsWrapper')
        self.counter = document.getElementById('offerCounter')
        self.empty_state = document.getElementById('emptyOfferState')
        self.nav_buttons = document.getElementById('stackNavigation')
        self.accept_btn = document.getElementById('acceptOfferBtn')
        self.reject_btn = document.getElementById('rejectOfferBtn')
        
        # Initialize event handlers
        if self.accept_btn:
            self.accept_btn.addEventListener('click', create_proxy(self.accept_offer))
        if self.reject_btn:
            self.reject_btn.addEventListener('click', create_proxy(self.reject_offer))
            
    def fetch_offers(self):
        """Fetch offers data - would connect to backend in real implementation"""
        # For demo, using sample data
        return SAMPLE_OFFERS
        
    def initialize(self):
        """Set up the offer stack with data"""
        try:
            self.offers = self.fetch_offers()
            self.update_counter()
            
            if len(self.offers) > 0:
                self.empty_state.style.display = "none"
                self.nav_buttons.style.display = "flex"
                self.render_offers()
            else:
                self.empty_state.style.display = "flex"
                self.nav_buttons.style.display = "none"
                
            console.log("Offer stack initialized with", len(self.offers), "offers")
        except Exception as e:
            console.error("Error initializing offer stack:", e)
            
    def update_counter(self):
        """Update the offer counter display"""
        if len(self.offers) > 0:
            self.counter.textContent = f"{len(self.offers)} offer{'s' if len(self.offers) > 1 else ''} available"
        else:
            self.counter.textContent = "No offers available"
            
    def render_offers(self):
        """Render all offer cards in the stack with proper positioning"""
        try:
            # Clear existing cards
            card_elements = self.cards_wrapper.querySelectorAll('.offer-card')
            for card in card_elements:
                card.remove()
                
            # Create and add cards for each offer
            for i, offer in enumerate(self.offers):
                card = self.create_offer_card(offer)
                
                # Set initial position classes
                if i == self.current_index:
                    card.classList.add('active')
                elif i == self.current_index + 1:
                    card.classList.add('next')
                elif i == self.current_index + 2:
                    card.classList.add('next-plus-one')
                elif i < self.current_index:
                    card.classList.add('previous')
                else:
                    card.classList.add('upcoming')
                    
                self.cards_wrapper.appendChild(card)
        except Exception as e:
            console.error("Error rendering offers:", e)
            
    def create_offer_card(self, offer):
        """Create a DOM element for an offer card"""
        try:
            card = document.createElement('div')
            card.className = 'offer-card'
            card.id = f"offer-{offer['id']}"
            card.innerHTML = f"""
                <div class="card-header">
                    <div class="offer-badge">
                        <i class="fas fa-tag"></i> Offer
                    </div>
                    <div class="offer-from">{offer['from']}</div>
                </div>
                
                <div class="offer-content">
                    <img src="{offer['image_url']}" alt="{offer['title']}" class="offer-image">
                    <div class="offer-details">
                        <div>
                            <div class="offer-title">{offer['title']}</div>
                            <div class="offer-description">{offer['description']}</div>
                        </div>
                        <div class="offer-value">{offer['value']}</div>
                    </div>
                </div>
                
                <div class="offer-time">{offer['posted_time']}</div>
            """
            return card
        except Exception as e:
            console.error("Error creating offer card:", e)
            empty_div = document.createElement('div')
            return empty_div
            
    def update_card_positions(self):
        """Update the position classes of all cards after navigation"""
        try:
            cards = self.cards_wrapper.querySelectorAll('.offer-card')
            
            for i, card in enumerate(cards):
                # Remove all position classes
                card.classList.remove('active', 'next', 'next-plus-one', 'previous', 'upcoming')
                
                # Add appropriate position class
                if i == self.current_index:
                    card.classList.add('active')
                elif i == self.current_index + 1:
                    card.classList.add('next')
                elif i == self.current_index + 2:
                    card.classList.add('next-plus-one')
                elif i < self.current_index:
                    card.classList.add('previous')
                else:
                    card.classList.add('upcoming')
        except Exception as e:
            console.error("Error updating card positions:", e)
            
    def accept_offer(self, event=None):
        """Handle accept button click"""
        try:
            if len(self.offers) > 0 and self.current_index < len(self.offers):
                accepted_offer = self.offers[self.current_index]
                console.log("Accepted offer:", accepted_offer['title'])
                
                # Show confirmation (in a real app, would connect to backend)
                self.show_accept_confirmation(accepted_offer)
                
                # Remove the accepted offer from the stack
                self.offers.pop(self.current_index)
                
                # Update display
                self.update_counter()
                
                if len(self.offers) > 0:
                    self.render_offers()
                else:
                    self.empty_state.style.display = "flex"
                    self.nav_buttons.style.display = "none"
        except Exception as e:
            console.error("Error accepting offer:", e)
            
    def reject_offer(self, event=None):
        """Handle reject button click"""
        try:
            if len(self.offers) > 0 and self.current_index < len(self.offers):
                rejected_offer = self.offers[self.current_index]
                console.log("Rejected offer:", rejected_offer['title'])
                
                # Move to next offer if available
                if self.current_index < len(self.offers) - 1:
                    self.current_index += 1
                else:
                    # Loop back to the first offer if at the end
                    self.current_index = 0
                    
                # Update card positions with animation
                self.update_card_positions()
        except Exception as e:
            console.error("Error rejecting offer:", e)
            
    def show_accept_confirmation(self, offer):
        """Show confirmation message when accepting an offer"""
        try:
            # Create a temporary confirmation message
            confirmation = document.createElement('div')
            confirmation.className = 'offer-confirmation'
            confirmation.innerHTML = f"""
                <div class="confirmation-content">
                    <i class="fas fa-check-circle"></i>
                    <p>You've accepted the offer from {offer['from']}!</p>
                    <p class="confirmation-detail">The user will be notified.</p>
                </div>
            """
            confirmation.style.position = 'absolute'
            confirmation.style.top = '50%'
            confirmation.style.left = '50%'
            confirmation.style.transform = 'translate(-50%, -50%)'
            confirmation.style.backgroundColor = 'rgba(76, 175, 80, 0.9)'
            confirmation.style.color = 'white'
            confirmation.style.padding = '20px'
            confirmation.style.borderRadius = '10px'
            confirmation.style.textAlign = 'center'
            confirmation.style.zIndex = '10'
            confirmation.style.boxShadow = '0 4px 15px rgba(0, 0, 0, 0.3)'
            
            # Add icon styling
            icon = confirmation.querySelector('i')
            if icon:
                icon.style.fontSize = '40px'
                icon.style.marginBottom = '10px'
                
            # Add to the wrapper
            self.cards_wrapper.appendChild(confirmation)
            
            # Remove after 2 seconds
            def remove_confirmation():
                if confirmation and confirmation.parentNode:
                    confirmation.parentNode.removeChild(confirmation)
            
            window.setTimeout(create_proxy(remove_confirmation), 2000)
        except Exception as e:
            console.error("Error showing confirmation:", e)

# Initialize the offer stack
def initialize_offer_stack():
    try:
        offer_stack = OfferStack()
        offer_stack.initialize()
    except Exception as e:
        console.error("Error initializing offer stack:", e)

# Run initialization when the page loads
window.addEventListener('load', create_proxy(initialize_offer_stack))