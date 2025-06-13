import trafilatura
import requests
from bs4 import BeautifulSoup
import re

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    """
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text

def scrape_blackjack_strategy_charts(url: str) -> dict:
    """
    Scrape blackjack strategy charts from the given URL
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find strategy tables/charts in the HTML
        strategy_data = {
            'hard_totals': {},
            'soft_totals': {},
            'pairs': {}
        }
        
        # Look for tables containing strategy information
        tables = soup.find_all('table')
        
        for table in tables:
            # Try to identify what type of chart this is
            table_text = table.get_text().lower()
            
            if 'hard' in table_text and 'total' in table_text:
                strategy_data['hard_totals'] = parse_strategy_table(table, 'hard')
            elif 'soft' in table_text and 'total' in table_text:
                strategy_data['soft_totals'] = parse_strategy_table(table, 'soft')
            elif 'pair' in table_text or 'split' in table_text:
                strategy_data['pairs'] = parse_strategy_table(table, 'pairs')
        
        return strategy_data
        
    except Exception as e:
        print(f"Error scraping strategy charts: {e}")
        return {}

def parse_strategy_table(table, chart_type):
    """
    Parse a strategy table from HTML
    """
    strategy = {}
    
    try:
        rows = table.find_all('tr')
        
        # Get header row (dealer upcards)
        header_row = rows[0] if rows else None
        dealer_cards = []
        
        if header_row:
            headers = header_row.find_all(['th', 'td'])
            for header in headers[1:]:  # Skip first column (player hands)
                dealer_card = header.get_text().strip()
                if dealer_card in ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']:
                    dealer_cards.append(dealer_card)
        
        # Parse data rows
        for row in rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                continue
                
            player_hand = cells[0].get_text().strip()
            
            # Extract numeric value from player hand
            if chart_type == 'hard':
                try:
                    player_total = int(player_hand)
                    strategy[player_total] = {}
                except:
                    continue
            elif chart_type == 'soft':
                # Soft hands like "A,2" or "A2" 
                if 'A' in player_hand or 'a' in player_hand:
                    try:
                        # Extract the non-ace card value
                        num_part = re.findall(r'\d+', player_hand)
                        if num_part:
                            soft_total = int(num_part[0]) + 11  # Ace + other card
                            strategy[soft_total] = {}
                            player_total = soft_total
                        else:
                            continue
                    except:
                        continue
                else:
                    continue
            elif chart_type == 'pairs':
                # Pairs like "2,2" or "A,A"
                if ',' in player_hand or 'pair' in player_hand.lower():
                    try:
                        if 'A' in player_hand:
                            player_total = 11  # Ace pair
                        else:
                            pair_value = re.findall(r'\d+', player_hand)
                            if pair_value:
                                player_total = int(pair_value[0])
                            else:
                                continue
                        strategy[player_total] = {}
                    except:
                        continue
                else:
                    continue
            
            # Parse actions for each dealer upcard
            for i, dealer_card in enumerate(dealer_cards):
                if i + 1 < len(cells):
                    action_cell = cells[i + 1].get_text().strip().upper()
                    
                    # Map common abbreviations to full actions
                    action_map = {
                        'H': 'hit',
                        'S': 'stand', 
                        'D': 'double',
                        'DS': 'double',  # Double if allowed, otherwise stand
                        'DH': 'double',  # Double if allowed, otherwise hit
                        'P': 'split',
                        'SP': 'split',
                        'Y': 'split',
                        'N': 'stand',
                        'HIT': 'hit',
                        'STAND': 'stand',
                        'DOUBLE': 'double',
                        'SPLIT': 'split'
                    }
                    
                    action = action_map.get(action_cell, action_cell.lower())
                    
                    # Convert dealer card to numeric (A = 11)
                    dealer_value = 11 if dealer_card == 'A' else int(dealer_card)
                    
                    if player_total in strategy:
                        strategy[player_total][dealer_value] = action
    
    except Exception as e:
        print(f"Error parsing strategy table: {e}")
    
    return strategy