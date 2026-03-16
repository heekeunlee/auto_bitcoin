from datetime import datetime
import json
import os

def log_decision(decision_data: dict, price: float, account_info: dict = None, log_file: str = "logs/trading_log.json"):
    """
    Logs the AI decision and market context to a JSON file.
    """
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_price": price,
        "balance": account_info.get('balance', 0) if account_info else 0,
        "avg_buy_price": account_info.get('avg_buy_price', 0) if account_info else 0,
        **decision_data
    }
    
    try:
        # Load existing logs
        if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        else:
            logs = []
            
        logs.append(log_entry)
        
        # Save updated logs
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=4, ensure_ascii=False)
            
        return True
    except Exception as e:
        print(f"Logging failed: {e}")
        return False
