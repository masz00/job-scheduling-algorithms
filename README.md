# Job Scheduling — Laboratory Solutions

Solutions for the **Theory and Practice of Job Scheduling** course (7th semester, BSc Computer Science).  
Each lab tackles a different scheduling problem using a dedicated algorithm or metaheuristic, implemented in Python under a strict time limit.

---

## Labs at a glance

| | Problem | Optimisation criterion | Algorithm |
|-|---------|----------------------|-----------|
| [**Lab 1**](./Lab1/) | `1\|s-batch\|ΣDj` | total tardiness | GRASP + Simulated Annealing |
| [**Lab 2**](./Lab2/) | `P4\|rj\|ΣwjFj` | weighted flow time | WSPT greedy |
| [**Lab 3**](./lab3/) | `F4\|rj, Sij\|Cmax` | makespan | Multi-seed construction + LRD |

---

## What each lab contains

Every lab directory is self-contained and includes:

| File | Purpose |
|------|---------|
| `155830.py` | **Main solver** — reads an instance, runs the algorithm, writes the solution |
| `generator.py` | Generates random test instances of arbitrary size |
| `ver_sol.py` | Verifies solution correctness and recalculates the objective value |
| `ver_time.py` | Checks that the solver did not exceed the time limit |
| `run_tests.py` | Automates running the solver across an entire benchmark set |
| `analyze_results.py` | Aggregates benchmark output into a summary report |

---

## Usage

```bash
# Run the solver
python 155830.py <instance.txt> <output.txt> <time_limit_s>

# Verify the solution
python ver_sol.py <instance.txt> <output.txt>
```

The time limit is computed internally as `n/10 − 0.5 s`; the CLI argument is required by the grader.
