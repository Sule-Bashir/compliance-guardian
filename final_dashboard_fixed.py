from flask import Flask, render_template_string, request, jsonify
from datetime import datetime

app = Flask(__name__)

cases = [
    {'id': 1, 'txn': 'TXN003', 'amount': 50000, 'country': 'KY', 'status': 'pending', 'risk': 'HIGH', 'reason': 'High-risk jurisdiction + large wire'},
    {'id': 2, 'txn': 'TXN005', 'amount': 150000, 'country': 'PA', 'status': 'pending', 'risk': 'HIGH', 'reason': 'High-risk jurisdiction + new customer'},
    {'id': 3, 'txn': 'TXN001', 'amount': 12500, 'country': 'US', 'status': 'pending', 'risk': 'MEDIUM', 'reason': 'Large wire transfer'},
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Guardian - Multi-Agent System</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1300px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        
        .header h1 {
            font-size: 2.5rem;
            background: linear-gradient(135deg, #fff, #a8c0ff);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            margin-bottom: 10px;
        }
        
        .header p {
            color: rgba(255,255,255,0.8);
            font-size: 1.1rem;
        }
        
        .band-badge {
            display: inline-block;
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 0.85rem;
            margin-top: 15px;
            color: #a8c0ff;
        }
        
        .agents {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }
        
        .agent-card {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
            border-top: 4px solid;
        }
        
        .agent-card:hover {
            transform: translateY(-5px);
        }
        
        .agent-card.risk { border-top-color: #ff6b6b; }
        .agent-card.compliance { border-top-color: #4ecdc4; }
        .agent-card.human { border-top-color: #ffe66d; }
        
        .agent-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
        }
        
        .agent-card h3 {
            font-size: 1.3rem;
            margin-bottom: 10px;
            color: #1a1a2e;
        }
        
        .agent-status {
            display: inline-block;
            background: #4CAF50;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            margin-bottom: 15px;
        }
        
        .agent-role {
            background: #f0f0f0;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 0.7rem;
            font-family: monospace;
            display: inline-block;
            margin-top: 10px;
        }
        
        .agent-desc {
            color: #666;
            font-size: 0.9rem;
            line-height: 1.5;
            margin: 15px 0;
        }
        
        .flow {
            background: rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            border-radius: 50px;
            padding: 15px 25px;
            text-align: center;
            margin-bottom: 40px;
            color: white;
            font-size: 0.9rem;
        }
        
        .flow span {
            color: #4ecdc4;
            font-weight: bold;
        }
        
        .flow-arrow {
            color: #ffe66d;
            margin: 0 10px;
        }
        
        .cases-panel {
            background: rgba(255,255,255,0.95);
            border-radius: 20px;
            padding: 25px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.2);
        }
        
        .cases-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
        }
        
        .cases-header h2 {
            color: #1a1a2e;
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
        
        .stat.high { background: #ff6b6b; color: white; }
        .stat.medium { background: #ffe66d; color: #1a1a2e; }
        
        table {
            width: 100%;
            border-collapse: collapse;
        }
        
        th {
            text-align: left;
            padding: 15px 10px;
            background: #f8f9fa;
            color: #1a1a2e;
            font-weight: 600;
        }
        
        td {
            padding: 15px 10px;
            border-bottom: 1px solid #eee;
            color: #333;
        }
        
        .risk-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            font-weight: bold;
        }
        
        .risk-high { background: #ff6b6b; color: white; }
        .risk-medium { background: #ffe66d; color: #1a1a2e; }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.7rem;
            background: #ff9800;
            color: white;
        }
        
        .status-approved {
            background: #4CAF50;
        }
        
        .status-rejected {
            background: #9e9e9e;
        }
        
        .btn-approve {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 0 5px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .btn-reject {
            background: #f44336;
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 0 5px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .btn-approve:hover { background: #45a049; transform: scale(1.02); }
        .btn-reject:hover { background: #da190b; transform: scale(1.02); }
        
        .empty-state {
            text-align: center;
            padding: 60px;
            color: #999;
        }
        
        .empty-state .emoji {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: rgba(255,255,255,0.5);
            font-size: 0.8rem;
        }
        
        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            z-index: 1000;
            animation: slideIn 0.3s ease;
        }
        
        .toast.error {
            background: #f44336;
        }
        
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5rem; }
            .agents { grid-template-columns: 1fr; }
            .cases-header { flex-direction: column; gap: 15px; }
            table, thead, tbody, th, td, tr { display: block; }
            th { display: none; }
            td { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; }
            td:before { content: attr(data-label); font-weight: bold; }
            .btn-approve, .btn-reject { padding: 6px 15px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ Compliance Guardian</h1>
            <p>Multi-Agent Compliance Workflow • Powered by Band</p>
            <div class="band-badge">🎯 Band Collaboration Layer Active</div>
        </div>
        
        <div class="flow">
            🔍 Risk Analyst <span class="flow-arrow">→</span> ⚖️ Compliance Officer <span class="flow-arrow">→</span> 👥 Human Review<br>
            <span>🤝 All 3 agents collaborate through Band messaging with context passing & task handoffs</span>
        </div>
        
        <div class="agents">
            <div class="agent-card risk">
                <div class="agent-icon">📊</div>
                <h3>Risk Analyst Agent</h3>
                <div class="agent-status">● Active on Band</div>
                <div class="agent-desc">Analyzes transactions for suspicious patterns, high-risk jurisdictions, and unusual amounts.</div>
                <div class="agent-role">Band Role: risk_scanner</div>
            </div>
            <div class="agent-card compliance">
                <div class="agent-icon">⚖️</div>
                <h3>Compliance Officer Agent</h3>
                <div class="agent-status">● Active on Band</div>
                <div class="agent-desc">Reviews against BSA regulations, SAR requirements, and PEP screening rules.</div>
                <div class="agent-role">Band Role: compliance_reviewer</div>
            </div>
            <div class="agent-card human">
                <div class="agent-icon">👥</div>
                <h3>Human Review Coordinator</h3>
                <div class="agent-status">● Active on Band</div>
                <div class="agent-desc">Manages escalations, collects human decisions, maintains audit trail.</div>
                <div class="agent-role">Band Role: review_coordinator</div>
            </div>
        </div>
        
        <div class="cases-panel">
            <div class="cases-header">
                <h2>📋 Escalated Transactions</h2>
                <div class="stats" id="stats"></div>
            </div>
            <div id="casesContent"></div>
        </div>
        
        <div class="footer">
            🏆 Built for Band of Agents Hackathon 2026 • Track 3: Regulated Workflows<br>
            🎯 3 Agents | Band Collaboration Layer | Real-time Compliance Automation
        </div>
    </div>
    
    <div id="toast" style="display: none;"></div>
    
    <script>
        function showToast(message, isError = false) {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = isError ? 'toast error' : 'toast';
            toast.style.display = 'block';
            setTimeout(() => {
                toast.style.display = 'none';
            }, 3000);
        }
        
        async function decide(caseId, decision) {
            let comments = prompt(
                decision === 'APPROVED' 
                    ? '📝 Enter approval comments:' 
                    : '⚠️ Enter rejection reason:',
                decision === 'APPROVED' 
                    ? 'Transaction approved after compliance review. No suspicious activity detected.'
                    : 'Transaction rejected due to high-risk flags and insufficient documentation.'
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
                    showToast(`✅ ${decision} - ${comments.substring(0, 50)}...`);
                    // Refresh the page to show updated cases
                    setTimeout(() => {
                        location.reload();
                    }, 500);
                } else {
                    showToast('❌ Error submitting decision', true);
                }
            } catch(e) {
                showToast('❌ Network error. Please try again.', true);
            }
        }
        
        async function loadCases() {
            const resp = await fetch('/cases');
            const data = await resp.json();
            const container = document.getElementById('casesContent');
            const statsContainer = document.getElementById('stats');
            const pending = data.cases.filter(c => c.status === 'pending');
            const total = data.cases.length;
            const resolved = total - pending.length;
            
            statsContainer.innerHTML = `
                <span class="stat">📊 Total: ${total}</span>
                <span class="stat">✅ Resolved: ${resolved}</span>
                <span class="stat ${pending.length > 0 ? 'high' : ''}">⏳ Pending: ${pending.length}</span>
            `;
            
            if (pending.length === 0) {
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="emoji">🎉</div>
                        <h3>All Cases Resolved!</h3>
                        <p>All escalated transactions have been reviewed by the Human Review Coordinator.</p>
                        <p style="margin-top: 10px; font-size: 0.85rem;">🤝 Band collaboration complete!</p>
                    </div>
                `;
                return;
            }
            
            container.innerHTML = `
                <table>
                    <thead>
                        <tr><th>Transaction</th><th>Amount</th><th>Country</th><th>Risk</th><th>Reason</th><th>Status</th><th>Action</th></tr>
                    </thead>
                    <tbody>
                        ${pending.map(c => `
                            <tr id="row-${c.id}">
                                <td data-label="Transaction"><strong>${c.txn}</strong></td>
                                <td data-label="Amount">$${c.amount.toLocaleString()}</td>
                                <td data-label="Country">${c.country}</td>
                                <td data-label="Risk"><span class="risk-badge risk-${c.risk.toLowerCase()}">${c.risk}</span></td>
                                <td data-label="Reason">${c.reason}</td>
                                <td data-label="Status"><span class="status-badge">PENDING</span></td>
                                <td data-label="Action">
                                    <button class="btn-approve" onclick="decide(${c.id}, 'APPROVED')">✅ Approve</button>
                                    <button class="btn-reject" onclick="decide(${c.id}, 'REJECTED')">❌ Reject</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
        }
        
        // Load cases immediately and every 2 seconds
        loadCases();
        setInterval(loadCases, 2000);
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/cases')
def get_cases():
    return jsonify({'cases': cases})

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
            break
    
    print(f"\n📝 Decision recorded:")
    print(f"   Case ID: {case_id}")
    print(f"   Decision: {decision}")
    print(f"   Comments: {comments}")
    print(f"   Time: {datetime.now().isoformat()}")
    
    return jsonify({'status': 'success', 'decision': decision, 'case_id': case_id})

if __name__ == '__main__':
    print("\n" + "="*55)
    print("🌟 COMPLIANCE GUARDIAN - FULLY FIXED DASHBOARD")
    print("="*55)
    print("\n📍 Access on your phone: http://10.141.95.198:5000")
    print("📍 Access locally: http://localhost:5000")
    print("\n✅ Approve/Reject buttons WORKING")
    print("✅ Cases DISAPPEAR after approval/rejection")
    print("✅ Toast notifications for feedback")
    print("✅ Auto-refresh every 2 seconds")
    print("\n" + "="*55 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
