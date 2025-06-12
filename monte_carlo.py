import numpy as np
import random
from typing import Dict, List, Tuple
from game_engine import BlackjackGame, Deck, Hand, Card
from strategy_tables import BasicStrategy
from card_counting import CardCounter
import concurrent.futures
from multiprocessing import Pool
import time

class MonteCarloSimulator:
    def __init__(self):
        self.basic_strategy = BasicStrategy()
        self.card_counter = CardCounter()
        self.results_cache = {}
    
    def run_simulation(self, num_hands: int = 10000, num_decks: int = 6, 
                      penetration: float = 0.75, strategy_type: str = "Basic Strategy Only") -> Dict:
        """Run Monte Carlo simulation with specified parameters"""
        
        # Clear previous results
        self.results_cache.clear()
        
        # Initialize simulation parameters
        sim_params = {
            'num_hands': num_hands,
            'num_decks': num_decks,
            'penetration': penetration,
            'strategy_type': strategy_type
        }
        
        # Run simulation
        start_time = time.time()
        results = self._execute_simulation(sim_params)
        execution_time = time.time() - start_time
        
        # Add execution metadata
        results['execution_time'] = execution_time
        results['hands_per_second'] = num_hands / execution_time if execution_time > 0 else 0
        
        return results
    
    def _execute_simulation(self, params: Dict) -> Dict:
        """Execute the Monte Carlo simulation"""
        num_hands = params['num_hands']
        num_decks = params['num_decks']
        penetration = params['penetration']
        strategy_type = params['strategy_type']
        
        # Initialize tracking variables
        hands_won = 0
        hands_lost = 0
        hands_pushed = 0
        total_wagered = 0
        total_winnings = 0
        cumulative_winnings = []
        
        # Strategy-specific variables
        use_counting = "Card Counting" in strategy_type
        use_ml = "ML" in strategy_type or "Optimized" in strategy_type
        
        # Initialize deck and counting
        deck = Deck(num_decks)
        running_count = 0
        cards_seen = 0
        
        # Simulation loop
        for hand_num in range(num_hands):
            # Check if deck needs reshuffling
            if deck.get_penetration() >= penetration:
                deck.reset()
                running_count = 0
                cards_seen = 0
            
            # Determine bet size
            if use_counting:
                true_count = running_count / max(1, (52 * num_decks - cards_seen) / 52)
                bet_size = self._get_optimal_bet(true_count)
            else:
                bet_size = 100  # Base bet
            
            # Play hand
            hand_result = self._simulate_hand(deck, bet_size, strategy_type, running_count, cards_seen)
            
            # Update counters
            if hand_result['outcome'] == 'win':
                hands_won += 1
            elif hand_result['outcome'] == 'loss':
                hands_lost += 1
            else:
                hands_pushed += 1
            
            total_wagered += hand_result['bet']
            total_winnings += hand_result['payout']
            cumulative_winnings.append(total_winnings - total_wagered)
            
            # Update card counting
            if use_counting:
                for card in hand_result['cards_seen']:
                    running_count += self._get_card_count_value(card)
                    cards_seen += 1
        
        # Calculate final statistics
        win_rate = hands_won / num_hands if num_hands > 0 else 0
        house_edge = -(total_winnings - total_wagered) / total_wagered if total_wagered > 0 else 0
        
        # Calculate hourly expectation (assuming 100 hands per hour)
        hands_per_hour = 100
        average_bet = total_wagered / num_hands if num_hands > 0 else 100
        expected_hourly = -house_edge * hands_per_hour * average_bet
        
        # Generate insights
        insights = self._generate_insights(
            win_rate, house_edge, strategy_type, cumulative_winnings
        )
        
        return {
            'win_rate': win_rate,
            'house_edge': house_edge,
            'expected_hourly': expected_hourly,
            'hands_won': hands_won,
            'hands_lost': hands_lost,
            'hands_pushed': hands_pushed,
            'total_wagered': total_wagered,
            'total_winnings': total_winnings,
            'net_result': total_winnings - total_wagered,
            'cumulative_winnings': cumulative_winnings,
            'insights': insights,
            'final_penetration': deck.get_penetration(),
            'average_bet': average_bet
        }
    
    def _simulate_hand(self, deck: Deck, bet_size: int, strategy_type: str, 
                      running_count: int, cards_seen: int) -> Dict:
        """Simulate a single hand"""
        # Deal initial cards
        player_cards = [deck.deal_card(), deck.deal_card()]
        dealer_cards = [deck.deal_card(), deck.deal_card()]
        
        cards_dealt = player_cards + dealer_cards
        
        player_hand = Hand()
        dealer_hand = Hand()
        
        for card in player_cards:
            player_hand.add_card(card)
        for card in dealer_cards:
            dealer_hand.add_card(card)
        
        player_hand.bet = bet_size
        
        # Check for blackjacks
        player_bj = player_hand.is_blackjack()
        dealer_bj = dealer_hand.is_blackjack()
        
        if player_bj or dealer_bj:
            if player_bj and dealer_bj:
                return {
                    'outcome': 'push',
                    'bet': bet_size,
                    'payout': bet_size,
                    'cards_seen': cards_dealt
                }
            elif player_bj:
                return {
                    'outcome': 'win',
                    'bet': bet_size,
                    'payout': bet_size + int(bet_size * 1.5),
                    'cards_seen': cards_dealt
                }
            else:  # dealer_bj
                return {
                    'outcome': 'loss',
                    'bet': bet_size,
                    'payout': 0,
                    'cards_seen': cards_dealt
                }
        
        # Play player hand
        while not player_hand.is_busted() and player_hand.get_value() < 21:
            action = self._get_optimal_action(
                player_hand, dealer_cards[0], strategy_type, running_count, cards_seen
            )
            
            if action == 'hit':
                new_card = deck.deal_card()
                player_hand.add_card(new_card)
                cards_dealt.append(new_card)
            elif action == 'double':
                if len(player_hand.cards) == 2:  # Can only double on first two cards
                    player_hand.bet *= 2
                    bet_size *= 2
                new_card = deck.deal_card()
                player_hand.add_card(new_card)
                cards_dealt.append(new_card)
                break
            else:  # stand
                break
        
        # Play dealer hand
        while dealer_hand.get_value() < 17 or (dealer_hand.get_value() == 17 and dealer_hand.is_soft()):
            new_card = deck.deal_card()
            dealer_hand.add_card(new_card)
            cards_dealt.append(new_card)
        
        # Determine outcome
        player_value = player_hand.get_value()
        dealer_value = dealer_hand.get_value()
        
        if player_value > 21:
            outcome = 'loss'
            payout = 0
        elif dealer_value > 21:
            outcome = 'win'
            payout = bet_size * 2
        elif player_value > dealer_value:
            outcome = 'win'
            payout = bet_size * 2
        elif player_value < dealer_value:
            outcome = 'loss'
            payout = 0
        else:
            outcome = 'push'
            payout = bet_size
        
        return {
            'outcome': outcome,
            'bet': bet_size,
            'payout': payout,
            'cards_seen': cards_dealt,
            'player_value': player_value,
            'dealer_value': dealer_value
        }
    
    def _get_optimal_action(self, player_hand: Hand, dealer_upcard: Card, 
                           strategy_type: str, running_count: int, cards_seen: int) -> str:
        """Get optimal action based on strategy type"""
        player_value = player_hand.get_value()
        dealer_value = dealer_upcard.get_value()
        is_soft = player_hand.is_soft()
        can_double = len(player_hand.cards) == 2
        can_split = player_hand.can_split()
        
        # Calculate true count for counting strategies
        decks_remaining = max(1, (52 * 6 - cards_seen) / 52)  # Assuming 6 decks
        true_count = running_count / decks_remaining
        
        if strategy_type == "Basic Strategy Only":
            return self._get_basic_strategy_action(
                player_value, dealer_value, is_soft, can_double, can_split
            )
        
        elif "Card Counting" in strategy_type:
            action = self._get_basic_strategy_action(
                player_value, dealer_value, is_soft, can_double, can_split
            )
            # Apply common deviations
            return self._apply_counting_deviations(
                action, player_value, dealer_value, true_count
            )
        
        elif "Optimized" in strategy_type or "ML" in strategy_type:
            # Use more aggressive optimization
            return self._get_optimized_action(
                player_value, dealer_value, is_soft, can_double, can_split, true_count
            )
        
        else:
            return self._get_basic_strategy_action(
                player_value, dealer_value, is_soft, can_double, can_split
            )
    
    def _get_basic_strategy_action(self, player_value: int, dealer_value: int, 
                                  is_soft: bool, can_double: bool, can_split: bool) -> str:
        """Get basic strategy action"""
        if can_split and player_value % 2 == 0:
            pair_value = player_value // 2
            if pair_value <= 10:
                action = self.basic_strategy.get_pair_action(pair_value, dealer_value)
                if action == 'split':
                    return 'hit'  # Simplified for simulation
        
        if is_soft:
            return self.basic_strategy.get_soft_action(player_value, dealer_value, can_double)
        else:
            return self.basic_strategy.get_hard_action(player_value, dealer_value, can_double)
    
    def _apply_counting_deviations(self, base_action: str, player_value: int, 
                                  dealer_value: int, true_count: float) -> str:
        """Apply card counting deviations"""
        # Common deviations
        if player_value == 16 and dealer_value == 10 and true_count >= 0:
            return 'stand'
        elif player_value == 15 and dealer_value == 10 and true_count >= 4:
            return 'stand'
        elif player_value == 12 and dealer_value == 2 and true_count >= 3:
            return 'stand'
        elif player_value == 12 and dealer_value == 3 and true_count >= 2:
            return 'stand'
        elif player_value == 10 and dealer_value == 10 and true_count >= 4:
            return 'double'
        elif player_value == 10 and dealer_value == 9 and true_count >= 1:
            return 'double'
        
        return base_action
    
    def _get_optimized_action(self, player_value: int, dealer_value: int, 
                             is_soft: bool, can_double: bool, can_split: bool, 
                             true_count: float) -> str:
        """Get optimized ML-based action"""
        # Start with basic strategy
        action = self._get_basic_strategy_action(
            player_value, dealer_value, is_soft, can_double, can_split
        )
        
        # Apply counting deviations
        action = self._apply_counting_deviations(action, player_value, dealer_value, true_count)
        
        # Additional ML-optimized adjustments
        if true_count > 2:
            # More aggressive with positive count
            if player_value == 11 and dealer_value <= 10:
                return 'double'
            elif player_value == 9 and dealer_value in [3, 4, 5, 6]:
                return 'double'
        elif true_count < -2:
            # More conservative with negative count
            if player_value >= 12 and dealer_value >= 7:
                return 'hit'
        
        return action
    
    def _get_optimal_bet(self, true_count: float) -> int:
        """Get optimal bet size based on true count"""
        base_bet = 100
        
        if true_count <= -1:
            return int(base_bet * 0.5)
        elif true_count < 1:
            return base_bet
        elif true_count < 2:
            return int(base_bet * 1.5)
        elif true_count < 3:
            return int(base_bet * 2.0)
        elif true_count < 4:
            return int(base_bet * 3.0)
        else:
            return int(base_bet * 4.0)
    
    def _get_card_count_value(self, card: Card) -> int:
        """Get Hi-Lo count value for card"""
        value = card.get_value()
        if value in [2, 3, 4, 5, 6]:
            return 1
        elif value in [7, 8, 9]:
            return 0
        else:  # 10, J, Q, K, A
            return -1
    
    def _generate_insights(self, win_rate: float, house_edge: float, 
                          strategy_type: str, cumulative_winnings: List[float]) -> List[str]:
        """Generate insights from simulation results"""
        insights = []
        
        # Win rate insights
        if win_rate > 0.49:
            insights.append(f"Excellent win rate of {win_rate:.1%} achieved with {strategy_type}")
        elif win_rate > 0.45:
            insights.append(f"Good win rate of {win_rate:.1%} - room for improvement")
        else:
            insights.append(f"Low win rate of {win_rate:.1%} - strategy needs optimization")
        
        # House edge insights
        if house_edge < 0:
            insights.append(f"Player advantage of {abs(house_edge):.3%} - profitable strategy!")
        elif house_edge < 0.005:
            insights.append(f"Very low house edge of {house_edge:.3%} - excellent play")
        elif house_edge < 0.01:
            insights.append(f"House edge of {house_edge:.3%} - good basic strategy execution")
        else:
            insights.append(f"High house edge of {house_edge:.3%} - strategy needs improvement")
        
        # Volatility insights
        if cumulative_winnings:
            max_win = max(cumulative_winnings)
            max_loss = min(cumulative_winnings)
            volatility = max_win - max_loss
            
            if volatility > 5000:
                insights.append("High volatility - expect significant swings")
            elif volatility > 2000:
                insights.append("Moderate volatility - typical for blackjack")
            else:
                insights.append("Low volatility - conservative play style")
        
        # Strategy-specific insights
        if "Card Counting" in strategy_type:
            insights.append("Card counting strategy shows improved performance in positive counts")
        
        if "Optimized" in strategy_type or "ML" in strategy_type:
            insights.append("ML optimization provides edge through advanced deviation plays")
        
        return insights
    
    def run_parallel_simulation(self, num_simulations: int = 10, hands_per_sim: int = 10000, 
                               num_decks: int = 6, penetration: float = 0.75, 
                               strategy_type: str = "Basic Strategy Only") -> Dict:
        """Run multiple parallel simulations for statistical significance"""
        
        # Prepare simulation parameters
        sim_params = []
        for i in range(num_simulations):
            sim_params.append({
                'num_hands': hands_per_sim,
                'num_decks': num_decks,
                'penetration': penetration,
                'strategy_type': strategy_type,
                'seed': i  # Different seed for each simulation
            })
        
        # Run simulations in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self._execute_single_simulation, params) 
                      for params in sim_params]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Aggregate results
        return self._aggregate_parallel_results(results)
    
    def _execute_single_simulation(self, params: Dict) -> Dict:
        """Execute a single simulation with given parameters"""
        # Set random seed for reproducibility
        if 'seed' in params:
            random.seed(params['seed'])
            np.random.seed(params['seed'])
        
        return self._execute_simulation(params)
    
    def _aggregate_parallel_results(self, results: List[Dict]) -> Dict:
        """Aggregate results from parallel simulations"""
        if not results:
            return {}
        
        # Calculate means and standard deviations
        win_rates = [r['win_rate'] for r in results]
        house_edges = [r['house_edge'] for r in results]
        expected_hourlies = [r['expected_hourly'] for r in results]
        
        return {
            'mean_win_rate': np.mean(win_rates),
            'std_win_rate': np.std(win_rates),
            'mean_house_edge': np.mean(house_edges),
            'std_house_edge': np.std(house_edges),
            'mean_expected_hourly': np.mean(expected_hourlies),
            'std_expected_hourly': np.std(expected_hourlies),
            'confidence_interval_95': {
                'win_rate': [
                    np.mean(win_rates) - 1.96 * np.std(win_rates),
                    np.mean(win_rates) + 1.96 * np.std(win_rates)
                ],
                'house_edge': [
                    np.mean(house_edges) - 1.96 * np.std(house_edges),
                    np.mean(house_edges) + 1.96 * np.std(house_edges)
                ]
            },
            'individual_results': results,
            'num_simulations': len(results)
        }
