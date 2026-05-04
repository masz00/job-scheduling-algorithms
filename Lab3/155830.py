import sys
import time
import random

N = 0
P = []
R = []
S = []

def calc_cmax(seq):
    t1 = t2 = t3 = t4 = 0
    prev = None
    local_P, local_R, local_S = P, R, S
    for j in seq:
        setup = local_S[prev][j] if prev is not None else 0
        s1 = t1 + setup
        if s1 < local_R[j]: s1 = local_R[j]
        t1 = s1 + local_P[j][0]
        s2 = t2 + setup
        if s2 < t1: s2 = t1
        t2 = s2 + local_P[j][1]
        s3 = t3 + setup
        if s3 < t2: s3 = t2
        t3 = s3 + local_P[j][2]
        s4 = t4 + setup
        if s4 < t3: s4 = t3
        t4 = s4 + local_P[j][3]
        prev = j
    return t4

def generate_dominator_seed():
    indices = list(range(N))
    curr = min(indices, key=lambda x: R[x])
    chain = [curr]
    pool = set(indices) - {curr}
    late = []
    t = R[curr] + P[curr][0]
    while pool:
        candidates = list(pool)
        candidates.sort(key=lambda x: S[curr][x])
        best = -1
        found = False
        for cand in candidates:
            s = S[curr][cand]
            if max(0, R[cand] - (t + s)) < 10: 
                best = cand
                found = True
                break 
        if not found:
            blocker = candidates[0]
            if R[blocker] > t + S[curr][blocker] + 200:
                late.append(blocker); pool.remove(blocker); continue
            else: best = blocker
        chain.append(best); pool.remove(best)
        t = max(t + S[curr][best], R[best]) + P[best][0]
        curr = best
    late.sort(key=lambda x: R[x])
    return chain + late

def generate_tsp_seed():
    indices = list(range(N))
    curr = min(indices, key=lambda x: R[x])
    path = [curr]; pool = set(indices) - {curr}
    while pool:
        candidates = list(pool)
        if len(candidates) > 20:
            candidates.sort(key=lambda x: S[curr][x])
            candidates = candidates[:20]
        nxt = min(candidates, key=lambda x: R[x])
        path.append(nxt); pool.remove(nxt); curr = nxt
    return path


def solve(time_limit):
    start_time = time.time()
    cutoff = time_limit
    
    seeds = []
    seeds.append(generate_dominator_seed())
    seeds.append(generate_tsp_seed())
    
    indices = list(range(N))
    seeds.append(sorted(indices, key=lambda i: sum(P[i]), reverse=True))
    seeds.append(sorted(indices, key=lambda i: (R[i], sum(P[i]))))

    best_seq = []
    best_cmax = float('inf')
    

    seed_cutoff = start_time + (cutoff - start_time) * 0.2
    
    for s_idx, seed in enumerate(seeds):
        if time.time() > seed_cutoff and s_idx > 0: break
        
        curr_seq = []
        for job in seed:
            best_pos, best_val = -1, float('inf')
            step = 2 if N > 200 else 1
            for pos in range(0, len(curr_seq) + 1, step):
                cand = curr_seq[:pos] + [job] + curr_seq[pos:]
                c = calc_cmax(cand)
                if c < best_val: best_val = c; best_pos = pos
            
            if best_pos == -1: curr_seq.append(job)
            else: curr_seq.insert(best_pos, job)
        
        c = calc_cmax(curr_seq)
        if c < best_cmax:
            best_cmax = c
            best_seq = curr_seq

    curr_seq = list(best_seq)
    curr_cmax = best_cmax
    
    search_radius = 50
    stagnation = 0
    max_stagnation = 300

    while time.time() - start_time < cutoff:
        d = max(2, min(25, int(N * 0.005)))
        candidate = list(curr_seq)
        removed = []
        
        idxs = sorted(random.sample(range(len(candidate)), d), reverse=True)
        for idx in idxs: removed.append(candidate.pop(idx))
            
        for job in removed:
            best_pos, best_val = -1, float('inf')
            for pos in range(len(candidate) + 1):
                cand = candidate[:pos] + [job] + candidate[pos:]
                c = calc_cmax(cand)
                if c < best_val: best_val = c; best_pos = pos
            candidate.insert(best_pos, job)
            
        improved = True
        while improved:
            improved = False
            if time.time() - start_time > cutoff: break
            
            target_idx = random.randrange(len(candidate))
            
            job = candidate.pop(target_idx)
            candidate.insert(target_idx, job)
            best_local_c = calc_cmax(candidate) 
            candidate.pop(target_idx)
            
            start = max(0, target_idx - search_radius)
            end = min(len(candidate) + 1, target_idx + search_radius)
            best_pos = target_idx
            
            for pos in range(start, end):
                if pos == target_idx: continue
                cand = candidate[:pos] + [job] + candidate[pos:]
                c = calc_cmax(cand)
                if c < best_local_c: best_local_c = c; best_pos = pos
            
            candidate.insert(best_pos, job)
            
            if best_local_c < curr_cmax:
                curr_cmax = best_local_c
                improved = True
                
            if not improved:
                swap_limit = 20
                for _ in range(swap_limit):
                    i = best_pos
                    j = random.randrange(len(candidate))
                    if i == j: continue
                    candidate[i], candidate[j] = candidate[j], candidate[i]
                    c = calc_cmax(candidate)
                    if c < curr_cmax:
                        curr_cmax = c
                        improved = True
                        break 
                    else:
                        candidate[i], candidate[j] = candidate[j], candidate[i]

        c_final = calc_cmax(candidate)
        if c_final <= curr_cmax:
            curr_cmax = c_final
            curr_seq = list(candidate)
            if c_final < best_cmax:
                best_cmax = c_final
                best_seq = list(candidate)
                stagnation = 0
            else: stagnation += 1
        else:
            stagnation += 1
            if random.random() < 0.015: 
                curr_seq = list(candidate)
                curr_cmax = c_final
                
        if stagnation > max_stagnation:
            curr_seq = list(best_seq)
            stagnation = 0

    return best_cmax, best_seq

def main():
    global N, P, R, S
    if len(sys.argv) < 3: return 

    with open(sys.argv[1], 'r') as f:
        data = f.read().split()
    it = iter(data)
    
    sys.setrecursionlimit(5000)
    random.seed(1)

    try:
        N = int(next(it))
        P.clear(); R.clear(); S.clear()
        for _ in range(N):
            P.append([int(next(it)) for _ in range(4)])
            R.append(int(next(it)))
        raw_S = [int(next(it)) for _ in range(N*N)]
        S = [raw_S[i*N:(i+1)*N] for i in range(N)]
    except StopIteration: return

    time_limit = (N * 0.1) - 0.5

    cmax, seq = solve(time_limit)
    final_ids = [i+1 for i in seq]

    with open(sys.argv[2], 'w') as f:
        f.write(f"{cmax}\n")
        f.write(" ".join(map(str, final_ids)) + "\n")

if __name__ == "__main__":
    main()