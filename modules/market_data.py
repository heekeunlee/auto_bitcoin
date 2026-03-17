import pyupbit
import pandas as pd
from typing import Dict, Optional
import pandas_ta as pta
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
        # Fetch hourly data for the last 200 hours for EMA 200 and other long-term indicators
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count=200)
        
        if df is None or df.empty:
            return {"error": "Failed to retrieve OHLCV data"}

        # --- 1. Basic Indicators (using pandas-ta) ---
        # RSI
        df['rsi'] = df.ta.rsi(length=14)

        # MACD
        macd = df.ta.macd()
        if macd is not None:
            df['macd'] = macd.iloc[:, 0]
            df['macd_signal'] = macd.iloc[:, 2]
            df['macd_diff'] = macd.iloc[:, 1]
        
        # Bollinger Bands
        bb = df.ta.bbands(length=20, std=2)
        if bb is not None:
            df['bb_low'] = bb.iloc[:, 0]
            df['bb_mid'] = bb.iloc[:, 1]
            df['bb_high'] = bb.iloc[:, 2]

        # --- 2. Advanced Indicators (using pandas-ta) ---
        # SuperTrend
        supertrend = df.ta.supertrend(length=7, multiplier=3.0)
        if supertrend is not None:
            df['supertrend'] = supertrend.iloc[:, 0]
            df['supertrend_direction'] = supertrend.iloc[:, 1] # 1 for long, -1 for short

        # Ichimoku Cloud
        ichimoku, span = df.ta.ichimoku()
        if ichimoku is not None:
            df['span_a'] = ichimoku.iloc[:, 0]
            df['span_b'] = ichimoku.iloc[:, 1]
            df['lead_span_a'] = ichimoku.iloc[:, 2]
            df['lead_span_b'] = ichimoku.iloc[:, 3]

        # Money Flow Index (MFI)
        df['mfi'] = df.ta.mfi(length=14)

        # EMA Cloud
        df['ema_20'] = df.ta.ema(length=20)
        df['ema_50'] = df.ta.ema(length=50)
        df['ema_200'] = df.ta.ema(length=200)

        # ADX (Trend Strength)
        df_adx = df.ta.adx()
        if df_adx is not None:
            df['adx'] = df_adx.iloc[:, 0]

        # ATR (Volatility)
        df['atr'] = df.ta.atr(length=14)

        # OBV (On-Balance Volume)
        df['obv'] = df.ta.obv()

        # 2. Get the latest 24 hours of data including indicators
        # Fill NaNs/Infs with 0 to prevent invalid JSON which crashes the dashboard
        df = df.replace([float('inf'), float('-inf')], 0).fillna(0)
        last_24h_df = df.tail(24).copy()
        
        # 3. Fix: Convert Timestamp index to string for JSON serialization
        last_24h_df.index = last_24h_df.index.strftime('%Y-%m-%d %H:%M:%S')
        
        # Basic summary for AI
        summary = {
            "ticker": ticker,
            "current_price": pyupbit.get_current_price(ticker),
            "market_summary_now": {
                "rsi": round(last_24h_df['rsi'].iloc[-1], 2) if 'rsi' in last_24h_df else 0,
                "macd": round(last_24h_df['macd'].iloc[-1], 2) if 'macd' in last_24h_df else 0,
                "supertrend": last_24h_df['supertrend_direction'].iloc[-1] if 'supertrend_direction' in last_24h_df else 0, # 1: Bull, -1: Bear
                "mfi": round(last_24h_df['mfi'].iloc[-1], 2) if 'mfi' in last_24h_df else 0,
                "adx": round(last_24h_df['adx'].iloc[-1], 2) if 'adx' in last_24h_df else 0,
                "ichimoku_signal": "Above Cloud" if last_24h_df['close'].iloc[-1] > last_24h_df['lead_span_a'].iloc[-1] else "Below Cloud",
                "trend_ema20_vs_50": "Bullish" if last_24h_df['ema_20'].iloc[-1] > last_24h_df['ema_50'].iloc[-1] else "Bearish",
                "volatility_atr": round(last_24h_df['atr'].iloc[-1], 2) if 'atr' in last_24h_df else 0
            },
            "ohlcv_with_indicators_last_24h": last_24h_df.to_dict(orient='index')
        }
        
        return summary
    except Exception as e:
        return {"error": f"Error in get_market_analysis_data: {str(e)}"}
