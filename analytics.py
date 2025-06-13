import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from database import DatabaseManager

class Analytics:
    def __init__(self):
        self.db = DatabaseManager()
        self.session_data = []
        self.performance_history = []
        self.decision_log = []
        self.counting_accuracy_log = []
        self.current_session = {
            'start_time': None,
            'hands_played': 0,
            'decisions': [],
            'counts': [],
            'results': []
        }
        self.tracking_active = False
        self.current_player_id = None
        self.current_session_id = None
    
    def initialize_tracking(self, username: str = "guest"):
        """Initialize performance tracking"""
        try:
            # Get or create player
            player = self.db.get_player(username)
            if not player:
                player = self.db.create_player(username)
            
            self.current_player_id = player.id
            
            # Start new game session
            game_session = self.db.start_game_session(player.id)
            self.current_session_id = game_session.id
            
            self.tracking_active = True
            self.current_session = {
                'start_time': datetime.now(),
                'hands_played': 0,
                'decisions': [],
                'counts': [],
                'results': []
            }
        except Exception as e:
            print(f"Database initialization error: {e}")
            # Fallback to in-memory tracking
            self.tracking_active = True
            self.current_session = {
                'start_time': datetime.now(),
                'hands_played': 0,
                'decisions': [],
                'counts': [],
                'results': []
            }
    
    def log_decision(self, situation: Dict, action_taken: str, correct_action: str, 
                    outcome: str, true_count: float = 0):
        """Log a player decision for analysis"""
        if not self.tracking_active:
            return
        
        decision_entry = {
            'timestamp': datetime.now(),
            'player_total': situation.get('player_total', 0),
            'dealer_upcard': situation.get('dealer_upcard', 0),
            'is_soft': situation.get('is_soft', False),
            'can_double': situation.get('can_double', False),
            'can_split': situation.get('can_split', False),
            'action_taken': action_taken,
            'correct_action': correct_action,
            'is_correct': action_taken.lower() == correct_action.lower(),
            'outcome': outcome,
            'true_count': true_count,
            'hand_number': self.current_session['hands_played']
        }
        
        # Log to database if available
        if self.current_player_id and self.current_session_id:
            try:
                self.db.log_player_decision(self.current_player_id, self.current_session_id, decision_entry)
            except Exception as e:
                print(f"Database logging error: {e}")
        
        self.decision_log.append(decision_entry)
        self.current_session['decisions'].append(decision_entry)
    
    def log_count_accuracy(self, actual_count: int, player_count: int, 
                          cards_seen: int, true_count: float):
        """Log card counting accuracy"""
        if not self.tracking_active:
            return
        
        count_entry = {
            'timestamp': datetime.now(),
            'actual_running_count': actual_count,
            'player_running_count': player_count,
            'accuracy': 1.0 if actual_count == player_count else 0.0,
            'error': abs(actual_count - player_count),
            'cards_seen': cards_seen,
            'true_count': true_count,
            'hand_number': self.current_session['hands_played']
        }
        
        self.counting_accuracy_log.append(count_entry)
        self.current_session['counts'].append(count_entry)
    
    def log_hand_result(self, bet_amount: int, payout: int, win: bool, 
                       push: bool = False):
        """Log hand result"""
        if not self.tracking_active:
            return
        
        self.current_session['hands_played'] += 1
        
        result_entry = {
            'timestamp': datetime.now(),
            'hand_number': self.current_session['hands_played'],
            'bet_amount': bet_amount,
            'payout': payout,
            'net_result': payout - bet_amount,
            'win': win,
            'push': push,
            'loss': not win and not push
        }
        
        self.current_session['results'].append(result_entry)
    
    def end_session(self):
        """End current session and save data"""
        if not self.tracking_active or not self.current_session['start_time']:
            return
        
        session_summary = {
            'session_id': len(self.session_data),
            'start_time': self.current_session['start_time'],
            'end_time': datetime.now(),
            'duration_minutes': (datetime.now() - self.current_session['start_time']).total_seconds() / 60,
            'hands_played': self.current_session['hands_played'],
            'total_decisions': len(self.current_session['decisions']),
            'correct_decisions': sum(1 for d in self.current_session['decisions'] if d['is_correct']),
            'decision_accuracy': 0 if len(self.current_session['decisions']) == 0 else 
                               sum(1 for d in self.current_session['decisions'] if d['is_correct']) / len(self.current_session['decisions']),
            'total_wagered': sum(r['bet_amount'] for r in self.current_session['results']),
            'total_winnings': sum(r['payout'] for r in self.current_session['results']),
            'net_result': sum(r['net_result'] for r in self.current_session['results']),
            'hands_won': sum(1 for r in self.current_session['results'] if r['win']),
            'hands_lost': sum(1 for r in self.current_session['results'] if r['loss']),
            'hands_pushed': sum(1 for r in self.current_session['results'] if r['push']),
            'win_rate': 0 if self.current_session['hands_played'] == 0 else 
                       sum(1 for r in self.current_session['results'] if r['win']) / self.current_session['hands_played'],
            'house_edge': 0,
            'counting_accuracy': 0 if len(self.current_session['counts']) == 0 else
                               sum(c['accuracy'] for c in self.current_session['counts']) / len(self.current_session['counts'])
        }
        
        # Calculate house edge
        if session_summary['total_wagered'] > 0:
            session_summary['house_edge'] = -session_summary['net_result'] / session_summary['total_wagered']
        
        self.session_data.append(session_summary)
        self.performance_history.append(session_summary)
        
        # Reset current session
        self.current_session = {
            'start_time': None,
            'hands_played': 0,
            'decisions': [],
            'counts': [],
            'results': []
        }
        self.tracking_active = False
    
    def get_performance_data(self) -> List[Dict]:
        """Get historical performance data"""
        if not self.performance_history:
            # Generate sample data for demonstration
            sample_data = []
            base_date = datetime.now() - timedelta(days=30)
            
            for i in range(15):  # 15 sessions over 30 days
                session_date = base_date + timedelta(days=i*2)
                
                # Simulate improvement over time
                base_win_rate = 0.42 + (i * 0.005)  # Gradually improving
                base_house_edge = 0.015 - (i * 0.0008)  # Gradually decreasing
                
                sample_data.append({
                    'session_date': session_date,
                    'session_id': i,
                    'hands_played': np.random.randint(50, 200),
                    'win_rate': max(0.35, min(0.52, base_win_rate + np.random.normal(0, 0.02))),
                    'house_edge': max(0.001, base_house_edge + np.random.normal(0, 0.003)),
                    'decision_accuracy': min(0.98, 0.75 + (i * 0.012) + np.random.normal(0, 0.05)),
                    'counting_accuracy': min(0.95, 0.60 + (i * 0.015) + np.random.normal(0, 0.06)),
                    'net_result': np.random.randint(-500, 800),
                })
            
            return sample_data
        
        return [
            {
                'session_date': session['start_time'],
                'session_id': session['session_id'],
                'hands_played': session['hands_played'],
                'win_rate': session['win_rate'],
                'house_edge': session['house_edge'],
                'decision_accuracy': session['decision_accuracy'],
                'counting_accuracy': session['counting_accuracy'],
                'net_result': session['net_result'],
            }
            for session in self.performance_history
        ]
    
    def get_decision_accuracy(self) -> Dict[str, float]:
        """Get decision accuracy by action type"""
        if not self.decision_log:
            # Return sample data
            return {
                'Hit': 0.89,
                'Stand': 0.92,
                'Double': 0.78,
                'Split': 0.83,
                'Overall': 0.87
            }
        
        accuracy_by_action = {}
        action_counts = {}
        
        for decision in self.decision_log:
            action = decision['action_taken'].title()
            if action not in accuracy_by_action:
                accuracy_by_action[action] = 0
                action_counts[action] = 0
            
            if decision['is_correct']:
                accuracy_by_action[action] += 1
            action_counts[action] += 1
        
        # Calculate percentages
        for action in accuracy_by_action:
            if action_counts[action] > 0:
                accuracy_by_action[action] = accuracy_by_action[action] / action_counts[action]
        
        # Overall accuracy
        total_correct = sum(1 for d in self.decision_log if d['is_correct'])
        total_decisions = len(self.decision_log)
        overall_accuracy = total_correct / total_decisions if total_decisions > 0 else 0
        
        accuracy_by_action['Overall'] = overall_accuracy
        
        return accuracy_by_action
    
    def get_common_mistakes(self) -> List[Dict]:
        """Get most common mistakes"""
        if not self.decision_log:
            # Return sample mistakes
            return [
                {
                    'situation': '16 vs 10',
                    'incorrect_action': 'Hit',
                    'correct_action': 'Stand (positive count)',
                    'frequency': 12,
                    'cost': 150
                },
                {
                    'situation': 'Soft 18 vs 9',
                    'incorrect_action': 'Stand',
                    'correct_action': 'Hit',
                    'frequency': 8,
                    'cost': 80
                },
                {
                    'situation': '12 vs 2',
                    'incorrect_action': 'Hit',
                    'correct_action': 'Stand (high count)',
                    'frequency': 6,
                    'cost': 45
                },
                {
                    'situation': '9 vs 2',
                    'incorrect_action': 'Hit',
                    'correct_action': 'Double',
                    'frequency': 5,
                    'cost': 75
                },
                {
                    'situation': 'A,6 vs 3',
                    'incorrect_action': 'Hit',
                    'correct_action': 'Double',
                    'frequency': 4,
                    'cost': 60
                }
            ]
        
        mistake_counts = {}
        for decision in self.decision_log:
            if not decision['is_correct']:
                situation = f"{decision['player_total']} vs {decision['dealer_upcard']}"
                if decision['is_soft']:
                    situation = f"Soft {situation}"
                
                key = (situation, decision['action_taken'], decision['correct_action'])
                if key not in mistake_counts:
                    mistake_counts[key] = {'count': 0, 'cost': 0}
                
                mistake_counts[key]['count'] += 1
                # Estimate cost based on typical bet size
                mistake_counts[key]['cost'] += 50  # Assume $50 average mistake cost
        
        # Convert to list and sort by frequency
        mistakes = []
        for (situation, incorrect, correct), data in mistake_counts.items():
            mistakes.append({
                'situation': situation,
                'incorrect_action': incorrect,
                'correct_action': correct,
                'frequency': data['count'],
                'cost': data['cost']
            })
        
        return sorted(mistakes, key=lambda x: x['frequency'], reverse=True)
    
    def get_counting_accuracy(self) -> List[Dict]:
        """Get card counting accuracy over time"""
        if not self.counting_accuracy_log:
            # Generate sample counting accuracy data
            sample_data = []
            for i in range(50):  # 50 hands
                accuracy = 0.65 + (i * 0.006) + np.random.normal(0, 0.1)  # Improving over time
                accuracy = max(0.2, min(1.0, accuracy))
                
                sample_data.append({
                    'hand_number': i + 1,
                    'accuracy': accuracy,
                    'running_accuracy': sum(s['accuracy'] for s in sample_data[:i+1]) / (i + 1) if i >= 0 else accuracy
                })
            
            return sample_data
        
        # Calculate running accuracy
        data = []
        running_total = 0
        for i, entry in enumerate(self.counting_accuracy_log):
            running_total += entry['accuracy']
            data.append({
                'hand_number': entry['hand_number'],
                'accuracy': entry['accuracy'],
                'running_accuracy': running_total / (i + 1),
                'error': entry['error'],
                'true_count': entry['true_count']
            })
        
        return data
    
    def get_accuracy_by_count_level(self) -> Dict[str, float]:
        """Get counting accuracy by true count level"""
        if not self.counting_accuracy_log:
            # Return sample data
            return {
                'Very Low (-3 to -2)': 0.72,
                'Low (-2 to -1)': 0.78,
                'Neutral (-1 to +1)': 0.85,
                'High (+1 to +2)': 0.81,
                'Very High (+2 to +3)': 0.75,
                'Extreme (>+3)': 0.68
            }
        
        count_ranges = {
            'Very Low (-3 to -2)': (-3, -2),
            'Low (-2 to -1)': (-2, -1),
            'Neutral (-1 to +1)': (-1, 1),
            'High (+1 to +2)': (1, 2),
            'Very High (+2 to +3)': (2, 3),
            'Extreme (>+3)': (3, float('inf'))
        }
        
        accuracy_by_range = {}
        
        for range_name, (min_count, max_count) in count_ranges.items():
            relevant_entries = [
                entry for entry in self.counting_accuracy_log
                if min_count <= entry['true_count'] < max_count
            ]
            
            if relevant_entries:
                accuracy = sum(entry['accuracy'] for entry in relevant_entries) / len(relevant_entries)
                accuracy_by_range[range_name] = accuracy
            else:
                accuracy_by_range[range_name] = 0.0
        
        return accuracy_by_range
    
    def get_skill_progression_summary(self) -> Dict:
        """Get overall skill progression summary"""
        performance_data = self.get_performance_data()
        
        if len(performance_data) < 2:
            return {
                'sessions_completed': len(performance_data),
                'total_hands': sum(p['hands_played'] for p in performance_data),
                'improvement_trend': 'Insufficient data',
                'current_skill_level': 'Beginner',
                'recommendations': ['Play more hands to establish baseline']
            }
        
        # Calculate improvements
        first_sessions = performance_data[:3]  # First 3 sessions
        recent_sessions = performance_data[-3:]  # Last 3 sessions
        
        avg_early_winrate = sum(s['win_rate'] for s in first_sessions) / len(first_sessions)
        avg_recent_winrate = sum(s['win_rate'] for s in recent_sessions) / len(recent_sessions)
        
        avg_early_accuracy = sum(s['decision_accuracy'] for s in first_sessions) / len(first_sessions)
        avg_recent_accuracy = sum(s['decision_accuracy'] for s in recent_sessions) / len(recent_sessions)
        
        avg_early_house_edge = sum(s['house_edge'] for s in first_sessions) / len(first_sessions)
        avg_recent_house_edge = sum(s['house_edge'] for s in recent_sessions) / len(recent_sessions)
        
        # Determine skill level
        if avg_recent_accuracy > 0.95 and avg_recent_house_edge < 0.003:
            skill_level = 'Expert'
        elif avg_recent_accuracy > 0.90 and avg_recent_house_edge < 0.006:
            skill_level = 'Advanced'
        elif avg_recent_accuracy > 0.85 and avg_recent_house_edge < 0.01:
            skill_level = 'Intermediate'
        elif avg_recent_accuracy > 0.75:
            skill_level = 'Beginner+'
        else:
            skill_level = 'Beginner'
        
        # Generate recommendations
        recommendations = []
        if avg_recent_accuracy < 0.85:
            recommendations.append('Focus on basic strategy memorization')
        if avg_recent_house_edge > 0.01:
            recommendations.append('Practice decision-making in stressful situations')
        if len(performance_data) > 5 and avg_recent_accuracy > 0.90:
            recommendations.append('Consider learning card counting techniques')
        
        return {
            'sessions_completed': len(performance_data),
            'total_hands': sum(p['hands_played'] for p in performance_data),
            'win_rate_improvement': avg_recent_winrate - avg_early_winrate,
            'accuracy_improvement': avg_recent_accuracy - avg_early_accuracy,
            'house_edge_reduction': avg_early_house_edge - avg_recent_house_edge,
            'current_skill_level': skill_level,
            'current_win_rate': avg_recent_winrate,
            'current_accuracy': avg_recent_accuracy,
            'current_house_edge': avg_recent_house_edge,
            'recommendations': recommendations if recommendations else ['Continue practicing to maintain skill level']
        }
    
    def export_session_data(self) -> str:
        """Export session data as JSON string"""
        export_data = {
            'sessions': self.session_data,
            'decisions': self.decision_log,
            'counting_accuracy': self.counting_accuracy_log,
            'export_timestamp': datetime.now().isoformat()
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def import_session_data(self, json_data: str) -> bool:
        """Import session data from JSON string"""
        try:
            data = json.loads(json_data)
            
            if 'sessions' in data:
                self.session_data.extend(data['sessions'])
                self.performance_history.extend(data['sessions'])
            
            if 'decisions' in data:
                # Convert timestamp strings back to datetime objects
                for decision in data['decisions']:
                    if isinstance(decision['timestamp'], str):
                        decision['timestamp'] = datetime.fromisoformat(decision['timestamp'])
                self.decision_log.extend(data['decisions'])
            
            if 'counting_accuracy' in data:
                for entry in data['counting_accuracy']:
                    if isinstance(entry['timestamp'], str):
                        entry['timestamp'] = datetime.fromisoformat(entry['timestamp'])
                self.counting_accuracy_log.extend(data['counting_accuracy'])
            
            return True
        except Exception as e:
            return False
