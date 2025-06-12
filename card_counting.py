from typing import Dict, List, Tuple
import numpy as np

class CardCounter:
    def __init__(self):
        # Different counting systems
        self.counting_systems = {
            'Hi-Lo': {
                2: 1, 3: 1, 4: 1, 5: 1, 6: 1,
                7: 0, 8: 0, 9: 0,
                10: -1, 11: -1  # J, Q, K, A
            },
            'Hi-Opt I': {
                2: 0, 3: 1, 4: 1, 5: 1, 6: 1,
                7: 0, 8: 0, 9: 0,
                10: -1, 11: 0  # A is neutral
            },
            'Hi-Opt II': {
                2: 1, 3: 1, 4: 2, 5: 2, 6: 1,
                7: 1, 8: 0, 9: 0,
                10: -2, 11: 0
            },
            'Omega II': {
                2: 1, 3: 1, 4: 2, 5: 2, 6: 2,
                7: 1, 8: 0, 9: -1,
                10: -2, 11: 0
            },
            'Red 7': {
                2: 1, 3: 1, 4: 1, 5: 1, 6: 1,
                7: 1, 8: 0, 9: 0,  # Red 7s count as +1
                10: -1, 11: -1
            }
        }
        
        self.running_count = 0
        self.cards_seen = 0
        self.current_system = 'Hi-Lo'
    
    def reset_count(self):
        """Reset the running count"""
        self.running_count = 0
        self.cards_seen = 0
    
    def count_card(self, card, system: str = 'Hi-Lo'):
        """Count a single card"""
        card_value = card.get_value() if hasattr(card, 'get_value') else card
        
        # Convert face cards to 10, Ace to 11
        if card_value > 10:
            card_value = 10
        
        count_value = self.counting_systems[system].get(card_value, 0)
        self.running_count += count_value
        self.cards_seen += 1
        
        return count_value
    
    def count_cards(self, cards: List, system: str = 'Hi-Lo') -> int:
        """Count multiple cards and return total count change"""
        total_count_change = 0
        for card in cards:
            count_change = self.count_card(card, system)
            total_count_change += count_change
        
        return total_count_change
    
    def get_true_count(self, num_decks: int = 6) -> float:
        """Calculate true count"""
        decks_remaining = max(0.5, (52 * num_decks - self.cards_seen) / 52)
        return self.running_count / decks_remaining
    
    def get_count_info(self, dealt_cards: List, num_decks: int = 6) -> Dict:
        """Get comprehensive count information"""
        # Reset and recount all dealt cards
        temp_running_count = 0
        
        for card in dealt_cards:
            card_value = card.get_value() if hasattr(card, 'get_value') else card
            if card_value > 10:
                card_value = 10
            
            count_value = self.counting_systems[self.current_system].get(card_value, 0)
            temp_running_count += count_value
        
        # Calculate true count
        cards_seen = len(dealt_cards)
        decks_remaining = max(0.5, (52 * num_decks - cards_seen) / 52)
        true_count = temp_running_count / decks_remaining
        
        # Calculate penetration
        total_cards = 52 * num_decks
        penetration = cards_seen / total_cards
        
        # Determine betting recommendation
        betting_recommendation = self._get_betting_recommendation(true_count)
        
        return {
            'running_count': temp_running_count,
            'true_count': true_count,
            'cards_seen': cards_seen,
            'decks_remaining': decks_remaining,
            'penetration': penetration,
            'system': self.current_system,
            'betting_recommendation': betting_recommendation,
            'advantage_estimate': self._estimate_player_advantage(true_count)
        }
    
    def _get_betting_recommendation(self, true_count: float) -> Dict:
        """Get betting recommendation based on true count"""
        if true_count <= -1:
            return {
                'multiplier': 0.5,
                'description': 'Minimum bet - deck favors dealer'
            }
        elif true_count < 1:
            return {
                'multiplier': 1.0,
                'description': 'Base bet - neutral deck'
            }
        elif true_count < 2:
            return {
                'multiplier': 2.0,
                'description': 'Double bet - slight player advantage'
            }
        elif true_count < 3:
            return {
                'multiplier': 3.0,
                'description': 'Triple bet - good player advantage'
            }
        elif true_count < 4:
            return {
                'multiplier': 4.0,
                'description': 'Quadruple bet - strong player advantage'
            }
        else:
            return {
                'multiplier': 5.0,
                'description': 'Maximum bet - very strong player advantage'
            }
    
    def _estimate_player_advantage(self, true_count: float) -> float:
        """Estimate player advantage based on true count"""
        # Each point of true count is approximately 0.5% advantage
        base_house_edge = 0.005  # 0.5% house edge with basic strategy
        return (true_count * 0.005) - base_house_edge
    
    def get_count_values(self, system: str) -> Dict:
        """Get card values for a specific counting system"""
        if system not in self.counting_systems:
            system = 'Hi-Lo'
        
        system_values = self.counting_systems[system].copy()
        
        # Convert to more readable format
        readable_values = {}
        for value, count in system_values.items():
            if value == 11:
                readable_values['A'] = count
            elif value == 10:
                readable_values['10/J/Q/K'] = count
            else:
                readable_values[str(value)] = count
        
        return readable_values
    
    def get_deviation_recommendations(self, player_total: int, dealer_upcard: int, 
                                    true_count: float, system: str = 'Hi-Lo') -> Dict:
        """Get playing deviation recommendations based on count"""
        deviations = self._get_system_deviations(system)
        
        situation_key = (player_total, dealer_upcard)
        
        if situation_key in deviations:
            deviation = deviations[situation_key]
            
            if true_count >= deviation['threshold']:
                return {
                    'recommended_action': deviation['deviation_action'],
                    'basic_strategy_action': deviation['basic_action'],
                    'reason': f"True count {true_count:.1f} exceeds threshold of {deviation['threshold']:+.1f}",
                    'expected_value_gain': deviation.get('ev_gain', 0),
                    'deviation_applies': True
                }
        
        return {
            'deviation_applies': False,
            'reason': 'No deviation applies for this count'
        }
    
    def _get_system_deviations(self, system: str) -> Dict:
        """Get playing deviations for counting system"""
        # Common Hi-Lo deviations (situation: (player_total, dealer_upcard))
        hi_lo_deviations = {
            (16, 10): {
                'basic_action': 'hit',
                'deviation_action': 'stand',
                'threshold': 0,
                'ev_gain': 0.054
            },
            (15, 10): {
                'basic_action': 'hit',
                'deviation_action': 'stand',
                'threshold': 4,
                'ev_gain': 0.021
            },
            (13, 2): {
                'basic_action': 'hit',
                'deviation_action': 'stand',
                'threshold': -1,
                'ev_gain': 0.013
            },
            (13, 3): {
                'basic_action': 'hit',
                'deviation_action': 'stand',
                'threshold': -2,
                'ev_gain': 0.015
            },
            (12, 2): {
                'basic_action': 'hit',
                'deviation_action': 'stand',
                'threshold': 3,
                'ev_gain': 0.018
            },
            (12, 3): {
                'basic_action': 'hit',
                'deviation_action': 'stand',
                'threshold': 2,
                'ev_gain': 0.026
            },
            (12, 4): {
                'basic_action': 'stand',
                'deviation_action': 'hit',
                'threshold': -1,
                'ev_gain': 0.012
            },
            (10, 10): {
                'basic_action': 'hit',
                'deviation_action': 'double',
                'threshold': 4,
                'ev_gain': 0.031
            },
            (10, 9): {
                'basic_action': 'hit',
                'deviation_action': 'double',
                'threshold': 1,
                'ev_gain': 0.025
            },
            (9, 2): {
                'basic_action': 'hit',
                'deviation_action': 'double',
                'threshold': 1,
                'ev_gain': 0.019
            },
            (9, 7): {
                'basic_action': 'hit',
                'deviation_action': 'double',
                'threshold': 3,
                'ev_gain': 0.015
            }
        }
        
        # For other systems, use Hi-Lo as base with adjustments
        if system == 'Hi-Lo':
            return hi_lo_deviations
        else:
            # For other systems, adjust thresholds based on system efficiency
            adjusted_deviations = {}
            efficiency_multiplier = self._get_system_efficiency_multiplier(system)
            
            for situation, deviation in hi_lo_deviations.items():
                adjusted_deviation = deviation.copy()
                adjusted_deviation['threshold'] *= efficiency_multiplier
                adjusted_deviations[situation] = adjusted_deviation
            
            return adjusted_deviations
    
    def _get_system_efficiency_multiplier(self, system: str) -> float:
        """Get efficiency multiplier for different counting systems"""
        efficiency_ratings = {
            'Hi-Lo': 1.0,
            'Hi-Opt I': 1.08,
            'Hi-Opt II': 1.15,
            'Omega II': 1.20,
            'Red 7': 0.95
        }
        
        return efficiency_ratings.get(system, 1.0)
    
    def get_insurance_recommendation(self, true_count: float) -> Dict:
        """Get insurance bet recommendation"""
        # Insurance is profitable when true count is +3 or higher
        insurance_threshold = 3
        
        if true_count >= insurance_threshold:
            return {
                'take_insurance': True,
                'reason': f'True count {true_count:.1f} makes insurance profitable',
                'expected_value': (true_count - 2) * 0.025  # Approximate EV per unit bet
            }
        else:
            return {
                'take_insurance': False,
                'reason': f'True count {true_count:.1f} below profitable threshold of +{insurance_threshold}',
                'expected_value': (true_count - 2) * 0.025
            }
    
    def get_surrender_recommendations(self, player_total: int, dealer_upcard: int, 
                                    true_count: float) -> Dict:
        """Get surrender recommendations based on count"""
        surrender_situations = {
            (15, 10): -1,  # Surrender 15 vs 10 when TC <= -1
            (15, 9): 2,    # Surrender 15 vs 9 when TC >= +2
            (14, 10): 3,   # Surrender 14 vs 10 when TC >= +3
            (16, 9): -1,   # Surrender 16 vs 9 when TC <= -1
            (16, 10): -1,  # Surrender 16 vs 10 when TC <= -1 (some variations)
            (16, 11): -1   # Surrender 16 vs A when TC <= -1
        }
        
        situation_key = (player_total, dealer_upcard)
        
        if situation_key in surrender_situations:
            threshold = surrender_situations[situation_key]
            
            if (threshold > 0 and true_count >= threshold) or \
               (threshold < 0 and true_count <= threshold):
                return {
                    'surrender': True,
                    'reason': f'Count-based surrender: TC {true_count:.1f}',
                    'threshold': threshold
                }
        
        return {
            'surrender': False,
            'reason': 'No count-based surrender recommendation'
        }
    
    def simulate_count_accuracy(self, num_hands: int = 100) -> Dict:
        """Simulate counting accuracy over multiple hands"""
        results = {
            'hands_simulated': num_hands,
            'perfect_count_hands': 0,
            'average_error': 0,
            'max_error': 0,
            'accuracy_by_penetration': {}
        }
        
        total_error = 0
        max_error = 0
        perfect_hands = 0
        
        # Simulate hands with different penetration levels
        for penetration in [0.25, 0.5, 0.75]:
            cards_dealt = int(52 * 6 * penetration)  # 6-deck game
            
            # Simulate random card distribution
            cards = []
            for _ in range(cards_dealt):
                card_value = np.random.choice([2,3,4,5,6,7,8,9,10,10,10,10,11])
                cards.append(card_value)
            
            # Calculate perfect count
            perfect_count = sum(self.counting_systems['Hi-Lo'].get(card, 0) for card in cards)
            
            # Simulate player counting with errors
            player_count = perfect_count + np.random.randint(-2, 3)  # Random error
            
            error = abs(perfect_count - player_count)
            total_error += error
            max_error = max(max_error, error)
            
            if error == 0:
                perfect_hands += 1
            
            results['accuracy_by_penetration'][f'{penetration:.0%}'] = {
                'perfect_count': perfect_count,
                'typical_error': np.random.randint(0, 3),
                'accuracy_rate': max(0.6, 1.0 - (penetration * 0.4))  # Accuracy decreases with penetration
            }
        
        results['perfect_count_hands'] = perfect_hands
        results['average_error'] = total_error / len(results['accuracy_by_penetration'])
        results['max_error'] = max_error
        
        return results
