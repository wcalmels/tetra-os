"""
================================================================================
TETRA OS — tetra_os_improved.py
Sistema base de optimización con 5 algoritmos y consciencia auto-optimizante
Autor: Walter Calmels K.
================================================================================
"""

import numpy as np
import time
import json
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple, Callable
from collections import defaultdict
from pathlib import Path
import warnings
warnings.filterwarnings("ignore")

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("TetraOS")

# ── Directorios ───────────────────────────────────────────────────────────────
DATA_DIR   = Path("tetra_data")
MODELS_DIR = DATA_DIR / "models"
RESULTS_DIR= DATA_DIR / "results"
LOGS_DIR   = DATA_DIR / "logs"

for _d in [DATA_DIR, MODELS_DIR, RESULTS_DIR, LOGS_DIR]:
    _d.mkdir(parents=True, exist_ok=True)


# ==============================================================================
# ESTRUCTURAS DE DATOS
# ==============================================================================

@dataclass
class OptimizationResult:
    solution:       np.ndarray
    objective_value:float
    iterations:     int
    converged:      bool
    execution_time: float
    algorithm:      str
    metadata:       Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        d = {
            "solution":        self.solution.tolist(),
            "objective_value": self.objective_value,
            "iterations":      self.iterations,
            "converged":       self.converged,
            "execution_time":  self.execution_time,
            "algorithm":       self.algorithm,
            "metadata":        {k: (v.tolist() if isinstance(v, np.ndarray) else v)
                                for k, v in self.metadata.items()},
        }
        return d


@dataclass
class ProblemDefinition:
    problem_id:         str
    problem_type:       str
    dimensions:         int
    bounds:             Tuple[float, float]
    objective_function: Optional[Callable] = None
    constraints:        Optional[List[Callable]] = None
    metadata:           Dict[str, Any] = field(default_factory=dict)


# ==============================================================================
# FUNCIONES BENCHMARK
# ==============================================================================

class BenchmarkFunctions:
    @staticmethod
    def sphere(x: np.ndarray) -> float:
        return float(np.sum(x ** 2))

    @staticmethod
    def rosenbrock(x: np.ndarray) -> float:
        return float(np.sum(100 * (x[1:] - x[:-1] ** 2) ** 2 + (1 - x[:-1]) ** 2))

    @staticmethod
    def rastrigin(x: np.ndarray) -> float:
        A = 10
        return float(A * len(x) + np.sum(x ** 2 - A * np.cos(2 * np.pi * x)))

    @staticmethod
    def ackley(x: np.ndarray) -> float:
        n = len(x)
        return float(
            -20 * np.exp(-0.2 * np.sqrt(np.sum(x ** 2) / n))
            - np.exp(np.sum(np.cos(2 * np.pi * x)) / n)
            + 20 + np.e
        )

    @staticmethod
    def schwefel(x: np.ndarray) -> float:
        return float(418.9829 * len(x) - np.sum(x * np.sin(np.sqrt(np.abs(x)))))

    @staticmethod
    def griewank(x: np.ndarray) -> float:
        return float(
            1
            + np.sum(x ** 2) / 4000
            - np.prod(np.cos(x / np.sqrt(np.arange(1, len(x) + 1))))
        )


# ==============================================================================
# ALGORITMOS DE OPTIMIZACIÓN
# ==============================================================================

class GradientDescentOptimizer:
    name = "GradientDescent"

    def optimize(self, objective, dim, bounds, max_iter=1000, **kw) -> OptimizationResult:
        t0 = time.time()
        lo, hi = bounds
        lr       = kw.get("learning_rate", 0.01)
        momentum = kw.get("momentum", 0.9)
        tol      = kw.get("tolerance", 1e-6)
        eps      = 1e-8

        x   = np.random.uniform(lo, hi, dim)
        vel = np.zeros(dim)
        best_x, best_f = x.copy(), objective(x)
        history = [best_f]

        obj_tol = kw.get("objective_tolerance", 1e-2)
        stopped_early = False
        for i in range(max_iter):
            # Numerical gradient
            grad = np.array([
                (objective(x + eps * np.eye(dim)[j])
                 - objective(x - eps * np.eye(dim)[j])) / (2 * eps)
                for j in range(dim)
            ])
            vel = momentum * vel - lr * grad
            x   = np.clip(x + vel, lo, hi)
            f   = objective(x)
            if f < best_f:
                best_f, best_x = f, x.copy()
            history.append(best_f)
            if i > 10 and abs(history[-1] - history[-10]) < tol:
                stopped_early = True
                break

        return OptimizationResult(
            solution=best_x, objective_value=best_f,
            iterations=i + 1, converged=stopped_early or best_f < obj_tol,
            execution_time=time.time() - t0, algorithm=self.name,
            metadata={"history": history[-100:], "final_lr": lr},
        )


class GeneticAlgorithmOptimizer:
    name = "GeneticAlgorithm"

    def optimize(self, objective, dim, bounds, max_iter=1000, **kw) -> OptimizationResult:
        t0 = time.time()
        lo, hi      = bounds
        pop_size    = kw.get("population_size", 100)
        mut_rate    = kw.get("mutation_rate", 0.1)
        cross_rate  = kw.get("crossover_rate", 0.8)
        n_elite     = max(1, int(pop_size * kw.get("elitism", 0.1)))

        pop     = np.random.uniform(lo, hi, (pop_size, dim))
        fitness = np.array([objective(ind) for ind in pop])
        best_idx = int(np.argmin(fitness))
        best_x, best_f = pop[best_idx].copy(), fitness[best_idx]
        history = [best_f]

        obj_tol = kw.get("objective_tolerance", 1e-2)
        stopped_early = False
        for gen in range(max_iter):
            elite_idx = np.argsort(fitness)[:n_elite]
            new_pop   = [pop[i].copy() for i in elite_idx]

            while len(new_pop) < pop_size:
                # Tournament selection
                p1 = self._tournament(pop, fitness)
                p2 = self._tournament(pop, fitness)
                # Crossover
                child = p1.copy()
                if np.random.rand() < cross_rate:
                    pt = np.random.randint(1, dim)
                    child = np.concatenate([p1[:pt], p2[pt:]])
                # Mutation
                mask = np.random.rand(dim) < mut_rate
                child[mask] += np.random.normal(0, 0.1 * (hi - lo), mask.sum())
                child = np.clip(child, lo, hi)
                new_pop.append(child)

            pop     = np.array(new_pop[:pop_size])
            fitness = np.array([objective(ind) for ind in pop])
            idx     = int(np.argmin(fitness))
            if fitness[idx] < best_f:
                best_f, best_x = fitness[idx], pop[idx].copy()
            history.append(best_f)
            if gen > 50 and abs(history[-1] - history[-50]) < 1e-6:
                stopped_early = True
                break

        return OptimizationResult(
            solution=best_x, objective_value=best_f,
            iterations=gen + 1, converged=stopped_early or best_f < obj_tol,
            execution_time=time.time() - t0, algorithm=self.name,
            metadata={"history": history[-100:],
                      "diversity": float(np.std(fitness))},
        )

    def _tournament(self, pop, fitness, k=3):
        idxs = np.random.choice(len(pop), k, replace=False)
        return pop[idxs[int(np.argmin(fitness[idxs]))]].copy()


class ParticleSwarmOptimizer:
    name = "ParticleSwarm"

    def optimize(self, objective, dim, bounds, max_iter=1000, **kw) -> OptimizationResult:
        t0 = time.time()
        lo, hi = bounds
        n   = kw.get("n_particles", 50)
        w   = kw.get("inertia", 0.7)
        c1  = kw.get("cognitive", 1.5)
        c2  = kw.get("social", 1.5)
        tol = kw.get("tolerance", 1e-6)

        pos  = np.random.uniform(lo, hi, (n, dim))
        vel  = np.zeros((n, dim))
        pb   = pos.copy()
        pf   = np.array([objective(p) for p in pos])
        gi   = int(np.argmin(pf))
        gb   = pos[gi].copy()
        gf   = float(pf[gi])
        history = [gf]

        obj_tol = kw.get("objective_tolerance", 1e-2)
        stopped_early = False
        for i in range(max_iter):
            r1 = np.random.rand(n, dim)
            r2 = np.random.rand(n, dim)
            vel = w * vel + c1 * r1 * (pb - pos) + c2 * r2 * (gb - pos)
            pos = np.clip(pos + vel, lo, hi)
            fits = np.array([objective(p) for p in pos])
            better = fits < pf
            pb[better] = pos[better]
            pf[better] = fits[better]
            idx = int(np.argmin(fits))
            if fits[idx] < gf:
                gf, gb = float(fits[idx]), pos[idx].copy()
            history.append(gf)
            if i > 20 and abs(history[-1] - history[-20]) < tol:
                stopped_early = True
                break

        return OptimizationResult(
            solution=gb, objective_value=gf,
            iterations=i + 1, converged=stopped_early or gf < obj_tol,
            execution_time=time.time() - t0, algorithm=self.name,
            metadata={"history": history[-100:],
                      "swarm_diversity": float(np.mean(np.std(pos, axis=0)))},
        )


class SimulatedAnnealingOptimizer:
    name = "SimulatedAnnealing"

    def optimize(self, objective, dim, bounds, max_iter=1000, **kw) -> OptimizationResult:
        t0 = time.time()
        lo, hi  = bounds
        T       = kw.get("initial_temperature", 100.0)
        T_min   = kw.get("min_temperature", 0.01)
        alpha   = kw.get("cooling_rate", 0.95)

        x       = np.random.uniform(lo, hi, dim)
        f       = objective(x)
        best_x, best_f = x.copy(), f
        history = [best_f]
        accepted= []
        i       = 0

        while T > T_min and i < max_iter:
            step  = T / 100.0 * (hi - lo)
            x_new = np.clip(x + np.random.normal(0, step, dim), lo, hi)
            f_new = objective(x_new)
            delta = f_new - f
            if delta < 0 or np.random.rand() < np.exp(-delta / max(T, 1e-10)):
                x, f = x_new, f_new
                accepted.append(1)
                if f < best_f:
                    best_f, best_x = f, x.copy()
            else:
                accepted.append(0)
            history.append(best_f)
            T *= alpha
            i += 1

        return OptimizationResult(
            solution=best_x, objective_value=best_f,
            iterations=i, converged=T <= T_min or best_f < kw.get("objective_tolerance", 1e-2),
            execution_time=time.time() - t0, algorithm=self.name,
            metadata={"history": history[-100:], "final_T": T,
                      "acceptance_rate": float(np.mean(accepted[-100:]))},
        )


class DifferentialEvolutionOptimizer:
    name = "DifferentialEvolution"

    def optimize(self, objective, dim, bounds, max_iter=1000, **kw) -> OptimizationResult:
        t0 = time.time()
        lo, hi  = bounds
        pop_size= kw.get("population_size", 50)
        F       = kw.get("mutation_factor", 0.8)
        CR      = kw.get("crossover_rate", 0.9)
        tol     = kw.get("tolerance", 1e-6)

        pop     = np.random.uniform(lo, hi, (pop_size, dim))
        fitness = np.array([objective(ind) for ind in pop])
        best_idx= int(np.argmin(fitness))
        best_x  = pop[best_idx].copy()
        best_f  = float(fitness[best_idx])
        history = [best_f]

        obj_tol = kw.get("objective_tolerance", 1e-2)
        stopped_early = False
        for gen in range(max_iter):
            for i in range(pop_size):
                others = [j for j in range(pop_size) if j != i]
                a, b, c = pop[np.random.choice(others, 3, replace=False)]
                mutant  = np.clip(a + F * (b - c), lo, hi)
                cross   = np.random.rand(dim) < CR
                if not cross.any():
                    cross[np.random.randint(dim)] = True
                trial   = np.where(cross, mutant, pop[i])
                tf      = objective(trial)
                if tf < fitness[i]:
                    pop[i], fitness[i] = trial, tf
                    if tf < best_f:
                        best_f, best_x = tf, trial.copy()
            history.append(best_f)
            if gen > 30 and abs(history[-1] - history[-30]) < tol:
                stopped_early = True
                break

        return OptimizationResult(
            solution=best_x, objective_value=best_f,
            iterations=gen + 1, converged=stopped_early or best_f < obj_tol,
            execution_time=time.time() - t0, algorithm=self.name,
            metadata={"history": history[-100:],
                      "population_diversity": float(np.std(fitness))},
        )


# ==============================================================================
# SISTEMA DE CONSCIENCIA
# ==============================================================================

class AdvancedConsciousness:
    def __init__(self):
        self.level          = 0.5
        self.learning_rate  = 0.1
        self.memory         = []
        self.algo_perf      = defaultdict(lambda: {
            "successes": 0, "failures": 0,
            "avg_time": 0.0, "avg_quality": 0.0, "convergence_rate": 0.0,
        })
        self.selection_matrix = defaultdict(lambda: defaultdict(float))
        self.adaptation       = {"exploration": 0.3, "exploitation": 0.7}

    def learn(self, result: OptimizationResult, problem_type: str):
        algo  = result.algorithm
        stats = self.algo_perf[algo]
        alpha = 0.2

        quality = 1.0 / (1.0 + result.objective_value) if result.converged else 0.0

        if result.converged:
            stats["successes"] += 1
        else:
            stats["failures"] += 1

        stats["avg_time"]        = alpha * result.execution_time + (1 - alpha) * stats["avg_time"]
        stats["avg_quality"]     = alpha * quality               + (1 - alpha) * stats["avg_quality"]
        stats["convergence_rate"]= alpha * (1.0 if result.converged else 0.0) + (1 - alpha) * stats["convergence_rate"]

        total = stats["successes"] + stats["failures"]
        if total:
            sr    = stats["successes"] / total
            score = sr * 0.4 + stats["avg_quality"] * 0.4 + (1 / (1 + stats["avg_time"])) * 0.2
            self.selection_matrix[problem_type][algo] = score

        if quality > 0.7:
            self.level = min(0.97, self.level + 0.005)

        self.memory.append({
            "ts": datetime.now().isoformat(),
            "algo": algo, "problem": problem_type,
            "quality": quality, "converged": result.converged,
        })
        if len(self.memory) > 500:
            self.memory = self.memory[-500:]

        self._adapt()

    def select_algorithm(self, problem_type: str, available: List[str]) -> str:
        scores = self.selection_matrix.get(problem_type, {})
        if not scores or np.random.rand() < self.adaptation["exploration"]:
            algo = np.random.choice(available)
            logger.info(f"Explore → {algo}")
            return algo
        scored = [(a, scores.get(a, 0)) for a in available]
        algo   = max(scored, key=lambda x: x[1])[0]
        logger.info(f"Exploit → {algo} (score={scores[algo]:.3f})")
        return algo

    def _adapt(self):
        if len(self.memory) < 20:
            return
        sr = sum(1 for m in self.memory[-20:] if m["quality"] > 0.5) / 20
        if sr > 0.75:
            self.adaptation["exploitation"] = min(0.9, self.adaptation["exploitation"] + 0.02)
        elif sr < 0.4:
            self.adaptation["exploration"] = min(0.5, self.adaptation["exploration"] + 0.02)
        self.adaptation["exploitation"] = 1.0 - self.adaptation["exploration"]

    def get_summary(self) -> Dict:
        return {
            "consciousness_level": self.level,
            "total_experiences":   len(self.memory),
            "adaptation":          self.adaptation.copy(),
            "algorithm_performance": {
                algo: {
                    "total": s["successes"] + s["failures"],
                    "success_rate": s["successes"] / max(1, s["successes"] + s["failures"]),
                    "avg_time":    s["avg_time"],
                    "avg_quality": s["avg_quality"],
                }
                for algo, s in self.algo_perf.items()
                if s["successes"] + s["failures"] > 0
            },
        }

    def save(self, path: Path):
        state = {
            "level":         self.level,
            "learning_rate": self.learning_rate,
            "algo_perf":     dict(self.algo_perf),
            "selection_matrix": {k: dict(v) for k, v in self.selection_matrix.items()},
            "adaptation":    self.adaptation,
            "memory":        self.memory[-100:],
        }
        path.write_text(json.dumps(state, indent=2, default=str))

    def load(self, path: Path):
        if not path.exists():
            return
        state = json.loads(path.read_text())
        self.level            = state["level"]
        self.learning_rate    = state["learning_rate"]
        self.adaptation       = state["adaptation"]
        self.memory           = state.get("memory", [])
        for k, v in state.get("algo_perf", {}).items():
            self.algo_perf[k] = v
        for k, v in state.get("selection_matrix", {}).items():
            self.selection_matrix[k] = defaultdict(float, v)


# ==============================================================================
# ORQUESTADOR PRINCIPAL
# ==============================================================================

class TetraOrchestrator:
    ALGORITHMS = {
        "GradientDescent":      GradientDescentOptimizer(),
        "GeneticAlgorithm":     GeneticAlgorithmOptimizer(),
        "ParticleSwarm":        ParticleSwarmOptimizer(),
        "SimulatedAnnealing":   SimulatedAnnealingOptimizer(),
        "DifferentialEvolution":DifferentialEvolutionOptimizer(),
    }

    def __init__(self, load_previous_state: bool = True):
        self.consciousness  = AdvancedConsciousness()
        self.execution_log  = []
        self.n_executions   = 0
        self._state_file    = MODELS_DIR / "consciousness_state.json"

        if load_previous_state and self._state_file.exists():
            self.consciousness.load(self._state_file)
            logger.info("Consciousness state loaded.")

        logger.info(f"TetraOrchestrator ready — {len(self.ALGORITHMS)} algorithms.")

    def solve(self, problem: ProblemDefinition, max_iterations: int = 1000) -> OptimizationResult:
        logger.info(f"Solving '{problem.problem_id}' [{problem.problem_type}] dim={problem.dimensions}")

        if problem.objective_function is None:
            raise ValueError("objective_function must be set on ProblemDefinition")

        algo_name = self.consciousness.select_algorithm(
            problem.problem_type, list(self.ALGORITHMS.keys())
        )
        algo = self.ALGORITHMS[algo_name]

        result = algo.optimize(
            problem.objective_function,
            problem.dimensions,
            problem.bounds,
            max_iterations,
        )

        self.consciousness.learn(result, problem.problem_type)
        self.execution_log.append({
            "ts":        datetime.now().isoformat(),
            "problem":   problem.problem_id,
            "algorithm": algo_name,
            "objective": result.objective_value,
            "converged": result.converged,
            "time":      result.execution_time,
        })
        self.n_executions += 1

        if self.n_executions % 10 == 0:
            self.save_state()

        logger.info(
            f"  → {algo_name} | obj={result.objective_value:.4e} "
            f"| iter={result.iterations} | time={result.execution_time:.3f}s"
        )
        return result

    def benchmark(
        self,
        functions: List[Tuple[str, Callable]],
        dimensions: List[int] = [10, 20, 30],
        runs_per_config: int = 3,
    ) -> Dict:
        logger.info("Starting benchmark suite...")
        results = []
        for fname, func in functions:
            for dim in dimensions:
                for run in range(runs_per_config):
                    prob = ProblemDefinition(
                        problem_id=f"{fname}_{dim}D_r{run}",
                        problem_type="benchmark",
                        dimensions=dim,
                        bounds=(-5.0, 5.0),
                        objective_function=func,
                    )
                    res = self.solve(prob, max_iterations=500)
                    results.append({
                        "function":   fname,
                        "dimensions": dim,
                        "run":        run,
                        "algorithm":  res.algorithm,
                        "objective":  res.objective_value,
                        "time":       res.execution_time,
                        "converged":  res.converged,
                    })

        # Analysis
        algos = list({r["algorithm"] for r in results})
        funcs = list({r["function"]  for r in results})

        by_algo = {
            a: {
                "avg_obj":  float(np.mean([r["objective"] for r in results if r["algorithm"] == a])),
                "avg_time": float(np.mean([r["time"]      for r in results if r["algorithm"] == a])),
                "conv_rate":float(np.mean([r["converged"] for r in results if r["algorithm"] == a])),
                "runs":     sum(1 for r in results if r["algorithm"] == a),
            }
            for a in algos
        }
        by_func = {
            f: {
                "avg_obj":  float(np.mean([r["objective"] for r in results if r["function"] == f])),
                "best_obj": float(np.min( [r["objective"] for r in results if r["function"] == f])),
                "best_algo": min(
                    [r for r in results if r["function"] == f],
                    key=lambda x: x["objective"]
                )["algorithm"],
            }
            for f in funcs
        }

        analysis = {
            "total_runs":    len(results),
            "best_algorithm":min(by_algo, key=lambda a: by_algo[a]["avg_obj"]),
            "avg_conv_rate": float(np.mean([r["converged"] for r in results])),
            "avg_time":      float(np.mean([r["time"]      for r in results])),
            "by_algorithm":  by_algo,
            "by_function":   by_func,
        }

        # Save
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = RESULTS_DIR / f"benchmark_{ts}.json"
        path.write_text(json.dumps({"results": results, "analysis": analysis},
                                   indent=2, default=str))
        logger.info(f"Benchmark saved → {path}")
        return analysis

    def get_status_report(self) -> Dict:
        return {
            "system_info": {
                "total_executions":     self.n_executions,
                "algorithms_available": list(self.ALGORITHMS.keys()),
                "consciousness_level":  self.consciousness.level,
            },
            "performance": self.consciousness.get_summary(),
            "recent_results": self.execution_log[-10:],
        }

    def print_status(self):
        r = self.get_status_report()
        print("\n" + "=" * 70)
        print("📊  TETRA OS — STATUS REPORT")
        print("=" * 70)
        si = r["system_info"]
        print(f"  Executions      : {si['total_executions']}")
        print(f"  Consciousness   : {si['consciousness_level']:.3f}")
        print(f"  Algorithms      : {len(si['algorithms_available'])}")
        pf = r["performance"]
        print(f"\n  Exploration     : {pf['adaptation']['exploration']:.2f}")
        print(f"  Exploitation    : {pf['adaptation']['exploitation']:.2f}")
        if pf["algorithm_performance"]:
            print("\n  Per-algorithm performance:")
            for algo, s in pf["algorithm_performance"].items():
                print(f"    {algo:<26} success={s['success_rate']:.1%}"
                      f"  quality={s['avg_quality']:.3f}  time={s['avg_time']:.3f}s")
        print("=" * 70)

    def save_state(self):
        self.consciousness.save(self._state_file)
        log_path = RESULTS_DIR / "execution_log.json"
        log_path.write_text(json.dumps(self.execution_log[-200:],
                                       indent=2, default=str))


# ==============================================================================
# QUICK DEMO
# ==============================================================================

def quick_demo():
    print("\n" + "=" * 70)
    print("⚡  TETRA OS — Quick Demo")
    print("=" * 70)

    orch = TetraOrchestrator(load_previous_state=False)

    tests = [
        ("Sphere 10D",     BenchmarkFunctions.sphere,     10, (-5.0,  5.0)),
        ("Rastrigin 10D",  BenchmarkFunctions.rastrigin,  10, (-5.12, 5.12)),
        ("Rosenbrock 10D", BenchmarkFunctions.rosenbrock, 10, (-5.0,  5.0)),
    ]

    for name, func, dim, bnds in tests:
        prob = ProblemDefinition(
            problem_id=name.replace(" ", "_"),
            problem_type="demo",
            dimensions=dim,
            bounds=bnds,
            objective_function=func,
        )
        res = orch.solve(prob, max_iterations=300)
        print(f"  {name:<20} → obj={res.objective_value:.4e}"
              f"  algo={res.algorithm}  time={res.execution_time:.3f}s")

    orch.print_status()
    return orch


if __name__ == "__main__":
    quick_demo()