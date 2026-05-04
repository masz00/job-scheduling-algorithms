import random
import os
from typing import List, Tuple

MY_ID = 155830
OUTPUT_DIR = "instancje"
N_SIZES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]


M_MACHINES = 4
P_MIN, P_MAX = 2, 20       
W_MIN, W_MAX = 500, 1000   

def gen_instance(n: int, seed: int) -> Tuple[List[int], List[int], List[int]]:

    rnd = random.Random(seed)
    
    p = [rnd.randint(P_MIN, P_MAX) for _ in range(n)]
    w = [rnd.randint(W_MIN, W_MAX) for _ in range(n)]
    
    r: List[int]

    avg_p = (P_MIN + P_MAX) / 2
    total_load = n * avg_p
    avg_machine_load = total_load / M_MACHINES

    base_r_max = int(avg_machine_load) 

    r = [rnd.randint(0, base_r_max) for _ in range(n)]
    r[0] = 0        
    return p, r, w

def save_instance(filename: str, n: int, p: List[int], r: List[int], w: List[int]) -> None:
    try:
        with open(filename, "w") as f:
            f.write(f"{n}\n")
            for pj, rj, wj in zip(p, r, w):
                f.write(f"{pj} {rj} {wj}\n")
    except IOError as e:
        print(f"Błąd zapisu do pliku {filename}: {e}")

def generate_final_instances(output_dir: str = OUTPUT_DIR, sizes: List[int] = N_SIZES):
    os.makedirs(output_dir, exist_ok=True)
    print(f"Rozpoczynam generowanie instancji do katalogu: {output_dir}")
    for n in sizes:
        seed = n
        p, r, w = gen_instance(n, seed)
        
        filename = os.path.join(output_dir, f"in_{MY_ID}_{n}.txt")
        save_instance(filename, n, p, r, w)
    print("Zakończono generowanie instancji.")

if __name__ == "__main__":
    generate_final_instances()