# Lab 3 — `F4|rj, Sij|Cmax`

## Problem

**4-machine flow shop** with release dates and sequence-dependent setup times.

Each job `Jj` must pass through all 4 machines **in order** with operation times `p1j, p2j, p3j, p4j`. Additional constraints:
- `rj` — job cannot start before its release date
- `Sij` — switching from job `Ji` to job `Jj` requires a setup time (same duration on every machine)

**Objective:** minimise makespan `Cmax = max{Cj}` — finish all jobs as early as possible.

```
Input:   n
         p1.1 p1.2 p1.3 p1.4 r1
         ...
         pn.1 pn.2 pn.3 pn.4 rn
         S11 ... S1n
         ...
         Sn1 ... Snn

Output:  Cmax
         J(1) J(2) ... J(n)
```

---

## Algorithm

The solver uses **multi-seed construction** to build a strong initial solution, then refines it with a **Large Neighbourhood Search (Ruin & Recreate)** loop.

### Cmax evaluation

All moves and insertions are evaluated using `calc_cmax(seq)`, which simulates the flow shop in `O(n)`:

```
t1 = t2 = t3 = t4 ← 0
prev ← none

for j in seq:
    setup ← S[prev][j]  (0 if first job)

    s1 ← max(t1 + setup, rj);   t1 ← s1 + p1j
    s2 ← max(t2 + setup, t1);   t2 ← s2 + p2j
    s3 ← max(t3 + setup, t2);   t3 ← s3 + p3j
    s4 ← max(t4 + setup, t3);   t4 ← s4 + p4j
    prev ← j

return t4
```

### Phase 1 — Multi-seed construction

Four candidate orderings are generated, each refined by **best-insertion**:

```
for each seed_ordering:
    seq ← []
    for job in seed_ordering:
        best_pos ← argmin_{pos ∈ 0..|seq|} calc_cmax(insert(seq, pos, job))
        insert job at best_pos
    update global best if calc_cmax(seq) improves
```

| Seed | Ordering strategy |
|------|------------------|
| **Dominator** | start from earliest `rj`; greedily chain by minimum `Sij`; push late jobs to end |
| **TSP-like** | nearest-neighbour by `rj` from a restricted candidate window |
| **LPT** | descending `Σpij` — longest jobs first |
| **ERT + LPT** | sort by `(rj, Σpij)` — earliest release, then longest |

### Phase 2 — LRD (Large Neighbourhood Search: Ruin & Recreate)

```
best ← solution from Phase 1
current ← best
stagnation ← 0

while time_remaining:
    d ← clamp(round(n · 0.005), 2, 25)

    # Ruin
    removed ← random sample of d jobs from current
    candidate ← current without removed jobs

    # Recreate
    for job in removed:
        best_pos ← argmin_{pos} calc_cmax(insert(candidate, pos, job))
        insert job at best_pos

    # Local search
    pick random job j from candidate
    find better position for j in window [pos−50, pos+50]
    if found: move j, mark improved

    # Perturbation (if no improvement)
    if not improved:
        try up to 20 random pairwise swaps; accept first that improves

    # Acceptance
    if calc_cmax(candidate) ≤ calc_cmax(current):
        current ← candidate
    elif random() < 0.015:
        current ← candidate        # escape local optimum

    if calc_cmax(current) < calc_cmax(best):
        best ← current
        stagnation ← 0
    else:
        stagnation += 1
        if stagnation > 300:
            current ← best         # restart from global best
            stagnation ← 0

return best
```

**Time limit:** `n · 0.1 − 0.5 s`

---

## Files

```
lab3/
├── 155830.py          # solver  (load → seeds → LRD → save)
├── ver_sol.py         # verifies solution correctness and Cmax value
├── run_tests.py       # batch runner for benchmarking
├── analyze_results.py # aggregates benchmark results
├── massive_tester.py  # stress tester (many instances, repeated runs)
└── i.py               # utility script
```
