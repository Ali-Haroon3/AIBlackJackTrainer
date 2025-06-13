from PIL import Image, ImageDraw, ImageFont
import os
import requests
import base64
import io
from typing import Dict, Tuple

class CardRenderer:
    def __init__(self):
        self.card_width = 120
        self.card_height = 168
        self.corner_radius = 12
        
        # Card mapping for nicubunu.ro images
        self.card_mapping = {
            # Hearts
            ('2', 'Hearts'): 'hearts_2.svg',
            ('3', 'Hearts'): 'hearts_3.svg',
            ('4', 'Hearts'): 'hearts_4.svg',
            ('5', 'Hearts'): 'hearts_5.svg',
            ('6', 'Hearts'): 'hearts_6.svg',
            ('7', 'Hearts'): 'hearts_7.svg',
            ('8', 'Hearts'): 'hearts_8.svg',
            ('9', 'Hearts'): 'hearts_9.svg',
            ('10', 'Hearts'): 'hearts_10.svg',
            ('J', 'Hearts'): 'hearts_jack.svg',
            ('Q', 'Hearts'): 'hearts_queen.svg',
            ('K', 'Hearts'): 'hearts_king.svg',
            ('A', 'Hearts'): 'hearts_ace.svg',
            
            # Diamonds
            ('2', 'Diamonds'): 'diamonds_2.svg',
            ('3', 'Diamonds'): 'diamonds_3.svg',
            ('4', 'Diamonds'): 'diamonds_4.svg',
            ('5', 'Diamonds'): 'diamonds_5.svg',
            ('6', 'Diamonds'): 'diamonds_6.svg',
            ('7', 'Diamonds'): 'diamonds_7.svg',
            ('8', 'Diamonds'): 'diamonds_8.svg',
            ('9', 'Diamonds'): 'diamonds_9.svg',
            ('10', 'Diamonds'): 'diamonds_10.svg',
            ('J', 'Diamonds'): 'diamonds_jack.svg',
            ('Q', 'Diamonds'): 'diamonds_queen.svg',
            ('K', 'Diamonds'): 'diamonds_king.svg',
            ('A', 'Diamonds'): 'diamonds_ace.svg',
            
            # Clubs
            ('2', 'Clubs'): 'clubs_2.svg',
            ('3', 'Clubs'): 'clubs_3.svg',
            ('4', 'Clubs'): 'clubs_4.svg',
            ('5', 'Clubs'): 'clubs_5.svg',
            ('6', 'Clubs'): 'clubs_6.svg',
            ('7', 'Clubs'): 'clubs_7.svg',
            ('8', 'Clubs'): 'clubs_8.svg',
            ('9', 'Clubs'): 'clubs_9.svg',
            ('10', 'Clubs'): 'clubs_10.svg',
            ('J', 'Clubs'): 'clubs_jack.svg',
            ('Q', 'Clubs'): 'clubs_queen.svg',
            ('K', 'Clubs'): 'clubs_king.svg',
            ('A', 'Clubs'): 'clubs_ace.svg',
            
            # Spades
            ('2', 'Spades'): 'spades_2.svg',
            ('3', 'Spades'): 'spades_3.svg',
            ('4', 'Spades'): 'spades_4.svg',
            ('5', 'Spades'): 'spades_5.svg',
            ('6', 'Spades'): 'spades_6.svg',
            ('7', 'Spades'): 'spades_7.svg',
            ('8', 'Spades'): 'spades_8.svg',
            ('9', 'Spades'): 'spades_9.svg',
            ('10', 'Spades'): 'spades_10.svg',
            ('J', 'Spades'): 'spades_jack.svg',
            ('Q', 'Spades'): 'spades_queen.svg',
            ('K', 'Spades'): 'spades_king.svg',
            ('A', 'Spades'): 'spades_ace.svg',
        }
        
        # Base URL for the card images
        self.base_url = "https://nicubunu.ro/graphics/playingcards/simple/"
        
        # Card colors
        self.colors = {
            'red': (220, 20, 20),
            'black': (50, 50, 50),
            'white': (255, 255, 255),
            'card_bg': (250, 250, 250),
            'border': (200, 200, 200),
            'back': (0, 50, 150)
        }
        
        # Suit symbols
        self.suits = {
            'Hearts': '♥',
            'Diamonds': '♦', 
            'Clubs': '♣',
            'Spades': '♠'
        }
        
        self.suit_colors = {
            'Hearts': self.colors['red'],
            'Diamonds': self.colors['red'],
            'Clubs': self.colors['black'],
            'Spades': self.colors['black']
        }
    
    def create_card_image(self, rank: str, suit: str) -> Image.Image:
        """Create a visual card image"""
        # Create card background
        img = Image.new('RGBA', (self.card_width, self.card_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw card background with rounded corners
        self._draw_rounded_rectangle(
            draw, 
            (2, 2, self.card_width-2, self.card_height-2),
            self.corner_radius,
            fill=self.colors['card_bg'],
            outline=self.colors['border'],
            width=2
        )
        
        # Get suit color
        suit_color = self.suit_colors[suit]
        suit_symbol = self.suits[suit]
        
        try:
            # Try to use a better font
            font_large = ImageFont.truetype("arial.ttf", 24)
            font_small = ImageFont.truetype("arial.ttf", 16)
        except:
            # Fallback to default font
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Draw rank in top-left corner
        draw.text((8, 8), rank, fill=suit_color, font=font_large)
        draw.text((12, 32), suit_symbol, fill=suit_color, font=font_small)
        
        # Draw rank in bottom-right corner (rotated)
        draw.text((self.card_width-25, self.card_height-35), rank, fill=suit_color, font=font_large)
        draw.text((self.card_width-20, self.card_height-55), suit_symbol, fill=suit_color, font=font_small)
        
        # Draw center suit symbol
        center_x = self.card_width // 2
        center_y = self.card_height // 2
        
        try:
            font_center = ImageFont.truetype("arial.ttf", 40)
        except:
            font_center = ImageFont.load_default()
        
        # Calculate text size for centering
        bbox = draw.textbbox((0, 0), suit_symbol, font=font_center)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        draw.text(
            (center_x - text_width//2, center_y - text_height//2),
            suit_symbol,
            fill=suit_color,
            font=font_center
        )
        
        return img
    
    def create_card_back(self) -> Image.Image:
        """Create a card back image"""
        img = Image.new('RGBA', (self.card_width, self.card_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw card background
        self._draw_rounded_rectangle(
            draw,
            (2, 2, self.card_width-2, self.card_height-2),
            self.corner_radius,
            fill=self.colors['back'],
            outline=self.colors['border'],
            width=2
        )
        
        # Draw pattern
        for i in range(0, self.card_width, 20):
            for j in range(0, self.card_height, 20):
                if (i + j) % 40 == 0:
                    draw.ellipse((i+5, j+5, i+15, j+15), fill=(255, 255, 255, 100))
        
        return img
    
    def _draw_rounded_rectangle(self, draw, coords, radius, **kwargs):
        """Draw a rounded rectangle"""
        x1, y1, x2, y2 = coords
        
        # Draw main rectangle
        draw.rectangle((x1+radius, y1, x2-radius, y2), **kwargs)
        draw.rectangle((x1, y1+radius, x2, y2-radius), **kwargs)
        
        # Draw corners
        draw.pieslice((x1, y1, x1+2*radius, y1+2*radius), 180, 270, **kwargs)
        draw.pieslice((x2-2*radius, y1, x2, y1+2*radius), 270, 360, **kwargs)
        draw.pieslice((x1, y2-2*radius, x1+2*radius, y2), 90, 180, **kwargs)
        draw.pieslice((x2-2*radius, y2-2*radius, x2, y2), 0, 90, **kwargs)
    
    def get_card_image_base64(self, rank: str, suit: str) -> str:
        """Get card image as base64 string for embedding in HTML"""
        try:
            # Try to get external card image first
            card_key = (rank, suit)
            if card_key in self.card_mapping:
                card_filename = self.card_mapping[card_key]
                card_url = f"{self.base_url}{card_filename}"
                
                # Generate locally instead of using external URLs for reliability
                img = self.create_card_image(rank, suit)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                img_str = base64.b64encode(buffer.getvalue()).decode()
                return f"data:image/png;base64,{img_str}"
            
            # Fallback to generated card image
            img = self.create_card_image(rank, suit)
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            # Fallback to generated image on any error
            img = self.create_card_image(rank, suit)
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
    
    def get_card_back_base64(self) -> str:
        """Get card back image as base64 string"""
        import base64
        import io
        
        img = self.create_card_back()
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"

def create_table_background() -> str:
    """Create a casino table background"""
    width, height = 800, 600
    img = Image.new('RGB', (width, height), (0, 100, 0))  # Green felt
    draw = ImageDraw.Draw(img)
    
    # Draw table outline
    draw.ellipse((50, 150, width-50, height-50), outline=(200, 150, 0), width=8)
    
    # Draw dealer area
    draw.arc((50, 150, width-50, 350), 0, 180, fill=(200, 150, 0), width=4)
    
    # Draw betting circles
    circle_y = height - 120
    for i in range(3):
        circle_x = 200 + i * 200
        draw.ellipse((circle_x-30, circle_y-30, circle_x+30, circle_y+30), 
                    outline=(200, 150, 0), width=3)
    
    # Convert to base64
    import base64
    import io
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"