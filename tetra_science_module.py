"""
================================================================================
TETRA OS — tetra_science_module.py
Módulos científicos: Drug Design, Materials, Energy
Autor: Walter Calmels K.
================================================================================
"""

import numpy as np
import time
import json
import random
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

Path("tetra_data/results").mkdir(parents=True, exist_ok=True)


# ==============================================================================
# ESTRUCTURAS DE DATOS
# ==============================================================================

@dataclass
class MolecularStructure:
    smiles:          str
    molecular_weight:float
    num_atoms:       int
    properties:      Dict[str, float]

    def to_dict(self):
        return {
            "smiles":           self.smiles,
            "molecular_weight": self.molecular_weight,
            "num_atoms":        self.num_atoms,
            "properties":       self.properties,
        }


@dataclass
class MaterialComposition:
    elements:        Dict[str, float]
    crystal_structure:str
    properties:      Dict[str, float]

    def to_dict(self):
        return {
            "elements":          self.elements,
            "crystal_structure": self.crystal_structure,
            "properties":        self.properties,
        }


# ==============================================================================
# DRUG DESIGN OPTIMIZER
# ==============================================================================

FRAGMENTS = [
    "benzene","pyridine","furan","thiophene","imidazole",
    "morpholine","piperidine","piperazine","indole","quinoline",
]

ELEMENT_DB = {
    "Ti": {"atomic_weight":47.87,"cost_per_kg":15, "density":4.51},
    "Al": {"atomic_weight":26.98,"cost_per_kg":2,  "density":2.70},
    "Fe": {"atomic_weight":55.85,"cost_per_kg":0.5,"density":7.87},
    "Ni": {"atomic_weight":58.69,"cost_per_kg":18, "density":8.90},
    "Cr": {"atomic_weight":52.00,"cost_per_kg":8,  "density":7.19},
    "Co": {"atomic_weight":58.93,"cost_per_kg":30, "density":8.86},
    "Cu": {"atomic_weight":63.55,"cost_per_kg":8,  "density":8.96},
    "Mg": {"atomic_weight":24.31,"cost_per_kg":3,  "density":1.74},
    "V":  {"atomic_weight":50.94,"cost_per_kg":30, "density":6.11},
    "Zr": {"atomic_weight":91.22,"cost_per_kg":40, "density":6.52},
}

CRYSTAL_STRUCTURES = ["FCC","BCC","HCP","Cubic","Tetragonal","Orthorhombic"]

ENERGY_TECH = {
    "solar_pv":      {"efficiency":(0.15,0.25),"lcoe":(20,60), "cf":(0.15,0.25),"cost_mw":1.0},
    "wind":          {"efficiency":(0.35,0.45),"lcoe":(30,80), "cf":(0.25,0.45),"cost_mw":1.5},
    "battery_storage":{"efficiency":(0.85,0.95),"lcoe":(100,300),"cf":(0.90,0.99),"cost_mw":0.5},
    "hydrogen":      {"efficiency":(0.50,0.70),"lcoe":(80,200),"cf":(0.80,0.95),"cost_mw":2.0},
}


class DrugDesignOptimizer:
    """Fragment-based drug design with multi-objective optimization."""

    def generate_candidate_molecules(self, n: int = 100) -> List[MolecularStructure]:
        candidates = []
        for i in range(n):
            mw  = np.random.uniform(200, 600)
            logP= np.random.uniform(-2, 5)
            hbd = int(np.random.randint(0, 6))
            hba = int(np.random.randint(0, 11))
            tpsa= np.random.uniform(20, 140)
            rb  = int(np.random.randint(0, 11))
            frags = random.sample(FRAGMENTS, min(3, len(FRAGMENTS)))
            ba   = -5.0 - 2.0 * np.exp(-((mw-400)**2)/(2*100**2)) \
                        - 1.5 * np.exp(-((logP-2.5)**2)/(2*1.5**2)) \
                        + np.random.normal(0, 0.3)
            candidates.append(MolecularStructure(
                smiles="-".join(frags),
                molecular_weight=mw,
                num_atoms=int(mw / 13),
                properties={"binding_affinity":ba,"logP":logP,
                            "hbd":hbd,"hba":hba,"tpsa":tpsa,"rotatable_bonds":rb},
            ))
        return candidates

    def _score(self, mol: MolecularStructure) -> float:
        p = mol.properties
        binding_score = min(1.0, abs(p["binding_affinity"]) / 15.0)
        violations    = sum([
            mol.molecular_weight > 500,
            p["logP"] > 5,
            p.get("hbd", 0) > 5,
            p.get("hba", 0) > 10,
        ])
        lipinski_score= max(0.0, (4 - violations) / 4.0)
        dl_score      = max(0.0, 1.0
                            - (0.3 if (p.get("tpsa",0) < 20 or p.get("tpsa",0) > 140) else 0)
                            - (0.2 if p.get("rotatable_bonds",0) > 10 else 0))
        return binding_score * 0.4 + lipinski_score * 0.35 + dl_score * 0.25

    # Public alias
    def _calculate_drug_score(self, mol: MolecularStructure) -> float:
        return self._score(mol)

    def _mutate(self, mol: MolecularStructure) -> MolecularStructure:
        p   = mol.properties.copy()
        keys= random.sample(list(p.keys()), min(2, len(p)))
        for k in keys:
            if k == "binding_affinity":
                p[k] += np.random.normal(0, 0.5)
            elif k == "logP":
                p[k] += np.random.normal(0, 0.3)
            else:
                p[k] += np.random.normal(0, 0.2)
        return MolecularStructure(
            smiles=mol.smiles + "*",
            molecular_weight=mol.molecular_weight + np.random.normal(0, 10),
            num_atoms=mol.num_atoms + np.random.randint(-2, 3),
            properties=p,
        )

    def optimize_drug_candidate(
        self,
        mol: MolecularStructure,
        target: str = "GPCR",
        max_iterations: int = 100,
    ) -> Dict[str, Any]:
        print(f"  💊 Optimizing for {target} ...")
        current  = mol
        best     = current
        best_sc  = self._score(current)
        history  = [best_sc]
        T        = 1.0

        for i in range(max_iterations):
            candidate = self._mutate(current)
            sc        = self._score(candidate)
            T         = 1.0 - i / max_iterations
            if sc > best_sc or np.random.rand() < T:
                current = candidate
                if sc > best_sc:
                    best, best_sc = candidate, sc
            history.append(best_sc)

        return {
            "optimized_molecule": best.to_dict(),
            "final_score":        best_sc,
            "improvement":        best_sc - history[0],
            "iterations":         max_iterations,
            "optimization_history": history[-20:],
        }


# ==============================================================================
# MATERIALS OPTIMIZER
# ==============================================================================

class MaterialsOptimizer:
    """Alloy design via composition-space search."""

    def design_alloy(
        self,
        target_properties: Dict[str, float],
        available_elements: Optional[List[str]] = None,
        max_iterations: int = 200,
    ) -> Dict[str, Any]:
        if available_elements is None:
            available_elements = list(ELEMENT_DB.keys())

        available_elements = [e for e in available_elements if e in ELEMENT_DB]
        print(f"  🔧 Designing alloy from {available_elements} ...")

        best = self._random_composition(available_elements)
        best_sc = self._evaluate(best, target_properties)
        history = [best_sc]

        for _ in range(max_iterations):
            candidate = self._mutate_composition(best, available_elements)
            sc = self._evaluate(candidate, target_properties)
            if sc > best_sc:
                best, best_sc = candidate, sc
            history.append(best_sc)

        predicted = self._predict_properties(best)
        return {
            "composition":          best.to_dict(),
            "predicted_properties": predicted,
            "optimization_score":   best_sc,
            "estimated_cost_per_kg":self._cost(best),
            "history":              history[-20:],
        }

    def _random_composition(self, elements: List[str]) -> MaterialComposition:
        n    = np.random.randint(2, min(5, len(elements) + 1))
        sel  = random.sample(elements, n)
        fracs= np.random.dirichlet(np.ones(n))
        return MaterialComposition(
            elements={e: float(f) for e, f in zip(sel, fracs)},
            crystal_structure=random.choice(CRYSTAL_STRUCTURES),
            properties={},
        )

    def _evaluate(self, comp: MaterialComposition, targets: Dict[str, float]) -> float:
        pred  = self._predict_properties(comp)
        score = 0.0
        for prop, target in targets.items():
            if prop in pred and target != 0:
                diff = abs(pred[prop] - target) / abs(target)
                score += max(0, 1.0 - diff)
        return score / max(1, len(targets))

    def _predict_properties(self, comp: MaterialComposition) -> Dict[str, float]:
        density = sum(ELEMENT_DB[e]["density"]    * f for e, f in comp.elements.items() if e in ELEMENT_DB)
        cost    = sum(ELEMENT_DB[e]["cost_per_kg"]* f for e, f in comp.elements.items() if e in ELEMENT_DB)
        # Empirical strength / modulus / hardness (hashed for reproducibility)
        rng = np.random.RandomState(hash(str(sorted(comp.elements.items()))) % (2**31))
        sigma = 200 + sum(f * (rng.randint(200, 700)) for _, f in comp.elements.items())
        E     = 50  + sum(f * (rng.randint(50,  250)) for _, f in comp.elements.items())
        hv    = 100 + sum(f * (rng.randint(100, 400)) for _, f in comp.elements.items())
        return {
            "density_g_cm3":        round(float(density), 3),
            "cost_per_kg":          round(float(cost), 2),
            "tensile_strength_mpa": round(float(sigma), 1),
            "youngs_modulus_gpa":   round(float(E), 1),
            "hardness_hv":          round(float(hv), 1),
            "melting_point_k":      round(float(1200 + np.random.uniform(-200, 400)), 0),
        }

    def _mutate_composition(
        self, comp: MaterialComposition, elements: List[str]
    ) -> MaterialComposition:
        el   = comp.elements.copy()
        roll = np.random.rand()
        if roll < 0.5 and len(el) >= 2:
            k1, k2 = random.sample(list(el.keys()), 2)
            delta   = np.random.uniform(-0.15, 0.15)
            el[k1]  = max(0.01, el[k1] + delta)
            el[k2]  = max(0.01, el[k2] - delta)
        elif roll < 0.75 and len(el) < 6:
            unused = [e for e in elements if e not in el]
            if unused:
                el[random.choice(unused)] = 0.1
        elif len(el) > 2:
            del el[random.choice(list(el.keys()))]
        total = sum(el.values())
        el    = {k: v / total for k, v in el.items()}
        return MaterialComposition(elements=el,
                                   crystal_structure=comp.crystal_structure,
                                   properties={})

    def _cost(self, comp: MaterialComposition) -> float:
        return round(sum(ELEMENT_DB[e]["cost_per_kg"] * f
                         for e, f in comp.elements.items() if e in ELEMENT_DB), 2)


# ==============================================================================
# ENERGY SYSTEM OPTIMIZER
# ==============================================================================

class EnergySystemOptimizer:
    """Multi-source energy mix optimization."""

    def optimize_energy_mix(
        self,
        demand_profile: Dict[str, float],
        budget_million_usd: float,
        constraints: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        avg_demand = float(np.mean(list(demand_profile.values()))) if demand_profile else 100.0
        print(f"  ⚡ Optimizing energy mix (demand≈{avg_demand:.0f} MW, budget=${budget_million_usd}M) ...")

        best_config = self._random_config()
        best_sc     = self._evaluate_config(best_config, avg_demand, budget_million_usd)
        history     = [best_sc]

        for _ in range(100):
            candidate = self._mutate_config(best_config)
            sc        = self._evaluate_config(candidate, avg_demand, budget_million_usd)
            if sc > best_sc:
                best_config, best_sc = candidate, sc
            history.append(best_sc)

        total_cap = sum(best_config["capacities"].values())
        lcoe      = self._weighted_lcoe(best_config)
        ren_frac  = self._renewable_fraction(best_config)

        return {
            "optimal_mix":           best_config,
            "total_capacity_mw":     round(total_cap, 1),
            "weighted_lcoe_usd_mwh": lcoe,
            "renewable_fraction":    round(ren_frac, 3),
            "optimization_score":    best_sc,
            "history":               history[-20:],
        }

    def _random_config(self) -> Dict:
        techs = random.sample(list(ENERGY_TECH.keys()), np.random.randint(2, len(ENERGY_TECH)+1))
        return {"capacities": {t: np.random.uniform(10, 300) for t in techs},
                "storage_hours": np.random.uniform(2, 10)}

    def _evaluate_config(self, cfg: Dict, demand: float, budget: float) -> float:
        total_cost = sum(cap * ENERGY_TECH[t]["cost_mw"]
                         for t, cap in cfg["capacities"].items())
        if total_cost > budget:
            return 0.05
        total_cap   = sum(cfg["capacities"].values())
        ratio       = total_cap / max(demand, 1)
        cap_score   = 1.0 if 0.9 <= ratio <= 1.5 else (ratio / 0.9 if ratio < 0.9 else 1.5 / ratio)
        ren_bonus   = self._renewable_fraction(cfg)
        cost_score  = max(0, 1.0 - total_cost / budget)
        return cap_score * 0.5 + ren_bonus * 0.3 + cost_score * 0.2

    def _mutate_config(self, cfg: Dict) -> Dict:
        new = {"capacities": cfg["capacities"].copy(),
               "storage_hours": cfg["storage_hours"]}
        if new["capacities"]:
            t = random.choice(list(new["capacities"].keys()))
            new["capacities"][t] = max(10, new["capacities"][t] + np.random.uniform(-50, 50))
        new["storage_hours"] = max(1, min(20, new["storage_hours"] + np.random.uniform(-1, 1)))
        return new

    def _renewable_fraction(self, cfg: Dict) -> float:
        renewables = {"solar_pv", "wind"}
        total = sum(cfg["capacities"].values())
        if total == 0:
            return 0.0
        return sum(cap for t, cap in cfg["capacities"].items() if t in renewables) / total

    def _weighted_lcoe(self, cfg: Dict) -> float:
        total = sum(cfg["capacities"].values())
        if total == 0:
            return 0.0
        lcoe = sum(
            (cap / total) * float(np.mean(ENERGY_TECH[t]["lcoe"]))
            for t, cap in cfg["capacities"].items()
            if t in ENERGY_TECH
        )
        return round(lcoe, 2)


# ==============================================================================
# SCIENTIFIC ORCHESTRATOR
# ==============================================================================

class ScientificOrchestrator:
    """Runs drug, materials and energy projects."""

    def __init__(self):
        self.drug_opt      = DrugDesignOptimizer()
        self.mat_opt       = MaterialsOptimizer()
        self.energy_opt    = EnergySystemOptimizer()
        self.project_log   = []
        print("🔬 ScientificOrchestrator ready.")

    # ── Drug ──────────────────────────────────────────────────────────────────
    def run_drug_discovery_project(
        self,
        target: str = "GPCR",
        n_candidates: int = 50,
    ) -> Dict[str, Any]:
        print(f"\n💊 Drug Discovery — target={target}, n={n_candidates}")
        t0         = time.time()
        candidates = self.drug_opt.generate_candidate_molecules(n_candidates)
        scored     = sorted(candidates, key=self.drug_opt._score, reverse=True)
        top5_results = [
            self.drug_opt.optimize_drug_candidate(mol, target, max_iterations=50)
            for mol in scored[:5]
        ]
        best = max(top5_results, key=lambda r: r["final_score"])
        summary = {
            "project_type":     "drug_discovery",
            "target":           target,
            "candidates_total": n_candidates,
            "best_candidate":   best,
            "top5_candidates":  top5_results,
            "elapsed_s":        round(time.time() - t0, 2),
            "timestamp":        datetime.now().isoformat(),
        }
        self.project_log.append(summary)
        print(f"  ✅ Best score={best['final_score']:.3f}  improvement={best['improvement']:.3f}")
        return summary

    # ── Materials ─────────────────────────────────────────────────────────────
    def run_materials_design_project(
        self,
        target_properties: Optional[Dict[str, float]] = None,
        elements: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if target_properties is None:
            target_properties = {"tensile_strength_mpa": 900, "density_g_cm3": 4.0}
        print(f"\n🔧 Materials Design — targets={target_properties}")
        t0     = time.time()
        result = self.mat_opt.design_alloy(target_properties, elements, max_iterations=150)
        summary = {
            "project_type":     "materials_design",
            "target_properties":target_properties,
            "result":           result,
            "elapsed_s":        round(time.time() - t0, 2),
            "timestamp":        datetime.now().isoformat(),
        }
        self.project_log.append(summary)
        print(f"  ✅ score={result['optimization_score']:.3f}  cost=${result['estimated_cost_per_kg']}/kg")
        return summary

    # ── Energy ────────────────────────────────────────────────────────────────
    def run_energy_optimization_project(
        self,
        demand_mw: float = 100.0,
        budget_million: float = 200.0,
    ) -> Dict[str, Any]:
        print(f"\n⚡ Energy Optimization — demand={demand_mw}MW  budget=${budget_million}M")
        t0 = time.time()
        demand_profile = {f"h{i}": demand_mw * (0.7 + 0.3 * np.sin(i * np.pi / 12))
                          for i in range(24)}
        result = self.energy_opt.optimize_energy_mix(demand_profile, budget_million)
        summary = {
            "project_type":  "energy_optimization",
            "demand_mw":     demand_mw,
            "budget_million":budget_million,
            "result":        result,
            "elapsed_s":     round(time.time() - t0, 2),
            "timestamp":     datetime.now().isoformat(),
        }
        self.project_log.append(summary)
        print(f"  ✅ capacity={result['total_capacity_mw']:.1f}MW  "
              f"RE={result['renewable_fraction']:.1%}  "
              f"LCOE=${result['weighted_lcoe_usd_mwh']}/MWh")
        return summary

    # ── Integrated ────────────────────────────────────────────────────────────
    def run_integrated_project(self) -> Dict[str, Any]:
        print("\n🚀 Running integrated multi-domain project...")
        drug      = self.run_drug_discovery_project(n_candidates=30)
        materials = self.run_materials_design_project()
        energy    = self.run_energy_optimization_project()
        return {"drug": drug, "materials": materials, "energy": energy,
                "timestamp": datetime.now().isoformat()}

    def get_project_report(self) -> Dict:
        by_type = {}
        for p in self.project_log:
            by_type.setdefault(p["project_type"], []).append(p)
        return {
            "total_projects":    len(self.project_log),
            "projects_by_type":  {k: len(v) for k, v in by_type.items()},
            "latest_project":    self.project_log[-1] if self.project_log else None,
        }


# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    orch = ScientificOrchestrator()
    orch.run_drug_discovery_project(n_candidates=20)
    orch.run_materials_design_project()
    orch.run_energy_optimization_project()
    print("\n", orch.get_project_report())