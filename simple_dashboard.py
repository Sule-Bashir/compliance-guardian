from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# Simple cases data
cases = [
    {'id': 1, 'txn': 'TXN003', 'amount': 50000, 'country': 'KY', 'status': 'pending'},
    {'id': 2, 'txn': 'TXN005', 'amount': 150000, 'country': 'PA', 'status': 'pending'},
    {'id': 3, 'txn': 'TXN001', 'amount': 12500, 'country': 'US', 'status': 'pending'},
]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Guardian - Simple Test</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #0f2027; color: white; }
        .case { background: white; color: black; padding: 15px; margin: 10px 0; border-radius: 10px; display: flex; justify-content: space-between; align-items: center; }
        button { padding: 8px 20px; margin: 0 5px; border: none; border-radius: 5px; cursor: pointer; }
        .approve { background: #4CAF50; color: white; }
        .reject { background: #f44336; color: white; }
        .pending { background: #ff9800; color: white; padding: 3px 10px; border-radius: 15px; font-size: 12px; }
        .approved { background: #4CAF50; }
        .rejected { background: #9e9e9e; }
        #message { padding: 10px; margin: 10px 0; border-radius: 5px; display: none; }
        .success { background: #4CAF50; }
        .error { background: #f44336; }
    </style>
</head>
<body>
    <h1>🛡️ Compliance Guardian</h1>
    <p>3 Agents Collaborating Through Band: Risk Analyst → Compliance Officer → Human Review</p>
    
    <div id="message"></div>
    
    <h2>📋 Cases Requiring Review</h2>
    <div id="casesList"></div>
    
    <script>
        function showMessage(msg, type) {
            const msgDiv = document.getElementById('message');
            msgDiv.textContent = msg;
            msgDiv.className = type;
            msgDiv.style.display = 'block';
            setTimeout(() => { msgDiv.style.display = 'none'; }, 2000);
        }
        
        async function decide(caseId, decision) {
            const comments = prompt("Enter review comments:", decision === 'APPROVED' ? "Transaction approved after review" : "Transaction rejected - suspicious activity");
            if (!comments) return;
            
            try {
                const resp = await fetch('/decide', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ case_id: caseId, decision: decision, comments: comments })
                });
                const data = await resp.json();
                if (data.status === 'success') {
                    showMessage(`✅ Case ${caseId} ${decision}`, 'success');
                    location.reload();
                }
            } catch(e) {
                showMessage('Error: ' + e.message, 'error');
            }
        }
        
        async function loadCases() {
            const resp = await fetch('/cases');
            const data = await resp.json();
            const container = document.getElementById('casesList');
            const pending = data.cases.filter(c => c.status === 'pending');
            
            if (pending.length === 0) {
                container.innerHTML = '<p>✅ All cases resolved! Great job!</p>';
                return;
            }
            
            container.innerHTML = pending.map(c => `
                <div class="case">
                    <div>
                        <strong>${c.txn}</strong><br>
                        $${c.amount.toLocaleString()} | ${c.country}
                    </div>
                    <div>
                        <span class="pending">PENDING</span>
                    </div>
                    <div>
                        <button class="approve" onclick="decide(${c.id}, 'APPROVED')">✅ Approve</button>
                        <button class="reject" onclick="decide(${c.id}, 'REJECTED')">❌ Reject</button>
                    </div>
                </div>
            `).join('');
        }
        
        loadCases();
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
            case['comments'] = comments
            break
    
    return jsonify({'status': 'success', 'decision': decision})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("✅ SIMPLE DASHBOARD - Approve/Reject WORKING")
    print("📍 http://localhost:5000")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)
