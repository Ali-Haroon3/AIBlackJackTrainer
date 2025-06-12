from typing import Dict, List, Tuple

class BasicStrategy:
    def __init__(self):
        # Hard totals strategy (player total, dealer upcard) -> action
        self.hard_strategy = {
            # Player 5-8: Always hit
            5: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            6: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            7: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            8: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # Player 9: Double vs 3-6, otherwise hit
            9: {2: 'hit', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # Player 10: Double vs 2-9, hit vs 10/A
            10: {2: 'double', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'double', 8: 'double', 9: 'double', 10: 'hit', 11: 'hit'},
            
            # Player 11: Double vs 2-10, hit vs A
            11: {2: 'double', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'double', 8: 'double', 9: 'double', 10: 'double', 11: 'hit'},
            
            # Player 12: Stand vs 4-6, hit otherwise
            12: {2: 'hit', 3: 'hit', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # Player 13-16: Stand vs 2-6, hit vs 7-A
            13: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            14: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            15: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            16: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # Player 17-21: Always stand
            17: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            18: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            19: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            20: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            21: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
        }
        
        # Soft totals strategy (A,2 = 13, A,3 = 14, etc.)
        self.soft_strategy = {
            # A,2 (soft 13): Double vs 5-6, otherwise hit
            13: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # A,3 (soft 14): Double vs 5-6, otherwise hit
            14: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # A,4 (soft 15): Double vs 4-6, otherwise hit
            15: {2: 'hit', 3: 'hit', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # A,5 (soft 16): Double vs 4-6, otherwise hit
            16: {2: 'hit', 3: 'hit', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # A,6 (soft 17): Double vs 3-6, otherwise hit
            17: {2: 'hit', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # A,7 (soft 18): Stand vs 2,7,8; Double vs 3-6; Hit vs 9,10,A
            18: {2: 'stand', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'stand', 8: 'stand', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # A,8 (soft 19): Always stand
            19: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            
            # A,9 (soft 20): Always stand
            20: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            
            # A,10 (soft 21): Always stand
            21: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
        }
        
        # Pair splitting strategy
        self.pair_strategy = {
            # A,A: Always split
            11: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'split', 9: 'split', 10: 'split', 11: 'split'},
            
            # 10,10: Never split
            10: {2: 'stand', 3: 'stand', 4: 'stand', 5: 'stand', 6: 'stand', 7: 'stand', 8: 'stand', 9: 'stand', 10: 'stand', 11: 'stand'},
            
            # 9,9: Split vs 2-9 except 7, stand vs 7,10,A
            9: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'stand', 8: 'split', 9: 'split', 10: 'stand', 11: 'stand'},
            
            # 8,8: Always split
            8: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'split', 9: 'split', 10: 'split', 11: 'split'},
            
            # 7,7: Split vs 2-7, hit vs 8-A
            7: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # 6,6: Split vs 2-6, hit vs 7-A
            6: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # 5,5: Never split (treat as 10)
            5: {2: 'double', 3: 'double', 4: 'double', 5: 'double', 6: 'double', 7: 'double', 8: 'double', 9: 'double', 10: 'hit', 11: 'hit'},
            
            # 4,4: Hit vs all (or split vs 5-6 in some variations)
            4: {2: 'hit', 3: 'hit', 4: 'hit', 5: 'hit', 6: 'hit', 7: 'hit', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # 3,3: Split vs 2-7, hit vs 8-A
            3: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
            
            # 2,2: Split vs 2-7, hit vs 8-A
            2: {2: 'split', 3: 'split', 4: 'split', 5: 'split', 6: 'split', 7: 'split', 8: 'hit', 9: 'hit', 10: 'hit', 11: 'hit'},
        }
    
    def get_hard_action(self, player_total: int, dealer_upcard: int, can_double: bool = True) -> str:
        """Get action for hard totals"""
        if player_total not in self.hard_strategy:
            if player_total < 5:
                return 'hit'
            elif player_total > 21:
                return 'stand'  # Already busted
            else:
                return 'hit'
        
        action = self.hard_strategy[player_total].get(dealer_upcard, 'hit')
        
        # If can't double, convert double to hit
        if action == 'double' and not can_double:
            return 'hit'
        
        return action
    
    def get_soft_action(self, player_total: int, dealer_upcard: int, can_double: bool = True) -> str:
        """Get action for soft totals"""
        if player_total not in self.soft_strategy:
            if player_total < 13:
                return 'hit'
            elif player_total > 21:
                return 'stand'
            else:
                return 'stand'
        
        action = self.soft_strategy[player_total].get(dealer_upcard, 'hit')
        
        # If can't double, convert double to hit (except soft 18 vs 2,7,8 which becomes stand)
        if action == 'double' and not can_double:
            if player_total == 18 and dealer_upcard in [2, 7, 8]:
                return 'stand'
            else:
                return 'hit'
        
        return action
    
    def get_pair_action(self, pair_value: int, dealer_upcard: int) -> str:
        """Get action for pairs"""
        if pair_value not in self.pair_strategy:
            return 'hit'
        
        return self.pair_strategy[pair_value].get(dealer_upcard, 'hit')
    
    def get_chart_data(self) -> Dict:
        """Get strategy chart data for visualization"""
        # Create matrices for heatmap visualization
        dealer_cards = list(range(2, 12))  # 2-10, A=11
        
        # Hard totals chart
        hard_hands = list(range(5, 22))
        hard_matrix = []
        hard_actions = []
        
        for player_total in hard_hands:
            row_values = []
            row_actions = []
            for dealer_card in dealer_cards:
                action = self.get_hard_action(player_total, dealer_card)
                # Convert action to numeric for heatmap
                action_value = {'hit': 0, 'stand': 1, 'double': 2, 'split': 3}[action]
                row_values.append(action_value)
                row_actions.append(action.upper()[:1])  # H, S, D, P
            hard_matrix.append(row_values)
            hard_actions.append(row_actions)
        
        # Soft totals chart
        soft_hands = list(range(13, 22))
        soft_matrix = []
        soft_actions = []
        
        for player_total in soft_hands:
            row_values = []
            row_actions = []
            for dealer_card in dealer_cards:
                action = self.get_soft_action(player_total, dealer_card)
                action_value = {'hit': 0, 'stand': 1, 'double': 2, 'split': 3}[action]
                row_values.append(action_value)
                row_actions.append(action.upper()[:1])
            soft_matrix.append(row_values)
            soft_actions.append(row_actions)
        
        # Pairs chart
        pair_values = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        pair_matrix = []
        pair_actions = []
        
        for pair_value in pair_values:
            row_values = []
            row_actions = []
            for dealer_card in dealer_cards:
                action = self.get_pair_action(pair_value, dealer_card)
                action_value = {'hit': 0, 'stand': 1, 'double': 2, 'split': 3}[action]
                row_values.append(action_value)
                row_actions.append(action.upper()[:1])
            pair_matrix.append(row_values)
            pair_actions.append(row_actions)
        
        return {
            'values': hard_matrix,
            'actions': hard_actions,
            'dealer_cards': ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A'],
            'player_hands': [str(x) for x in hard_hands],
            'soft_values': soft_matrix,
            'soft_actions': soft_actions,
            'soft_hands': [f"A,{x-11}" for x in soft_hands],
            'pair_values': pair_matrix,
            'pair_actions': pair_actions,
            'pair_hands': [f"{x},{x}" for x in pair_values]
        }
    
    def get_action_explanation(self, player_total: int, dealer_upcard: int, 
                              is_soft: bool = False, is_pair: bool = False) -> str:
        """Get explanation for recommended action"""
        if is_pair:
            pair_value = player_total // 2
            action = self.get_pair_action(pair_value, dealer_upcard)
            
            if action == 'split':
                return f"Split {pair_value}s: Mathematically favorable to play two separate hands"
            elif action == 'stand':
                return f"Don't split {pair_value}s: Better to keep the strong total of {player_total}"
            else:
                return f"Don't split {pair_value}s: Treat as regular hand and {action}"
        
        elif is_soft:
            action = self.get_soft_action(player_total, dealer_upcard)
            
            if action == 'double':
                return f"Double soft {player_total}: Take advantage of dealer's weak upcard"
            elif action == 'hit':
                return f"Hit soft {player_total}: Cannot bust and dealer has advantage"
            else:
                return f"Stand on soft {player_total}: Good total against dealer {dealer_upcard}"
        
        else:
            action = self.get_hard_action(player_total, dealer_upcard)
            
            if action == 'hit':
                if player_total <= 11:
                    return f"Hit {player_total}: Cannot bust, must improve hand"
                else:
                    return f"Hit {player_total}: Dealer likely to make strong hand"
            elif action == 'stand':
                if dealer_upcard <= 6:
                    return f"Stand on {player_total}: Let dealer bust with weak upcard"
                else:
                    return f"Stand on {player_total}: Strong enough total"
            elif action == 'double':
                return f"Double on {player_total}: Favorable situation for extra bet"
        
        return f"Recommended action: {action}"
