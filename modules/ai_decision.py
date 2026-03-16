import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class AIDecider:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o" # Using a high-performance model for analysis

    def decide(self, market_data: dict) -> dict:
        """
        Sends market data to OpenAI and receives a trading decision.
        """
        system_prompt = """
        You are a highly sophisticated cryptocurrency quantitative analyst and trader. 
        Your task is to analyze Bitcoin (BTC) market data and provide a definitive trading decision: BUY, SELL, or HOLD.

        You are provided with:
        1. Current Price and 24h Summary.
        2. Technical Indicators (from Advanced TA Library):
           - RSI: > 70 overbought, < 30 oversold.
           - MACD: Crossovers and momentum.
           - SuperTrend: Trend direction (1 for Bullish, -1 for Bearish).
           - Ichimoku Cloud: Check if price is 'Above Cloud' (Bullish) or 'Below Cloud' (Bearish).
           - MFI (Money Flow Index): Volume-weighted RSI. High (>80) is overbought, Low (<20) is oversold.
           - ADX: Measures trend strength (values > 25 indicate a strong trend).
           - EMA (20, 50, 200): Trend confirmation. Check for Golden Cross (Short > Long) or Death Cross.
           - ATR: Measures volatility (higher ATR means higher risk/reward).
        3. Detailed 24-hour OHLCV data with hourly indicators.

        Strategic Guidelines:
        - Prioritize Capital Preservation: If the technical signals are conflicting or the trend is weak, choose 'HOLD'.
        - Fee Awareness: Each trade on Upbit costs 0.05%. Your expected profit must significantly exceed this to justify a 'BUY' or 'SELL'.
        - Multi-Factor Analysis: Look for convergence between different indicators (e.g., oversold RSI + SuperTrend Bullish + Above Ichimoku Cloud).
        - Risk Management: Avoid buying at the top of volatility ranges unless a strong breakout is confirmed by volume (MFI).

        Your response must be a strict JSON object:
        {
            "decision": "BUY" | "SELL" | "HOLD",
            "reason": "기술적 지표와 가격 액션에 기반하여 이유를 한국어로 상세히 설명해주세요.",
            "confidence": 0.0 to 1.0
        }
        """
        
        user_prompt = f"Current Market Data for BTC:\n{json.dumps(market_data, indent=2)}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            decision_json = json.loads(response.choices[0].message.content)
            return decision_json
            
        except Exception as e:
            return {
                "decision": "HOLD",
                "reason": f"Error during AI analysis: {str(e)}",
                "confidence": 0
            }
