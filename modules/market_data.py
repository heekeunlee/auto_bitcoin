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

        # --- NEW INDICATORS ---
        # 1. Stochastic Oscillator
        stoch = ta.momentum.StochasticOscillator(high=df['high'], low=df['low'], close=df['close'], window=14, smooth_window=3)
        df['stoch_k'] = stoch.stoch()
        df['stoch_d'] = stoch.stoch_signal()

        # 2. ADX (Average Directional Index) - Trend Strength
        adx = ta.trend.ADXIndicator(high=df['high'], low=df['low'], close=df['close'], window=14)
        df['adx'] = adx.adx()

        # 3. Moving Averages (EMA 20, 50, 200) - Trend Confirmation
        df['ema_20'] = ta.trend.EMAIndicator(close=df['close'], window=20).ema_indicator()
        df['ema_50'] = ta.trend.EMAIndicator(close=df['close'], window=50).ema_indicator()
        df['ema_200'] = ta.trend.EMAIndicator(close=df['close'], window=200).ema_indicator()

        # 4. ATR (Average True Range) - Volatility
        df['atr'] = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()

        # 5. OBV (On-Balance Volume) - Volume Trend
        df['obv'] = ta.volume.OnBalanceVolumeIndicator(close=df['close'], volume=df['volume']).on_balance_volume()

        # 2. Get the latest 24 hours of data including indicators
        last_24h_df = df.tail(24).copy()
        
        # 3. Fix: Convert Timestamp index to string for JSON serialization
        last_24h_df.index = last_24h_df.index.strftime('%Y-%m-%d %H:%M:%S')
        
        # Basic summary for AI
        summary = {
            "ticker": ticker,
            "current_price": pyupbit.get_current_price(ticker),
            "market_summary_now": {
                "rsi": round(last_24h_df['rsi'].iloc[-1], 2),
                "macd": round(last_24h_df['macd'].iloc[-1], 2),
                "stoch_k": round(last_24h_df['stoch_k'].iloc[-1], 2),
                "adx": round(last_24h_df['adx'].iloc[-1], 2),
                "trend_ema20_vs_50": "Bullish" if last_24h_df['ema_20'].iloc[-1] > last_24h_df['ema_50'].iloc[-1] else "Bearish",
                "volatility_atr": round(last_24h_df['atr'].iloc[-1], 2)
            },
            "ohlcv_with_indicators_last_24h": last_24h_df.to_dict(orient='index')
        }
        
        return summary
    except Exception as e:
        return {"error": f"Error in get_market_analysis_data: {str(e)}"}
