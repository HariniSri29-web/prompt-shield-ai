"""Flask web UI + JSON API for Prompt Shield AI.   Run: python app.py  ->  http://127.0.0.1:5000"""
from flask import Flask, jsonify, render_template_string, request
from prompt_shield import PromptShield

app = Flask(__name__)
shield = PromptShield()

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Prompt Shield AI</title>
<style>
body{font-family:system-ui,sans-serif;max-width:860px;margin:2rem auto;padding:0 1rem;color:#1f2937}
h1{text-align:center}textarea{width:100%;height:110px;padding:.7rem;font-size:1rem;border:1px solid #cbd5e1;border-radius:8px;box-sizing:border-box}
button{margin-top:.6rem;padding:.6rem 1.4rem;font-size:1rem;border:0;border-radius:8px;background:#2563eb;color:#fff;cursor:pointer}
.card{margin-top:1.2rem;padding:1rem;border-radius:10px;border:2px solid}
.LOW{border-color:#16a34a;background:#f0fdf4}.MEDIUM{border-color:#f59e0b;background:#fffbeb}.HIGH{border-color:#dc2626;background:#fef2f2}
.bar{height:12px;background:#e5e7eb;border-radius:6px;overflow:hidden}.bar div{height:100%}
table{width:100%;border-collapse:collapse;margin-top:1.5rem;font-size:.9rem}td,th{border-bottom:1px solid #e5e7eb;padding:.4rem;text-align:left}
</style></head><body>
<h1>Prompt Shield AI</h1>
<textarea id="p" placeholder="Type a prompt to screen..."></textarea><br><button onclick="go()">Analyze prompt</button>
<div id="out"></div><h3>Recent logs</h3><table id="logs"></table>
<script>
const col={LOW:'#16a34a',MEDIUM:'#f59e0b',HIGH:'#dc2626'};
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
async function go(){
  const r=await (await fetch('/api/analyze',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({prompt:document.getElementById('p').value})})).json();
  if(r.error){document.getElementById('out').innerHTML='<div class="card HIGH">'+esc(r.error)+'</div>';return}
  document.getElementById('out').innerHTML=`<div class="card ${r.risk_level}"><b>${r.label} - ${r.action}</b> (risk ${r.risk_score})
  <div class="bar"><div style="width:${r.risk_score*100}%;background:${col[r.risk_level]}"></div></div>
  <p>ML score: ${r.ml_score} | Rule score: ${r.rule_score}</p>
  <p>Matched rules: ${r.matched_rules.map(m=>esc(m.rule)).join(', ')||'none'}</p>
  <p>${esc(r.message)}</p></div>`;
  logs();
}
async function logs(){
  const rows=await (await fetch('/api/logs')).json();
  document.getElementById('logs').innerHTML='<tr><th>Time</th><th>Action</th><th>Risk</th><th>Prompt</th></tr>'+
   rows.map(x=>`<tr><td>${esc(x.timestamp)}</td><td>${esc(x.action)}</td><td>${x.risk_score}</td><td>${esc(x.original_prompt.slice(0,80))}</td></tr>`).join('');
}
logs();
</script></body></html>"""


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    prompt = (data.get("prompt") or "").strip()
    if not prompt:
        return jsonify({"error": "Please provide a prompt."}), 400
    if len(prompt) > 5000:
        return jsonify({"error": "Prompt too long (max 5000 characters)."}), 400
    return jsonify(shield.analyze(prompt, user_id=data.get("user_id", "web")))


@app.get("/api/logs")
def logs():
    return jsonify(shield.db.recent(15))


@app.get("/api/stats")
def stats():
    return jsonify(shield.db.stats())


if __name__ == "__main__":
    app.run(debug=False)
