#!/usr/bin/env python3
"""
Agent 2: Compliance Officer Agent
Reviews flagged transactions against regulatory rules
"""
import json
import os
from datetime import datetime

class MockBandAgent:
    def __init__(self, name, role, api_key):
        self.name = name
        self.role = role
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
        print(f"🏃 {self.name} is running...")

BandAgent = MockBandAgent

agent = BandAgent(
    name="Compliance-Officer",
    role="compliance_reviewer",
    api_key=os.environ.get("BAND_API_KEY", "mock_key_123")
)

def perform_compliance_review(transaction, risk_analysis):
    actions_required = []
    regulations_triggered = []
    
    if transaction["amount"] > 10000:
        actions_required.append("FILE_SAR")
        regulations_triggered.append("BSA_SAR_REQUIREMENT")
    
    high_risk_countries = ["KY", "PA", "AE"]
    if transaction["country"] in high_risk_countries:
        actions_required.append("ENHANCED_DUE_DILIGENCE")
        regulations_triggered.append("PEP_SCREENING_REQUIRED")
    
    if actions_required:
        if "FILE_SAR" in actions_required:
            final_action = "ESCALATE_TO_HUMAN_REVIEW"
            priority = "URGENT"
        else:
            final_action = "HOLD_FOR_REVIEW"
            priority = "HIGH"
    else:
        final_action = "APPROVE"
        priority = "NORMAL"
    
    return {
        "final_action": final_action,
        "priority": priority,
        "actions_required": actions_required,
        "regulations_triggered": regulations_triggered,
        "review_completed_at": datetime.now().isoformat()
    }

@agent.on_message()
async def handle_message(message):
    if getattr(message, 'type', None) == "risk_assessment":
        data = json.loads(message.content)
        transaction = data["transaction"]
        risk_analysis = data["analysis"]
        
        review_result = perform_compliance_review(transaction, risk_analysis)
        
        if review_result["final_action"] == "ESCALATE_TO_HUMAN_REVIEW":
            await agent.send_message(
                to="Human-Review-Coordinator",
                content=json.dumps({
                    "transaction": transaction,
                    "risk_analysis": risk_analysis,
                    "compliance_review": review_result,
                    "escalation_reason": "SAR filing required",
                    "timestamp": datetime.now().isoformat()
                }),
                message_type="escalation_request"
            )
            return {"status": "escalated", "review_result": review_result}
        
        return {"status": "reviewed", "review_result": review_result}
    
    return {"status": "ignored"}

if __name__ == "__main__":
    print("\n" + "="*50)
    print("⚖️ Compliance Officer Agent Started")
    print("="*50)
