# Lab 2 — `P4|rj|ΣwjFj`

## Problem

**4 identical parallel machines**, jobs have release dates and weights.

Each job `Jj` is characterised by:
- `pj` — processing time
- `rj` — release date (earliest possible start)
- `wj` — weight (priority)

A job can only start after `rj`. Each job runs on exactly one machine without preemption.

**Objective:** minimise `ΣwjFj` where `Fj = Cj − rj` — total weighted flow time.

```
Input:   n
         p1 r1 w1
         ...
         pn rn wn

Output:  ΣwjFj
         <sequence on machine 1>
         <sequence on machine 2>
         <sequence on machine 3>
         <sequence on machine 4>
```

---

## Algorithm

**WSPT — Weighted Shortest Processing Time**

A deterministic greedy heuristic that minimises the weighted flow time on a single machine exactly, adapted here to the parallel-machine case via a list scheduling approach.

```
sort jobs ascending by pj / wj   # short and high-priority jobs first

for each job j in sorted order:
    m* ← machine with minimum free_time
    start_j ← max(rj, free_time[m*])
    assign j to m*
    free_time[m*] ← start_j + pj
```

Complexity: `O(n log n)` — single pass, no metaheuristic, fully deterministic.

The ratio `pj / wj` is the classical WSPT key: on a single machine with no release dates it yields the optimal `ΣwjFj`. With release dates and parallel machines it serves as a strong constructive heuristic.

---

## Files

```
Lab2/
├── 155830.py          # solver  (load → WSPT → save)
├── generator.py       # random instance generator
├── run_tests.py       # batch runner for benchmarking
├── ver_sol.py         # verifies solution correctness and ΣwjFj value
├── ver_time.py        # checks time limit compliance
└── analyze_results.py # aggregates benchmark results
```
