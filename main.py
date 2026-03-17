import os
import time
from dotenv import load_dotenv
from modules.market_data import get_current_status, get_market_analysis_data, get_account_balance
from modules.ai_decision import AIDecider
from modules.risk_manager import validate_decision
from modules.logger import log_decision

# Load Environment Variables
load_dotenv()

def run_trading_cycle():
    print("\n" + "="*50)
    print(f"Starting AI Trading Cycle: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)

    # 1. Fetch Market Data & Balance
    ticker = "KRW-BTC"
    print(f"[*] Fetching market data for {ticker}...")
    market_status = get_current_status(ticker)
    account_info = get_account_balance("BTC")
    
    if "error" in market_status:
        print(f"[!] Error fetching status: {market_status['error']}")
        return

    print(f"[+] Current Price: {market_status['current_price']:,} KRW")
    print(f"[+] Account Balance: {account_info.get('balance', 0)} BTC")

    # 2. Prepare Detailed Data for AI
    analysis_data = get_market_analysis_data(ticker)
    # Include balance context for AI
    analysis_data['account_balance'] = account_info

    # 3. Get AI Decision
    print("[*] Requesting AI analysis (In Korean)...")
    decider = AIDecider()
    decision = decider.decide(analysis_data)

    # 4. Validate & Risk Check
    if validate_decision(decision):
        print("\n--- AI DECISION ---")
        print(f"Decision: {decision['decision']}")
        print(f"Confidence: {decision['confidence'] * 100}%")
        print(f"Reason: {decision['reason']}")
        print("-------------------\n")
        
        # 5. Log the decision
        log_decision(decision, market_status['current_price'], account_info, analysis_data)
        print("[+] Logged decision with full market data to logs/trading_log.json")
        
        # ⚠️ MVP: Physical execution is DISABLED
        print("[!] Execution mode: MVP (Observation Only)")
    else:
        print("[!] Invalid decision received from AI. Falling back to HOLD.")

if __name__ == "__main__":
    try:
        run_trading_cycle()
    except KeyboardInterrupt:
        print("\n[!] Program terminated by user.")
    except Exception as e:
        print(f"\n[!] Unexpected error: {e}")
