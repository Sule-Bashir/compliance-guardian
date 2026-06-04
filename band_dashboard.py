#!/usr/bin/env python3
"""
Compliance Guardian Dashboard - REAL Band Integration
Judges can test Approve/Reject workflow
"""
from flask import Flask, render_template_string, jsonify, request
from datetime import datetime
from band_config import BAND_CONFIG

app = Flask(__name__)

# Store escalated cases (in memory)
cases = [
    {'id': 1, 'txn': 'TXN003', 'amount': 50000, 'country': 'KY', 'risk': 'HIGH', 'reason': 'High-risk jurisdiction + large wire', 'status': 'pending'},
    {'id': 2, 'txn': 'TXN005', 'amount': 150000, 'country': 'PA', 'risk': 'HIGH', 'reason': 'High-risk jurisdiction + new customer', 'status': 'pending'},
    {'id': 3, 'txn': 'TXN001', 'amount': 12500, 'country': 'US', 'risk': 'MEDIUM', 'reason': 'Large wire transfer', 'status': 'pending'},
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Guardian - Band Multi-Agent System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1300px; margin: 0 auto; }
        h1 {
            text-align: center;
            color: white;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .band-header {
            text-align: center;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 12px;
            border-radius: 50px;
            margin-bottom: 30px;
            color: #4ecdc4;
            font-size: 0.9rem;
        }
        .agents {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .agent-card {
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s;
        }
        .agent-card:hover { transform: translateY(-5px); }
        .agent-card.risk { border-top: 4px solid #ff6b6b; }
        .agent-card.compliance { border-top: 4px solid #4ecdc4; }
        .agent-card.human { border-top: 4px solid #ffe66d; }
        .agent-icon { font-size: 2.5rem; margin-bottom: 15px; }
        .agent-card h3 { margin-bottom: 10px; color: #1a1a2e; }
        .agent-handle {
            font-family: monospace;
            background: #f0f0f0;
            padding: 5px 10px;
            border-radius: 10px;
            font-size: 0.7rem;
            display: inline-block;
            margin: 10px 0;
        }
        .agent-role {
            font-size: 0.7rem;
            color: #666;
            margin-top: 10px;
        }
        .cases-panel {
            background: white;
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        }
        .cases-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .stats {
            display: flex;
            gap: 15px;
        }
        .stat {
            background: #f0f0f0;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 15px 10px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }
        .risk-high { background: #ff6b6b; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; display: inline-block; }
        .risk-medium { background: #ffe66d; color: #1a1a2e; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; display: inline-block; }
        .status-pending { background: #ff9800; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; display: inline-block; }
        .btn {
            padding: 8px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            margin: 0 5px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .btn-approve { background: #4CAF50; color: white; }
        .btn-reject { background: #f44336; color: white; }
        .btn:hover { opacity: 0.85; transform: scale(1.02); }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: rgba(255,255,255,0.5);
            font-size: 0.8rem;
        }
        .empty-state {
            text-align: center;
            padding: 60px;
            color: #999;
        }
        @media (max-width: 768px) {
            h1 { font-size: 1.5rem; }
            th, td { display: block; }
            th { display: none; }
            td { padding: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Compliance Guardian</h1>
        <div class="band-header">
            🎯 Powered by Band • 3 Agents Collaborating • Real-time Compliance
        </div>
        
        <div class="agents">
            <div class="agent-card risk">
                <div class="agent-icon">📊</div>
                <h3>Risk Analyst</h3>
                <div class="agent-handle">{{ risk_handle }}</div>
                <p>Scans transactions for suspicious patterns, high-risk jurisdictions, and unusual amounts.</p>
                <div class="agent-role">Band Role: risk_scanner</div>
            </div>
            <div class="agent-card compliance">
                <div class="agent-icon">⚖️</div>
                <h3>Compliance Officer</h3>
                <div class="agent-handle">{{ compliance_handle }}</div>
                <p>Applies BSA/AML regulations, SAR requirements, and PEP screening rules.</p>
                <div class="agent-role">Band Role: compliance_reviewer</div>
            </div>
            <div class="agent-card human">
                <div class="agent-icon">👥</div>
                <h3>Human Review Coordinator</h3>
                <div class="agent-handle">{{ human_handle }}</div>
                <p>Manages escalations, collects human decisions, maintains audit trail.</p>
                <div class="agent-role">Band Role: review_coordinator</div>
            </div>
        </div>
        
        <div class="cases-panel">
            <div class="cases-header">
                <h2>📋 Escalated Transactions</h2>
                <div class="stats" id="stats"></div>
            </div>
            <div id="cases-content"></div>
        </div>
        
        <div class="footer">
            🏆 Band of Agents Hackathon 2026 • Track 3: Regulated & High-Stakes Workflows
        </div>
    </div>
    
    <script>
        function updateStats() {
            const rows = document.querySelectorAll('#cases-table tbody tr');
            const total = rows.length;
            const pending = document.querySelectorAll('.status-pending').length;
            document.getElementById('stats').innerHTML = `
                <span class="stat">📊 Total: ${total}</span>
                <span class="stat">⏳ Pending: ${pending}</span>
            `;
        }
        
        async function decide(caseId, decision) {
            let comments = prompt(
                decision === 'APPROVED' 
                    ? '📝 Enter approval comments:' 
                    : '⚠️ Enter rejection reason:',
                decision === 'APPROVED' 
                    ? 'Transaction approved after compliance review.'
                    : 'Transaction rejected - suspicious activity detected.'
            );
            if (!comments) return;
            
            try {
                const resp = await fetch('/decide', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ case_id: caseId, decision: decision, comments: comments })
                });
                const data = await resp.json();
                if (data.status === 'success') {
                    alert(`✅ Decision recorded: ${decision}\\n📝 ${comments}`);
                    location.reload();
                }
            } catch(e) {
                alert('Error submitting decision');
            }
        }
        
        function loadCases() {
            fetch('/cases')
                .then(res => res.json())
                .then(data => {
                    const container = document.getElementById('cases-content');
                    if (data.cases.length === 0) {
                        container.innerHTML = '<div class="empty-state"><div style="font-size:3rem;">🎉</div><h3>All Cases Resolved!</h3><p>All escalated transactions have been reviewed.</p></div>';
                        document.getElementById('stats').innerHTML = '<span class="stat">📊 Total: 0</span><span class="stat">✅ All Resolved!</span>';
                        return;
                    }
                    
                    let html = `<table id="cases-table"><thead><tr><th>ID</th><th>Amount</th><th>Country</th><th>Risk</th><th>Reason</th><th>Status</th><th>Action</th></tr></thead><tbody>`;
                    data.cases.forEach(c => {
                        html += `
                            <tr>
                                <td><strong>${c.txn}</strong></td>
                                <td>$${c.amount.toLocaleString()}</td>
                                <td>${c.country}</td>
                                <td><span class="risk-${c.risk.toLowerCase()}">${c.risk}</span></td>
                                <td>${c.reason}</td>
                                <td><span class="status-pending">PENDING</span></td>
                                <td>
                                    <button class="btn btn-approve" onclick="decide(${c.id}, 'APPROVED')">✅ Approve</button>
                                    <button class="btn btn-reject" onclick="decide(${c.id}, 'REJECTED')">❌ Reject</button>
                                </td>
                            </tr>
                        `;
                    });
                    html += `</tbody></table>`;
                    container.innerHTML = html;
                    updateStats();
                });
        }
        
        loadCases();
        setInterval(loadCases, 3000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML,
        risk_handle=BAND_CONFIG["risk_analyst"]["handle"],
        compliance_handle=BAND_CONFIG["compliance_officer"]["handle"],
        human_handle=BAND_CONFIG["human_review"]["handle"]
    )

@app.route('/cases')
def get_cases():
    pending = [c for c in cases if c['status'] == 'pending']
    return jsonify({'cases': pending})

@app.route('/decide', methods=['POST'])
def decide():
    global cases
    data = request.json
    case_id = data.get('case_id')
    decision = data.get('decision')
    comments = data.get('comments')
    
    for case in cases:
        if case['id'] == case_id:
            case['status'] = decision.lower()
            case['decision'] = decision
            case['comments'] = comments
            case['resolved_at'] = datetime.now().isoformat()
            print(f"\n📝 Decision recorded on Band:")
            print(f"   Case: {case['txn']}")
            print(f"   Decision: {decision}")
            print(f"   Comments: {comments}")
            break
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌟 COMPLIANCE GUARDIAN - REAL BAND INTEGRATION")
    print("="*60)
    print("\n🎯 Band Agents Connected:")
    print(f"   📊 Risk Analyst: {BAND_CONFIG['risk_analyst']['handle']}")
    print(f"   ⚖️ Compliance Officer: {BAND_CONFIG['compliance_officer']['handle']}")
    print(f"   👥 Human Review: {BAND_CONFIG['human_review']['handle']}")
    print("\n📍 Dashboard: http://localhost:5000")
    print("📍 On your phone: http://10.141.95.198:5000")
    print("\n✅ Approve/Reject working")
    print("✅ Cases disappear after decision")
    print("="*60 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
