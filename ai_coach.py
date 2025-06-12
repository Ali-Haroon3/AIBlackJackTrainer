import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import os
from strategy_tables import BasicStrategy
from card_counting import CardCounter

class AICoach:
    def __init__(self):
        self.basic_strategy = BasicStrategy()
        self.card_counter = CardCounter()
        self.ml_model = None
        self.training_data = []
        self.performance_history = []
        
        # Load or create ML model
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize or load the ML model"""
        try:
            if os.path.exists('ai_model.pkl'):
                with open('ai_model.pkl', 'rb') as f:
                    self.ml_model = pickle.load(f)
            else:
                self._create_initial_model()
        except:
            self._create_initial_model()
    
    def _create_initial_model(self):
        """Create initial ML model with synthetic training data"""
        # Generate training data based on basic strategy
        X, y = self._generate_training_data()
        
        self.ml_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        if len(X) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.ml_model.fit(X_train, y_train)
            
            # Save model
            try:
                with open('ai_model.pkl', 'wb') as f:
                    pickle.dump(self.ml_model, f)
            except:
                pass  # Continue without saving if there's an error
    
    def _generate_training_data(self) -> Tuple[List, List]:
        """Generate training data from basic strategy and card counting"""
        X = []
        y = []
        
        # Generate scenarios for all possible hands
        for player_total in range(5, 22):
            for dealer_upcard in range(2, 12):  # 2-10, A=11
                for is_soft in [True, False]:
                    for can_double in [True, False]:
                        for can_split in [True, False]:
                            for true_count in [-3, -1, 0, 1, 3]:
                                # Create feature vector
                                features = [
                                    player_total,
                                    dealer_upcard,
                                    int(is_soft),
                                    int(can_double),
                                    int(can_split),
                                    true_count,
                                    abs(true_count),  # Count magnitude
                                    1 if true_count > 0 else 0,  # Positive count
                                ]
                                
                                # Get basic strategy action
                                action = self._get_basic_strategy_action(
                                    player_total, dealer_upcard, is_soft, can_double, can_split
                                )
                                
                                # Modify based on count
                                if true_count != 0:
                                    action = self._adjust_for_count(action, true_count, player_total, dealer_upcard)
                                
                                X.append(features)
                                y.append(self._encode_action(action))
        
        return X, y
    
    def _get_basic_strategy_action(self, player_total: int, dealer_upcard: int, 
                                  is_soft: bool, can_double: bool, can_split: bool) -> str:
        """Get basic strategy action"""
        if can_split and player_total % 2 == 0:
            pair_value = player_total // 2
            if pair_value <= 10:
                return self.basic_strategy.get_pair_action(pair_value, dealer_upcard)
        
        if is_soft:
            return self.basic_strategy.get_soft_action(player_total, dealer_upcard, can_double)
        else:
            return self.basic_strategy.get_hard_action(player_total, dealer_upcard, can_double)
    
    def _adjust_for_count(self, action: str, true_count: float, player_total: int, dealer_upcard: int) -> str:
        """Adjust action based on true count"""
        # Common deviations
        deviations = {
            (16, 10): {'action': 'stand', 'threshold': 0},
            (15, 10): {'action': 'stand', 'threshold': 4},
            (12, 2): {'action': 'stand', 'threshold': 3},
            (12, 3): {'action': 'stand', 'threshold': 2},
            (13, 2): {'action': 'stand', 'threshold': -1},
            (10, 10): {'action': 'double', 'threshold': 4},
            (10, 9): {'action': 'double', 'threshold': 1},
        }
        
        key = (player_total, dealer_upcard)
        if key in deviations:
            deviation = deviations[key]
            if true_count >= deviation['threshold']:
                return deviation['action']
        
        return action
    
    def _encode_action(self, action: str) -> int:
        """Encode action as number"""
        action_map = {
            'hit': 0,
            'stand': 1,
            'double': 2,
            'split': 3,
            'surrender': 4
        }
        return action_map.get(action.lower(), 0)
    
    def _decode_action(self, action_num: int) -> str:
        """Decode action number to string"""
        action_map = {
            0: 'Hit',
            1: 'Stand',
            2: 'Double',
            3: 'Split',
            4: 'Surrender'
        }
        return action_map.get(action_num, 'Hit')
    
    def get_recommendation(self, player_hands: List, dealer_upcard) -> Dict:
        """Get AI recommendation for current situation"""
        if not player_hands:
            return {'action': 'Hit', 'reason': 'No valid hand', 'win_probability': 0.5}
        
        # Use the first/current hand for recommendation
        current_hand = player_hands[0] if isinstance(player_hands, list) else player_hands
        player_total = current_hand.get_value() if hasattr(current_hand, 'get_value') else 17
        dealer_value = dealer_upcard.get_value() if hasattr(dealer_upcard, 'get_value') else 10
        
        # Check if hand is soft
        is_soft = current_hand.is_soft() if hasattr(current_hand, 'is_soft') else False
        can_double = len(current_hand.cards) == 2 if hasattr(current_hand, 'cards') else False
        can_split = current_hand.can_split() if hasattr(current_hand, 'can_split') else False
        
        # Get current count
        true_count = 0  # Will be updated with actual count
        
        # Create feature vector
        features = np.array([[
            player_total,
            dealer_value,
            int(is_soft),
            int(can_double),
            int(can_split),
            true_count,
            abs(true_count),
            1 if true_count > 0 else 0,
        ]])
        
        # Get ML prediction
        if self.ml_model:
            try:
                prediction = self.ml_model.predict(features)[0]
                probabilities = self.ml_model.predict_proba(features)[0]
                action = self._decode_action(prediction)
                confidence = np.max(probabilities)
            except:
                action = 'Hit'
                confidence = 0.5
        else:
            action = 'Hit'
            confidence = 0.5
        
        # Get basic strategy recommendation as fallback
        basic_action = self._get_basic_strategy_action(
            player_total, dealer_value, is_soft, can_double, can_split
        )
        
        # Calculate win probability estimate
        win_probability = self._estimate_win_probability(
            player_total, dealer_value, action, true_count
        )
        
        # Generate reasoning
        reason = self._generate_reasoning(
            action, basic_action, player_total, dealer_value, true_count, confidence
        )
        
        return {
            'action': action,
            'reason': reason,
            'win_probability': win_probability,
            'confidence': confidence,
            'basic_strategy': basic_action
        }
    
    def _estimate_win_probability(self, player_total: int, dealer_value: int, 
                                action: str, true_count: float) -> float:
        """Estimate win probability for given situation"""
        # Base probabilities from basic strategy tables
        base_probs = {
            'hit': 0.45,
            'stand': 0.42,
            'double': 0.48,
            'split': 0.46
        }
        
        base_prob = base_probs.get(action.lower(), 0.45)
        
        # Adjust for player total
        if player_total >= 17:
            base_prob += 0.1
        elif player_total <= 11:
            base_prob += 0.05
        
        # Adjust for dealer upcard
        if dealer_value in [2, 3, 4, 5, 6]:  # Dealer weak
            base_prob += 0.1
        elif dealer_value in [9, 10, 11]:  # Dealer strong
            base_prob -= 0.1
        
        # Adjust for count
        count_adjustment = true_count * 0.02
        base_prob += count_adjustment
        
        return max(0.1, min(0.9, base_prob))
    
    def _generate_reasoning(self, action: str, basic_action: str, player_total: int, 
                          dealer_value: int, true_count: float, confidence: float) -> str:
        """Generate human-readable reasoning"""
        reasons = []
        
        if action.lower() == basic_action.lower():
            reasons.append("Follows basic strategy")
        else:
            reasons.append(f"Deviates from basic strategy ({basic_action})")
        
        if true_count > 1:
            reasons.append("Positive count favors player")
        elif true_count < -1:
            reasons.append("Negative count favors dealer")
        
        if dealer_value in [2, 3, 4, 5, 6]:
            reasons.append("Dealer showing weak card")
        elif dealer_value in [9, 10, 11]:
            reasons.append("Dealer showing strong card")
        
        if confidence > 0.8:
            reasons.append("High confidence recommendation")
        elif confidence < 0.6:
            reasons.append("Low confidence - consider alternatives")
        
        return "; ".join(reasons)
    
    def get_count_info(self, dealt_cards: List) -> Dict:
        """Get card counting information"""
        return self.card_counter.get_count_info(dealt_cards)
    
    def get_basic_strategy_chart(self) -> Dict:
        """Get basic strategy chart data for visualization"""
        return self.basic_strategy.get_chart_data()
    
    def get_count_values(self, system: str) -> Dict:
        """Get card values for counting system"""
        return self.card_counter.get_count_values(system)
    
    def get_betting_strategy(self) -> Dict:
        """Get betting strategy based on count"""
        return {
            "< -2": 0.5,
            "-2 to -1": 0.8,
            "-1 to +1": 1.0,
            "+1 to +2": 1.5,
            "+2 to +3": 2.0,
            "+3 to +4": 3.0,
            "> +4": 4.0
        }
    
    def get_playing_deviations(self) -> Dict:
        """Get common playing deviations"""
        return {
            "16 vs 10": {
                "standard": "Hit",
                "deviation": "Stand when True Count ≥ 0",
                "threshold": 0.0,
                "ev_gain": 0.054
            },
            "15 vs 10": {
                "standard": "Hit",
                "deviation": "Stand when True Count ≥ +4",
                "threshold": 4.0,
                "ev_gain": 0.021
            },
            "12 vs 2": {
                "standard": "Hit",
                "deviation": "Stand when True Count ≥ +3",
                "threshold": 3.0,
                "ev_gain": 0.018
            },
            "12 vs 3": {
                "standard": "Hit",
                "deviation": "Stand when True Count ≥ +2",
                "threshold": 2.0,
                "ev_gain": 0.026
            },
            "10 vs 10": {
                "standard": "Hit",
                "deviation": "Double when True Count ≥ +4",
                "threshold": 4.0,
                "ev_gain": 0.031
            }
        }
    
    def update_model(self, game_data: List[Dict]):
        """Update ML model with new game data"""
        if not game_data:
            return
        
        # Extract features and outcomes from game data
        X_new = []
        y_new = []
        
        for game in game_data:
            features = self._extract_features(game)
            outcome = self._determine_optimal_action(game)
            
            if features and outcome is not None:
                X_new.append(features)
                y_new.append(outcome)
        
        if X_new and self.ml_model:
            try:
                # Retrain model with new data
                X_new = np.array(X_new)
                y_new = np.array(y_new)
                
                # Combine with existing training data if available
                if hasattr(self, 'training_X'):
                    X_combined = np.vstack([self.training_X, X_new])
                    y_combined = np.hstack([self.training_y, y_new])
                else:
                    X_combined = X_new
                    y_combined = y_new
                
                self.ml_model.fit(X_combined, y_combined)
                
                # Save updated model
                with open('ai_model.pkl', 'wb') as f:
                    pickle.dump(self.ml_model, f)
                
                self.training_X = X_combined
                self.training_y = y_combined
                
            except Exception as e:
                pass  # Continue without updating if there's an error
    
    def _extract_features(self, game_data: Dict) -> Optional[List]:
        """Extract features from game data"""
        try:
            return [
                game_data.get('player_total', 0),
                game_data.get('dealer_upcard', 0),
                int(game_data.get('is_soft', False)),
                int(game_data.get('can_double', False)),
                int(game_data.get('can_split', False)),
                game_data.get('true_count', 0),
                abs(game_data.get('true_count', 0)),
                1 if game_data.get('true_count', 0) > 0 else 0,
            ]
        except:
            return None
    
    def _determine_optimal_action(self, game_data: Dict) -> Optional[int]:
        """Determine optimal action based on game outcome"""
        try:
            action_taken = game_data.get('action_taken', '').lower()
            outcome = game_data.get('outcome', '')
            
            # Simple heuristic: if action led to win, it was good
            if outcome == 'win':
                return self._encode_action(action_taken)
            elif outcome == 'loss':
                # Return alternative action (simplified)
                alternatives = {'hit': 'stand', 'stand': 'hit', 'double': 'hit', 'split': 'hit'}
                alt_action = alternatives.get(action_taken, 'hit')
                return self._encode_action(alt_action)
            else:
                return self._encode_action(action_taken)
        except:
            return None
