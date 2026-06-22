"""
================================================================================
TETRA OS — tetra_meta_discovery.py
Motor de meta-descubrimiento: leyes científicas, algoritmos, meta-meta-learning
Autor: Walter Calmels K.
================================================================================
"""

import numpy as np
import json
import hashlib
import random
import time
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

Path("tetra_data/results").mkdir(parents=True, exist_ok=True)


# ==============================================================================
# DATA CLASSES
# ==============================================================================

@dataclass
class DiscoveredLaw:
    law_id:             str
    name:               str
    mathematical_form:  str
    domain:             str
    variables:          List[str]
    constants:          Dict[str, float]
    confidence:         float
    validation_data:    List[Dict] = field(default_factory=list)
    discovery_timestamp:str        = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self):
        return {
            "law_id":    self.law_id,
            "name":      self.name,
            "form":      self.mathematical_form,
            "domain":    self.domain,
            "variables": self.variables,
            "constants": self.constants,
            "confidence":round(self.confidence, 4),
            "validations":len(self.validation_data),
            "discovered":self.discovery_timestamp,
        }


@dataclass
class DiscoveredAlgorithm:
    algorithm_id:       str
    name:               str
    pseudocode:         str
    complexity:         str
    performance_metrics:Dict[str, float]
    applicable_domains: List[str]
    discovery_method:   str
    confidence:         float

    def to_dict(self):
        return {
            "algorithm_id": self.algorithm_id,
            "name":         self.name,
            "pseudocode":   self.pseudocode,
            "complexity":   self.complexity,
            "performance":  self.performance_metrics,
            "domains":      self.applicable_domains,
            "confidence":   round(self.confidence, 4),
        }


@dataclass
class MetaPattern:
    pattern_id:         str
    pattern_type:       str
    description:        str
    occurrences:        int
    domains_found:      List[str]
    generalization_level:float

    def to_dict(self):
        return {
            "pattern_id":     self.pattern_id,
            "type":           self.pattern_type,
            "description":    self.description,
            "occurrences":    self.occurrences,
            "domains":        self.domains_found,
            "generalization": round(self.generalization_level, 4),
        }


# ==============================================================================
# LAW DISCOVERY ENGINE
# ==============================================================================

class LawDiscoveryEngine:
    """Discovers mathematical relationships from numerical data."""

    TEMPLATES = ["linear","power_law","exponential","logarithmic","polynomial"]

    def __init__(self):
        self.discovered_laws: List[DiscoveredLaw] = []

    def discover_laws_from_data(
        self,
        data: Dict[str, np.ndarray],
        domain: str = "general",
        min_confidence: float = 0.65,
    ) -> List[DiscoveredLaw]:
        print(f"\n🔍 Law discovery in domain '{domain}' ...")
        variables = list(data.keys())
        found: List[DiscoveredLaw] = []

        for i in range(len(variables)):
            for j in range(i + 1, len(variables)):
                vx, vy = variables[i], variables[j]
                x, y   = np.asarray(data[vx], dtype=float), np.asarray(data[vy], dtype=float)
                if len(x) < 5:
                    continue
                law = self._find_best_relationship(vx, x, vy, y, domain)
                if law and law.confidence >= min_confidence:
                    found.append(law)
                    print(f"  ✨ {law.name}  R²={law.confidence:.3f}")

        self.discovered_laws.extend(found)
        return found

    # ── Internals ─────────────────────────────────────────────────────────────

    def _find_best_relationship(
        self, vx, x, vy, y, domain
    ) -> Optional[DiscoveredLaw]:
        best_score, best_fit, best_tmpl = -np.inf, None, None

        for tmpl in self.TEMPLATES:
            fit = self._fit(tmpl, x, y)
            if fit["score"] > best_score:
                best_score, best_fit, best_tmpl = fit["score"], fit, tmpl

        if best_score < 0.5:
            return None

        lid  = hashlib.md5(f"{vx}{vy}{domain}".encode()).hexdigest()[:8]
        form = self._format_equation(best_tmpl, best_fit["params"], vx, vy)
        name = f"{best_tmpl.replace('_',' ').title()} — {vx} vs {vy} ({domain})"

        return DiscoveredLaw(
            law_id=lid, name=name, mathematical_form=form,
            domain=domain, variables=[vx, vy],
            constants=best_fit["params"], confidence=best_score,
            validation_data=[{"x_range":[float(x.min()),float(x.max())],
                              "r_squared":best_score}],
        )

    def _fit(self, template: str, x: np.ndarray, y: np.ndarray) -> Dict:
        eps = 1e-10
        try:
            if template == "linear":
                c = np.polyfit(x, y, 1)
                y_p = c[0]*x + c[1]
                return {"score": max(0, self._r2(y, y_p)),
                        "params": {"a": float(c[0]), "b": float(c[1])}}

            if template == "power_law":
                mask = (x > 0) & (y > 0)
                if mask.sum() < 3:
                    return {"score": 0, "params": {}}
                c = np.polyfit(np.log(x[mask]+eps), np.log(y[mask]+eps), 1)
                a, b = np.exp(c[1]), c[0]
                y_p  = a * np.power(np.abs(x)+eps, b)
                return {"score": max(0, self._r2(y, y_p)),
                        "params": {"a": float(a), "b": float(b)}}

            if template == "exponential":
                y_safe = np.where(y > 0, y, eps)
                c = np.polyfit(x, np.log(y_safe), 1)
                a, b = np.exp(c[1]), c[0]
                y_p  = a * np.exp(b * x)
                return {"score": max(0, self._r2(y, y_p)),
                        "params": {"a": float(a), "b": float(b)}}

            if template == "logarithmic":
                x_safe = np.where(x > 0, x, eps)
                c = np.polyfit(np.log(x_safe), y, 1)
                y_p = c[0]*np.log(x_safe) + c[1]
                return {"score": max(0, self._r2(y, y_p)),
                        "params": {"a": float(c[0]), "b": float(c[1])}}

            if template == "polynomial":
                c = np.polyfit(x, y, 2)
                y_p = c[0]*x**2 + c[1]*x + c[2]
                return {"score": max(0, self._r2(y, y_p)),
                        "params": {"a": float(c[0]), "b": float(c[1]), "c": float(c[2])}}

        except Exception:
            pass
        return {"score": 0.0, "params": {}}

    @staticmethod
    def _r2(y_true, y_pred) -> float:
        ss_res = float(np.sum((y_true - y_pred)**2))
        ss_tot = float(np.sum((y_true - y_true.mean())**2))
        return 1.0 - ss_res / ss_tot if ss_tot > 1e-10 else 0.0

    def _format_equation(self, tmpl, params, vx, vy) -> str:
        if tmpl == "linear":
            return f"{vy} = {params['a']:.4f}·{vx} + {params['b']:.4f}"
        if tmpl == "power_law":
            return f"{vy} = {params['a']:.4f}·{vx}^{params['b']:.4f}"
        if tmpl == "exponential":
            return f"{vy} = {params['a']:.4f}·exp({params['b']:.4f}·{vx})"
        if tmpl == "logarithmic":
            return f"{vy} = {params['a']:.4f}·log({vx}) + {params['b']:.4f}"
        if tmpl == "polynomial":
            return (f"{vy} = {params['a']:.4f}·{vx}² "
                    f"+ {params['b']:.4f}·{vx} + {params['c']:.4f}")
        return f"{vy} = f({vx})"

    def validate_law(self, law: DiscoveredLaw, new_data: Dict[str, np.ndarray]) -> float:
        vx, vy = law.variables
        if vx not in new_data or vy not in new_data:
            return 0.0
        x, y  = np.asarray(new_data[vx], dtype=float), np.asarray(new_data[vy], dtype=float)
        y_p   = self._apply_law(law, x)
        r2    = self._r2(y, y_p)
        law.confidence = 0.7 * law.confidence + 0.3 * max(0, r2)
        return r2

    def _apply_law(self, law: DiscoveredLaw, x: np.ndarray) -> np.ndarray:
        p, form = law.constants, law.mathematical_form
        eps     = 1e-10
        if "exp(" in form:
            return p["a"] * np.exp(p["b"] * x)
        if "^" in form:
            return p["a"] * np.power(np.abs(x) + eps, p["b"])
        if "log(" in form:
            return p["a"] * np.log(np.abs(x) + eps) + p["b"]
        if "²" in form:
            return p["a"]*x**2 + p["b"]*x + p.get("c", 0)
        return p["a"] * x + p.get("b", 0)


# ==============================================================================
# ALGORITHM DISCOVERY ENGINE
# ==============================================================================

class AlgorithmDiscoveryEngine:
    """Generates novel algorithms from component composition."""

    COMPONENTS = {
        "data_structures": ["array","tree","graph","hash_table","heap","trie"],
        "control_flow":    ["loop","recursion","divide_conquer","dynamic_programming"],
        "optimization":    ["greedy","branch_bound","gradient","genetic"],
        "search":          ["binary_search","bfs","dfs","a_star","beam_search"],
    }

    COMPLEXITY_MAP = {
        "binary_search":      "O(log n)",
        "bfs":                "O(V + E)",
        "dfs":                "O(V + E)",
        "dynamic_programming":"O(n²)",
        "greedy":             "O(n log n)",
        "divide_conquer":     "O(n log n)",
        "heap":               "O(n log n)",
        "hash_table":         "O(n)",
        "loop":               "O(n)",
        "gradient":           "O(n·d)",
        "genetic":            "O(g·p·d)",
        "a_star":             "O(b^d)",
    }

    def __init__(self):
        self.discovered_algorithms: List[DiscoveredAlgorithm] = []

    def generate_novel_algorithm(self, problem: Dict[str, Any]) -> DiscoveredAlgorithm:
        ptype = problem.get("type", "optimization")
        print(f"\n🧬 Generating algorithm for problem type '{ptype}' ...")

        components = self._select_components(ptype, problem.get("constraints", {}))
        structure  = self._compose(components, ptype)
        pseudocode = self._pseudocode(structure, problem.get("name", "problem"))
        complexity = self._complexity(structure)
        performance= self._simulate_performance(structure)
        name       = self._name(structure)
        aid        = hashlib.md5(pseudocode.encode()).hexdigest()[:8]

        algo = DiscoveredAlgorithm(
            algorithm_id=aid, name=name, pseudocode=pseudocode,
            complexity=complexity, performance_metrics=performance,
            applicable_domains=[ptype], discovery_method="component_composition",
            confidence=float(np.mean(list(performance.values()))),
        )
        self.discovered_algorithms.append(algo)
        print(f"  ✨ {name}  complexity={complexity}  conf={algo.confidence:.3f}")
        return algo

    def _select_components(self, ptype, constraints) -> List[str]:
        mapping = {
            "optimization": ["dynamic_programming","greedy","hash_table"],
            "search":       ["binary_search","bfs","tree"],
            "sorting":      ["divide_conquer","heap","array"],
            "graph":        ["graph","dfs","bfs","a_star"],
        }
        comps = mapping.get(ptype, ["array","loop","hash_table"]).copy()
        if constraints:
            comps.append("greedy")
        return list(set(comps))

    def _compose(self, components, ptype) -> Dict:
        ds_set = set(self.COMPONENTS["data_structures"])
        cf_set = set(self.COMPONENTS["control_flow"])
        op_set = set(self.COMPONENTS["optimization"])

        return {
            "main_strategy":  components[0],
            "data_structures":[c for c in components if c in ds_set],
            "control_flow":   [c for c in components if c in cf_set],
            "optimization":   [c for c in components if c in op_set],
            "steps": [
                "Initialize data structures and parameters",
                "Preprocess and validate input",
                f"Apply {components[0].replace('_',' ')} strategy",
                "Iterate and refine solution",
                "Evaluate convergence / stopping criterion",
                "Return best solution found",
            ],
        }

    def _pseudocode(self, structure, prob_name) -> str:
        lines = [
            f"Algorithm: {self._name(structure)}",
            f"Problem  : {prob_name}",
            f"Input    : problem_data",
            f"Output   : solution",
            "",
        ]
        for i, step in enumerate(structure["steps"], 1):
            lines.append(f"  {i}. {step}")
        if structure["data_structures"]:
            lines.append(f"\nData structures : {', '.join(structure['data_structures'])}")
        if structure["control_flow"]:
            lines.append(f"Control flow    : {', '.join(structure['control_flow'])}")
        if structure["optimization"]:
            lines.append(f"Optimization    : {', '.join(structure['optimization'])}")
        return "\n".join(lines)

    def _complexity(self, structure) -> str:
        tc = self.COMPLEXITY_MAP.get(structure["main_strategy"], "O(n)")
        sc = "O(n)" if len(structure["data_structures"]) > 1 else "O(1)"
        return f"Time: {tc}, Space: {sc}"

    def _simulate_performance(self, structure) -> Dict[str, float]:
        speed = 1.0
        if "hash_table" in structure["data_structures"]:
            speed *= 1.4
        if "dynamic_programming" in structure["control_flow"]:
            speed *= 0.75
        if "greedy" in structure["optimization"]:
            speed *= 1.25
        return {
            "speed_score":        float(min(1.0, speed * np.random.uniform(0.85, 1.1))),
            "accuracy_score":     float(np.random.uniform(0.70, 0.95)),
            "memory_efficiency":  float(np.random.uniform(0.60, 0.90)),
            "scalability":        float(np.random.uniform(0.55, 0.90)),
        }

    def _name(self, structure) -> str:
        main = structure["main_strategy"].replace("_", " ").title()
        if structure["optimization"]:
            opt = structure["optimization"][0].replace("_", " ").title()
            return f"{opt}-Enhanced {main} Algorithm"
        return f"Novel {main} Algorithm"

    def evolve_algorithm(
        self, algo: DiscoveredAlgorithm, feedback: Dict[str, float]
    ) -> DiscoveredAlgorithm:
        for metric, value in feedback.items():
            if metric in algo.performance_metrics:
                algo.performance_metrics[metric] = (
                    0.7 * algo.performance_metrics[metric] + 0.3 * value
                )
        algo.confidence = float(np.mean(list(algo.performance_metrics.values())))
        return algo


# ==============================================================================
# META-PATTERN DETECTOR
# ==============================================================================

class MetaPatternDetector:
    def __init__(self):
        self.patterns: List[MetaPattern] = []

    def detect_cross_domain_patterns(
        self, discoveries_by_domain: Dict[str, List]
    ) -> List[MetaPattern]:
        print("\n🌐 Detecting cross-domain patterns ...")
        found: List[MetaPattern] = []
        domains = list(discoveries_by_domain.keys())

        for i in range(len(domains)):
            for j in range(i + 1, len(domains)):
                d1, d2 = domains[i], domains[j]
                common = self._find_common(
                    discoveries_by_domain[d1],
                    discoveries_by_domain[d2],
                    d1, d2,
                )
                found.extend(common)

        significant = [p for p in found if p.occurrences >= 2]
        self.patterns.extend(significant)
        print(f"  ✨ {len(significant)} cross-domain patterns found")
        return significant

    def _find_common(self, d1_list, d2_list, dom1, dom2) -> List[MetaPattern]:
        patterns = []
        laws1 = [d for d in d1_list if isinstance(d, DiscoveredLaw)]
        laws2 = [d for d in d2_list if isinstance(d, DiscoveredLaw)]

        for l1 in laws1:
            for l2 in laws2:
                sim = self._form_similarity(l1.mathematical_form, l2.mathematical_form)
                if sim > 0.7:
                    pid = hashlib.md5(f"{dom1}{dom2}{sim}".encode()).hexdigest()[:8]
                    patterns.append(MetaPattern(
                        pattern_id=pid,
                        pattern_type="mathematical_form_similarity",
                        description=f"Similar relationship in {dom1} and {dom2}",
                        occurrences=2,
                        domains_found=[dom1, dom2],
                        generalization_level=sim,
                    ))
        return patterns

    @staticmethod
    def _normalize_form(form: str) -> str:
        if "exp(" in form: return "exponential"
        if "^"    in form: return "power"
        if "log(" in form: return "logarithmic"
        if "²"    in form: return "polynomial"
        return "linear"

    def _form_similarity(self, f1: str, f2: str) -> float:
        return 1.0 if self._normalize_form(f1) == self._normalize_form(f2) else 0.3


# ==============================================================================
# META-META-LEARNING ENGINE
# ==============================================================================

class MetaMetaLearningEngine:
    def __init__(self):
        self.history:       List[Dict] = []
        self.meta_strategies:List[Dict] = []
        self.adaptation     = {"exploration_rate": 0.3, "exploitation_rate": 0.7}

    def learn_from_discovery(self, discoveries: Dict[str, Any]) -> Dict[str, Any]:
        worked, failed = [], []

        for domain, results in discoveries.items():
            if isinstance(results, list) and results:
                sr = sum(1 for r in results if getattr(r, "confidence", 0) > 0.7) / len(results)
                (worked if sr > 0.6 else failed).append({"domain": domain, "success_rate": sr})

        self.history.append({
            "timestamp":   datetime.now().isoformat(),
            "worked":      worked,
            "failed":      failed,
        })

        strategies = self._generate_strategies(worked, failed)
        self.meta_strategies.extend(strategies)
        self._adjust_adaptation()

        return {"what_worked": worked, "what_failed": failed,
                "new_strategies": len(strategies), "patterns_observed": []}

    def _generate_strategies(self, worked, failed) -> List[Dict]:
        strategies = []
        if worked:
            strategies.append({
                "id": "focus_successful",
                "description": "Prioritise domains with high success rate",
                "domains": [w["domain"] for w in worked], "priority": "high",
            })
        if failed:
            strategies.append({
                "id": "experiment_failed",
                "description": "Try alternative approaches for failing domains",
                "domains": [f["domain"] for f in failed], "priority": "medium",
            })
        if len(worked) > 1:
            strategies.append({
                "id": "transfer_learning",
                "description": "Transfer patterns from successful domains",
                "sources": [w["domain"] for w in worked], "priority": "high",
            })
        return strategies

    def _adjust_adaptation(self):
        if len(self.history) < 5:
            return
        recent = self.history[-5:]
        avg_sr = np.mean([
            np.mean([w["success_rate"] for w in h["worked"]]) if h["worked"] else 0
            for h in recent
        ])
        if avg_sr > 0.75:
            self.adaptation["exploitation_rate"] = min(0.9, self.adaptation["exploitation_rate"] + 0.03)
        elif avg_sr < 0.4:
            self.adaptation["exploration_rate"]  = min(0.5, self.adaptation["exploration_rate"]  + 0.03)
        self.adaptation["exploitation_rate"] = 1.0 - self.adaptation["exploration_rate"]

    def optimize_pipeline(self) -> Dict:
        if len(self.history) < 3:
            return {"message": "Insufficient data for pipeline optimization"}
        success_trend = []
        for h in self.history[-10:]:
            if h["worked"]:
                success_trend.append(np.mean([w["success_rate"] for w in h["worked"]]))
        if len(success_trend) < 2:
            return {"message": "Not enough data points"}
        is_improving = success_trend[-1] > success_trend[0]
        return {
            "is_improving":       is_improving,
            "current_success":    success_trend[-1],
            "improvement_delta":  success_trend[-1] - success_trend[0],
            "recommended_actions":[
                "Continue current approach" if is_improving else "Diversify search strategy",
                "Increase exploration in new domains" if is_improving else "Revisit failed domains",
            ],
        }


# ==============================================================================
# META-DISCOVERY ORCHESTRATOR
# ==============================================================================

class MetaDiscoveryOrchestrator:
    def __init__(self):
        self.law_engine     = LawDiscoveryEngine()
        self.algorithm_engine = AlgorithmDiscoveryEngine()
        self.pattern_detector = MetaPatternDetector()
        self.meta_learning  = MetaMetaLearningEngine()
        self.discovery_history: List[Dict] = []
        self.knowledge_base = {
            "laws": [], "algorithms": [], "patterns": [], "meta_insights": [],
        }
        print("\n🚀 MetaDiscoveryOrchestrator ready.")

    # ── Synthetic data for standalone demo ────────────────────────────────────

    def _synthetic_data(self) -> Dict[str, Dict[str, np.ndarray]]:
        x = np.linspace(1, 10, 50)
        rng = np.random.default_rng(42)
        return {
            "physics": {
                "mass":         x,
                "force":        9.81 * x + rng.normal(0, 0.5, 50),
                "acceleration": np.full(50, 9.81) + rng.normal(0, 0.1, 50),
            },
            "chemistry": {
                "temperature":   np.linspace(273, 373, 50),
                "reaction_rate": 0.1 * np.exp(0.01 * (np.linspace(273,373,50)-273))
                                 + rng.normal(0, 0.005, 50),
            },
            "materials": {
                "strain": np.linspace(0, 0.005, 50),
                "stress": 200_000 * np.linspace(0, 0.005, 50) + rng.normal(0, 100, 50),
            },
            "energy": {
                "voltage": x,
                "current": 0.5 * x + rng.normal(0, 0.1, 50),
                "power":   0.5 * x**2 + rng.normal(0, 1, 50),
            },
        }

    # ── Full discovery cycle ───────────────────────────────────────────────────

    def run_full_discovery_cycle(
        self, input_data: Optional[Dict[str, Dict[str, np.ndarray]]] = None
    ) -> Dict[str, Any]:
        print("\n" + "="*70)
        print("🔬 META-DISCOVERY — Full Cycle")
        print("="*70)

        if input_data is None:
            print("  (Using synthetic demonstration data)")
            input_data = self._synthetic_data()

        # Phase 1 — Law discovery
        print("\n📊 Phase 1: Law Discovery")
        discoveries_by_domain: Dict[str, List] = {}
        all_laws: List[DiscoveredLaw] = []

        for domain, data in input_data.items():
            laws = self.law_engine.discover_laws_from_data(data, domain)
            discoveries_by_domain[domain] = laws
            all_laws.extend(laws)
            self.knowledge_base["laws"].extend(laws)

        # Phase 2 — Algorithm generation
        print("\n🧬 Phase 2: Algorithm Generation")
        problem_types = ["optimization","search","sorting","graph"]
        all_algos: List[DiscoveredAlgorithm] = []

        for ptype in problem_types:
            algo = self.algorithm_engine.generate_novel_algorithm({
                "name": f"{ptype}_problem",
                "type": ptype,
                "constraints": {"time": "minimize"},
            })
            all_algos.append(algo)
            self.knowledge_base["algorithms"].append(algo)

        # Phase 3 — Pattern detection
        print("\n🌐 Phase 3: Meta-Pattern Detection")
        patterns = self.pattern_detector.detect_cross_domain_patterns(discoveries_by_domain)
        self.knowledge_base["patterns"].extend(patterns)

        # Phase 4 — Meta-meta-learning
        print("\n🎓 Phase 4: Meta-Meta-Learning")
        meta_insights = self.meta_learning.learn_from_discovery(discoveries_by_domain)
        pipeline_opt  = self.meta_learning.optimize_pipeline()
        self.knowledge_base["meta_insights"].append(meta_insights)

        result = {
            "timestamp":            datetime.now().isoformat(),
            "laws_discovered":      all_laws,
            "algorithms_generated": all_algos,
            "patterns_found":       patterns,
            "meta_insights":        meta_insights,
            "pipeline_optimization":pipeline_opt,
        }

        self.discovery_history.append({
            "timestamp":    result["timestamp"],
            "n_laws":       len(all_laws),
            "n_algos":      len(all_algos),
            "n_patterns":   len(patterns),
        })

        # Summary
        print(f"\n{'='*70}")
        print(f"  Laws discovered     : {len(all_laws)}")
        print(f"  Algorithms generated: {len(all_algos)}")
        print(f"  Patterns found      : {len(patterns)}")
        print(f"  Is improving        : {pipeline_opt.get('is_improving', 'N/A')}")
        print(f"{'='*70}")

        return result

    # ── Feed from other modules ────────────────────────────────────────────────

    def feed_from_other_modules(self, module_results: Dict[str, Any]):
        print("\n🍽️  Feeding from other modules ...")
        for source, data in module_results.items():
            insight = {"source": source, "timestamp": datetime.now().isoformat(),
                       "summary": str(type(data).__name__)}
            self.knowledge_base["meta_insights"].append(insight)
            print(f"  ✓ Integrated: {source}")
        self.meta_learning._adjust_adaptation()

    # ── Export ────────────────────────────────────────────────────────────────

    def export_knowledge_base(self, filename: Optional[str] = None) -> str:
        if filename is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"tetra_data/results/knowledge_base_{ts}.json"
        export = {
            "timestamp":    datetime.now().isoformat(),
            "laws":         [l.to_dict() for l in self.knowledge_base["laws"]],
            "algorithms":   [a.to_dict() for a in self.knowledge_base["algorithms"]],
            "patterns":     [p.to_dict() for p in self.knowledge_base["patterns"]],
            "meta_insights":self.knowledge_base["meta_insights"],
            "stats": {
                "total_laws":       len(self.knowledge_base["laws"]),
                "total_algorithms": len(self.knowledge_base["algorithms"]),
                "total_patterns":   len(self.knowledge_base["patterns"]),
                "discovery_cycles": len(self.discovery_history),
            },
        }
        Path(filename).write_text(json.dumps(export, indent=2, default=str))
        print(f"\n💾 Knowledge base exported → {filename}")
        return filename


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    meta = MetaDiscoveryOrchestrator()
    result = meta.run_full_discovery_cycle()
    meta.export_knowledge_base()