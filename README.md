# Blackjack AI Training & Strategy Optimization

A comprehensive Python-based blackjack training application with AI coaching, card counting practice, and Monte Carlo strategy optimization using Streamlit.

## Features

- **Interactive Blackjack Training**: Realistic casino table interface with professional card graphics
- **BJA Basic Strategy Charts**: Color-coded S17/H17 strategy tables matching Blackjack Apprenticeship standards
- **AI Coach**: Machine learning-powered recommendations with real-time decision analysis
- **Card Counting Practice**: Multiple counting systems (Hi-Lo, KO, Hi-Opt I/II, Omega II)
- **Performance Analytics**: PostgreSQL-backed session tracking and skill progression analysis
- **Monte Carlo Simulation**: Advanced strategy optimization and variance analysis
- **User Management**: Individual player profiles with comprehensive statistics

## Installation

### Prerequisites
- **Python 3.8+** (tested up to 3.13)  
- **Git**  
- **PostgreSQL 14+** (optional — the app falls back to SQLite if no `DATABASE_URL` is set)

### Setup Instructions
1. **Clone the repository**
    ```
    git clone https://github.com/yourusername/blackjack-ai-training.git
    cd blackjack-ai-training
    ```
2. **Create a virtual environment & install dependencies**
    ```
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt            # pinned versions
    ```
3. **Run the application**
    ```
    python -m streamlit run app.py             # add --server.port 8501 if needed
    ```
4. **Access the application** — visit `http://localhost:8501` in your browser.

4. **Access the application** — visit `http://localhost:8501` in your browser.

## Configuration

### Database Setup
*SQLite (default demo mode)* – if `DATABASE_URL` is **not** set, the app creates `blackjack_training.db` in the project root.

*PostgreSQL (production)*  

export DATABASE_URL="postgresql://username:password@localhost:5432/blackjack_training"
(createuser -s username && createdb blackjack_training -O username)

Additional `PGHOST`, `PGPORT`, etc. are optional because the URL already encodes them.

### AI Features (optional)

For enhanced AI coaching capabilities:
```bash
export ANTHROPIC_API_KEY="your_anthropic_api_key_here"
```

## Usage

### Game Training
- Start with "Game Training" to practice basic blackjack decisions
- The AI coach provides real-time feedback and strategy recommendations
- Track your performance across sessions

### Strategy Analysis
- Study color-coded BJA basic strategy charts
- Compare S17 vs H17 dealer rule variations
- Learn optimal decision-making for every situation

### Card Counting Practice
- Practice with multiple counting systems
- Test your counting accuracy with interactive exercises
- Learn betting strategies based on true count

### Performance Analytics
- View detailed statistics on decision accuracy
- Identify strengths and weaknesses in your play
- Export session data for external analysis

## File Structure

```
blackjack-ai-training/
├── app.py                  # Main Streamlit application
├── game_engine.py          # Core blackjack game logic
├── enhanced_ai_coach.py    # AI coaching system
├── bja_strategy.py         # BJA basic strategy implementation
├── bja_charts.py          # Color-coded strategy chart renderer
├── blackjack_table.py     # Realistic casino table interface
├── card_counting.py        # Card counting systems
├── card_visuals.py         # Card rendering utilities
├── database.py            # Database models and management
├── analytics.py           # Performance tracking
├── user_management.py     # User authentication
├── monte_carlo.py         # Monte Carlo simulation
├── card_images/           # SVG card graphics from nicubunu.ro
└── attached_assets/       # BJA strategy chart references
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Card graphics courtesy of [nicubunu.ro](https://nicubunu.ro/graphics/playingcards/simple/)
- Basic strategy charts based on Blackjack Apprenticeship standards
- Built with Streamlit, scikit-learn, and PostgreSQL

## Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Production Deployment
The application is configured for deployment on platforms like:
- Streamlit Cloud
- Heroku
- Railway
- Google Cloud Run
- AWS ECS

For cloud deployment, ensure environment variables are properly configured for your database and API keys.
