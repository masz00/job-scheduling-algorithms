import random
import os
from typing import List, Tuple

MY_ID = 155830
OUTPUT_DIR = "instances"
N_SIZES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
P_MIN, P_MAX = 40, 120
S_MIN, S_MAX = 10, 40

def gen_instance(n: int, seed: int) -> Tuple[List[List[int]], List[int], List[List[int]]]:
    rnd = random.Random(seed)
    
    jobs_data = []

    avg_p = (P_MIN + P_MAX) / 2
    total_work_load = n * avg_p
    
    max_release_time = int(total_work_load * 0.4)

    for _ in range(n):
        p_times = [rnd.randint(P_MIN, P_MAX) for _ in range(4)]
        
        r_time = rnd.randint(0, max_release_time)
        jobs_data.append(p_times + [r_time])

    s_matrix = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0)
            else:
                row.append(rnd.randint(S_MIN, S_MAX))
        s_matrix.append(row)

    return jobs_data, s_matrix

def save_instance(filename: str, n: int, jobs_data: List[List[int]], s_matrix: List[List[int]]) -> None:
    with open(filename, "w") as f:
        f.write(f"{n}\n")

        for job in jobs_data:
            line = " ".join(map(str, job))
            f.write(f"{line}\n")
    
        for row in s_matrix:
            line = " ".join(map(str, row))
            f.write(f"{line}\n")

def generate_final_instances(output_dir: str = OUTPUT_DIR, sizes: List[int] = N_SIZES):
    os.makedirs(output_dir, exist_ok=True)
    for n in sizes:
        seed = n 
        jobs_data, s_matrix = gen_instance(n, seed)
        
        filename = os.path.join(output_dir, f"in_{MY_ID}_{n}.txt")
        save_instance(filename, n, jobs_data, s_matrix)
        print(f"Generated: {filename} (Size: {n})")

if __name__ == "__main__":
    generate_final_instances()