
# PROJECT_BRIEF.md
## AI Bitcoin Auto Trading System (Python + Upbit + OpenAI)

---

# 1. Project Overview

This project builds an **AI-assisted Bitcoin trading system** using Python.

The system will:

1. Retrieve Bitcoin market data from the **Upbit exchange API**
2. Analyze the market data using **OpenAI models**
3. Generate a structured trading decision:
   - BUY
   - SELL
   - HOLD
4. Output the decision in **structured JSON format**

⚠️ Important:  
**The first milestone (MVP) must NOT execute real trades.**  
It should only produce trading decisions.

---

# 2. Development Environment

IDE: Antigravity (agent-first coding environment)

Language:
- Python 3.10+

Package manager:
- pip

Environment configuration:
- `.env` file for secrets

External APIs available:

Upbit API
- Access Key
- Secret Key

OpenAI API
- OPENAI_API_KEY

---

# 3. Required Python Libraries

Create a `requirements.txt` file with the following dependencies:

python-dotenv  
openai  
pyupbit  

Optional later:

pandas  
numpy  
ta  
loguru  

---

# 4. Project Architecture

The system must be **modular and production-ready in structure**.

Use the following project layout:

crypto-ai-trader/

main.py  
requirements.txt  
.env  

modules/

market_data.py  
ai_decision.py  
risk_manager.py  
logger.py  

logs/

trading_log.json  

---

# 5. Responsibilities of Each Module

## main.py

Entry point of the application.

Responsibilities:

- load environment variables
- retrieve market data
- call AI decision module
- print decision result
- store result in log

---

## market_data.py

Responsibilities:

Fetch Bitcoin market data from Upbit.

Functions:

get_current_price()

get_ohlcv_data()

Return data in dictionary format.

---

## ai_decision.py

Responsibilities:

Send market data to OpenAI and receive a decision.

Prompt should instruct the AI to behave like a **professional cryptocurrency trader**.

Expected JSON response format:

{
 "decision": "BUY | SELL | HOLD",
 "reason": "short explanation"
}

---

## risk_manager.py

Responsibilities:

Validate AI decision before execution.

Example rules:

- Prevent excessive position size
- Reject invalid responses
- Ensure decision format correctness

For MVP, simply validate JSON structure.

---

## logger.py

Responsibilities:

Log all AI decisions.

Log format:

{
 "timestamp": "",
 "price": "",
 "decision": "",
 "reason": ""
}

Logs should be stored in:

logs/trading_log.json

---

# 6. Environment Variables

The system must load API keys using python-dotenv.

Example `.env` file:

OPENAI_API_KEY=your_openai_key  
UPBIT_ACCESS_KEY=your_upbit_access_key  
UPBIT_SECRET_KEY=your_upbit_secret_key  

⚠️ Never hardcode API keys inside Python files.

---

# 7. Core Workflow

The system should perform the following workflow:

1. Load environment variables
2. Fetch BTC price from Upbit
3. Prepare market data payload
4. Send payload to OpenAI
5. Receive AI decision
6. Validate decision
7. Log the result
8. Print output to console

---

# 8. Example Execution Output

Console output example:

Bitcoin price: 94,000,000 KRW

AI Decision:

{
 "decision": "HOLD",
 "reason": "Market momentum unclear"
}

---

# 9. Security Requirements

Strictly enforce the following:

- API keys must only exist in `.env`
- Do not expose secrets
- Avoid committing `.env` to git

---

# 10. Coding Standards

The generated code must follow these standards:

- Modular functions
- Clear docstrings
- Type hints where appropriate
- Error handling for API calls
- Readable structure

---

# 11. Error Handling

The system must gracefully handle:

- API failures
- Network errors
- Invalid AI response
- JSON parsing errors

Fallback behavior:

If AI response fails, default decision:

HOLD

---

# 12. Future Development Phases

These are NOT required for MVP but must be considered in architecture.

Phase 2 – Technical Indicators

Add:

RSI  
MACD  
Bollinger Bands  

---

Phase 3 – Paper Trading

Simulate trades without real capital.

Track:

- virtual balance
- trade history
- performance

---

Phase 4 – Real Trading

Enable order execution via Upbit API.

Add:

- order execution module
- position tracking
- stop loss / take profit

---

Phase 5 – Monitoring Dashboard

Optional UI:

Streamlit dashboard displaying:

- trade history
- performance
- AI decisions

---

# 13. Agent Instructions

Antigravity Agent should:

1. Create the full project structure
2. Generate Python modules
3. Implement basic functionality
4. Ensure code runs successfully
5. Avoid overengineering

Focus on **clarity and modular architecture**.

---

# 14. Design Philosophy

The system should resemble a **professional quantitative trading tool** rather than a simple script.

Priorities:

- modular design
- safety
- extensibility
- maintainability

---

END OF PROJECT BRIEF
