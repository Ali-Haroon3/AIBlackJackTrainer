import streamlit as st
import pandas as pd
from typing import Dict, List

class BJAChartRenderer:
    """Render BJA strategy charts with proper color coding and formatting"""
    
    def __init__(self):
        # Color scheme matching BJA charts
        self.colors = {
            'hit': '#FF6B6B',        # Red for Hit
            'stand': '#4ECDC4',      # Teal for Stand  
            'double': '#45B7D1',     # Blue for Double
            'split': '#96CEB4',      # Green for Split
            'surrender': '#FECA57',   # Yellow for Surrender
            'header': '#2C3E50',     # Dark for headers
            'background': '#F8F9FA'   # Light background
        }
        
        # S17 Strategy (Dealer stands on soft 17)
        self.s17_hard_totals = {
            17: ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
            16: ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
            15: ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
            14: ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
            13: ['S', 'S', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
            12: ['H', 'H', 'S', 'S', 'S', 'H', 'H', 'H', 'H', 'H'],
            11: ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H'],
            10: ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'H', 'H'],
            9:  ['H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'],
            8:  ['H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H', 'H']
        }
        
        self.s17_soft_totals = {
            'A,9': ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
            'A,8': ['S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S', 'S'],
            'A,7': ['S', 'Ds', 'Ds', 'Ds', 'Ds', 'S', 'S', 'H', 'H', 'H'],
            'A,6': ['H', 'D', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'],
            'A,5': ['H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'],
            'A,4': ['H', 'H', 'D', 'D', 'D', 'H', 'H', 'H', 'H', 'H'],
            'A,3': ['H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H'],
            'A,2': ['H', 'H', 'H', 'D', 'D', 'H', 'H', 'H', 'H', 'H']
        }
        
        self.s17_pairs = {
            'A,A': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
            'T,T': ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
            '9,9': ['Y', 'Y', 'Y', 'Y', 'Y', 'N', 'Y', 'Y', 'N', 'N'],
            '8,8': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y'],
            '7,7': ['Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N'],
            '6,6': ['Y/N', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N', 'N'],
            '5,5': ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N'],
            '4,4': ['N', 'N', 'N', 'Y/N', 'Y/N', 'N', 'N', 'N', 'N', 'N'],
            '3,3': ['Y/N', 'Y/N', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N'],
            '2,2': ['Y/N', 'Y/N', 'Y', 'Y', 'Y', 'Y', 'N', 'N', 'N', 'N']
        }
        
        # H17 Strategy (Dealer hits on soft 17) - slight differences
        self.h17_hard_totals = self.s17_hard_totals.copy()
        self.h17_hard_totals[11] = ['D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D', 'D']  # 11 vs A is double in H17
        
        self.h17_soft_totals = self.s17_soft_totals.copy()
        self.h17_soft_totals['A,8'] = ['S', 'S', 'S', 'S', 'Ds', 'S', 'S', 'S', 'S', 'S']  # A,8 vs 6 is Ds in H17
        
        self.h17_pairs = self.s17_pairs.copy()
        
        self.surrender_s17 = {
            16: ['', '', '', '', '', '', '', '', 'SUR', 'SUR'],
            15: ['', '', '', '', '', '', '', '', '', 'SUR']
        }
        
        self.surrender_h17 = {
            17: ['', '', '', '', '', '', '', '', '', 'SUR'],
            16: ['', '', '', '', '', '', '', 'SUR', 'SUR', 'SUR'],
            15: ['', '', '', '', '', '', '', '', 'SUR', 'SUR']
        }
        
        self.dealer_cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'A']
    
    def get_cell_color(self, action: str) -> str:
        """Get background color for action"""
        if action == 'H':
            return self.colors['hit']
        elif action == 'S':
            return self.colors['stand']
        elif action in ['D', 'Ds']:
            return self.colors['double']
        elif action in ['Y', 'Y/N']:
            return self.colors['split']
        elif action == 'SUR':
            return self.colors['surrender']
        else:
            return self.colors['background']
    
    def render_strategy_table(self, data: Dict, title: str, row_labels: List[str]):
        """Render a strategy table with color coding"""
        st.markdown(f"### {title}")
        
        # Create HTML table with color coding
        html = f"""
        <div style="overflow-x: auto;">
        <table style="border-collapse: collapse; width: 100%; margin: 10px 0;">
        <thead>
        <tr style="background-color: {self.colors['header']};">
        <th style="color: white; padding: 8px; border: 1px solid #ddd; text-align: center;">Hand</th>
        """
        
        for card in self.dealer_cards:
            html += f'<th style="color: white; padding: 8px; border: 1px solid #ddd; text-align: center;">{card}</th>'
        
        html += '</tr></thead><tbody>'
        
        for i, (hand, actions) in enumerate(data.items()):
            label = row_labels[i] if i < len(row_labels) else str(hand)
            html += f'<tr><td style="background-color: {self.colors["header"]}; color: white; padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{label}</td>'
            
            for action in actions:
                bg_color = self.get_cell_color(action)
                text_color = 'white' if action in ['H', 'S', 'D', 'Ds', 'SUR'] else 'black'
                html += f'<td style="background-color: {bg_color}; color: {text_color}; padding: 8px; border: 1px solid #ddd; text-align: center; font-weight: bold;">{action}</td>'
            
            html += '</tr>'
        
        html += '</tbody></table></div>'
        st.markdown(html, unsafe_allow_html=True)
    
    def render_s17_charts(self):
        """Render S17 strategy charts"""
        st.markdown("## S17 Basic Strategy")
        st.markdown("*Dealer stands on soft 17*")
        
        # Hard totals
        hard_labels = [str(i) for i in range(17, 7, -1)]
        self.render_strategy_table(self.s17_hard_totals, "Hard Totals", hard_labels)
        
        # Soft totals  
        soft_labels = list(self.s17_soft_totals.keys())
        self.render_strategy_table(self.s17_soft_totals, "Soft Totals", soft_labels)
        
        # Pairs
        pair_labels = list(self.s17_pairs.keys())
        self.render_strategy_table(self.s17_pairs, "Pair Splitting", pair_labels)
        
        # Surrender
        if self.surrender_s17:
            surrender_labels = [str(i) for i in self.surrender_s17.keys()]
            self.render_strategy_table(self.surrender_s17, "Late Surrender", surrender_labels)
    
    def render_h17_charts(self):
        """Render H17 strategy charts"""
        st.markdown("## H17 Basic Strategy")
        st.markdown("*Dealer hits on soft 17*")
        
        # Hard totals
        hard_labels = [str(i) for i in range(17, 7, -1)]
        self.render_strategy_table(self.h17_hard_totals, "Hard Totals", hard_labels)
        
        # Soft totals
        soft_labels = list(self.h17_soft_totals.keys())
        self.render_strategy_table(self.h17_soft_totals, "Soft Totals", soft_labels)
        
        # Pairs
        pair_labels = list(self.h17_pairs.keys())
        self.render_strategy_table(self.h17_pairs, "Pair Splitting", pair_labels)
        
        # Surrender
        if self.surrender_h17:
            surrender_labels = [str(i) for i in self.surrender_h17.keys()]
            self.render_strategy_table(self.surrender_h17, "Late Surrender", surrender_labels)
    
    def render_legend(self):
        """Render color legend"""
        st.markdown("### Legend")
        
        legend_html = f"""
        <div style="display: flex; flex-wrap: wrap; gap: 15px; margin: 10px 0;">
        <div style="display: flex; align-items: center;"><div style="width: 20px; height: 20px; background-color: {self.colors['hit']}; margin-right: 5px;"></div><span><strong>H</strong> = Hit</span></div>
        <div style="display: flex; align-items: center;"><div style="width: 20px; height: 20px; background-color: {self.colors['stand']}; margin-right: 5px;"></div><span><strong>S</strong> = Stand</span></div>
        <div style="display: flex; align-items: center;"><div style="width: 20px; height: 20px; background-color: {self.colors['double']}; margin-right: 5px;"></div><span><strong>D</strong> = Double if allowed, otherwise hit</span></div>
        <div style="display: flex; align-items: center;"><div style="width: 20px; height: 20px; background-color: {self.colors['double']}; margin-right: 5px;"></div><span><strong>Ds</strong> = Double if allowed, otherwise stand</span></div>
        <div style="display: flex; align-items: center;"><div style="width: 20px; height: 20px; background-color: {self.colors['split']}; margin-right: 5px;"></div><span><strong>Y</strong> = Split the pair</span></div>
        <div style="display: flex; align-items: center;"><div style="width: 20px; height: 20px; background-color: {self.colors['split']}; margin-right: 5px;"></div><span><strong>Y/N</strong> = Split if Double After Split allowed</span></div>
        <div style="display: flex; align-items: center;"><div style="width: 20px; height: 20px; background-color: {self.colors['surrender']}; margin-right: 5px;"></div><span><strong>SUR</strong> = Surrender</span></div>
        </div>
        """
        st.markdown(legend_html, unsafe_allow_html=True)