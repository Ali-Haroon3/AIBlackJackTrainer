import streamlit as st
import base64
from PIL import Image, ImageDraw, ImageFont
import io
import os

class BlackjackTable:
    """Create a realistic blackjack table interface"""
    
    def __init__(self):
        self.table_width = 800
        self.table_height = 500
        self.card_width = 80
        self.card_height = 112
        
        # Card mapping for local files
        self.card_mapping = {
            ('A', 'Hearts'): 'hearts_ace.svg',
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
            
            ('A', 'Diamonds'): 'diamonds_ace.svg',
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
            
            ('A', 'Clubs'): 'clubs_ace.svg',
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
            
            ('A', 'Spades'): 'spades_ace.svg',
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
        }
    
    def get_card_image(self, rank, suit):
        """Get card image, fallback to generated if file not found"""
        card_key = (rank, suit)
        if card_key in self.card_mapping:
            card_file = f"card_images/{self.card_mapping[card_key]}"
            if os.path.exists(card_file):
                try:
                    with open(card_file, 'rb') as f:
                        return f"data:image/svg+xml;base64,{base64.b64encode(f.read()).decode()}"
                except:
                    pass
        
        # Fallback to generated card
        return self.create_card_image(rank, suit)
    
    def create_card_image(self, rank, suit):
        """Create a fallback card image"""
        img = Image.new('RGB', (self.card_width, self.card_height), 'white')
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([0, 0, self.card_width-1, self.card_height-1], outline='black', width=2)
        
        # Set color based on suit
        color = 'red' if suit in ['Hearts', 'Diamonds'] else 'black'
        
        # Draw rank and suit
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        # Suit symbols
        suit_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
        symbol = suit_symbols.get(suit, suit[0])
        
        # Draw rank in corners
        draw.text((5, 5), rank, fill=color, font=font)
        draw.text((5, self.card_height-25), rank, fill=color, font=font)
        
        # Draw suit symbol
        draw.text((self.card_width//2-10, self.card_height//2-10), symbol, fill=color, font=font)
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
    
    def create_table_background(self):
        """Create a casino-style blackjack table background"""
        return """
        <div style="
            background: radial-gradient(ellipse at center, #0F5132 0%, #0A3D26 50%, #062A1B 100%);
            border: 8px solid #8B4513;
            border-radius: 50px;
            padding: 30px;
            margin: 20px auto;
            max-width: 900px;
            position: relative;
            box-shadow: inset 0 0 50px rgba(0,0,0,0.3), 0 0 20px rgba(0,0,0,0.5);
        ">
            <div style="
                border: 3px solid #FFD700;
                border-radius: 40px;
                padding: 20px;
                background: linear-gradient(135deg, #0F5132 0%, #228B22 100%);
                position: relative;
            ">
                <div style="
                    position: absolute;
                    top: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    color: #FFD700;
                    font-size: 16px;
                    font-weight: bold;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                ">DEALER</div>
                
                <div style="
                    position: absolute;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    color: #FFD700;
                    font-size: 16px;
                    font-weight: bold;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
                ">PLAYER</div>
                
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 20px;
                    transform: translateY(-50%);
                    color: #FFD700;
                    font-size: 12px;
                    font-weight: bold;
                    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
                    writing-mode: vertical-rl;
                ">BLACKJACK PAYS 3:2</div>
                
                <div style="min-height: 400px; position: relative;">
        """
    
    def render_cards_on_table(self, player_hands, dealer_hand, show_dealer_hole_card=False):
        """Render cards positioned on the blackjack table"""
        table_html = self.create_table_background()
        
        # Dealer cards area
        table_html += '<div style="text-align: center; margin: 40px 0 60px 0;">'
        
        if dealer_hand:
            for i, card in enumerate(dealer_hand):
                if i == 1 and not show_dealer_hole_card:
                    # Show card back for hole card
                    card_img = self.get_card_back()
                else:
                    card_img = self.get_card_image(card['rank'], card['suit'])
                
                overlap = i * 60  # Slight overlap for realistic look
                table_html += f'''
                <img src="{card_img}" style="
                    width: {self.card_width}px;
                    height: {self.card_height}px;
                    margin-left: {-overlap if i > 0 else 0}px;
                    box-shadow: 2px 2px 8px rgba(0,0,0,0.4);
                    border-radius: 8px;
                    position: relative;
                    z-index: {10-i};
                " />
                '''
        
        table_html += '</div>'
        
        # Player cards area
        table_html += '<div style="text-align: center; margin: 60px 0 40px 0;">'
        
        if player_hands:
            for hand_idx, hand in enumerate(player_hands):
                if len(player_hands) > 1:
                    table_html += f'<div style="display: inline-block; margin: 0 20px;"><div style="color: #FFD700; font-weight: bold; margin-bottom: 10px;">Hand {hand_idx + 1}</div>'
                
                for i, card in enumerate(hand['cards']):
                    card_img = self.get_card_image(card['rank'], card['suit'])
                    overlap = i * 60
                    table_html += f'''
                    <img src="{card_img}" style="
                        width: {self.card_width}px;
                        height: {self.card_height}px;
                        margin-left: {-overlap if i > 0 else 0}px;
                        box-shadow: 2px 2px 8px rgba(0,0,0,0.4);
                        border-radius: 8px;
                        position: relative;
                        z-index: {10-i};
                    " />
                    '''
                
                if len(player_hands) > 1:
                    table_html += '</div>'
        
        table_html += '</div>'
        
        # Close table
        table_html += '</div></div></div>'
        
        return table_html
    
    def get_card_back(self):
        """Get card back image"""
        back_file = "card_images/back.svg"
        if os.path.exists(back_file):
            try:
                with open(back_file, 'rb') as f:
                    return f"data:image/svg+xml;base64,{base64.b64encode(f.read()).decode()}"
            except:
                pass
        
        # Fallback card back
        img = Image.new('RGB', (self.card_width, self.card_height), '#000080')
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([0, 0, self.card_width-1, self.card_height-1], outline='white', width=2)
        
        # Draw pattern
        for i in range(0, self.card_width, 20):
            for j in range(0, self.card_height, 20):
                if (i + j) % 40 == 0:
                    draw.ellipse((i+5, j+5, i+15, j+15), fill='white')
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"