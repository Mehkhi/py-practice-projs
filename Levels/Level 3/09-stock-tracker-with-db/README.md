# Stock Tracker with DB

A Python application for tracking stock prices, calculating technical indicators, setting alerts, generating charts, and backtesting strategies.

## Features

- **Daily Fetch & Store**: Fetches daily stock prices from Alpha Vantage API and stores in SQLite database without duplicates.
- **Technical Indicators**: Calculates SMA, EMA, and RSI using pandas.
- **Alerts**: Checks for overbought/oversold conditions and price crossings.
- **Charts & Export**: Generates matplotlib charts and exports data to CSV.
- **Backtesting**: Simple moving average crossover strategy with performance metrics.
- **Caching & Rate Limiting**: Implements API caching and backoff for rate limits.
- **Dockerized**: Runs in a Docker container.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set your Alpha Vantage API key in `.env`
3. Run `python main.py` to execute all features

## Docker

Build and run with Docker Compose: `docker-compose up`

## Usage

- `python fetcher.py` - Fetch and store data
- `python scheduler.py` - Run daily scheduler
- `python indicators.py` - Calculate indicators
- `python alerts.py` - Check alerts
- `python charts.py` - Generate charts and export
- `python backtest.py` - Run backtest
