import random
import numpy as np
from typing import List, Dict, Tuple, Optional

class Card:
    def __init__(self, suit: str, rank: str):
        self.suit = suit
        self.rank = rank
    
    def __str__(self):
        return f"{self.rank}{self.suit[0]}"
    
    def get_value(self) -> int:
        """Get the blackjack value of the card"""
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11  # Aces are handled separately
        else:
            return int(self.rank)

class Deck:
    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self.cards = []
        self.dealt_cards = []
        self.reset()
    
    def reset(self):
        """Create a fresh deck"""
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        self.cards = []
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.cards.append(Card(suit, rank))
        
        self.shuffle()
        self.dealt_cards = []
    
    def shuffle(self):
        """Shuffle the deck"""
        random.shuffle(self.cards)
    
    def deal_card(self) -> Card:
        """Deal one card from the deck"""
        if len(self.cards) < 20:  # Reshuffle when running low
            self.reset()
        
        card = self.cards.pop()
        self.dealt_cards.append(card)
        return card
    
    def get_penetration(self) -> float:
        """Calculate deck penetration"""
        total_cards = 52 * self.num_decks
        return len(self.dealt_cards) / total_cards

class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.bet = 0
        self.is_split = False
        self.is_doubled = False
        self.is_surrender = False
    
    def add_card(self, card: Card):
        """Add a card to the hand"""
        self.cards.append(card)
    
    def get_value(self) -> int:
        """Calculate the best value of the hand"""
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                total += 11
            else:
                total += card.get_value()
        
        # Adjust for aces
        while total > 21 and aces > 0:
            total -= 10
            aces -= 1
        
        return total
    
    def is_soft(self) -> bool:
        """Check if hand is soft (contains usable ace)"""
        total = 0
        aces = 0
        
        for card in self.cards:
            if card.rank == 'A':
                aces += 1
                total += 11
            else:
                total += card.get_value()
        
        return aces > 0 and total <= 21
    
    def is_busted(self) -> bool:
        """Check if hand is busted"""
        return self.get_value() > 21
    
    def is_blackjack(self) -> bool:
        """Check if hand is blackjack"""
        return len(self.cards) == 2 and self.get_value() == 21
    
    def can_split(self) -> bool:
        """Check if hand can be split"""
        return len(self.cards) == 2 and self.cards[0].get_value() == self.cards[1].get_value()
    
    def __str__(self):
        return ' '.join([str(card) for card in self.cards])

class BlackjackGame:
    def __init__(self, num_decks: int = 6):
        self.deck = Deck(num_decks)
        self.player_hands: List[Hand] = []
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        self.game_active = False
        self.hand_complete = False
        self.current_bet = 0
        
        # Statistics tracking
        self.hands_played = 0
        self.hands_won = 0
        self.total_wagered = 0
        self.total_winnings = 0
        self.session_history = []
    
    def new_hand(self, bet_amount: int):
        """Start a new hand"""
        self.current_bet = bet_amount
        self.player_hands = [Hand()]
        self.dealer_hand = Hand()
        self.current_hand_index = 0
        self.game_active = True
        self.hand_complete = False
        
        # Deal initial cards
        self.player_hands[0].add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())
        self.player_hands[0].add_card(self.deck.deal_card())
        self.dealer_hand.add_card(self.deck.deal_card())
        
        self.player_hands[0].bet = bet_amount
        
        # Check for blackjacks
        if self.player_hands[0].is_blackjack():
            if self.dealer_hand.is_blackjack():
                self.hand_complete = True
            else:
                self.hand_complete = True
    
    def player_hit(self):
        """Player hits"""
        if not self.can_player_act():
            return
        
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.add_card(self.deck.deal_card())
        
        if current_hand.is_busted():
            self._next_hand_or_dealer()
    
    def player_stand(self):
        """Player stands"""
        if not self.can_player_act():
            return
        
        self._next_hand_or_dealer()
    
    def double_down(self):
        """Player doubles down"""
        if not self.can_double_down():
            return
        
        current_hand = self.player_hands[self.current_hand_index]
        current_hand.bet *= 2
        current_hand.is_doubled = True
        current_hand.add_card(self.deck.deal_card())
        
        self._next_hand_or_dealer()
    
    def split_hand(self):
        """Split the current hand"""
        if not self.can_split():
            return
        
        current_hand = self.player_hands[self.current_hand_index]
        
        # Create new hand with second card
        new_hand = Hand()
        new_hand.add_card(current_hand.cards.pop())
        new_hand.bet = current_hand.bet
        new_hand.is_split = True
        
        # Add cards to both hands
        current_hand.add_card(self.deck.deal_card())
        new_hand.add_card(self.deck.deal_card())
        
        # Insert new hand after current hand
        self.player_hands.insert(self.current_hand_index + 1, new_hand)
    
    def _next_hand_or_dealer(self):
        """Move to next hand or dealer turn"""
        self.current_hand_index += 1
        
        if self.current_hand_index >= len(self.player_hands):
            self._dealer_turn()
        
    def _dealer_turn(self):
        """Dealer plays their hand"""
        # Dealer hits on soft 17
        while self.dealer_hand.get_value() < 17 or (
            self.dealer_hand.get_value() == 17 and self.dealer_hand.is_soft()
        ):
            self.dealer_hand.add_card(self.deck.deal_card())
        
        self.hand_complete = True
        self._update_statistics()
    
    def can_player_act(self) -> bool:
        """Check if player can take action"""
        if not self.game_active or self.hand_complete:
            return False
        
        if self.current_hand_index >= len(self.player_hands):
            return False
        
        current_hand = self.player_hands[self.current_hand_index]
        return not current_hand.is_busted() and not current_hand.is_blackjack()
    
    def can_double_down(self) -> bool:
        """Check if player can double down"""
        if not self.can_player_act():
            return False
        
        current_hand = self.player_hands[self.current_hand_index]
        return len(current_hand.cards) == 2
    
    def can_split(self) -> bool:
        """Check if player can split"""
        if not self.can_player_act():
            return False
        
        current_hand = self.player_hands[self.current_hand_index]
        return current_hand.can_split() and len(self.player_hands) < 4
    
    def get_hand_result(self) -> Dict:
        """Get the result of the completed hand"""
        if not self.hand_complete:
            return {}
        
        results = []
        total_payout = 0
        
        for hand in self.player_hands:
            result = self._evaluate_hand(hand)
            results.append(result)
            total_payout += result['payout']
        
        overall_win = total_payout > 0
        
        return {
            'win': overall_win,
            'payout': total_payout,
            'message': self._get_result_message(results),
            'individual_results': results
        }
    
    def _evaluate_hand(self, hand: Hand) -> Dict:
        """Evaluate a single hand against dealer"""
        player_value = hand.get_value()
        dealer_value = self.dealer_hand.get_value()
        
        # Player busted
        if player_value > 21:
            return {
                'result': 'lose',
                'payout': 0,
                'reason': 'Player busted'
            }
        
        # Player blackjack
        if hand.is_blackjack():
            if self.dealer_hand.is_blackjack():
                return {
                    'result': 'push',
                    'payout': hand.bet,
                    'reason': 'Both blackjack'
                }
            else:
                return {
                    'result': 'blackjack',
                    'payout': hand.bet + int(hand.bet * 1.5),
                    'reason': 'Player blackjack'
                }
        
        # Dealer busted
        if dealer_value > 21:
            return {
                'result': 'win',
                'payout': hand.bet * 2,
                'reason': 'Dealer busted'
            }
        
        # Compare values
        if player_value > dealer_value:
            return {
                'result': 'win',
                'payout': hand.bet * 2,
                'reason': f'Player {player_value} beats dealer {dealer_value}'
            }
        elif player_value < dealer_value:
            return {
                'result': 'lose',
                'payout': 0,
                'reason': f'Dealer {dealer_value} beats player {player_value}'
            }
        else:
            return {
                'result': 'push',
                'payout': hand.bet,
                'reason': f'Push at {player_value}'
            }
    
    def _get_result_message(self, results: List[Dict]) -> str:
        """Generate result message"""
        if len(results) == 1:
            return results[0]['reason']
        
        messages = []
        for i, result in enumerate(results, 1):
            messages.append(f"Hand {i}: {result['reason']}")
        
        return "; ".join(messages)
    
    def _update_statistics(self):
        """Update game statistics"""
        self.hands_played += 1
        self.total_wagered += sum(hand.bet for hand in self.player_hands)
        
        result = self.get_hand_result()
        if result['win']:
            self.hands_won += 1
        
        self.total_winnings += result['payout'] - sum(hand.bet for hand in self.player_hands)
        
        # Store hand history
        self.session_history.append({
            'hand_number': self.hands_played,
            'bet': sum(hand.bet for hand in self.player_hands),
            'result': result,
            'player_hands': [str(hand) for hand in self.player_hands],
            'dealer_hand': str(self.dealer_hand),
            'deck_penetration': self.deck.get_penetration()
        })
    
    def get_session_stats(self) -> Dict:
        """Get current session statistics"""
        if self.hands_played == 0:
            return {
                'hands_played': 0,
                'win_rate': 0.0,
                'net_winnings': 0,
                'house_edge': 0.0
            }
        
        win_rate = self.hands_won / self.hands_played
        house_edge = -self.total_winnings / self.total_wagered if self.total_wagered > 0 else 0
        
        return {
            'hands_played': self.hands_played,
            'win_rate': win_rate,
            'net_winnings': self.total_winnings,
            'house_edge': house_edge
        }
    
    def reset_hand(self):
        """Reset for next hand"""
        self.game_active = False
        self.hand_complete = False
        self.current_hand_index = 0
    
    def get_player_display(self) -> Dict:
        """Get player hand display info"""
        if not self.player_hands:
            return {'cards': '', 'value': 0}
        
        current_hand = self.player_hands[self.current_hand_index] if self.current_hand_index < len(self.player_hands) else self.player_hands[0]
        return {
            'cards': str(current_hand),
            'value': current_hand.get_value()
        }
    
    def get_dealer_display(self) -> Dict:
        """Get dealer hand display info"""
        if self.hand_complete:
            return {
                'cards': str(self.dealer_hand),
                'value': self.dealer_hand.get_value()
            }
        else:
            # Hide hole card
            visible_cards = [str(self.dealer_hand.cards[0]), '??']
            return {
                'cards': ' '.join(visible_cards),
                'value': '?'
            }
    
    @property
    def player_hand(self) -> List[Hand]:
        """Get current player hands"""
        return self.player_hands
    
    @property
    def dealer_hand_cards(self) -> Hand:
        """Get dealer hand"""
        return self.dealer_hand
    
    @property
    def dealt_cards(self) -> List[Card]:
        """Get all dealt cards for counting"""
        return self.deck.dealt_cards
    
    @property
    def cards_dealt(self) -> int:
        """Get number of cards dealt"""
        return len(self.deck.dealt_cards)
