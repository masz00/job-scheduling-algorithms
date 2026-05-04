# Lab 1 — `1|s-batch|ΣDj`

## Problem

**Single-machine batch scheduling** to minimise total tardiness.

`n` jobs are grouped into **batches** (s-batch model). One machine processes batches sequentially. All jobs within a batch complete at the same time — the batch completion time `Ck`, which equals the cumulative processing time of all jobs in that batch. A fixed setup time `s` is paid between every two consecutive batches.

**Objective:** minimise `ΣDj` where `Dj = max(0, Cj − dj)` — total lateness across all jobs.

```
Input:   n s
         p1 d1
         ...
         pn dn

Output:  ΣDj
         k
         <jobs in batch 1>
         ...
         <jobs in batch k>
```

---

## Algorithm

The solver uses a two-phase **GRASP + Simulated Annealing** approach.

### Phase 1 — Greedy randomised construction (GRASP)

Builds an initial feasible batch assignment:

```
α ← 0.1
current_batch ← []
remaining ← all jobs

while remaining not empty:
    d_min ← min due date in remaining
    RCL   ← { j ∈ remaining : dj ≤ d_min · (1 + α) }
    j     ← random choice from RCL

    if current_batch empty or (current_time + Σp_current + pj) ≤ dj:
        add j to current_batch
    else:
        close current_batch → append to solution
        current_time += Σp_current + s
        current_batch ← [j]

append remaining current_batch
```

### Phase 2 — Simulated Annealing

Improves the solution through stochastic neighbourhood search:

```
T      ← 0.05 · criterion(initial_solution)
cool   ← 0.9995
best   ← initial_solution

while time_remaining:
    move ← random choice from {move, swap, split, merge}
    candidate ← apply move to current solution
    Δ ← criterion(candidate) − criterion(current)

    if Δ < 0 or random() < exp(−Δ / T):
        current ← candidate

    if criterion(candidate) < criterion(best):
        best ← candidate

    T ← T · cool

return best
```

**Neighbourhood moves:**

| Move | Description |
|------|-------------|
| `move` | relocate one job from batch A to batch B |
| `swap` | exchange one job between batch A and batch B |
| `split` | move one job from its batch into a new single-job batch |
| `merge` | combine two batches into one |

**Time limit:** `n/10 − 0.5 s`

---

## Files

```
Lab1/
├── 155830.py          # solver  (load → GRASP → SA → save)
├── generator.py       # random instance generator
├── run_tests.py       # batch runner for benchmarking
├── ver_sol.py         # verifies solution correctness and ΣDj value
├── ver_time.py        # checks time limit compliance
└── analyze_results.py # aggregates benchmark results
```
