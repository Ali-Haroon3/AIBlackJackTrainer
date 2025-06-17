"""
Simplified Complete Blackjack Training Application
Removes PostgreSQL dependencies while maintaining all core functionality
"""

import os
import json
import uuid
import random
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'blackjack-training-simple'
CORS(app)

# Simple implementations without external dependencies
class SimpleCard:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
    
    def get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)
    
    def get_count_value(self, system='Hi-Lo'):
        if system == 'Hi-Lo':
            if self.rank in ['2', '3', '4', '5', '6']:
                return 1
            elif self.rank in ['10', 'J', 'Q', 'K', 'A']:
                return -1
        return 0
    
    def to_dict(self):
        return {'suit': self.suit, 'rank': self.rank}

class SimpleDeck:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.cards = []
        self.dealt_cards = 0
        self.reset()
    
    def reset(self):
        suits = ['hearts', 'diamonds', 'clubs', 'spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        self.cards = []
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(SimpleCard(suit, rank))
        
        random.shuffle(self.cards)
        self.dealt_cards = 0
    
    def deal_card(self):
        if len(self.cards) - self.dealt_cards < 20:  # Reshuffle when low
            self.reset()
        
        card = self.cards[self.dealt_cards]
        self.dealt_cards += 1
        return card
    
    def get_penetration(self):
        return round((self.dealt_cards / len(self.cards)) * 100, 1)

class SimpleHand:
    def __init__(self):
        self.cards = []
        self.bet = 0
        self.is_doubled = False
        self.is_split = False
    
    def add_card(self, card):
        self.cards.append(card)
    
    def get_value(self):
        total = 0
        aces = 0
        
        for card in self.cards:
            value = card.get_value()
            if value == 11:
                aces += 1
            total += value
        
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_soft(self):
        total = 0
        aces = 0
        
        for card in self.cards:
            value = card.get_value()
            if value == 11:
                aces += 1
            total += value
        
        return total <= 21 and aces > 0 and any(card.rank == 'A' for card in self.cards)
    
    def is_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21
    
    def is_bust(self):
        return self.get_value() > 21
    
    def can_split(self):
        return len(self.cards) == 2 and self.cards[0].get_value() == self.cards[1].get_value()
    
    def can_double(self):
        return len(self.cards) == 2
    
    def to_dict(self):
        return {
            'cards': [card.to_dict() for card in self.cards],
            'value': self.get_value(),
            'bet': self.bet,
            'is_soft': self.is_soft(),
            'is_blackjack': self.is_blackjack(),
            'is_bust': self.is_bust(),
            'can_split': self.can_split(),
            'can_double': self.can_double(),
            'is_doubled': self.is_doubled
        }

class SimpleGameSession:
    def __init__(self, starting_bankroll=1000):
        self.session_id = str(uuid.uuid4())
        self.deck = SimpleDeck()
        self.player_hands = [SimpleHand()]
        self.dealer_hand = SimpleHand()
        self.current_hand = 0
        self.game_phase = 'betting'  # betting, playing, complete
        self.current_bankroll = starting_bankroll
        self.running_count = 0
        self.hands_played = 0
        self.session_profit = 0
        self.stats = {
            'hands_won': 0,
            'hands_lost': 0,
            'hands_pushed': 0,
            'blackjacks': 0,
            'doubles_won': 0,
            'splits_won': 0,
            'total_wagered': 0,
            'decisions': []
        }
    
    def update_count(self, card):
        count_value = card.get_count_value('Hi-Lo')
        self.running_count += count_value
        return count_value
    
    def get_true_count(self):
        decks_remaining = max(1, 6 - (self.deck.dealt_cards / 52))
        return round(self.running_count / decks_remaining, 1)
    
    def get_betting_recommendation(self):
        true_count = self.get_true_count()
        if true_count >= 2:
            return 50
        elif true_count >= 1:
            return 20
        else:
            return 10
    
    def new_hand(self, bet_amount):
        if self.current_bankroll < bet_amount:
            return False
        
        # Reset for new hand
        self.player_hands = [SimpleHand()]
        self.dealer_hand = SimpleHand()
        self.current_hand = 0
        self.game_phase = 'playing'
        
        # Place bet
        self.player_hands[0].bet = bet_amount
        self.current_bankroll -= bet_amount
        self.stats['total_wagered'] += bet_amount
        
        # Deal initial cards
        for _ in range(2):
            card = self.deck.deal_card()
            self.player_hands[0].add_card(card)
            self.update_count(card)
            
            card = self.deck.deal_card()
            self.dealer_hand.add_card(card)
            self.update_count(card)
        
        # Check for blackjack
        if self.player_hands[0].is_blackjack():
            self.dealer_play()
        
        return True
    
    def player_action(self, action, hand_index=None):
        if self.game_phase != 'playing':
            return False
        
        if hand_index is None:
            hand_index = self.current_hand
        
        current_hand = self.player_hands[hand_index]
        
        if action == 'hit':
            card = self.deck.deal_card()
            current_hand.add_card(card)
            self.update_count(card)
            
            if current_hand.is_bust():
                self._next_hand_or_dealer()
        
        elif action == 'stand':
            self._next_hand_or_dealer()
        
        elif action == 'double' and current_hand.can_double():
            if self.current_bankroll >= current_hand.bet:
                self.current_bankroll -= current_hand.bet
                self.stats['total_wagered'] += current_hand.bet
                current_hand.bet *= 2
                current_hand.is_doubled = True
                
                card = self.deck.deal_card()
                current_hand.add_card(card)
                self.update_count(card)
                
                self._next_hand_or_dealer()
        
        elif action == 'split' and current_hand.can_split():
            if self.current_bankroll >= current_hand.bet and len(self.player_hands) < 4:
                # Create new hand
                new_hand = SimpleHand()
                new_hand.bet = current_hand.bet
                new_hand.add_card(current_hand.cards.pop())
                
                self.current_bankroll -= current_hand.bet
                self.stats['total_wagered'] += current_hand.bet
                
                # Add cards to both hands
                card1 = self.deck.deal_card()
                current_hand.add_card(card1)
                self.update_count(card1)
                
                card2 = self.deck.deal_card()
                new_hand.add_card(card2)
                self.update_count(card2)
                
                self.player_hands.append(new_hand)
        
        return True
    
    def _next_hand_or_dealer(self):
        self.current_hand += 1
        if self.current_hand >= len(self.player_hands):
            self.dealer_play()
    
    def dealer_play(self):
        while self.dealer_hand.get_value() < 17:
            card = self.deck.deal_card()
            self.dealer_hand.add_card(card)
            self.update_count(card)
        
        self._resolve_hands()
        self.game_phase = 'complete'
        self.hands_played += 1
    
    def _resolve_hands(self):
        dealer_value = self.dealer_hand.get_value()
        dealer_blackjack = self.dealer_hand.is_blackjack()
        dealer_bust = self.dealer_hand.is_bust()
        
        for hand in self.player_hands:
            player_value = hand.get_value()
            player_blackjack = hand.is_blackjack()
            player_bust = hand.is_bust()
            
            if player_bust:
                # Player loses, dealer keeps the bet
                self.stats['hands_lost'] += 1
            elif dealer_bust:
                # Dealer busts, player wins
                payout = hand.bet * 2
                self.current_bankroll += payout
                self.session_profit += hand.bet
                self.stats['hands_won'] += 1
                if hand.is_doubled:
                    self.stats['doubles_won'] += 1
            elif player_blackjack and not dealer_blackjack:
                # Player blackjack wins 3:2
                payout = hand.bet + (hand.bet * 1.5)
                self.current_bankroll += payout
                self.session_profit += hand.bet * 1.5
                self.stats['blackjacks'] += 1
                self.stats['hands_won'] += 1
            elif player_value > dealer_value:
                # Player wins
                payout = hand.bet * 2
                self.current_bankroll += payout
                self.session_profit += hand.bet
                self.stats['hands_won'] += 1
                if hand.is_doubled:
                    self.stats['doubles_won'] += 1
            elif player_value == dealer_value:
                # Push - return bet
                self.current_bankroll += hand.bet
                self.stats['hands_pushed'] += 1
            else:
                # Player loses
                self.stats['hands_lost'] += 1
                self.session_profit -= hand.bet
    
    def get_basic_strategy_action(self, hand_index=0):
        if hand_index >= len(self.player_hands):
            return "stand"
        
        hand = self.player_hands[hand_index]
        player_value = hand.get_value()
        dealer_upcard = self.dealer_hand.cards[0].get_value()
        
        # Simple basic strategy
        if player_value < 12:
            return "hit"
        elif player_value >= 17:
            return "stand"
        elif dealer_upcard in [2, 3, 4, 5, 6]:
            return "stand"
        else:
            return "hit"
    
    def get_ai_recommendation(self):
        if self.game_phase != 'playing' or self.current_hand >= len(self.player_hands):
            return None
        
        action = self.get_basic_strategy_action(self.current_hand)
        return {
            "action": action,
            "confidence": 85,
            "reasoning": f"Basic strategy recommends {action}"
        }
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'player_hands': [hand.to_dict() for hand in self.player_hands],
            'dealer_hand': self.dealer_hand.to_dict(),
            'current_hand': self.current_hand,
            'game_phase': self.game_phase,
            'current_bankroll': self.current_bankroll,
            'running_count': self.running_count,
            'true_count': self.get_true_count(),
            'deck_penetration': self.deck.get_penetration(),
            'hands_played': self.hands_played,
            'session_profit': self.session_profit,
            'betting_recommendation': self.get_betting_recommendation(),
            'stats': self.stats
        }

# Global session storage
sessions = {}

@app.route('/')
def home():
    return render_template('complete_app.html')

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"})

@app.route('/api/new_session', methods=['POST'])
def new_session():
    data = request.get_json() or {}
    starting_bankroll = data.get('starting_bankroll', 1000)
    
    session = SimpleGameSession(starting_bankroll)
    sessions[session.session_id] = session
    
    return jsonify({
        'session_id': session.session_id,
        'game_state': session.to_dict()
    })

@app.route('/api/place_bet', methods=['POST'])
def place_bet():
    data = request.get_json()
    session_id = data.get('session_id')
    bet_amount = data.get('bet_amount', 10)
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    success = session.new_hand(bet_amount)
    
    if not success:
        return jsonify({'error': 'Insufficient funds'}), 400
    
    ai_rec = session.get_ai_recommendation()
    
    return jsonify({
        'game_state': session.to_dict(),
        'ai_recommendation': ai_rec
    })

@app.route('/api/player_action', methods=['POST'])
def player_action():
    data = request.get_json()
    session_id = data.get('session_id')
    action = data.get('action')
    hand_index = data.get('hand_index')
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    success = session.player_action(action, hand_index)
    
    if not success:
        return jsonify({'error': 'Invalid action'}), 400
    
    ai_rec = session.get_ai_recommendation()
    
    return jsonify({
        'game_state': session.to_dict(),
        'ai_recommendation': ai_rec
    })

@app.route('/api/strategy_charts')
def get_strategy_charts():
    chart_type = request.args.get('type', 'basic')
    dealer_rules = request.args.get('dealer_rules', 'S17')
    
    # Basic strategy charts based on dealer rules
    if dealer_rules == 'S17':
        basic_chart = {
            'hard_totals': {
                '17': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'S', '8': 'S', '9': 'S', '10': 'S', 'A': 'S'},
                '16': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '15': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '14': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '13': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '12': {'2': 'H', '3': 'H', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '11': {'2': 'D', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'D', '8': 'D', '9': 'D', '10': 'D', 'A': 'H'},
                '10': {'2': 'D', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'D', '8': 'D', '9': 'D', '10': 'H', 'A': 'H'},
                '9': {'2': 'H', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '8': {'2': 'H', '3': 'H', '4': 'H', '5': 'H', '6': 'H', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'}
            },
            'soft_totals': {
                'A,9': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'S', '8': 'S', '9': 'S', '10': 'S', 'A': 'S'},
                'A,8': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'S', '8': 'S', '9': 'S', '10': 'S', 'A': 'S'},
                'A,7': {'2': 'S', '3': 'Ds', '4': 'Ds', '5': 'Ds', '6': 'Ds', '7': 'S', '8': 'S', '9': 'H', '10': 'H', 'A': 'H'},
                'A,6': {'2': 'H', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,5': {'2': 'H', '3': 'H', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,4': {'2': 'H', '3': 'H', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,3': {'2': 'H', '3': 'H', '4': 'H', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,2': {'2': 'H', '3': 'H', '4': 'H', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'}
            },
            'pairs': {
                'A,A': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'Y', '9': 'Y', '10': 'Y', 'A': 'Y'},
                '10,10': {'2': 'N', '3': 'N', '4': 'N', '5': 'N', '6': 'N', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '9,9': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'N', '8': 'Y', '9': 'Y', '10': 'N', 'A': 'N'},
                '8,8': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'Y', '9': 'Y', '10': 'Y', 'A': 'Y'},
                '7,7': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '6,6': {'2': 'Y/N', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '5,5': {'2': 'N', '3': 'N', '4': 'N', '5': 'N', '6': 'N', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '4,4': {'2': 'N', '3': 'N', '4': 'N', '5': 'Y/N', '6': 'Y/N', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '3,3': {'2': 'Y/N', '3': 'Y/N', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '2,2': {'2': 'Y/N', '3': 'Y/N', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'}
            },
            'surrender': {
                '16': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': 'SUR', 'A': 'SUR'},
                '15': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': 'SUR', 'A': ''}
            }
        }
        
        # S17 Deviation chart with true count indices
        deviation_chart = {
            'hard_totals': {
                '16': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '4+', '10': '0+', 'A': ''},
                '15': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '4+', 'A': ''},
                '13': {'2': '-1-', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': ''},
                '12': {'2': '3+', '3': '2+', '4': '0-', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': ''},
                '11': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': '1+'},
                '10': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '4+', 'A': '4+'},
                '9': {'2': '1+', '3': '', '4': '', '5': '', '6': '', '7': '3+', '8': '', '9': '', '10': '', 'A': ''},
                '8': {'2': '', '3': '', '4': '', '5': '', '6': '2+', '7': '', '8': '', '9': '', '10': '', 'A': ''}
            },
            'soft_totals': {
                'A,8': {'2': '', '3': '', '4': '3+', '5': '1+', '6': '1+', '7': '', '8': '', '9': '', '10': '', 'A': ''},
                'A,6': {'2': '1+', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': ''}
            },
            'pairs': {
                '10,10': {'2': '', '3': '', '4': '6+', '5': '5+', '6': '4+', '7': '', '8': '', '9': '', '10': '', 'A': ''}
            },
            'surrender': {
                '16': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '4+', '10': '-1-', 'A': ''},
                '15': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '2+', 'A': '2+'}
            },
            'insurance': {'all': '3+'}
        }
    else:  # H17
        basic_chart = {
            'hard_totals': {
                '17': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'S', '8': 'S', '9': 'S', '10': 'S', 'A': 'S'},
                '16': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '15': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '14': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '13': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '12': {'2': 'H', '3': 'H', '4': 'S', '5': 'S', '6': 'S', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '11': {'2': 'D', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'D', '8': 'D', '9': 'D', '10': 'D', 'A': 'D'},
                '10': {'2': 'D', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'D', '8': 'D', '9': 'D', '10': 'H', 'A': 'H'},
                '9': {'2': 'H', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                '8': {'2': 'H', '3': 'H', '4': 'H', '5': 'H', '6': 'H', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'}
            },
            'soft_totals': {
                'A,9': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'S', '7': 'S', '8': 'S', '9': 'S', '10': 'S', 'A': 'S'},
                'A,8': {'2': 'S', '3': 'S', '4': 'S', '5': 'S', '6': 'Ds', '7': 'S', '8': 'S', '9': 'S', '10': 'S', 'A': 'S'},
                'A,7': {'2': 'Ds', '3': 'Ds', '4': 'Ds', '5': 'Ds', '6': 'Ds', '7': 'S', '8': 'S', '9': 'H', '10': 'H', 'A': 'H'},
                'A,6': {'2': 'H', '3': 'D', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,5': {'2': 'H', '3': 'H', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,4': {'2': 'H', '3': 'H', '4': 'D', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,3': {'2': 'H', '3': 'H', '4': 'H', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'},
                'A,2': {'2': 'H', '3': 'H', '4': 'H', '5': 'D', '6': 'D', '7': 'H', '8': 'H', '9': 'H', '10': 'H', 'A': 'H'}
            },
            'pairs': {
                'A,A': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'Y', '9': 'Y', '10': 'Y', 'A': 'Y'},
                '10,10': {'2': 'N', '3': 'N', '4': 'N', '5': 'N', '6': 'N', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '9,9': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'N', '8': 'Y', '9': 'Y', '10': 'N', 'A': 'N'},
                '8,8': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'Y', '9': 'Y', '10': 'Y', 'A': 'Y'},
                '7,7': {'2': 'Y', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '6,6': {'2': 'Y/N', '3': 'Y', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '5,5': {'2': 'N', '3': 'N', '4': 'N', '5': 'N', '6': 'N', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '4,4': {'2': 'N', '3': 'N', '4': 'N', '5': 'Y/N', '6': 'Y/N', '7': 'N', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '3,3': {'2': 'Y/N', '3': 'Y/N', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'},
                '2,2': {'2': 'Y/N', '3': 'Y/N', '4': 'Y', '5': 'Y', '6': 'Y', '7': 'Y', '8': 'N', '9': 'N', '10': 'N', 'A': 'N'}
            },
            'surrender': {
                '17': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': 'SUR'},
                '16': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': 'SUR', '10': 'SUR', 'A': 'SUR'},
                '15': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': 'SUR', 'A': 'SUR'},
                '8,8': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': 'SUR'}
            }
        }
        
        # H17 Deviation chart
        deviation_chart = {
            'hard_totals': {
                '16': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '4+', '10': '0+', 'A': '3+'},
                '15': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '4+', 'A': '5+'},
                '13': {'2': '-1-', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': ''},
                '12': {'2': '3+', '3': '2+', '4': '0-', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': ''},
                '10': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '4+', 'A': '3+'},
                '9': {'2': '1+', '3': '', '4': '', '5': '', '6': '', '7': '3+', '8': '', '9': '', '10': '', 'A': ''},
                '8': {'2': '', '3': '', '4': '', '5': '', '6': '2+', '7': '', '8': '', '9': '', '10': '', 'A': ''}
            },
            'soft_totals': {
                'A,8': {'2': '', '3': '', '4': '3+', '5': '1+', '6': '0-', '7': '', '8': '', '9': '', '10': '', 'A': ''},
                'A,6': {'2': '1+', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '', 'A': ''}
            },
            'pairs': {
                '10,10': {'2': '', '3': '', '4': '6+', '5': '5+', '6': '4+', '7': '', '8': '', '9': '', '10': '', 'A': ''}
            },
            'surrender': {
                '16': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '4+', '10': '-1-', 'A': ''},
                '15': {'2': '', '3': '', '4': '', '5': '', '6': '', '7': '', '8': '', '9': '', '10': '2+', 'A': '-1+'}
            },
            'insurance': {'all': '3+'}
        }
    
    if chart_type == 'deviations':
        return jsonify({
            'chart_type': chart_type,
            'dealer_rules': dealer_rules,
            'charts': deviation_chart
        })
    else:
        return jsonify({
            'chart_type': chart_type,
            'dealer_rules': dealer_rules,
            'charts': basic_chart
        })

@app.route('/api/analytics')
def get_analytics():
    session_id = request.args.get('session_id')
    
    if session_id not in sessions:
        return jsonify({'error': 'Session not found'}), 404
    
    session = sessions[session_id]
    
    return jsonify({
        'session_summary': {
            'hands_played': session.hands_played,
            'win_rate': round((session.stats['hands_won'] / max(1, session.hands_played)) * 100, 1),
            'session_profit': session.session_profit,
            'total_wagered': session.stats['total_wagered'],
            'blackjacks': session.stats['blackjacks'],
            'current_bankroll': session.current_bankroll
        }
    })

@app.route('/api/monte_carlo', methods=['POST'])
def monte_carlo_simulation():
    data = request.get_json()
    num_hands = data.get('num_hands', 1000)
    betting_strategy = data.get('betting_strategy', 'flat')
    counting_system = data.get('counting_system', 'Hi-Lo')
    
    # Enhanced Monte Carlo simulation with realistic blackjack probabilities
    wins = 0
    losses = 0
    pushes = 0
    blackjacks = 0
    total_profit = 0
    bankroll_history = []
    current_bankroll = 1000
    
    # Realistic blackjack probabilities
    win_prob = 0.423  # Player wins approximately 42.3%
    lose_prob = 0.489  # Player loses approximately 48.9%
    push_prob = 0.088  # Push approximately 8.8%
    blackjack_prob = 0.048  # Blackjack approximately 4.8%
    
    for hand in range(num_hands):
        # Simulate true count for count-based strategies
        true_count = random.uniform(-3, 3)
        
        # Determine bet size based on strategy
        if betting_strategy == 'flat':
            bet = 10
        elif betting_strategy == 'basic_count':
            # Conservative count-based betting (1-4 spread)
            if true_count >= 2:
                bet = 40
            elif true_count >= 1:
                bet = 20
            else:
                bet = 10
        elif betting_strategy == 'aggressive_count':
            # Aggressive count-based betting (1-12 spread)
            if true_count >= 4:
                bet = 120
            elif true_count >= 3:
                bet = 80
            elif true_count >= 2:
                bet = 40
            elif true_count >= 1:
                bet = 20
            else:
                bet = 10
        elif betting_strategy == 'kelly':
            # Kelly Criterion betting (simplified)
            advantage = max(0, true_count * 0.5)  # Rough advantage estimate
            if advantage > 0:
                kelly_fraction = advantage / 2  # Simplified Kelly
                bet = min(100, max(10, int(1000 * kelly_fraction / 100) * 10))
            else:
                bet = 10
        else:
            bet = 10  # Default flat betting
        
        # Simulate hand outcome
        rand = random.random()
        
        if rand < blackjack_prob:
            # Blackjack - pays 3:2
            payout = bet * 1.5
            total_profit += payout
            current_bankroll += payout
            wins += 1
            blackjacks += 1
        elif rand < blackjack_prob + win_prob:
            # Regular win
            total_profit += bet
            current_bankroll += bet
            wins += 1
        elif rand < blackjack_prob + win_prob + push_prob:
            # Push - no money changes hands
            pushes += 1
        else:
            # Loss
            total_profit -= bet
            current_bankroll -= bet
            losses += 1
        
        # Track bankroll every 100 hands
        if hand % 100 == 0:
            bankroll_history.append(current_bankroll)
    
    win_rate = round((wins / num_hands) * 100, 1)
    house_edge = round((-total_profit / (num_hands * 10)) * 100, 2)
    hourly_hands = 80  # Typical hands per hour
    hourly_ev = round((total_profit / num_hands) * hourly_hands, 2)
    
    # Calculate risk of ruin (simplified)
    max_drawdown = max(bankroll_history) - min(bankroll_history) if bankroll_history else 0
    risk_of_ruin = min(100, max(0, (max_drawdown / 1000) * 50))
    
    return jsonify({
        'total_hands': num_hands,
        'wins': wins,
        'losses': losses,
        'pushes': pushes,
        'blackjacks': blackjacks,
        'win_rate': win_rate,
        'net_result': total_profit,
        'house_edge': house_edge,
        'hourly_ev': hourly_ev,
        'risk_of_ruin': round(risk_of_ruin, 1),
        'final_bankroll': current_bankroll,
        'max_drawdown': round(max_drawdown, 2),
        'betting_strategy': betting_strategy,
        'counting_system': counting_system,
        'bankroll_history': bankroll_history[:10]  # First 10 checkpoints
    })

@app.route('/api/card_counting_practice', methods=['POST'])
def card_counting_practice():
    data = request.get_json()
    system = data.get('system', 'Hi-Lo')
    num_cards = data.get('num_cards', 10)
    
    # Generate random cards
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    cards = []
    running_count = 0
    
    for _ in range(num_cards):
        suit = random.choice(suits)
        rank = random.choice(ranks)
        card = SimpleCard(suit, rank)
        cards.append(card.to_dict())
        running_count += card.get_count_value(system)
    
    return jsonify({
        'cards': cards,
        'running_count': running_count,
        'system': system
    })

@app.route('/api/validate_count', methods=['POST'])
def validate_user_count():
    data = request.get_json()
    user_count = data.get('user_count', 0)
    cards_data = data.get('cards', [])
    system = data.get('system', 'Hi-Lo')
    
    # Calculate actual count
    actual_count = 0
    for card_data in cards_data:
        card = SimpleCard(card_data['suit'], card_data['rank'])
        actual_count += card.get_count_value(system)
    
    correct = user_count == actual_count
    accuracy = 100 if correct else 0
    
    return jsonify({
        'correct': correct,
        'user_count': user_count,
        'actual_count': actual_count,
        'accuracy': accuracy
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)