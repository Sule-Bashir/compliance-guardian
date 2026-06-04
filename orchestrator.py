#!/usr/bin/env python3
"""
Main Orchestrator - Demonstrates multi-agent collaboration
"""
import json
import time
from datetime import datetime

# Mock Band client
class MockBandClient:
    def __init__(self, api_key, room):
        self.api_key = api_key
        self.room = room
        print(f"🎯 Band Client Connected to room: {room}")
    
    def send_and_wait(self, to, content, message_type, timeout=10):
        print(f"   📨 Sending to {to}: {message_type}")
        return type('Response', (), {'content': json.dumps({"status": "ok"})})()

TEST_TRANSACTIONS = [
    {"id": "TXN001", "amount": 12500, "country": "US", "type": "wire", "customer_tenure_days": 45},
    {"id": "TXN002", "amount": 500, "country": "CA", "type": "credit", "customer_tenure_days": 730},
    {"id": "TXN003", "amount": 50000, "country": "KY", "type": "wire", "customer_tenure_days": 2},
    {"id": "TXN004", "amount": 2800, "country": "US", "type": "ach", "customer_tenure_days": 365},
    {"id": "TXN005", "amount": 150000, "country": "PA", "type": "wire", "customer_tenure_days": 1},
]

def analyze_transaction(tx):
    risk_score = 40 if tx["amount"] > 10000 else 0
    risk_score += 30 if tx["country"] in ["KY", "PA"] else 0
    risk_score += 20 if tx["customer_tenure_days"] < 30 else 0
    risk_score += 10 if tx["type"] == "wire" else 0
    return min(risk_score, 100)

def get_risk_level(score):
    if score >= 50: return "🔴 HIGH"
    if score >= 25: return "🟡 MEDIUM"
    return "🟢 LOW"

def run_workflow():
    print("\n" + "="*70)
    print("🏦 COMPLIANCE GUARDIAN - Multi-Agent Collaboration Demo")
    print("="*70)
    
    print("\n🎯 WORKFLOW:")
    print("   Agent 1 (Risk Analyst) → Agent 2 (Compliance Officer) → Agent 3 (Human Review)")
    print("   " + "─"*55)
    print("   All communication happens through Band collaboration layer\n")
    
    client = MockBandClient(api_key="mock", room="compliance_workflow_room")
    
    results = []
    
    for tx in TEST_TRANSACTIONS:
        print(f"\n{'─'*70}")
        print(f"📋 Processing: {tx['id']} | ${tx['amount']:,} | {tx['country']} | {tx['type']}")
        print(f"{'─'*70}")
        
        # Agent 1: Risk Analysis
        print("   🔍 [Agent 1] Risk Analyst: Scanning transaction...")
        risk_score = analyze_transaction(tx)
        risk_level = get_risk_level(risk_score)
        print(f"   📊 Risk Score: {risk_score}% {risk_level}")
        
        # Send via Band (Agent 1 → Agent 2)
        client.send_and_wait("Compliance-Officer", json.dumps(tx), "risk_assessment")
        
        # Agent 2: Compliance Review
        print("   ⚖️ [Agent 2] Compliance Officer: Reviewing regulations...")
        
        if risk_score >= 50:
            print("   ⚠️ HIGH RISK → SAR Filing Required")
            print("   📤 Escalating to Human Review Coordinator via Band...")
            print("   👥 [Agent 3] Human Review: Case created for manual review")
            final_action = "ESCALATED"
        elif risk_score >= 25:
            print("   📋 MEDIUM RISK → Enhanced due diligence recommended")
            final_action = "HOLD_FOR_REVIEW"
        else:
            print("   ✅ LOW RISK → Auto-approved")
            final_action = "APPROVED"
        
        results.append({
            "transaction_id": tx["id"],
            "risk_score": risk_score,
            "final_action": final_action,
            "timestamp": datetime.now().isoformat()
        })
        
        time.sleep(1)  # Simulate real-time processing
    
    # Summary Report
    print("\n" + "="*70)
    print("📊 PROCESSING SUMMARY")
    print("="*70)
    print(f"\n{'ID':<12} {'Amount':<12} {'Risk Score':<12} {'Action':<15}")
    print("─"*55)
    for r in results:
        print(f"{r['transaction_id']:<12} ${r['risk_score']:<11} {r['risk_score']:<11}% {r['final_action']:<15}")
    
    escalated = [r for r in results if r['final_action'] == 'ESCALATED']
    approved = [r for r in results if r['final_action'] == 'APPROVED']
    
    print(f"\n📈 Results:")
    print(f"   ✅ Auto-approved: {len(approved)} transactions")
    print(f"   ⚠️ Escalated to Human: {len(escalated)} transactions")
    print(f"   🤖 Agents used: 3 (Risk Analyst, Compliance Officer, Human Review)")
    print(f"   🔗 Collaboration Layer: Band (agent-to-agent messaging)")
    
    print("\n" + "="*70)
    print("🏆 READY FOR BAND OF AGENTS HACKATHON 2026")
    print("="*70)
    print("\n📅 During the hackathon (June 12-19):")
    print("   1. Replace MockBandAgent with real Band SDK")
    print("   2. Add your Band API key")
    print("   3. Deploy to Replit for web dashboard")
    print("   4. Submit to lablab.ai\n")

if __name__ == "__main__":
    run_workflow()
