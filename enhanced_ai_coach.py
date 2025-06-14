import numpy as np
from typing import Dict, List, Tuple, Optional
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import os
from bja_strategy import BJABasicStrategy
from card_counting import CardCounter
from collections import defaultdict
import json

class EnhancedAICoach:
    def __init__(self):
        self.basic_strategy = BJABasicStrategy()
        self.card_counter = CardCounter()
        self.ml_model = None
        self.training_data = []
        self.performance_history = []
        
        # Player analysis tracking
        self.player_patterns = defaultdict(list)
        self.mistake_analysis = defaultdict(int)
        self.strength_areas = defaultdict(float)
        self.weakness_areas = defaultdict(float)
        self.counting_accuracy_history = []
        
        # Current session tracking
        self.current_session = {
            'decisions': [],
            'counting_attempts': [],
            'correct_decisions': 0,
            'total_decisions': 0,
            'counting_system': 'Hi-Lo'
        }
        
        # Initialize ML model
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
        X, y = self._generate_training_data()
        
        self.ml_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        if len(X) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            self.ml_model.fit(X_train, y_train)
            
            try:
                with open('ai_model.pkl', 'wb') as f:
                    pickle.dump(self.ml_model, f)
            except:
                pass
    
    def _generate_training_data(self) -> Tuple[List, List]:
        """Generate training data from basic strategy and card counting"""
        X = []
        y = []
        
        for player_total in range(5, 22):
            for dealer_upcard in range(2, 12):
                for is_soft in [True, False]:
                    for can_double in [True, False]:
                        for can_split in [True, False]:
                            for true_count in [-3, -1, 0, 1, 3]:
                                features = [
                                    player_total,
                                    dealer_upcard,
                                    int(is_soft),
                                    int(can_double),
                                    int(can_split),
                                    true_count,
                                    abs(true_count),
                                    1 if true_count > 0 else 0,
                                ]
                                
                                action = self._get_basic_strategy_action(
                                    player_total, dealer_upcard, is_soft, can_double, can_split
                                )
                                
                                if true_count != 0:
                                    action = self._adjust_for_count(action, true_count, player_total, dealer_upcard)
                                
                                X.append(features)
                                y.append(self._encode_action(action))
        
        return X, y
    
    def _get_basic_strategy_action(self, player_total: int, dealer_upcard: int, 
                                  is_soft: bool, can_double: bool, can_split: bool) -> str:
        """Get basic strategy action using BJA chart"""
        return self.basic_strategy.get_action(
            player_total=player_total,
            dealer_upcard=dealer_upcard,
            is_soft=is_soft,
            is_pair=can_split,
            can_double=can_double,
            can_surrender=False
        )
    
    def _adjust_for_count(self, action: str, true_count: float, player_total: int, dealer_upcard: int) -> str:
        """Adjust action based on true count"""
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
    
    def set_counting_system(self, system: str):
        """Set the counting system for the session"""
        self.current_session['counting_system'] = system
        self.card_counter.current_system = system
    
    def get_recommendation(self, player_hands: List, dealer_upcard, show_advice: bool = False) -> Dict:
        """Get AI recommendation for current situation"""
        if not player_hands:
            return {'action': 'Hit', 'reason': 'No valid hand', 'win_probability': 0.5, 'show_advice': show_advice}
        
        try:
            current_hand = player_hands[0] if isinstance(player_hands, list) else player_hands
            player_total = current_hand.get_value() if hasattr(current_hand, 'get_value') else 17
            dealer_value = dealer_upcard.get_value() if hasattr(dealer_upcard, 'get_value') else 10
            
            is_soft = current_hand.is_soft() if hasattr(current_hand, 'is_soft') else False
            can_double = len(current_hand.cards) == 2 if hasattr(current_hand, 'cards') else False
            can_split = current_hand.can_split() if hasattr(current_hand, 'can_split') else False
            
            true_count = 0
            
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
            
            basic_action = self._get_basic_strategy_action(
                player_total, dealer_value, is_soft, can_double, can_split
            )
            
            win_probability = self._estimate_win_probability(
                player_total, dealer_value, action, true_count
            )
            
            reason = self._generate_reasoning(
                action, basic_action, player_total, dealer_value, true_count, confidence
            ) if show_advice else "Click 'Get Hint' for advice"
            
            return {
                'action': action,  # Always return the actual action
                'reason': reason,
                'win_probability': win_probability,
                'confidence': confidence,
                'basic_strategy': basic_action,
                'reasoning': reason
            }
        except Exception as e:
            # Fallback for any errors
            return {
                'action': 'Hit',  # Always return actual action, never "Hidden"
                'reason': "Using basic strategy fallback",
                'win_probability': 0.5,
                'confidence': 0.5,
                'basic_strategy': 'Hit',
                'reasoning': "Basic strategy recommendation"
            }
    
    def _estimate_win_probability(self, player_total: int, dealer_value: int, 
                                action: str, true_count: float) -> float:
        """Estimate win probability for given situation"""
        base_probs = {
            'hit': 0.45,
            'stand': 0.42,
            'double': 0.48,
            'split': 0.46
        }
        
        base_prob = base_probs.get(action.lower(), 0.45)
        
        if player_total >= 17:
            base_prob += 0.1
        elif player_total <= 11:
            base_prob += 0.05
        
        if dealer_value in [2, 3, 4, 5, 6]:
            base_prob += 0.1
        elif dealer_value in [9, 10, 11]:
            base_prob -= 0.1
        
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
    
    def log_player_decision(self, situation: Dict, action_taken: str, correct_action: str, outcome: str):
        """Log a player's decision for analysis"""
        decision = {
            'situation': situation,
            'action_taken': action_taken,
            'correct_action': correct_action,
            'outcome': outcome,
            'is_correct': action_taken.lower() == correct_action.lower()
        }
        
        self.current_session['decisions'].append(decision)
        self.current_session['total_decisions'] += 1
        
        if decision['is_correct']:
            self.current_session['correct_decisions'] += 1
        else:
            # Track mistake patterns
            situation_key = f"{situation.get('player_total', 0)}_vs_{situation.get('dealer_upcard', 0)}"
            if situation.get('is_soft', False):
                situation_key = f"soft_{situation_key}"
            
            self.mistake_analysis[situation_key] += 1
        
        # Update strength/weakness analysis
        self._update_skill_analysis(decision)
    
    def _update_skill_analysis(self, decision: Dict):
        """Update player's strength and weakness analysis"""
        situation = decision['situation']
        situation_type = self._categorize_situation(situation)
        
        if decision['is_correct']:
            self.strength_areas[situation_type] = self.strength_areas.get(situation_type, 0) + 1
        else:
            self.weakness_areas[situation_type] = self.weakness_areas.get(situation_type, 0) + 1
    
    def _categorize_situation(self, situation: Dict) -> str:
        """Categorize the playing situation"""
        player_total = situation.get('player_total', 0)
        is_soft = situation.get('is_soft', False)
        can_split = situation.get('can_split', False)
        
        if can_split:
            return "Pair Splitting"
        elif is_soft:
            return "Soft Hands"
        elif player_total <= 11:
            return "Low Totals"
        elif player_total >= 17:
            return "High Totals"
        else:
            return "Stiff Hands"
    
    def test_counting_knowledge(self, dealt_cards: List, player_guess: int) -> Dict:
        """Test player's card counting accuracy"""
        try:
            actual_count = 0
            system = self.current_session['counting_system']
            
            # Reset card counter and count all dealt cards
            self.card_counter.reset_count()
            for card in dealt_cards:
                actual_count += self.card_counter.count_card(card, system)
            
            is_correct = (player_guess == actual_count)
            error = abs(player_guess - actual_count)
            
            count_test = {
                'actual_count': actual_count,
                'player_guess': player_guess,
                'is_correct': is_correct,
                'error': error,
                'system': system
            }
            
            self.current_session['counting_attempts'].append(count_test)
            self.counting_accuracy_history.append(is_correct)
            
            return count_test
        except Exception as e:
            return {
                'actual_count': 0,
                'player_guess': player_guess,
                'is_correct': False,
                'error': abs(player_guess),
                'system': self.current_session.get('counting_system', 'Hi-Lo')
            }
    
    def get_count_info(self, dealt_cards: List, show_count: bool = False) -> Dict:
        """Get card counting information"""
        count_info = self.card_counter.get_count_info(dealt_cards)
        
        if not show_count:
            # Hide the actual count values
            count_info['running_count'] = "Hidden"
            count_info['true_count'] = "Hidden"
        
        count_info['show_count'] = show_count
        return count_info
    
    def get_player_analysis(self) -> Dict:
        """Get comprehensive analysis of player's performance"""
        total_decisions = self.current_session['total_decisions']
        correct_decisions = self.current_session['correct_decisions']
        
        analysis = {
            'overall_accuracy': correct_decisions / total_decisions if total_decisions > 0 else 0,
            'total_decisions': total_decisions,
            'correct_decisions': correct_decisions,
            'strengths': [],
            'weaknesses': [],
            'recommendations': [],
            'counting_accuracy': sum(self.counting_accuracy_history) / len(self.counting_accuracy_history) if self.counting_accuracy_history else 0,
            'mistake_patterns': dict(self.mistake_analysis)
        }
        
        # Identify strengths (>80% accuracy)
        for situation, correct_count in self.strength_areas.items():
            total_count = correct_count + self.weakness_areas.get(situation, 0)
            if total_count > 0:
                accuracy = correct_count / total_count
                if accuracy > 0.8 and total_count >= 3:
                    analysis['strengths'].append(f"{situation}: {accuracy:.1%} accuracy")
        
        # Identify weaknesses (<60% accuracy)
        for situation, wrong_count in self.weakness_areas.items():
            total_count = wrong_count + self.strength_areas.get(situation, 0)
            if total_count > 0:
                accuracy = self.strength_areas.get(situation, 0) / total_count
                if accuracy < 0.6 and total_count >= 3:
                    analysis['weaknesses'].append(f"{situation}: {accuracy:.1%} accuracy")
        
        # Generate recommendations
        analysis['recommendations'] = self._generate_recommendations(analysis)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if analysis['overall_accuracy'] < 0.7:
            recommendations.append("Focus on basic strategy fundamentals")
        
        if analysis['counting_accuracy'] < 0.8:
            recommendations.append("Practice card counting with easier scenarios")
        
        if 'Stiff Hands' in [w.split(':')[0] for w in analysis['weaknesses']]:
            recommendations.append("Review strategy for hands 12-16 vs dealer upcards")
        
        if 'Soft Hands' in [w.split(':')[0] for w in analysis['weaknesses']]:
            recommendations.append("Practice soft hand doubling situations")
        
        if 'Pair Splitting' in [w.split(':')[0] for w in analysis['weaknesses']]:
            recommendations.append("Study pair splitting strategy chart")
        
        # Most common mistakes
        if analysis['mistake_patterns']:
            most_common = max(analysis['mistake_patterns'].items(), key=lambda x: x[1])
            recommendations.append(f"Focus on situation: {most_common[0]} (made {most_common[1]} mistakes)")
        
        return recommendations
    
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