"""
================================================================================
TETRA OS — tetra_first_test.py
Suite de 7 tests completos — debe dar 7/7 PASSED
Autor: Walter Calmels K.
================================================================================
"""

import numpy as np
import json
import time
from datetime import datetime
from pathlib import Path

print("=" * 70)
print("🧪  TETRA OS — COMPLETE SYSTEM TEST SUITE")
print("=" * 70)
print(f"  Date : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"  NumPy: {np.__version__}")
print("=" * 70 + "\n")

Path("test_results").mkdir(exist_ok=True)
results: dict = {}


# ==============================================================================
# TEST 1 — Base optimization system
# ==============================================================================
print("TEST 1: Base Optimization System")
print("-" * 70)

try:
    from tetra_os_improved import TetraOrchestrator, ProblemDefinition, BenchmarkFunctions

    np.random.seed(42)
    orch = TetraOrchestrator(load_previous_state=False)
    # Prefer strong optimizers for a deterministic CI smoke test
    orch.consciousness.adaptation["exploration"] = 0.0
    orch.consciousness.selection_matrix["benchmark"] = {
        "DifferentialEvolution": 1.0,
        "ParticleSwarm": 0.95,
        "GeneticAlgorithm": 0.9,
        "GradientDescent": 0.5,
        "SimulatedAnnealing": 0.3,
    }

    prob = ProblemDefinition(
        problem_id="test_sphere_10d",
        problem_type="benchmark",
        dimensions=10,
        bounds=(-5.0, 5.0),
        objective_function=BenchmarkFunctions.sphere,
    )

    t0  = time.time()
    res = orch.solve(prob, max_iterations=500)
    dt  = time.time() - t0

    assert res.objective_value < 10.0,  f"Objective too high: {res.objective_value}"
    assert res.converged,               "Did not converge"
    assert res.execution_time < 60.0,   "Took too long"
    assert res.algorithm in orch.ALGORITHMS, "Unknown algorithm"

    print(f"  ✅ PASSED")
    print(f"     obj={res.objective_value:.6e}  iter={res.iterations}"
          f"  algo={res.algorithm}  time={dt:.3f}s")
    results["test1"] = {"status": "PASSED", "objective": res.objective_value,
                        "algorithm": res.algorithm, "time": dt}

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    results["test1"] = {"status": "FAILED", "error": str(e)}

print()

# ==============================================================================
# TEST 2 — Drug Discovery Module
# ==============================================================================
print("TEST 2: Drug Discovery Module")
print("-" * 70)

try:
    from tetra_science_module import DrugDesignOptimizer

    opt = DrugDesignOptimizer()

    t0   = time.time()
    mols = opt.generate_candidate_molecules(30)
    assert len(mols) == 30, "Wrong candidate count"

    scores = [opt._calculate_drug_score(m) for m in mols]
    assert all(0 <= s <= 1 for s in scores), "Scores out of range"

    best_mol = mols[int(np.argmax(scores))]
    opt_res  = opt.optimize_drug_candidate(best_mol, "Kinase", max_iterations=50)
    dt = time.time() - t0

    assert opt_res["final_score"] > 0,      "Invalid final score"
    assert opt_res["improvement"] >= -0.01, "Improvement went very negative"

    print(f"  ✅ PASSED")
    print(f"     candidates=30  best_score={opt_res['final_score']:.3f}"
          f"  improvement={opt_res['improvement']:.3f}  time={dt:.3f}s")
    results["test2"] = {"status": "PASSED", "best_score": opt_res["final_score"], "time": dt}

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    results["test2"] = {"status": "FAILED", "error": str(e)}

print()

# ==============================================================================
# TEST 3 — Materials Optimization
# ==============================================================================
print("TEST 3: Materials Optimization Module")
print("-" * 70)

try:
    from tetra_science_module import MaterialsOptimizer

    mat = MaterialsOptimizer()

    t0  = time.time()
    res = mat.design_alloy(
        target_properties={"tensile_strength_mpa": 800, "density_g_cm3": 4.5},
        available_elements=["Ti", "Al", "V", "Fe"],
        max_iterations=100,
    )
    dt = time.time() - t0

    assert "composition" in res,           "Missing composition"
    assert "predicted_properties" in res,  "Missing predicted properties"
    assert 0 <= res["optimization_score"] <= 1, "Score out of range"
    assert res["estimated_cost_per_kg"] > 0,    "Invalid cost"

    print(f"  ✅ PASSED")
    print(f"     score={res['optimization_score']:.3f}"
          f"  elements={list(res['composition']['elements'].keys())}"
          f"  cost=${res['estimated_cost_per_kg']:.2f}/kg  time={dt:.3f}s")
    results["test3"] = {"status": "PASSED", "score": res["optimization_score"], "time": dt}

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    results["test3"] = {"status": "FAILED", "error": str(e)}

print()

# ==============================================================================
# TEST 4 — Energy Optimization
# ==============================================================================
print("TEST 4: Energy System Optimization")
print("-" * 70)

try:
    from tetra_science_module import EnergySystemOptimizer

    eng = EnergySystemOptimizer()

    t0  = time.time()
    res = eng.optimize_energy_mix(
        demand_profile={"peak": 100.0, "base": 50.0},
        budget_million_usd=120.0,
    )
    dt = time.time() - t0

    assert "optimal_mix"            in res, "Missing optimal mix"
    assert "total_capacity_mw"      in res, "Missing capacity"
    assert "weighted_lcoe_usd_mwh"  in res, "Missing LCOE"
    assert 0 <= res["renewable_fraction"] <= 1, "RE fraction out of range"
    assert res["weighted_lcoe_usd_mwh"]   > 0,  "Invalid LCOE"

    print(f"  ✅ PASSED")
    print(f"     capacity={res['total_capacity_mw']:.1f}MW"
          f"  RE={res['renewable_fraction']:.1%}"
          f"  LCOE=${res['weighted_lcoe_usd_mwh']}/MWh  time={dt:.3f}s")
    results["test4"] = {"status": "PASSED",
                        "capacity_mw": res["total_capacity_mw"],
                        "renewable": res["renewable_fraction"], "time": dt}

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    results["test4"] = {"status": "FAILED", "error": str(e)}

print()

# ==============================================================================
# TEST 5 — Law Discovery Engine
# ==============================================================================
print("TEST 5: Law Discovery Engine")
print("-" * 70)

try:
    from tetra_meta_discovery import LawDiscoveryEngine

    engine = LawDiscoveryEngine()

    # Known linear relationship: y = 2x + 3
    np.random.seed(0)
    x = np.linspace(1, 10, 60)
    y = 2.0 * x + 3.0 + np.random.normal(0, 0.3, 60)

    t0   = time.time()
    laws = engine.discover_laws_from_data({"x_var": x, "y_var": y}, domain="test")
    dt   = time.time() - t0

    assert len(laws) > 0, "No laws discovered"
    best = max(laws, key=lambda l: l.confidence)
    assert best.confidence > 0.70, f"Low confidence: {best.confidence:.3f}"
    assert best.mathematical_form,  "Empty mathematical form"

    # Validate on new data
    x2 = np.linspace(10, 20, 30)
    y2 = 2.0 * x2 + 3.0 + np.random.normal(0, 0.5, 30)
    r2 = engine.validate_law(best, {"x_var": x2, "y_var": y2})

    print(f"  ✅ PASSED")
    print(f"     laws={len(laws)}  best_R²={best.confidence:.3f}"
          f"  form='{best.mathematical_form}'  validation_R²={r2:.3f}  time={dt:.3f}s")
    results["test5"] = {"status": "PASSED", "n_laws": len(laws),
                        "confidence": best.confidence, "time": dt}

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    results["test5"] = {"status": "FAILED", "error": str(e)}

print()

# ==============================================================================
# TEST 6 — Algorithm Generation Engine
# ==============================================================================
print("TEST 6: Algorithm Generation Engine")
print("-" * 70)

try:
    from tetra_meta_discovery import AlgorithmDiscoveryEngine

    engine = AlgorithmDiscoveryEngine()

    t0   = time.time()
    algo = engine.generate_novel_algorithm({
        "name": "test_optimization_problem",
        "type": "optimization",
        "constraints": {"time": "minimize"},
    })
    dt = time.time() - t0

    assert algo.name,               "Missing name"
    assert algo.pseudocode,         "Missing pseudocode"
    assert algo.complexity,         "Missing complexity"
    assert 0 < algo.confidence <= 1,"Confidence out of range"

    # Evolve with feedback
    evolved = engine.evolve_algorithm(algo, {
        "speed_score": 0.92, "accuracy_score": 0.88, "memory_efficiency": 0.79,
    })
    assert evolved.confidence > 0, "Invalid evolved confidence"

    print(f"  ✅ PASSED")
    print(f"     name='{algo.name}'  complexity='{algo.complexity}'"
          f"  confidence={algo.confidence:.3f}  time={dt:.3f}s")
    results["test6"] = {"status": "PASSED", "algorithm": algo.name,
                        "confidence": algo.confidence, "time": dt}

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    results["test6"] = {"status": "FAILED", "error": str(e)}

print()

# ==============================================================================
# TEST 7 — Full Integration Pipeline
# ==============================================================================
print("TEST 7: Full Integration Pipeline")
print("-" * 70)

try:
    from tetra_science_module  import ScientificOrchestrator
    from tetra_meta_discovery  import MetaDiscoveryOrchestrator

    science = ScientificOrchestrator()
    meta    = MetaDiscoveryOrchestrator()

    t0 = time.time()

    # Run science
    drug     = science.run_drug_discovery_project(n_candidates=15)
    materials= science.run_materials_design_project(
                   target_properties={"tensile_strength_mpa": 800})
    energy   = science.run_energy_optimization_project(demand_mw=50)

    # Feed to meta
    meta.feed_from_other_modules({
        "drug_discovery": drug,
        "materials":      materials,
        "energy":         energy,
    })

    # Meta-discovery cycle
    discovery_result = meta.run_full_discovery_cycle()
    dt = time.time() - t0

    assert "laws_discovered"      in discovery_result
    assert "algorithms_generated" in discovery_result
    assert "patterns_found"       in discovery_result
    assert len(discovery_result["algorithms_generated"]) >= 1
    assert science.get_project_report()["total_projects"] == 3

    n_laws  = len(discovery_result["laws_discovered"])
    n_algos = len(discovery_result["algorithms_generated"])
    n_pats  = len(discovery_result["patterns_found"])

    print(f"  ✅ PASSED")
    print(f"     laws={n_laws}  algorithms={n_algos}  patterns={n_pats}"
          f"  science_projects=3  time={dt:.3f}s")
    results["test7"] = {"status": "PASSED", "laws": n_laws,
                        "algorithms": n_algos, "patterns": n_pats, "time": dt}

except Exception as e:
    print(f"  ❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    results["test7"] = {"status": "FAILED", "error": str(e)}

# ==============================================================================
# FINAL REPORT
# ==============================================================================
print()
print("=" * 70)
print("📊  TEST SUMMARY")
print("=" * 70)

passed = sum(1 for r in results.values() if r.get("status") == "PASSED")
total  = len(results)

for name, r in results.items():
    icon = "✅" if r.get("status") == "PASSED" else "❌"
    t    = f"  {r.get('time',0):.3f}s" if "time" in r else ""
    print(f"  {icon}  {name}: {r.get('status','?')}{t}")

print()
print(f"  Total  : {total}")
print(f"  Passed : {passed}")
print(f"  Failed : {total - passed}")
print(f"  Rate   : {passed/total:.0%}")

# Save report
ts     = datetime.now().strftime("%Y%m%d_%H%M%S")
report = {
    "timestamp":    ts,
    "summary":      {"total": total, "passed": passed, "failed": total-passed,
                     "success_rate": passed/total},
    "tests":        results,
}
rfile = f"test_results/report_{ts}.json"
Path(rfile).write_text(json.dumps(report, indent=2, default=str))
print(f"\n  💾 Report saved: {rfile}")

print()
if passed == total:
    print("  🎉  ALL TESTS PASSED! System is fully operational.")
else:
    print(f"  ⚠️   {total-passed} test(s) failed. Check errors above.")
print("=" * 70)

raise SystemExit(0 if passed == total else 1)