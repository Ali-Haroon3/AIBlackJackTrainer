import os
import psycopg2
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from typing import Dict, List, Optional
import json

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    total_hands_played = Column(Integer, default=0)
    total_winnings = Column(Float, default=0.0)
    current_skill_level = Column(String(20), default='Beginner')
    
    # Relationships
    sessions = relationship("GameSession", back_populates="player")
    decisions = relationship("PlayerDecision", back_populates="player")

class GameSession(Base):
    __tablename__ = 'game_sessions'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    hands_played = Column(Integer, default=0)
    total_wagered = Column(Float, default=0.0)
    total_winnings = Column(Float, default=0.0)
    net_result = Column(Float, default=0.0)
    win_rate = Column(Float, default=0.0)
    house_edge = Column(Float, default=0.0)
    decision_accuracy = Column(Float, default=0.0)
    counting_accuracy = Column(Float, default=0.0)
    
    # Relationships
    player = relationship("Player", back_populates="sessions")
    hands = relationship("HandResult", back_populates="session")
    decisions = relationship("PlayerDecision", back_populates="session")
    count_logs = relationship("CountingLog", back_populates="session")

class HandResult(Base):
    __tablename__ = 'hand_results'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('game_sessions.id'), nullable=False)
    hand_number = Column(Integer, nullable=False)
    player_cards = Column(Text)  # JSON string of card data
    dealer_cards = Column(Text)  # JSON string of card data
    player_total = Column(Integer)
    dealer_total = Column(Integer)
    bet_amount = Column(Float)
    payout = Column(Float)
    outcome = Column(String(20))  # 'win', 'loss', 'push', 'blackjack'
    is_split = Column(Boolean, default=False)
    is_doubled = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    deck_penetration = Column(Float)
    
    # Relationships
    session = relationship("GameSession", back_populates="hands")

class PlayerDecision(Base):
    __tablename__ = 'player_decisions'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    session_id = Column(Integer, ForeignKey('game_sessions.id'), nullable=False)
    hand_number = Column(Integer)
    player_total = Column(Integer)
    dealer_upcard = Column(Integer)
    is_soft = Column(Boolean, default=False)
    can_double = Column(Boolean, default=False)
    can_split = Column(Boolean, default=False)
    action_taken = Column(String(20))
    correct_action = Column(String(20))
    is_correct = Column(Boolean)
    true_count = Column(Float, default=0.0)
    outcome = Column(String(20))
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    player = relationship("Player", back_populates="decisions")
    session = relationship("GameSession", back_populates="decisions")

class CountingLog(Base):
    __tablename__ = 'counting_logs'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('game_sessions.id'), nullable=False)
    hand_number = Column(Integer)
    actual_running_count = Column(Integer)
    player_running_count = Column(Integer)
    true_count = Column(Float)
    cards_seen = Column(Integer)
    accuracy = Column(Float)  # 1.0 for correct, 0.0 for incorrect
    error_magnitude = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("GameSession", back_populates="count_logs")

class StrategyPerformance(Base):
    __tablename__ = 'strategy_performance'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    situation_key = Column(String(50))  # e.g., "16_vs_10", "soft_18_vs_9"
    total_encounters = Column(Integer, default=0)
    correct_decisions = Column(Integer, default=0)
    accuracy_rate = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.create_tables()
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def create_player(self, username: str, email: Optional[str] = None) -> Player:
        """Create a new player"""
        session = self.get_session()
        try:
            player = Player(username=username, email=email)
            session.add(player)
            session.commit()
            session.refresh(player)
            return player
        finally:
            session.close()
    
    def get_player(self, username: str) -> Optional[Player]:
        """Get player by username"""
        session = self.get_session()
        try:
            return session.query(Player).filter(Player.username == username).first()
        finally:
            session.close()
    
    def start_game_session(self, player_id: int) -> GameSession:
        """Start a new game session"""
        session = self.get_session()
        try:
            game_session = GameSession(player_id=player_id)
            session.add(game_session)
            session.commit()
            session.refresh(game_session)
            return game_session
        finally:
            session.close()
    
    def end_game_session(self, session_id: int, stats: Dict):
        """End a game session with final statistics"""
        session = self.get_session()
        try:
            game_session = session.query(GameSession).filter(GameSession.id == session_id).first()
            if game_session:
                game_session.end_time = datetime.utcnow()
                game_session.hands_played = stats.get('hands_played', 0)
                game_session.total_wagered = stats.get('total_wagered', 0.0)
                game_session.total_winnings = stats.get('total_winnings', 0.0)
                game_session.net_result = stats.get('net_result', 0.0)
                game_session.win_rate = stats.get('win_rate', 0.0)
                game_session.house_edge = stats.get('house_edge', 0.0)
                game_session.decision_accuracy = stats.get('decision_accuracy', 0.0)
                game_session.counting_accuracy = stats.get('counting_accuracy', 0.0)
                session.commit()
        finally:
            session.close()
    
    def log_hand_result(self, session_id: int, hand_data: Dict):
        """Log the result of a single hand"""
        session = self.get_session()
        try:
            hand_result = HandResult(
                session_id=session_id,
                hand_number=hand_data.get('hand_number', 0),
                player_cards=json.dumps(hand_data.get('player_cards', [])),
                dealer_cards=json.dumps(hand_data.get('dealer_cards', [])),
                player_total=hand_data.get('player_total', 0),
                dealer_total=hand_data.get('dealer_total', 0),
                bet_amount=hand_data.get('bet_amount', 0.0),
                payout=hand_data.get('payout', 0.0),
                outcome=hand_data.get('outcome', 'loss'),
                is_split=hand_data.get('is_split', False),
                is_doubled=hand_data.get('is_doubled', False),
                deck_penetration=hand_data.get('deck_penetration', 0.0)
            )
            session.add(hand_result)
            session.commit()
        finally:
            session.close()
    
    def log_player_decision(self, player_id: int, session_id: int, decision_data: Dict):
        """Log a player's decision"""
        session = self.get_session()
        try:
            decision = PlayerDecision(
                player_id=player_id,
                session_id=session_id,
                hand_number=decision_data.get('hand_number', 0),
                player_total=decision_data.get('player_total', 0),
                dealer_upcard=decision_data.get('dealer_upcard', 0),
                is_soft=decision_data.get('is_soft', False),
                can_double=decision_data.get('can_double', False),
                can_split=decision_data.get('can_split', False),
                action_taken=decision_data.get('action_taken', ''),
                correct_action=decision_data.get('correct_action', ''),
                is_correct=decision_data.get('is_correct', False),
                true_count=decision_data.get('true_count', 0.0),
                outcome=decision_data.get('outcome', '')
            )
            session.add(decision)
            session.commit()
        finally:
            session.close()
    
    def log_counting_accuracy(self, session_id: int, count_data: Dict):
        """Log card counting accuracy"""
        session = self.get_session()
        try:
            count_log = CountingLog(
                session_id=session_id,
                hand_number=count_data.get('hand_number', 0),
                actual_running_count=count_data.get('actual_running_count', 0),
                player_running_count=count_data.get('player_running_count', 0),
                true_count=count_data.get('true_count', 0.0),
                cards_seen=count_data.get('cards_seen', 0),
                accuracy=count_data.get('accuracy', 0.0),
                error_magnitude=count_data.get('error_magnitude', 0)
            )
            session.add(count_log)
            session.commit()
        finally:
            session.close()
    
    def get_player_statistics(self, player_id: int) -> Dict:
        """Get comprehensive player statistics"""
        session = self.get_session()
        try:
            player = session.query(Player).filter(Player.id == player_id).first()
            if not player:
                return {}
            
            # Get session statistics
            sessions = session.query(GameSession).filter(
                GameSession.player_id == player_id,
                GameSession.end_time.isnot(None)
            ).all()
            
            # Calculate aggregated stats
            total_hands = sum(s.hands_played for s in sessions)
            total_wagered = sum(s.total_wagered for s in sessions)
            total_winnings = sum(s.total_winnings for s in sessions)
            avg_win_rate = sum(s.win_rate for s in sessions) / len(sessions) if sessions else 0
            avg_house_edge = sum(s.house_edge for s in sessions) / len(sessions) if sessions else 0
            avg_decision_accuracy = sum(s.decision_accuracy for s in sessions) / len(sessions) if sessions else 0
            avg_counting_accuracy = sum(s.counting_accuracy for s in sessions) / len(sessions) if sessions else 0
            
            return {
                'player_id': player_id,
                'username': player.username,
                'total_sessions': len(sessions),
                'total_hands': total_hands,
                'total_wagered': total_wagered,
                'total_winnings': total_winnings,
                'net_profit': total_winnings - total_wagered,
                'average_win_rate': avg_win_rate,
                'average_house_edge': avg_house_edge,
                'average_decision_accuracy': avg_decision_accuracy,
                'average_counting_accuracy': avg_counting_accuracy,
                'skill_level': player.current_skill_level,
                'member_since': player.created_at
            }
        finally:
            session.close()
    
    def get_session_history(self, player_id: int, limit: int = 10) -> List[Dict]:
        """Get recent session history for a player"""
        session = self.get_session()
        try:
            sessions = session.query(GameSession).filter(
                GameSession.player_id == player_id,
                GameSession.end_time.isnot(None)
            ).order_by(GameSession.start_time.desc()).limit(limit).all()
            
            return [
                {
                    'session_id': s.id,
                    'start_time': s.start_time,
                    'end_time': s.end_time,
                    'duration_minutes': (s.end_time - s.start_time).total_seconds() / 60 if s.end_time else 0,
                    'hands_played': s.hands_played,
                    'net_result': s.net_result,
                    'win_rate': s.win_rate,
                    'house_edge': s.house_edge,
                    'decision_accuracy': s.decision_accuracy,
                    'counting_accuracy': s.counting_accuracy
                }
                for s in sessions
            ]
        finally:
            session.close()
    
    def get_decision_patterns(self, player_id: int) -> Dict:
        """Analyze player's decision patterns and common mistakes"""
        session = self.get_session()
        try:
            decisions = session.query(PlayerDecision).filter(
                PlayerDecision.player_id == player_id
            ).all()
            
            if not decisions:
                return {}
            
            # Group decisions by situation
            situations = {}
            for decision in decisions:
                situation_key = f"{decision.player_total}_vs_{decision.dealer_upcard}"
                if decision.is_soft:
                    situation_key = f"soft_{situation_key}"
                
                if situation_key not in situations:
                    situations[situation_key] = {
                        'total': 0,
                        'correct': 0,
                        'incorrect_actions': {},
                        'correct_action': decision.correct_action
                    }
                
                situations[situation_key]['total'] += 1
                if decision.is_correct:
                    situations[situation_key]['correct'] += 1
                else:
                    action = decision.action_taken
                    if action not in situations[situation_key]['incorrect_actions']:
                        situations[situation_key]['incorrect_actions'][action] = 0
                    situations[situation_key]['incorrect_actions'][action] += 1
            
            # Calculate accuracy rates
            for situation in situations.values():
                situation['accuracy'] = situation['correct'] / situation['total'] if situation['total'] > 0 else 0
            
            return situations
        finally:
            session.close()
    
    def update_strategy_performance(self, player_id: int, situation_key: str, is_correct: bool):
        """Update strategy performance tracking"""
        session = self.get_session()
        try:
            perf = session.query(StrategyPerformance).filter(
                StrategyPerformance.player_id == player_id,
                StrategyPerformance.situation_key == situation_key
            ).first()
            
            if not perf:
                perf = StrategyPerformance(
                    player_id=player_id,
                    situation_key=situation_key,
                    total_encounters=0,
                    correct_decisions=0
                )
                session.add(perf)
            
            perf.total_encounters += 1
            if is_correct:
                perf.correct_decisions += 1
            
            perf.accuracy_rate = perf.correct_decisions / perf.total_encounters
            perf.last_updated = datetime.utcnow()
            
            session.commit()
        finally:
            session.close()