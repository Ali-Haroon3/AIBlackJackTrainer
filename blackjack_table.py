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
        
        # Card mapping for nicubunu.ro simple deck format
        self.card_mapping = {
            # Hearts (h)
            ('2', 'Hearts'): 'simple_h_2.svg',
            ('3', 'Hearts'): 'simple_h_3.svg',
            ('4', 'Hearts'): 'simple_h_4.svg',
            ('5', 'Hearts'): 'simple_h_5.svg',
            ('6', 'Hearts'): 'simple_h_6.svg',
            ('7', 'Hearts'): 'simple_h_7.svg',
            ('8', 'Hearts'): 'simple_h_8.svg',
            ('9', 'Hearts'): 'simple_h_9.svg',
            ('10', 'Hearts'): 'simple_h_10.svg',
            ('J', 'Hearts'): 'simple_h_j.svg',
            ('Q', 'Hearts'): 'simple_h_q.svg',
            ('K', 'Hearts'): 'simple_h_k.svg',
            ('A', 'Hearts'): 'simple_h_a.svg',
            
            # Diamonds (d)
            ('2', 'Diamonds'): 'simple_d_2.svg',
            ('3', 'Diamonds'): 'simple_d_3.svg',
            ('4', 'Diamonds'): 'simple_d_4.svg',
            ('5', 'Diamonds'): 'simple_d_5.svg',
            ('6', 'Diamonds'): 'simple_d_6.svg',
            ('7', 'Diamonds'): 'simple_d_7.svg',
            ('8', 'Diamonds'): 'simple_d_8.svg',
            ('9', 'Diamonds'): 'simple_d_9.svg',
            ('10', 'Diamonds'): 'simple_d_10.svg',
            ('J', 'Diamonds'): 'simple_d_j.svg',
            ('Q', 'Diamonds'): 'simple_d_q.svg',
            ('K', 'Diamonds'): 'simple_d_k.svg',
            ('A', 'Diamonds'): 'simple_d_a.svg',
            
            # Clubs (c)
            ('2', 'Clubs'): 'simple_c_2.svg',
            ('3', 'Clubs'): 'simple_c_3.svg',
            ('4', 'Clubs'): 'simple_c_4.svg',
            ('5', 'Clubs'): 'simple_c_5.svg',
            ('6', 'Clubs'): 'simple_c_6.svg',
            ('7', 'Clubs'): 'simple_c_7.svg',
            ('8', 'Clubs'): 'simple_c_8.svg',
            ('9', 'Clubs'): 'simple_c_9.svg',
            ('10', 'Clubs'): 'simple_c_10.svg',
            ('J', 'Clubs'): 'simple_c_j.svg',
            ('Q', 'Clubs'): 'simple_c_q.svg',
            ('K', 'Clubs'): 'simple_c_k.svg',
            ('A', 'Clubs'): 'simple_c_a.svg',
            
            # Spades (s)
            ('2', 'Spades'): 'simple_s_2.svg',
            ('3', 'Spades'): 'simple_s_3.svg',
            ('4', 'Spades'): 'simple_s_4.svg',
            ('5', 'Spades'): 'simple_s_5.svg',
            ('6', 'Spades'): 'simple_s_6.svg',
            ('7', 'Spades'): 'simple_s_7.svg',
            ('8', 'Spades'): 'simple_s_8.svg',
            ('9', 'Spades'): 'simple_s_9.svg',
            ('10', 'Spades'): 'simple_s_10.svg',
            ('J', 'Spades'): 'simple_s_j.svg',
            ('Q', 'Spades'): 'simple_s_q.svg',
            ('K', 'Spades'): 'simple_s_k.svg',
            ('A', 'Spades'): 'simple_s_a.svg',
        }
    
    def get_card_image(self, rank, suit):
        """Get card image, fallback to generated if file not found"""
        card_key = (rank, suit)
        if card_key in self.card_mapping:
            card_file = f"card_images/simple/{self.card_mapping[card_key]}"
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
        # Check for nicubunu card back variations
        back_files = [
            "card_images/simple/simple_jk_b.svg",  # Blue joker back
            "card_images/simple/simple_jk_r.svg",  # Red joker back
            "card_images/back.svg"                 # Generic back
        ]
        
        for back_file in back_files:
            if os.path.exists(back_file):
                try:
                    with open(back_file, 'rb') as f:
                        return f"data:image/svg+xml;base64,{base64.b64encode(f.read()).decode()}"
                except:
                    continue
        
        # Fallback card back with casino-style design
        img = Image.new('RGB', (self.card_width, self.card_height), '#0F4A9C')
        draw = ImageDraw.Draw(img)
        
        # Draw border
        draw.rectangle([0, 0, self.card_width-1, self.card_height-1], outline='white', width=2)
        draw.rectangle([3, 3, self.card_width-4, self.card_height-4], outline='gold', width=1)
        
        # Draw diamond pattern
        for i in range(10, self.card_width-10, 15):
            for j in range(10, self.card_height-10, 15):
                if (i + j) % 30 == 0:
                    draw.polygon([(i, j-5), (i+5, j), (i, j+5), (i-5, j)], fill='white', outline='gold')
        
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"