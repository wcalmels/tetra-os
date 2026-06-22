"""
================================================================================
TETRA OS — tetra_web_dashboard.py
Dashboard web interactivo (Flask)
Autor: Walter Calmels K.
Uso  : python tetra_web_dashboard.py
       Abrir http://localhost:8080
================================================================================
"""

import json
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# ── Flask (optional dep) ──────────────────────────────────────────────────────
try:
    from flask import Flask, jsonify, request, Response
    from flask_cors import CORS
    FLASK_OK = True
except ImportError:
    FLASK_OK = False

# ── Global state ──────────────────────────────────────────────────────────────
STATE: Dict[str, Any] = {
    "status":       "idle",
    "current_task": None,
    "results":      [],
    "metrics": {
        "total_optimizations": 0,
        "total_discoveries":   0,
        "success_rate":        0.0,
    },
}

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TETRA OS Dashboard</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;
     background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:20px;}
.container{max-width:1300px;margin:0 auto;}
h1{color:#fff;text-align:center;font-size:2.4em;margin-bottom:8px;
   text-shadow:2px 2px 6px rgba(0,0,0,.3);}
.tagline{color:rgba(255,255,255,.8);text-align:center;margin-bottom:24px;font-size:1em;}
.status-bar{display:flex;justify-content:space-around;background:#fff;
  border-radius:12px;padding:18px;margin-bottom:20px;
  box-shadow:0 4px 12px rgba(0,0,0,.12);}
.stat{text-align:center;}
.stat .val{font-size:2em;font-weight:600;color:#667eea;}
.stat .lbl{font-size:.8em;color:#888;margin-top:4px;}
.dot{display:inline-block;width:12px;height:12px;border-radius:50%;
     vertical-align:middle;margin-left:6px;}
.dot-idle{background:#22c55e;}
.dot-run{background:#f59e0b;animation:pulse 1s infinite;}
@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:16px;margin-bottom:20px;}
.card{background:#fff;border-radius:12px;padding:22px;
      box-shadow:0 4px 12px rgba(0,0,0,.1);transition:transform .2s;}
.card:hover{transform:translateY(-4px);}
.card h2{color:#333;font-size:1.25em;margin-bottom:14px;}
.btn{width:100%;padding:11px;margin-top:8px;border:none;border-radius:6px;
     font-size:.95em;cursor:pointer;font-weight:500;
     background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;
     transition:opacity .2s;}
.btn:hover{opacity:.88;}
.btn:disabled{background:#ccc;cursor:not-allowed;}
.btn-green{background:linear-gradient(135deg,#22c55e,#16a34a);}
label{display:block;font-size:.85em;color:#555;margin-bottom:4px;margin-top:10px;}
input,select{width:100%;padding:9px;border:1.5px solid #e0e0e0;border-radius:6px;
             font-size:.9em;transition:border-color .2s;}
input:focus,select:focus{outline:none;border-color:#667eea;}
.results-box{max-height:350px;overflow-y:auto;}
.result-item{background:#f5f5f5;border-left:4px solid #667eea;
             padding:12px;border-radius:4px;margin-bottom:8px;}
.result-item .type{font-weight:600;color:#667eea;font-size:.85em;margin-bottom:4px;}
.result-item .ts{font-size:.75em;color:#999;}
.log-box{background:#1e1e1e;color:#0f0;font-family:'Courier New',monospace;
         padding:14px;border-radius:8px;height:220px;overflow-y:auto;font-size:.82em;}
</style>
</head>
<body>
<div class="container">
  <h1>🚀 TETRA OS</h1>
  <p class="tagline">Self-Improving Optimization &amp; Scientific Discovery · Walter Calmels K.</p>

  <div class="status-bar">
    <div class="stat">
      <div class="val"><span id="sys-status">Idle</span><span class="dot dot-idle" id="dot"></span></div>
      <div class="lbl">System Status</div>
    </div>
    <div class="stat">
      <div class="val" id="n-opt">0</div><div class="lbl">Optimizations</div>
    </div>
    <div class="stat">
      <div class="val" id="n-disc">0</div><div class="lbl">Discoveries</div>
    </div>
    <div class="stat">
      <div class="val" id="sr">0%</div><div class="lbl">Success Rate</div>
    </div>
  </div>

  <div class="grid">
    <!-- Drug -->
    <div class="card">
      <h2>💊 Drug Discovery</h2>
      <label>Target Protein</label>
      <input id="drug-target" value="GPCR" placeholder="e.g. Kinase">
      <label>Candidates</label>
      <input id="drug-n" type="number" value="50" min="10" max="500">
      <button class="btn" onclick="runDrug()">Start Discovery</button>
    </div>
    <!-- Materials -->
    <div class="card">
      <h2>🔧 Materials Design</h2>
      <label>Tensile Strength (MPa)</label>
      <input id="mat-sigma" type="number" value="900">
      <label>Density (g/cm³)</label>
      <input id="mat-rho" type="number" value="4.0" step="0.1">
      <button class="btn" onclick="runMat()">Design Material</button>
    </div>
    <!-- Energy -->
    <div class="card">
      <h2>⚡ Energy System</h2>
      <label>Demand (MW)</label>
      <input id="en-demand" type="number" value="100">
      <label>Budget (M USD)</label>
      <input id="en-budget" type="number" value="200">
      <button class="btn" onclick="runEnergy()">Optimize Mix</button>
    </div>
    <!-- Meta -->
    <div class="card">
      <h2>🧠 Meta-Discovery</h2>
      <p style="font-size:.85em;color:#666;margin-bottom:12px;">
        Discover laws from accumulated knowledge and generate novel algorithms.
      </p>
      <button class="btn" onclick="runMeta()">Run Discovery Cycle</button>
      <button class="btn btn-green" style="margin-top:8px;" onclick="exportKB()">
        💾 Export Knowledge Base
      </button>
    </div>
  </div>

  <div class="card" style="margin-bottom:16px;">
    <h2>📊 Recent Results</h2>
    <div class="results-box" id="results-list">
      <p style="color:#aaa;text-align:center;padding:20px;">No results yet.</p>
    </div>
  </div>

  <div class="card">
    <h2>📝 System Log</h2>
    <div class="log-box" id="log">
      <div>[INFO] TETRA OS Dashboard ready</div>
    </div>
  </div>
</div>

<script>
let interval;

function log(msg){
  const el=document.getElementById('log');
  el.innerHTML+=`<div>[${new Date().toLocaleTimeString()}] ${msg}</div>`;
  el.scrollTop=el.scrollHeight;
}

async function updateStatus(){
  try{
    const r=await fetch('/api/status').then(r=>r.json());
    document.getElementById('sys-status').textContent=
      r.status.charAt(0).toUpperCase()+r.status.slice(1);
    const dot=document.getElementById('dot');
    dot.className='dot '+(r.status==='idle'?'dot-idle':'dot-run');
    const m=await fetch('/api/metrics').then(r=>r.json());
    document.getElementById('n-opt').textContent=m.total_optimizations;
    document.getElementById('n-disc').textContent=m.total_discoveries;
    document.getElementById('sr').textContent=(m.success_rate*100).toFixed(0)+'%';
  }catch(e){}
}

async function loadResults(){
  try{
    const d=await fetch('/api/results').then(r=>r.json());
    const box=document.getElementById('results-list');
    if(!d.results.length){
      box.innerHTML='<p style="color:#aaa;text-align:center;padding:20px;">No results yet.</p>';
      return;
    }
    box.innerHTML=[...d.results].reverse().map(r=>`
      <div class="result-item">
        <div class="type">${r.type.replace(/_/g,' ').toUpperCase()}</div>
        <div>${r.success?'✅ Success':'❌ Failed'}</div>
        <div class="ts">${new Date(r.timestamp).toLocaleString()}</div>
      </div>`).join('');
  }catch(e){}
}

async function post(url,body){
  const r=await fetch(url,{method:'POST',
    headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  return r.json();
}

async function runDrug(){
  const target=document.getElementById('drug-target').value;
  const n=parseInt(document.getElementById('drug-n').value);
  log(`Starting drug discovery — target=${target} n=${n}`);
  const r=await post('/api/optimize',{problem_type:'drug_design',target,n_candidates:n});
  log(r.message||'Request sent');
  setTimeout(loadResults,4000);
}

async function runMat(){
  const sigma=parseFloat(document.getElementById('mat-sigma').value);
  const rho  =parseFloat(document.getElementById('mat-rho').value);
  log(`Starting materials design — σ=${sigma} ρ=${rho}`);
  const r=await post('/api/optimize',{
    problem_type:'materials',
    target_properties:{tensile_strength_mpa:sigma,density_g_cm3:rho}});
  log(r.message||'Request sent');
  setTimeout(loadResults,4000);
}

async function runEnergy(){
  const demand=parseFloat(document.getElementById('en-demand').value);
  const budget=parseFloat(document.getElementById('en-budget').value);
  log(`Starting energy optimization — demand=${demand}MW budget=$${budget}M`);
  const r=await post('/api/optimize',{problem_type:'energy',demand_mw:demand,budget_million:budget});
  log(r.message||'Request sent');
  setTimeout(loadResults,4000);
}

async function runMeta(){
  log('Starting meta-discovery cycle ...');
  const r=await post('/api/discover',{});
  log(r.message||'Meta-discovery started');
  setTimeout(loadResults,6000);
}

function exportKB(){
  log('Exporting knowledge base ...');
  window.location.href='/api/export';
}

document.addEventListener('DOMContentLoaded',()=>{
  updateStatus();
  loadResults();
  interval=setInterval(()=>{updateStatus();loadResults();},3000);
});
</script>
</body>
</html>
"""


# ==============================================================================
# BACKGROUND TASKS
# ==============================================================================

def _bg_optimize(problem_type: str, params: Dict):
    STATE["status"]       = "running"
    STATE["current_task"] = f"Optimization: {problem_type}"
    try:
        if problem_type == "drug_design":
            from tetra_science_module import ScientificOrchestrator
            o  = ScientificOrchestrator()
            res= o.run_drug_discovery_project(
                    target=params.get("target","GPCR"),
                    n_candidates=params.get("n_candidates",50))
        elif problem_type == "materials":
            from tetra_science_module import ScientificOrchestrator
            o  = ScientificOrchestrator()
            res= o.run_materials_design_project(
                    target_properties=params.get(
                        "target_properties",{"tensile_strength_mpa":900}))
        elif problem_type == "energy":
            from tetra_science_module import ScientificOrchestrator
            o  = ScientificOrchestrator()
            res= o.run_energy_optimization_project(
                    demand_mw=params.get("demand_mw",100),
                    budget_million=params.get("budget_million",200))
        else:
            res= {"error": f"Unknown problem type: {problem_type}"}

        entry = {
            "id":        datetime.now().strftime("%Y%m%d_%H%M%S"),
            "type":      problem_type,
            "success":   "error" not in res,
            "timestamp": datetime.now().isoformat(),
        }
        STATE["results"].append(entry)
        STATE["metrics"]["total_optimizations"] += 1
        _recalc_sr()

    except Exception as e:
        print(f"[BG] Error in optimize: {e}")
    finally:
        STATE["status"]       = "idle"
        STATE["current_task"] = None


def _bg_discover(params: Dict):
    STATE["status"]       = "running"
    STATE["current_task"] = "Meta-Discovery"
    try:
        from tetra_meta_discovery import MetaDiscoveryOrchestrator
        meta = MetaDiscoveryOrchestrator()
        meta.run_full_discovery_cycle()
        entry = {
            "id":        datetime.now().strftime("%Y%m%d_%H%M%S"),
            "type":      "meta_discovery",
            "success":   True,
            "timestamp": datetime.now().isoformat(),
        }
        STATE["results"].append(entry)
        STATE["metrics"]["total_discoveries"] += 1
        _recalc_sr()
    except Exception as e:
        print(f"[BG] Error in discovery: {e}")
    finally:
        STATE["status"]       = "idle"
        STATE["current_task"] = None


def _recalc_sr():
    if not STATE["results"]:
        return
    ok = sum(1 for r in STATE["results"] if r.get("success"))
    STATE["metrics"]["success_rate"] = ok / len(STATE["results"])


# ==============================================================================
# FLASK APP
# ==============================================================================

def create_app() -> "Flask":
    if not FLASK_OK:
        raise ImportError("Flask not installed. Run: pip install flask flask-cors")

    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def index():
        return Response(DASHBOARD_HTML, mimetype="text/html")

    @app.route("/api/status")
    def api_status():
        return jsonify({
            "status":       STATE["status"],
            "current_task": STATE["current_task"],
            "timestamp":    datetime.now().isoformat(),
        })

    @app.route("/api/metrics")
    def api_metrics():
        return jsonify(STATE["metrics"])

    @app.route("/api/results")
    def api_results():
        return jsonify({"results": STATE["results"][-20:],
                        "total":   len(STATE["results"])})

    @app.route("/api/optimize", methods=["POST"])
    def api_optimize():
        data  = request.get_json(force=True) or {}
        ptype = data.get("problem_type", "drug_design")
        t     = threading.Thread(target=_bg_optimize, args=(ptype, data), daemon=True)
        t.start()
        return jsonify({"status":"started","message":f"Optimization '{ptype}' started"})

    @app.route("/api/discover", methods=["POST"])
    def api_discover():
        data = request.get_json(force=True) or {}
        t    = threading.Thread(target=_bg_discover, args=(data,), daemon=True)
        t.start()
        return jsonify({"status":"started","message":"Meta-discovery started"})

    @app.route("/api/export")
    def api_export():
        try:
            from tetra_meta_discovery import MetaDiscoveryOrchestrator
            meta  = MetaDiscoveryOrchestrator()
            fpath = meta.export_knowledge_base()
            data  = Path(fpath).read_text()
            return Response(data, mimetype="application/json",
                            headers={"Content-Disposition":
                                     "attachment;filename=knowledge_base.json"})
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app


# ==============================================================================
# MAIN
# ==============================================================================

def start_dashboard(host: str = "0.0.0.0", port: int = 8080, debug: bool = False):
    if not FLASK_OK:
        print("❌ Flask not available.")
        print("   pip install flask flask-cors")
        return

    app = create_app()
    print("\n" + "=" * 70)
    print("🌐  TETRA OS — Web Dashboard")
    print("=" * 70)
    print(f"   URL : http://localhost:{port}")
    print("   Stop: Ctrl+C")
    print("=" * 70 + "\n")
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="TETRA OS Web Dashboard")
    p.add_argument("--host",  default="0.0.0.0")
    p.add_argument("--port",  type=int, default=8080)
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()
    start_dashboard(args.host, args.port, args.debug)