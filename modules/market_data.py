import pyupbit
import pandas as pd
from typing import Dict, Optional
import ta
from ta.momentum import RSIIndicator
from ta.trend import MACD
from ta.volatility import BollingerBands
import os
from dotenv import load_dotenv

def get_account_balance(ticker: str = "BTC") -> Dict:
    """
    Returns the current balance and average buy price for the given ticker.
    """
    try:
        load_dotenv()
        access = os.getenv('UPBIT_ACCESS_KEY')
        secret = os.getenv('UPBIT_SECRET_KEY')
        upbit = pyupbit.Upbit(access, secret)
        
        balances = upbit.get_balances()
        for b in balances:
            if b['currency'] == ticker:
                return {
                    "balance": float(b['balance']),
                    "avg_buy_price": float(b['avg_buy_price']),
                    "unit_currency": b['unit_currency']
                }
        return {"balance": 0.0, "avg_buy_price": 0.0, "unit_currency": "KRW"}
    except Exception as e:
        return {"error": str(e)}

def get_current_status(ticker: str = "KRW-BTC") -> Dict:
    """
    Retrieves the current market status for a specific ticker.
    """
    try:
        current_price = pyupbit.get_current_price(ticker)
        # Get 24h OHLCV for basic context
        df_daily = pyupbit.get_ohlcv(ticker, interval="day", count=2)
        
        if df_daily is None or df_daily.empty:
            return {"error": "Could not fetch market data"}
            
        prev_close = df_daily.iloc[0]['close']
        change_rate = ((current_price - prev_close) / prev_close) * 100
        
        return {
            "ticker": ticker,
            "current_price": current_price,
            "prev_close": prev_close,
            "change_rate_24h": round(change_rate, 2),
            "high": df_daily.iloc[-1]['high'],
            "low": df_daily.iloc[-1]['low'],
            "volume": df_daily.iloc[-1]['volume']
        }
    except Exception as e:
        return {"error": str(e)}

def get_market_analysis_data(ticker: str = "KRW-BTC") -> Dict:
    """
    Fetches rich market data for AI analysis, including technical indicators.
    """
    try:
        # Fetch hourly data for the last 100 hours to have enough data for indicators
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count=100)
        
        if df is None or df.empty:
            return {"error": "Failed to retrieve OHLCV data"}

        # 1. Add Technical Indicators
        # RSI
        df['rsi'] = RSIIndicator(close=df['close'], window=14).rsi()
        
        # MACD
        macd = MACD(close=df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        df['macd_diff'] = macd.macd_diff()
        
        # Bollinger Bands
        bb = BollingerBands(close=df['close'])
        df['bb_high'] = bb.bollinger_hband()
        df['bb_low'] = bb.bollinger_lband()
        df['bb_mid'] = bb.bollinger_mavg()

        # 2. Get the latest 24 hours of data including indicators
        last_24h_df = df.tail(24).copy()
        
        # 3. Fix: Convert Timestamp index to string for JSON serialization
        last_24h_df.index = last_24h_df.index.strftime('%Y-%m-%d %H:%M:%S')
        
        # Basic summary for AI
        summary = {
            "ticker": ticker,
            "current_price": pyupbit.get_current_price(ticker),
            "market_summary_24h": {
                "rsi_avg": round(last_24h_df['rsi'].mean(), 2),
                "rsi_current": round(last_24h_df['rsi'].iloc[-1], 2),
                "macd_current": round(last_24h_df['macd'].iloc[-1], 2),
                "bb_current_upper": round(last_24h_df['bb_high'].iloc[-1], 2),
                "bb_current_lower": round(last_24h_df['bb_low'].iloc[-1], 2),
            },
            "ohlcv_with_indicators_last_24h": last_24h_df.to_dict(orient='index')
        }
        
        return summary
    except Exception as e:
        return {"error": f"Error in get_market_analysis_data: {str(e)}"}
