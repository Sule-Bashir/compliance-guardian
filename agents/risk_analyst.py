#!/usr/bin/env python3
"""
Agent 1: Risk Analyst Agent
Scans transactions for suspicious patterns and risk indicators
"""
import json
import os
from datetime import datetime

# Mock Band SDK (replace with real import during hackathon)
class MockBandAgent:
    def __init__(self, name, role, api_key):
        self.name = name
        self.role = role
        self.api_key = api_key
        print(f"✅ {name} Agent initialized (Role: {role})")
    
    def on_message(self):
        def decorator(func):
            self.handler = func
            return func
        return decorator
    
    async def send_message(self, to, content, message_type):
        print(f"   📤 [{self.name}] → [{to}]: {message_type}")
        return {"status": "sent"}
    
    def run(self):
        print(f"🏃 {self.name} is running and listening for messages...")

# Use mock for testing (replace with: from band_sdk import BandAgent during hackathon)
BandAgent = MockBandAgent

agent = BandAgent(
    name="Risk-Analyst",
    role="risk_scanner",
    api_key=os.environ.get("BAND_API_KEY", "mock_key_123")
)

def analyze_transaction(transaction):
    """Apply risk scoring rules"""
    risk_score = 0
    flags = []
    
    if transaction["amount"] > 10000:
        risk_score += 40
        flags.append("HIGH_VALUE_TRANSACTION")
    
    high_risk_countries = ["KY", "PA", "AE", "RU"]
    if transaction["country"] in high_risk_countries:
        risk_score += 30
        flags.append("HIGH_RISK_JURISDICTION")
    
    if transaction.get("customer_tenure_days", 0) < 30:
        risk_score += 20
        flags.append("NEW_CUSTOMER")
    
    if transaction.get("type") == "wire":
        risk_score += 10
        flags.append("WIRE_TRANSFER")
    
    return {
        "risk_score": min(risk_score, 100),
        "risk_level": "HIGH" if risk_score >= 50 else "MEDIUM" if risk_score >= 25 else "LOW",
        "flags": flags,
        "requires_review": risk_score >= 25
    }

@agent.on_message()
async def handle_message(message):
    if getattr(message, 'type', None) == "transaction_scan":
        transaction = json.loads(message.content)
        analysis = analyze_transaction(transaction)
        
        if analysis["risk_level"] in ["HIGH", "MEDIUM"]:
            await agent.send_message(
                to="Compliance-Officer",
                content=json.dumps({
                    "transaction": transaction,
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat()
                }),
                message_type="risk_assessment"
            )
        
        return {"status": "analyzed", "analysis": analysis}
    
    return {"status": "ignored"}

if __name__ == "__main__":
    print("\n" + "="*50)
    print("📊 Risk Analyst Agent Started")
    print("="*50)
    # agent.run()  # Uncomment during hackathon
