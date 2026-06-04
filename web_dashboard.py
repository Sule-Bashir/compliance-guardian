#!/usr/bin/env python3
"""
Simple Web Dashboard for Judges to Test Your System
Run this on Replit during the hackathon
"""
from flask import Flask, render_template_string, jsonify, request
import json
import os

app = Flask(__name__)

# Store escalated transactions (in memory for demo)
escalated_cases = []
case_id_counter = 1

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Guardian - Multi-Agent System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: white; text-align: center; margin-bottom: 10px; font-size: 2em; }
        .subtitle { color: rgba(255,255,255,0.8); text-align: center; margin-bottom: 30px; }
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .agent-card {
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            border-top: 4px solid #667eea;
        }
        .agent-card h3 { color: #667eea; margin-bottom: 10px; }
        .agent-card .status { color: #4CAF50; font-size: 0.85em; margin: 10px 0; }
        .agent-card .role { background: #f0f0f0; padding: 5px 10px; border-radius: 20px; font-size: 0.75em; display: inline-block; }
        .transactions-panel {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-top: 20px;
        }
        .transaction {
            border-bottom: 1px solid #eee;
            padding: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
        }
        .transaction:hover { background: #f9f9f9; }
        .badge { padding: 5px 12px; border-radius: 20px; font-size: 0.75em; font-weight: bold; }
        .badge.high { background: #f44336; color: white; }
        .badge.medium { background: #ff9800; color: white; }
        .badge.low { background: #4CAF50; color: white; }
        .badge.pending { background: #ff9800; color: white; }
        button {
            background: #667eea;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 0 5px;
        }
        button.approve { background: #4CAF50; }
        button.reject { background: #f44336; }
        button:hover { opacity: 0.9; }
        .modal {
            display: none;
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            background: rgba(0,0,0,0.5);
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            border-radius: 16px;
            padding: 30px;
            max-width: 500px;
            width: 90%;
        }
        textarea {
            width: 100%;
            padding: 10px;
            margin: 15px 0;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-family: inherit;
        }
        .flow-diagram {
            background: #1a1a2e;
            color: white;
            padding: 15px;
            border-radius: 12px;
            text-align: center;
            margin: 20px 0;
            font-size: 0.85em;
        }
        .flow-diagram span { color: #4CAF50; }
        .footer {
            text-align: center;
            color: rgba(255,255,255,0.6);
            margin-top: 30px;
            font-size: 0.8em;
        }
        @media (max-width: 600px) {
            .transaction { flex-direction: column; gap: 10px; text-align: center; }
            h1 { font-size: 1.5em; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Compliance Guardian</h1>
        <p class="subtitle">Multi-Agent Compliance Workflow • Powered by Band</p>
        
        <div class="flow-diagram">
            🔍 Risk Analyst → ⚖️ Compliance Officer → 👥 Human Review<br>
            <span>🤝 All agents collaborate through Band messaging layer</span>
        </div>
        
        <div class="agent-grid">
            <div class="agent-card">
                <h3>📊 Risk Analyst Agent</h3>
                <div class="status">🟢 Active on Band</div>
                <p>Analyzes transactions for suspicious patterns, high-risk jurisdictions, and unusual amounts.</p>
                <span class="role">Band Role: risk_scanner</span>
            </div>
            <div class="agent-card">
                <h3>⚖️ Compliance Officer Agent</h3>
                <div class="status">🟢 Active on Band</div>
                <p>Reviews against BSA regulations, SAR requirements, and PEP screening rules.</p>
                <span class="role">Band Role: compliance_reviewer</span>
            </div>
            <div class="agent-card">
                <h3>👥 Human Review Coordinator</h3>
                <div class="status">🟢 Active on Band</div>
                <p>Manages escalations, collects human decisions, maintains audit trail.</p>
                <span class="role">Band Role: review_coordinator</span>
            </div>
        </div>
        
        <div class="transactions-panel">
            <h2>📋 Escalated Transactions (Require Human Review)</h2>
            <div id="escalatedList"></div>
        </div>
        
        <div class="footer">
            <p>🏆 Built for Band of Agents Hackathon 2026 • Track 3: Regulated Workflows</p>
            <p>🎯 3 Agents | Band Collaboration Layer | Real-time Compliance Automation</p>
        </div>
    </div>
    
    <div id="reviewModal" class="modal">
        <div class="modal-content">
            <h3>📝 Human Review Required</h3>
            <div id="modalTxInfo"></div>
            <textarea id="comments" rows="3" placeholder="Enter review comments..."></textarea>
            <div style="display: flex; gap: 10px; justify-content: center;">
                <button class="approve" onclick="submitDecision('APPROVED')">✅ Approve</button>
                <button class="reject" onclick="submitDecision('REJECTED')">❌ Reject</button>
                <button onclick="closeModal()">Cancel</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentCaseId = null;
        
        async function loadEscalations() {
            try {
                const resp = await fetch('/api/escalations');
                const data = await resp.json();
                const container = document.getElementById('escalatedList');
                if (data.escalations && data.escalations.length > 0) {
                    container.innerHTML = data.escalations.map(c => `
                        <div class="transaction">
                            <div>
                                <strong>${c.transaction_id}</strong><br>
                                <small>Amount: $${c.amount.toLocaleString()} | Country: ${c.country}</small>
                            </div>
                            <div>
                                <span class="badge high">ESCALATED</span>
                                <span class="badge pending">${c.status}</span>
                            </div>
                            <div>
                                <button onclick="openReview(${c.case_id}, '${c.transaction_id}')">Review Case</button>
                            </div>
                        </div>
                    `).join('');
                } else {
                    container.innerHTML = '<p style="text-align:center;padding:40px;">✅ No pending escalations. All cases resolved.</p>';
                }
            } catch(e) {
                document.getElementById('escalatedList').innerHTML = '<p style="text-align:center;padding:40px;">⚠️ Connect to backend or run workflow first.</p>';
            }
        }
        
        function openReview(caseId, txId) {
            currentCaseId = caseId;
            document.getElementById('modalTxInfo').innerHTML = `<p><strong>Case ID:</strong> ${caseId}<br><strong>Transaction:</strong> ${txId}</p>`;
            document.getElementById('reviewModal').style.display = 'flex';
        }
        
        async function submitDecision(decision) {
            const comments = document.getElementById('comments').value;
            try {
                const resp = await fetch('/api/decide', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ case_id: currentCaseId, decision: decision, comments: comments })
                });
                const result = await resp.json();
                alert(`Decision: ${decision}\\n\\nComments recorded.`);
                closeModal();
                loadEscalations();
            } catch(e) {
                alert('Error submitting decision.');
            }
        }
        
        function closeModal() {
            document.getElementById('reviewModal').style.display = 'none';
            document.getElementById('comments').value = '';
            currentCaseId = null;
        }
        
        loadEscalations();
        setInterval(loadEscalations, 5000);
    </script>
</body>
</html>
'''

# Store escalated cases
escalated_cases = []
case_counter = 1

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/escalations')
def get_escalations():
    return jsonify({'escalations': escalated_cases})

@app.route('/api/decide', methods=['POST'])
def decide():
    global escalated_cases
    data = request.json
    case_id = data.get('case_id')
    decision = data.get('decision')
    comments = data.get('comments')
    
    for case in escalated_cases:
        if case['case_id'] == case_id:
            case['status'] = decision
            case['comments'] = comments
            case['resolved_at'] = __import__('datetime').datetime.now().isoformat()
            break
    
    return jsonify({'status': 'success', 'decision': decision})

def add_escalation(transaction_id, amount, country):
    global case_counter, escalated_cases
    escalated_cases.append({
        'case_id': case_counter,
        'transaction_id': transaction_id,
        'amount': amount,
        'country': country,
        'status': 'pending',
        'created_at': __import__('datetime').datetime.now().isoformat()
    })
    case_counter += 1

if __name__ == '__main__':
    # Add sample escalations to demo the UI
    add_escalation('TXN003', 50000, 'KY')
    add_escalation('TXN005', 150000, 'PA')
    add_escalation('TXN001', 12500, 'US')
    
    print("\n" + "="*50)
    print("🌐 Web Dashboard Starting...")
    print("📍 Access at: http://localhost:5000")
    print("="*50)
    app.run(host='0.0.0.0', port=5000, debug=False)
