import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
from game_engine import BlackjackGame
from enhanced_ai_coach import EnhancedAICoach
from monte_carlo import MonteCarloSimulator
from analytics import Analytics
from card_visuals import CardRenderer, create_table_background
from user_management import UserManager
import time

# Initialize session state
if 'game' not in st.session_state:
    st.session_state.game = BlackjackGame()
if 'coach' not in st.session_state:
    st.session_state.coach = EnhancedAICoach()
if 'show_advice' not in st.session_state:
    st.session_state.show_advice = False
if 'show_count' not in st.session_state:
    st.session_state.show_count = False
if 'counting_system' not in st.session_state:
    st.session_state.counting_system = 'Hi-Lo'
if 'analytics' not in st.session_state:
    st.session_state.analytics = Analytics()
if 'monte_carlo' not in st.session_state:
    st.session_state.monte_carlo = MonteCarloSimulator()
if 'card_renderer' not in st.session_state:
    st.session_state.card_renderer = CardRenderer()
if 'user_manager' not in st.session_state:
    st.session_state.user_manager = UserManager()

st.set_page_config(
    page_title="Blackjack AI Training",
    page_icon="🃏",
    layout="wide"
)

st.title("🃏 Blackjack AI Training & Strategy Optimization")

# Sidebar for navigation and user management
st.session_state.user_manager.render_login_form()

st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a section:", [
    "Game Training", 
    "Strategy Analysis", 
    "Monte Carlo Simulation", 
    "Performance Analytics",
    "Player Dashboard"
])

# Main content based on selected page
if page == "Game Training":
    st.header("Interactive Blackjack Training")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.subheader("🎰 Casino Table")
        
        # Display current game state
        game = st.session_state.game
        card_renderer = st.session_state.card_renderer
        
        # Create blackjack table background
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #0d5d0d 0%, #1a8a1a 50%, #0d5d0d 100%);
            padding: 20px;
            border-radius: 15px;
            border: 3px solid #ffd700;
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
            margin: 10px 0;
        ">
        """, unsafe_allow_html=True)
        
        # Game controls
        if not game.game_active:
            st.markdown("### 🎯 Place Your Bet")
            bet_amount = st.slider("Bet Amount ($)", min_value=10, max_value=500, value=50, step=10)
            
            col_deal, col_space = st.columns([1, 2])
            with col_deal:
                if st.button("🃏 Deal Cards", type="primary"):
                    game.new_hand(bet_amount)
                    st.rerun()
        
        else:
            # Display dealer's hand
            st.markdown("### 🎩 Dealer")
            dealer_hand = game.dealer_hand_cards
            dealer_cards_html = "<div style='display: flex; gap: 10px; justify-content: center; margin: 10px 0;'>"
            
            if game.hand_complete:
                # Show all dealer cards
                for card in dealer_hand.cards:
                    card_img = card_renderer.get_card_image_base64(card.rank, card.suit)
                    dealer_cards_html += f"<img src='{card_img}' style='width: 80px; height: 112px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>"
                dealer_value = dealer_hand.get_value()
                st.markdown(f"{dealer_cards_html}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 18px; color: white; font-weight: bold;'>Value: {dealer_value}</p>", unsafe_allow_html=True)
            else:
                # Show first card, hide second
                if len(dealer_hand.cards) > 0:
                    first_card = dealer_hand.cards[0]
                    card_img = card_renderer.get_card_image_base64(first_card.rank, first_card.suit)
                    dealer_cards_html += f"<img src='{card_img}' style='width: 80px; height: 112px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>"
                
                # Hidden card
                hidden_card_img = card_renderer.get_card_back_base64()
                dealer_cards_html += f"<img src='{hidden_card_img}' style='width: 80px; height: 112px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>"
                
                st.markdown(f"{dealer_cards_html}</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 18px; color: white; font-weight: bold;'>Value: ?</p>", unsafe_allow_html=True)
            
            # Display player's hand(s)
            st.markdown("### 🎲 Your Hand")
            player_hands = game.player_hand
            
            for i, hand in enumerate(player_hands):
                if len(player_hands) > 1:
                    st.markdown(f"**Hand {i+1}:**")
                
                player_cards_html = "<div style='display: flex; gap: 10px; justify-content: center; margin: 10px 0;'>"
                for card in hand.cards:
                    card_img = card_renderer.get_card_image_base64(card.rank, card.suit)
                    player_cards_html += f"<img src='{card_img}' style='width: 80px; height: 112px; border-radius: 8px; box-shadow: 2px 2px 5px rgba(0,0,0,0.3);'>"
                
                player_cards_html += "</div>"
                st.markdown(player_cards_html, unsafe_allow_html=True)
                
                hand_value = hand.get_value()
                soft_indicator = " (Soft)" if hand.is_soft() else ""
                
                st.markdown(f"<p style='text-align: center; font-size: 18px; color: white; font-weight: bold;'>Value: {hand_value}{soft_indicator}</p>", unsafe_allow_html=True)
                
                if hand.is_busted():
                    st.markdown("<p style='text-align: center; color: #ff4444; font-weight: bold; font-size: 16px;'>BUST!</p>", unsafe_allow_html=True)
                elif hand.is_blackjack():
                    st.markdown("<p style='text-align: center; color: #44ff44; font-weight: bold; font-size: 16px;'>BLACKJACK! 🎉</p>", unsafe_allow_html=True)
            
            # AI Coach and Card Counting Section
            st.markdown("### 🤖 AI Coach & Card Counting")
            
            # Counting system selection
            col1, col2, col3 = st.columns(3)
            with col1:
                counting_system = st.selectbox(
                    "Counting System:",
                    ['Hi-Lo', 'KO', 'Hi-Opt I', 'Hi-Opt II', 'Omega II'],
                    index=['Hi-Lo', 'KO', 'Hi-Opt I', 'Hi-Opt II', 'Omega II'].index(st.session_state.counting_system)
                )
                if counting_system != st.session_state.counting_system:
                    st.session_state.counting_system = counting_system
                    st.session_state.coach.set_counting_system(counting_system)
                    st.rerun()
            
            with col2:
                if st.button("Get Hint", use_container_width=True):
                    st.session_state.show_advice = True
                    st.rerun()
            
            with col3:
                if st.button("Show Count", use_container_width=True):
                    st.session_state.show_count = True
                    st.rerun()
            
            # Display AI recommendation if requested
            if st.session_state.show_advice and game.can_player_act():
                current_hand = game.player_hand[game.current_hand_index] if hasattr(game, 'current_hand_index') else game.player_hand[0]
                dealer_upcard = game.dealer_hand.cards[0] if game.dealer_hand.cards else None
                
                if dealer_upcard:
                    recommendation = st.session_state.coach.get_recommendation(
                        [current_hand], dealer_upcard, show_advice=True
                    )
                    
                    st.info(f"**AI Recommendation:** {recommendation['action']}")
                    st.caption(f"Reason: {recommendation['reason']}")
                    st.caption(f"Win Probability: {recommendation['win_probability']:.1%}")
            
            # Card counting practice
            if hasattr(game, 'dealt_cards') and game.dealt_cards:
                st.markdown("#### 🔢 Card Counting Practice")
                
                count_info = st.session_state.coach.get_count_info(
                    game.dealt_cards, 
                    st.session_state.show_count
                )
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    player_guess = st.number_input(
                        "Your count guess:", 
                        min_value=-50, 
                        max_value=50, 
                        value=0,
                        key="count_guess",
                        help="Enter your running count based on cards seen"
                    )
                
                with col2:
                    if st.button("Check Count", use_container_width=True):
                        result = st.session_state.coach.test_counting_knowledge(
                            game.dealt_cards, 
                            player_guess
                        )
                        
                        if result['is_correct']:
                            st.success(f"✓ Correct! Running count: {result['actual_count']}")
                        else:
                            st.error(f"✗ Incorrect. Actual: {result['actual_count']}, Your guess: {result['player_guess']}")
                        
                        # Log this counting attempt for analysis
                        current_user = st.session_state.user_manager.get_current_user()
                        if current_user:
                            situation = {
                                'cards_seen': len(game.dealt_cards),
                                'actual_count': result['actual_count'],
                                'system': result['system']
                            }
                            st.session_state.coach.log_player_decision(
                                situation, str(player_guess), str(result['actual_count']), 
                                "correct" if result['is_correct'] else "incorrect"
                            )
                
                with col3:
                    if st.session_state.show_count:
                        st.metric("Running Count", count_info.get('running_count', 0))
                        st.metric("True Count", f"{count_info.get('true_count', 0):.1f}")
                        
                        # Show additional counting info
                        if count_info.get('betting_advantage'):
                            advantage = count_info['betting_advantage']
                            if advantage > 0:
                                st.info(f"Player advantage: +{advantage:.1%}")
                            else:
                                st.warning(f"House advantage: {advantage:.1%}")
                    else:
                        st.info("Hidden - use 'Show Count'")
                        st.caption("Practice counting without seeing the actual values")
                
                # Show count values for selected system
                with st.expander("📚 Count Values Reference"):
                    count_values = st.session_state.coach.get_count_values(st.session_state.counting_system)
                    cols = st.columns(4)
                    for i, (card, value) in enumerate(count_values.items()):
                        with cols[i % 4]:
                            color = "green" if value > 0 else "red" if value < 0 else "gray"
                            st.markdown(f"**{card}**: <span style='color:{color}'>{value:+d}</span>", unsafe_allow_html=True)
            
            # Player actions
            if game.can_player_act():
                st.markdown("### 🎯 Choose Your Action")
                col_hit, col_stand, col_double, col_split = st.columns(4)
                
                with col_hit:
                    if st.button("👆 Hit", type="secondary", use_container_width=True):
                        # Log the decision for AI coach analysis
                        current_hand = game.player_hand[0] if game.player_hand else None
                        dealer_upcard = game.dealer_hand.cards[0] if game.dealer_hand.cards else None
                        
                        if current_hand and dealer_upcard:
                            # Get correct action for comparison
                            recommendation = st.session_state.coach.get_recommendation([current_hand], dealer_upcard, show_advice=True)
                            situation = {
                                'player_total': current_hand.get_value(),
                                'dealer_upcard': dealer_upcard.get_value(),
                                'is_soft': current_hand.is_soft(),
                                'can_double': len(current_hand.cards) == 2,
                                'can_split': current_hand.can_split()
                            }
                            st.session_state.coach.log_player_decision(
                                situation, "Hit", recommendation['basic_strategy'], "pending"
                            )
                        
                        game.player_hit()
                        st.session_state.show_advice = False
                        st.rerun()
                
                with col_stand:
                    if st.button("✋ Stand", type="secondary", use_container_width=True):
                        # Log the decision for AI coach analysis
                        current_hand = game.player_hand[0] if game.player_hand else None
                        dealer_upcard = game.dealer_hand.cards[0] if game.dealer_hand.cards else None
                        
                        if current_hand and dealer_upcard:
                            recommendation = st.session_state.coach.get_recommendation([current_hand], dealer_upcard, show_advice=True)
                            situation = {
                                'player_total': current_hand.get_value(),
                                'dealer_upcard': dealer_upcard.get_value(),
                                'is_soft': current_hand.is_soft(),
                                'can_double': len(current_hand.cards) == 2,
                                'can_split': current_hand.can_split()
                            }
                            st.session_state.coach.log_player_decision(
                                situation, "Stand", recommendation['basic_strategy'], "pending"
                            )
                        
                        game.player_stand()
                        st.session_state.show_advice = False
                        st.rerun()
                
                with col_double:
                    if game.can_double_down():
                        if st.button("⬆️ Double", type="secondary", use_container_width=True):
                            # Log the decision for AI coach analysis
                            current_hand = game.player_hand[0] if game.player_hand else None
                            dealer_upcard = game.dealer_hand.cards[0] if game.dealer_hand.cards else None
                            
                            if current_hand and dealer_upcard:
                                recommendation = st.session_state.coach.get_recommendation([current_hand], dealer_upcard, show_advice=True)
                                situation = {
                                    'player_total': current_hand.get_value(),
                                    'dealer_upcard': dealer_upcard.get_value(),
                                    'is_soft': current_hand.is_soft(),
                                    'can_double': True,
                                    'can_split': current_hand.can_split()
                                }
                                st.session_state.coach.log_player_decision(
                                    situation, "Double", recommendation['basic_strategy'], "pending"
                                )
                            
                            game.double_down()
                            st.session_state.show_advice = False
                            st.rerun()
                    else:
                        st.button("⬆️ Double", disabled=True, use_container_width=True)
                
                with col_split:
                    if game.can_split():
                        if st.button("↔️ Split", type="secondary", use_container_width=True):
                            # Log the decision for AI coach analysis
                            current_hand = game.player_hand[0] if game.player_hand else None
                            dealer_upcard = game.dealer_hand.cards[0] if game.dealer_hand.cards else None
                            
                            if current_hand and dealer_upcard:
                                recommendation = st.session_state.coach.get_recommendation([current_hand], dealer_upcard, show_advice=True)
                                situation = {
                                    'player_total': current_hand.get_value(),
                                    'dealer_upcard': dealer_upcard.get_value(),
                                    'is_soft': current_hand.is_soft(),
                                    'can_double': len(current_hand.cards) == 2,
                                    'can_split': True
                                }
                                st.session_state.coach.log_player_decision(
                                    situation, "Split", recommendation['basic_strategy'], "pending"
                                )
                            
                            game.split_hand()
                            st.session_state.show_advice = False
                            st.rerun()
                    else:
                        st.button("↔️ Split", disabled=True, use_container_width=True)
            
            # Show result if hand is complete
            if game.hand_complete:
                result = game.get_hand_result()
                if result['win']:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #4CAF50, #45a049); padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>🎉 WINNER! 🎉</h3>
                        <p style='color: white; margin: 5px 0; font-size: 16px;'>{result['message']}</p>
                        <p style='color: #ffff88; margin: 0; font-size: 18px; font-weight: bold;'>+${result['payout']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #f44336, #d32f2f); padding: 15px; border-radius: 10px; margin: 10px 0; text-align: center;'>
                        <h3 style='color: white; margin: 0;'>💸 House Wins</h3>
                        <p style='color: white; margin: 5px 0; font-size: 16px;'>{result['message']}</p>
                        <p style='color: #ffcccc; margin: 0; font-size: 18px; font-weight: bold;'>-${game.current_bet}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.button("🔄 New Hand", type="primary", use_container_width=True):
                    game.reset_hand()
                    st.session_state.show_advice = False  # Reset advice for new hand
                    st.session_state.show_count = False   # Reset count for new hand
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.subheader("AI Coach")
        
        if game.game_active and game.can_player_act():
            # Get AI recommendation
            try:
                current_hand = game.player_hand[game.current_hand_index] if game.current_hand_index < len(game.player_hand) else game.player_hand[0]
                dealer_upcard = game.dealer_hand_cards.cards[0] if len(game.dealer_hand_cards.cards) > 0 else None
                
                if dealer_upcard:
                    recommendation = st.session_state.coach.get_recommendation(
                        [current_hand], 
                        dealer_upcard
                    )
                    
                    if recommendation:
                        st.info(f"**Recommended Action:** {recommendation['action']}")
                        st.write(f"**Reason:** {recommendation['reason']}")
                        st.write(f"**Win Probability:** {recommendation['win_probability']:.1%}")
                    
                    # Card counting information
                    if game.cards_dealt > 0:
                        count_info = st.session_state.coach.get_count_info(game.dealt_cards)
                        st.write("**Card Count Info:**")
                        st.write(f"Running Count: {count_info['running_count']}")
                        st.write(f"True Count: {count_info['true_count']:.1f}")
                        st.write(f"Deck Penetration: {count_info['penetration']:.1%}")
                else:
                    st.write("Waiting for cards to be dealt...")
            except Exception as e:
                st.write("AI Coach initializing...")
    
    with col3:
        st.subheader("Statistics")
        stats = game.get_session_stats()
        st.metric("Hands Played", stats['hands_played'])
        st.metric("Win Rate", f"{stats['win_rate']:.1%}")
        st.metric("Net Winnings", f"${stats['net_winnings']}")
        st.metric("House Edge", f"{stats['house_edge']:.2%}")

elif page == "Strategy Analysis":
    st.header("Basic Strategy & Advanced Techniques")
    
    tab1, tab2, tab3 = st.tabs(["Basic Strategy", "Card Counting", "Advanced Strategies"])
    
    with tab1:
        st.subheader("BJA Basic Strategy Chart")
        
        # Create visual representation of the BJA strategy chart
        st.markdown("### Hard Totals")
        hard_data = []
        dealer_cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']
        
        # Hard totals from 8-17
        for total in range(8, 18):
            row = [str(total)]
            for dealer in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
                action = st.session_state.coach.basic_strategy.get_action(total, dealer, False, False, True, False)
                action_display = action.upper()[0] if action else 'H'
                row.append(action_display)
            hard_data.append(row)
        
        hard_df = pd.DataFrame(hard_data, columns=['Total'] + dealer_cards)
        st.dataframe(hard_df, use_container_width=True)
        
        st.markdown("### Soft Totals")
        soft_data = []
        
        # Soft totals A,2 through A,9
        for soft_total in range(13, 21):
            row = [f"A,{soft_total-11}"]
            for dealer in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
                action = st.session_state.coach.basic_strategy.get_action(soft_total, dealer, True, False, True, False)
                action_display = action.upper()[0] if action else 'H'
                row.append(action_display)
            soft_data.append(row)
        
        soft_df = pd.DataFrame(soft_data, columns=['Hand'] + dealer_cards)
        st.dataframe(soft_df, use_container_width=True)
        
        st.markdown("### Pair Splitting")
        pair_data = []
        
        # Pairs from 2,2 through A,A
        pairs = ['2,2', '3,3', '4,4', '5,5', '6,6', '7,7', '8,8', '9,9', '10,10', 'A,A']
        for i, pair in enumerate(pairs):
            pair_value = i + 2 if i < 9 else 11
            row = [pair]
            for dealer in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
                action = st.session_state.coach.basic_strategy.get_action(pair_value * 2, dealer, False, True, True, False)
                if 'split' in action.lower():
                    action_display = 'Y'
                else:
                    action_display = 'N'
                row.append(action_display)
            pair_data.append(row)
        
        pair_df = pd.DataFrame(pair_data, columns=['Pair'] + dealer_cards)
        st.dataframe(pair_df, use_container_width=True)
        
        # Add legend
        st.markdown("**Legend:** H=Hit, S=Stand, D=Double, Y=Split, N=Don't Split")
    
    with tab2:
        st.subheader("Card Counting Systems")
        
        counting_system = st.selectbox("Select Counting System:", [
            "Hi-Lo", "Hi-Opt I", "Hi-Opt II", "Omega II", "Red 7"
        ])
        
        count_values = st.session_state.coach.get_count_values(counting_system)
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Card Values:**")
            for card, value in count_values.items():
                st.write(f"{card}: {value:+d}")
        
        with col2:
            st.write("**Betting Strategy:**")
            betting_strategy = st.session_state.coach.get_betting_strategy()
            for count_range, bet_multiplier in betting_strategy.items():
                st.write(f"True Count {count_range}: {bet_multiplier}x base bet")
    
    with tab3:
        st.subheader("Advanced Playing Deviations")
        
        deviations = st.session_state.coach.get_playing_deviations()
        
        for situation, deviation in deviations.items():
            with st.expander(f"{situation}"):
                st.write(f"**Standard Play:** {deviation['standard']}")
                st.write(f"**Deviation:** {deviation['deviation']}")
                st.write(f"**True Count Threshold:** {deviation['threshold']:+.1f}")
                st.write(f"**Expected Value Gain:** {deviation['ev_gain']:.3f}")

elif page == "Monte Carlo Simulation":
    st.header("Monte Carlo Strategy Optimization")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Simulation Parameters")
        
        num_hands = st.number_input("Number of Hands", min_value=1000, max_value=1000000, value=10000, step=1000)
        num_decks = st.selectbox("Number of Decks", [1, 2, 4, 6, 8], index=3)
        penetration = st.slider("Deck Penetration", min_value=0.5, max_value=0.95, value=0.75, step=0.05)
        
        strategy_type = st.selectbox("Strategy Type", [
            "Basic Strategy Only",
            "Basic Strategy + Card Counting",
            "Optimized Strategy (ML)"
        ])
        
        if st.button("Run Simulation"):
            with st.spinner("Running Monte Carlo simulation..."):
                results = st.session_state.monte_carlo.run_simulation(
                    num_hands=num_hands,
                    num_decks=num_decks,
                    penetration=penetration,
                    strategy_type=strategy_type
                )
                st.session_state.simulation_results = results
    
    with col2:
        if 'simulation_results' in st.session_state:
            st.subheader("Simulation Results")
            results = st.session_state.simulation_results
            
            # Key metrics
            col_metric1, col_metric2, col_metric3 = st.columns(3)
            with col_metric1:
                st.metric("Win Rate", f"{results['win_rate']:.2%}")
            with col_metric2:
                st.metric("House Edge", f"{results['house_edge']:.3%}")
            with col_metric3:
                st.metric("Expected Hourly", f"${results['expected_hourly']:.2f}")
            
            # Results visualization
            fig_results = go.Figure()
            
            fig_results.add_trace(go.Scatter(
                x=list(range(len(results['cumulative_winnings']))),
                y=results['cumulative_winnings'],
                mode='lines',
                name='Cumulative Winnings',
                line=dict(color='blue')
            ))
            
            fig_results.update_layout(
                title="Cumulative Winnings Over Time",
                xaxis_title="Hand Number",
                yaxis_title="Cumulative Winnings ($)"
            )
            
            st.plotly_chart(fig_results, use_container_width=True)
            
            # Strategy optimization insights
            st.subheader("Strategy Insights")
            for insight in results['insights']:
                st.info(insight)

elif page == "Performance Analytics":
    st.header("📊 AI Coach Analysis")
    
    current_user = st.session_state.user_manager.get_current_user()
    
    if current_user:
        player_analysis = st.session_state.coach.get_player_analysis()
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Decision Accuracy", f"{player_analysis['overall_accuracy']:.1%}")
        with col2:
            st.metric("Total Decisions", player_analysis['total_decisions'])
        with col3:
            st.metric("Counting Accuracy", f"{player_analysis['counting_accuracy']:.1%}")
        with col4:
            correct_ratio = player_analysis['correct_decisions'] / max(1, player_analysis['total_decisions'])
            st.metric("Correct Actions", f"{correct_ratio:.1%}")
        
        # Strengths and weaknesses analysis
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Your Strengths")
            if player_analysis['strengths']:
                for strength in player_analysis['strengths']:
                    st.success(f"✓ {strength}")
            else:
                st.info("Play more hands to identify your strengths")
        
        with col2:
            st.subheader("📈 Areas to Improve")
            if player_analysis['weaknesses']:
                for weakness in player_analysis['weaknesses']:
                    st.warning(f"⚠ {weakness}")
            else:
                st.success("No major weaknesses found - great job!")
        
        # Personalized recommendations from AI coach
        if player_analysis['recommendations']:
            st.subheader("🤖 AI Coach Recommendations")
            for i, rec in enumerate(player_analysis['recommendations'], 1):
                st.info(f"{i}. {rec}")
        
        # Mistake patterns analysis
        if player_analysis['mistake_patterns']:
            st.subheader("🔍 Common Mistake Patterns")
            mistake_data = []
            for situation, count in player_analysis['mistake_patterns'].items():
                mistake_data.append({'Situation': situation.replace('_', ' vs '), 'Mistakes': count})
            
            if mistake_data:
                mistake_df = pd.DataFrame(mistake_data)
                st.dataframe(mistake_df, use_container_width=True)
        
        # Card counting progress
        if st.session_state.coach.counting_accuracy_history:
            st.subheader("📈 Card Counting Progress")
            counting_history = st.session_state.coach.counting_accuracy_history[-20:]  # Last 20 attempts
            
            fig = px.line(
                x=range(len(counting_history)), 
                y=[1 if correct else 0 for correct in counting_history],
                title="Card Counting Accuracy Over Time",
                labels={'x': 'Attempt Number', 'y': 'Correct (1) / Incorrect (0)'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Export session data
        if st.button("Export Performance Data"):
            export_data = {
                'player_analysis': player_analysis,
                'counting_history': st.session_state.coach.counting_accuracy_history,
                'session_data': st.session_state.coach.current_session,
                'counting_system': st.session_state.counting_system
            }
            
            st.download_button(
                label="Download Analysis Report",
                data=json.dumps(export_data, indent=2),
                file_name=f"blackjack_analysis_{current_user}.json",
                mime="application/json"
            )
    else:
        st.info("Please log in to view your AI coach analysis.")

elif page == "Player Dashboard":
    st.header("Player Dashboard")
    
    current_user = st.session_state.user_manager.get_current_user()
    
    if current_user:
        st.subheader(f"Welcome back, {current_user}!")
        
        # Get player statistics
        player_stats = st.session_state.user_manager.get_player_stats(current_user)
        
        if player_stats:
            # Overall statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Sessions", player_stats.get('total_sessions', 0))
            with col2:
                st.metric("Total Hands", player_stats.get('total_hands', 0))
            with col3:
                st.metric("Net Profit", f"${player_stats.get('net_profit', 0):.2f}")
            with col4:
                st.metric("Skill Level", player_stats.get('skill_level', 'Beginner'))
            
            # Performance metrics
            st.subheader("Performance Metrics")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Average Win Rate", f"{player_stats.get('average_win_rate', 0):.1%}")
            with col2:
                st.metric("House Edge", f"{player_stats.get('average_house_edge', 0):.3%}")
            with col3:
                st.metric("Decision Accuracy", f"{player_stats.get('average_decision_accuracy', 0):.1%}")
            
            # Session history
            st.subheader("Recent Sessions")
            session_history = st.session_state.user_manager.get_session_history(current_user, 10)
            
            if session_history:
                session_df = pd.DataFrame(session_history)
                session_df['start_time'] = pd.to_datetime(session_df['start_time'])
                session_df = session_df.sort_values('start_time', ascending=False)
                
                # Display as table
                st.dataframe(session_df[['start_time', 'hands_played', 'net_result', 'win_rate', 'decision_accuracy']], 
                           use_container_width=True)
                
                # Performance trend chart
                if len(session_df) > 1:
                    st.subheader("Performance Trend")
                    
                    fig_trend = px.line(session_df, 
                                      x='start_time', 
                                      y='net_result',
                                      title="Net Result Over Time")
                    st.plotly_chart(fig_trend, use_container_width=True)
            else:
                st.info("No session history available yet.")
        else:
            st.info("No player statistics available. Start playing to build your profile!")
    else:
        st.info("Please log in to view your dashboard.")

# Footer
st.markdown("---")
st.markdown("**Blackjack AI Training System** - Developed with advanced ML algorithms and Monte Carlo optimization")
