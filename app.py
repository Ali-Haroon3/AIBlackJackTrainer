import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from game_engine import BlackjackGame
from ai_coach import AICoach
from monte_carlo import MonteCarloSimulator
from analytics import Analytics
from card_visuals import CardRenderer, create_table_background
import time

# Initialize session state
if 'game' not in st.session_state:
    st.session_state.game = BlackjackGame()
if 'coach' not in st.session_state:
    st.session_state.coach = AICoach()
if 'analytics' not in st.session_state:
    st.session_state.analytics = Analytics()
if 'monte_carlo' not in st.session_state:
    st.session_state.monte_carlo = MonteCarloSimulator()
if 'card_renderer' not in st.session_state:
    st.session_state.card_renderer = CardRenderer()

st.set_page_config(
    page_title="Blackjack AI Training",
    page_icon="🃏",
    layout="wide"
)

st.title("🃏 Blackjack AI Training & Strategy Optimization")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.selectbox("Choose a section:", [
    "Game Training", 
    "Strategy Analysis", 
    "Monte Carlo Simulation", 
    "Performance Analytics"
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
            
            # Player actions
            if game.can_player_act():
                st.markdown("### 🎯 Choose Your Action")
                col_hit, col_stand, col_double, col_split = st.columns(4)
                
                with col_hit:
                    if st.button("👆 Hit", type="secondary", use_container_width=True):
                        game.player_hit()
                        st.rerun()
                
                with col_stand:
                    if st.button("✋ Stand", type="secondary", use_container_width=True):
                        game.player_stand()
                        st.rerun()
                
                with col_double:
                    if game.can_double_down():
                        if st.button("⬆️ Double", type="secondary", use_container_width=True):
                            game.double_down()
                            st.rerun()
                    else:
                        st.button("⬆️ Double", disabled=True, use_container_width=True)
                
                with col_split:
                    if game.can_split():
                        if st.button("↔️ Split", type="secondary", use_container_width=True):
                            game.split_hand()
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
        st.subheader("Basic Strategy Chart")
        strategy_chart = st.session_state.coach.get_basic_strategy_chart()
        
        fig = go.Figure(data=go.Heatmap(
            z=strategy_chart['values'],
            x=strategy_chart['dealer_cards'],
            y=strategy_chart['player_hands'],
            colorscale='RdYlGn',
            text=strategy_chart['actions'],
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title="Basic Strategy Chart",
            xaxis_title="Dealer Upcard",
            yaxis_title="Player Hand"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
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
    st.header("Training Performance Analytics")
    
    analytics = st.session_state.analytics
    
    # Load historical data
    performance_data = analytics.get_performance_data()
    
    if len(performance_data) > 0:
        tab1, tab2, tab3 = st.tabs(["Skill Progression", "Decision Analysis", "Counting Accuracy"])
        
        with tab1:
            st.subheader("Skill Development Over Time")
            
            # Win rate progression
            fig_winrate = px.line(
                performance_data, 
                x='session_date', 
                y='win_rate',
                title="Win Rate Progression"
            )
            st.plotly_chart(fig_winrate, use_container_width=True)
            
            # House edge reduction
            fig_house_edge = px.line(
                performance_data,
                x='session_date',
                y='house_edge',
                title="House Edge Reduction Over Time"
            )
            st.plotly_chart(fig_house_edge, use_container_width=True)
        
        with tab2:
            st.subheader("Decision Making Analysis")
            
            decision_accuracy = analytics.get_decision_accuracy()
            
            fig_decisions = px.bar(
                x=list(decision_accuracy.keys()),
                y=list(decision_accuracy.values()),
                title="Decision Accuracy by Action Type"
            )
            st.plotly_chart(fig_decisions, use_container_width=True)
            
            # Common mistakes
            st.subheader("Most Common Mistakes")
            mistakes = analytics.get_common_mistakes()
            for i, mistake in enumerate(mistakes[:5], 1):
                st.write(f"{i}. {mistake['situation']}: {mistake['incorrect_action']} → {mistake['correct_action']} ({mistake['frequency']} times)")
        
        with tab3:
            st.subheader("Card Counting Accuracy")
            
            counting_data = analytics.get_counting_accuracy()
            
            if len(counting_data) > 0:
                fig_counting = px.line(
                    counting_data,
                    x='hand_number',
                    y='accuracy',
                    title="Card Counting Accuracy Over Session"
                )
                st.plotly_chart(fig_counting, use_container_width=True)
                
                # Accuracy by count level
                accuracy_by_count = analytics.get_accuracy_by_count_level()
                fig_count_accuracy = px.bar(
                    x=list(accuracy_by_count.keys()),
                    y=list(accuracy_by_count.values()),
                    title="Counting Accuracy by True Count Level"
                )
                st.plotly_chart(fig_count_accuracy, use_container_width=True)
    
    else:
        st.info("No performance data available yet. Play some hands to see your analytics!")
        
        # Initialize tracking
        if st.button("Start Performance Tracking"):
            analytics.initialize_tracking()
            st.success("Performance tracking initialized!")

# Footer
st.markdown("---")
st.markdown("**Blackjack AI Training System** - Developed with advanced ML algorithms and Monte Carlo optimization")
