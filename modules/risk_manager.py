def validate_decision(decision_data: dict) -> bool:
    """
    Validates the AI's decision format and performs safety checks.
    For MVP, it ensures the required keys are present.
    """
    required_keys = ["decision", "reason", "confidence"]
    
    # 1. Check if all required keys are present
    if not all(k in decision_data for k in required_keys):
        return False
        
    # 2. Check if decision is a valid type
    if decision_data["decision"] not in ["BUY", "SELL", "HOLD"]:
        return False
        
    # 3. Confidence range check
    if not (0 <= decision_data["confidence"] <= 1):
        return False
        
    return True
