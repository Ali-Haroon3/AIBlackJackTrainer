# Blackjack AI Training Application

## Overview

This is a comprehensive Python-based blackjack training application with AI coaching, card counting practice, and Monte Carlo strategy optimization. The application is built using Streamlit for the web interface and provides an interactive casino-style blackjack table with professional card graphics, basic strategy charts, and advanced analytics.

## System Architecture

### Frontend Architecture
- **Streamlit Web Interface**: Interactive web application with real-time updates
- **Responsive Design**: Wide layout configuration for optimal table visualization
- **Component-Based Structure**: Modular UI components for different game sections
- **Visual Card Rendering**: Professional card graphics with SVG support
- **Interactive Controls**: Real-time button inputs and form handling

### Backend Architecture
- **Game Engine**: Core blackjack logic with proper card handling and game state management
- **AI Coach System**: Machine learning-powered decision recommendations with pattern analysis
- **Analytics Engine**: Comprehensive performance tracking and statistical analysis
- **Strategy Implementation**: Professional BJA (Blackjack Apprenticeship) strategy charts
- **Card Counting Systems**: Multiple counting systems (Hi-Lo, Hi-Opt I/II, Omega II)

## Key Components

### Core Game Components
1. **BlackjackGame (`game_engine.py`)**: Main game logic, card dealing, and hand evaluation
2. **Card and Deck Classes**: Proper card representation with suits and values
3. **Hand Management**: Player and dealer hand tracking with soft/hard total calculation
4. **Betting System**: Configurable bet amounts and payout calculations

### AI and Strategy Components
1. **EnhancedAICoach (`enhanced_ai_coach.py`)**: ML-powered coaching with personalized recommendations
2. **BJABasicStrategy (`bja_strategy.py`)**: Professional strategy implementation
3. **BasicStrategy (`strategy_tables.py`)**: Alternative strategy table implementation
4. **CardCounter (`card_counting.py`)**: Multiple counting system support

### Analytics and Data Components
1. **Analytics (`analytics.py`)**: Performance tracking and statistical analysis
2. **Database (`database.py`)**: SQLAlchemy-based data persistence with PostgreSQL support
3. **UserManager (`user_management.py`)**: Player profile and session management
4. **MonteCarloSimulator (`monte_carlo.py`)**: Advanced strategy optimization

### Visualization Components
1. **CardRenderer (`card_visuals.py`)**: Professional card graphics rendering
2. **BlackjackTable (`blackjack_table.py`)**: Realistic casino table interface
3. **BJAChartRenderer (`bja_charts.py`)**: Color-coded strategy chart display

## Data Flow

### Game Session Flow
1. **User Authentication**: Simple username-based login/registration
2. **Game Initialization**: Deck creation, shuffle, and initial dealing
3. **Decision Making**: Player input with optional AI coaching
4. **Hand Resolution**: Dealer play and outcome determination
5. **Analytics Recording**: Performance metrics and decision tracking
6. **Session Summary**: Statistical analysis and improvement recommendations

### Data Persistence Flow
1. **PostgreSQL Primary**: Full-featured database with comprehensive schema
2. **SQLite Fallback**: Local database when PostgreSQL unavailable
3. **Session Tracking**: Real-time performance metrics
4. **Historical Analysis**: Long-term skill progression tracking

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Web application framework and UI components
- **SQLAlchemy**: Database ORM and connection management
- **Pandas/Numpy**: Data manipulation and numerical computations
- **Plotly**: Interactive charts and visualizations

### Machine Learning Dependencies
- **Scikit-learn**: ML model training and prediction
- **Pickle**: Model serialization and persistence

### Database Dependencies
- **PostgreSQL**: Primary database (optional)
- **psycopg2-binary**: PostgreSQL Python adapter
- **SQLite**: Built-in fallback database

### Optional AI Enhancement
- **Anthropic API**: Advanced AI coaching features (requires API key)

### Web Scraping and Content
- **Requests**: HTTP client for external data
- **BeautifulSoup4**: HTML parsing for strategy content
- **Trafilatura**: Web content extraction
- **Pillow**: Image processing for card graphics

## Deployment Strategy

### Replit Deployment
- **Target**: Autoscale deployment on Replit platform
- **Port Configuration**: Streamlit on port 5000 (external port 80)
- **Environment**: Python 3.11 with PostgreSQL 16 support
- **Dependencies**: UV package manager with locked dependencies

### Local Development
- **Python Requirements**: 3.8+ with comprehensive package list
- **Database**: Optional PostgreSQL, fallback to SQLite
- **Environment Variables**: Configurable via .env file
- **Asset Management**: Automatic card image downloading

### Configuration Management
- **Environment Variables**: Database, API keys, and application settings
- **Graceful Fallbacks**: SQLite when PostgreSQL unavailable, basic coaching without AI
- **Asset Handling**: Fallback card rendering when images unavailable

## Changelog

```
Changelog:
- June 14, 2025: Initial setup
- June 14, 2025: Major interface redesign with bankroll management
- June 14, 2025: Added interactive card counting practice with user validation
- June 14, 2025: Fixed AI recommendation visibility issue
- June 14, 2025: Removed duplicate training controls and added split functionality
- June 14, 2025: Prepared AWS Amplify deployment configuration
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```