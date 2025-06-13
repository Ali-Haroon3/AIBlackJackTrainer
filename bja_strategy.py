from typing import Dict, List, Tuple

class BJABasicStrategy:
    """
    Exact Basic Strategy implementation based on the BJA (Blackjack Apprenticeship) chart
    """
    def __init__(self):
        # Pair splitting strategy from the BJA chart
        self.pair_strategy = {
            # Format: pair_value: {dealer_upcard: action}
            11: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'split', 9: 'split', 10: 'split', 11: 'split'},  # A,A
            10: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},  # 10,10
            9: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'stand', 8: 'split', 9: 'split', 10: 'stand', 11: 'stand'},   # 9,9
            8: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'split', 9: 'split', 10: 'split', 11: 'split'},   # 8,8
            7: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},         # 7,7
            6: {2: 'split/hit', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},       # 6,6
            5: {2: 'double', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'double', 8: 'double', 9: 'double', 10: 'hit', 11: 'hit'},  # 5,5 (treat as 10)
            4: {2: 'hit', 3: 'hit', 4: 'split/hit', 5: 'split/hit', 6: 'split/hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},    # 4,4
            3: {2: 'split/hit', 3: 'split/hit', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'}, # 3,3
            2: {2: 'split/hit', 3: 'split/hit', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'}, # 2,2
        }
        
        # Soft totals strategy from the BJA chart
        self.soft_strategy = {
            # A,9 (soft 20): Always stand
            20: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            # A,8 (soft 19): Always stand  
            19: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            # A,7 (soft 18): Double vs 3-6, stand vs 2,7,8, hit vs 9,10,A
            18: {2: 'stand', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'stand', 8: 'stand', 9: 'hit', 10: 'hit', 11: 'hit'},
            # A,6 (soft 17): Double vs 3-6, otherwise hit
            17: {2: 'hit', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # A,5 (soft 16): Double vs 4-6, otherwise hit
            16: {2: 'hit', 3: 'hit', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # A,4 (soft 15): Double vs 4-6, otherwise hit
            15: {2: 'hit', 3: 'hit', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # A,3 (soft 14): Double vs 5-6, otherwise hit
            14: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # A,2 (soft 13): Double vs 5-6, otherwise hit
            13: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
        }
        
        # Hard totals strategy from the BJA chart
        self.hard_strategy = {
            # 17-21: Always stand
            17: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            18: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            19: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            20: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            21: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            
            # 16: Stand vs 2-6, hit vs 7-A
            16: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # 15: Stand vs 2-6, hit vs 7-A  
            15: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # 14: Stand vs 2-6, hit vs 7-A
            14: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # 13: Stand vs 2-6, hit vs 7-A
            13: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            # 12: Hit vs 2,3 and 7-A, stand vs 4-6
            12: {2: 'hit', 3: 'hit', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # 11: Double vs all except A
            11: {2: 'double', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'double', 8: 'double', 9: 'double', 10: 'double', 11: 'hit'},
            # 10: Double vs 2-9, hit vs 10,A
            10: {2: 'double', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'double', 8: 'double', 9: 'double', 10: 'hit', 11: 'hit'},
            # 9: Double vs 3-6, otherwise hit
            9: {2: 'hit', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # 5-8: Always hit
            8: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            7: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            6: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            5: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
        }
        
        # Late surrender strategy (if available)
        self.surrender_strategy = {
            16: {9: 'surrender', 10: 'surrender', 11: 'surrender'},  # 16 vs 9,10,A
            15: {10: 'surrender'},  # 15 vs 10 only
        }
    
    def get_action(self, player_total: int, dealer_upcard: int, is_soft: bool = False, 
                   is_pair: bool = False, can_double: bool = True, can_surrender: bool = False) -> str:
        """Get the correct basic strategy action"""
        
        # Handle surrender first (if available)
        if can_surrender and player_total in self.surrender_strategy:
            if dealer_upcard in self.surrender_strategy[player_total]:
                return self.surrender_strategy[player_total][dealer_upcard]
        
        # Handle pairs
        if is_pair:
            pair_value = player_total // 2
            if pair_value in self.pair_strategy and dealer_upcard in self.pair_strategy[pair_value]:
                action = self.pair_strategy[pair_value][dealer_upcard]
                # Handle split/hit recommendations - prefer split if doubling after split allowed
                if action == 'split/hit':
                    return 'split'
                return action
        
        # Handle soft totals
        if is_soft and player_total in self.soft_strategy:
            action = self.soft_strategy[player_total][dealer_upcard]
            # If can't double, hit instead
            if action == 'double' and not can_double:
                return 'hit'
            return action
        
        # Handle hard totals
        if player_total in self.hard_strategy:
            action = self.hard_strategy[player_total][dealer_upcard]
            # If can't double, hit instead
            if action == 'double' and not can_double:
                return 'hit'
            return action
        
        # Default to hit for very low totals
        return 'hit'
    
    def get_chart_data(self) -> Dict:
        """Get strategy chart data for visualization"""
        return {
            'hard_totals': self.hard_strategy,
            'soft_totals': self.soft_strategy,
            'pairs': self.pair_strategy,
            'surrender': self.surrender_strategy
        }