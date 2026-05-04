import random
import os
from typing import List, Tuple

MY_ID = 155830
OUTPUT_DIR = "instances"
N_SIZES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]

S_TIME = 30            # setuptime, ma być stały, 30 to ~3p  
P_MIN, P_MAX = 2, 18   # Zakres czasów pakowania (p_j)
TIGHTNESS = 0.95       

def gen_instance(n: int, s_time: int, p_min: int, p_max: int, tightness: float, seed: int) -> Tuple[int, List[int], List[int]]: 
    #zwraca [Setuptime, [p1..pn] [d1..dn]]
    rnd = random.Random(seed)
    p = [rnd.randint(p_min, p_max) for _ in range(n)]
    
    accumulated_p = 0
    expected_completions = []
    for pj in p:
        accumulated_p += pj
        expected_completions.append(accumulated_p + s_time) #TODO Czy robić +s_time
        
    deadlines = []
    for ec in expected_completions:
        noise = rnd.randint(-int(0.2 * ec), int(0.2 * ec)) #random 20% (może należy wrzucić w parametr funkcji) miesza zeby kolejnosc nie byla prostoliniowa
        
        dj = max(s_time, int(ec * tightness + noise)) #

        deadlines.append(dj)
        
    return s_time, p, deadlines

def save_instance(filename: str, n: int, s_time: int, p: List[int], d: List[int]) -> None:
    with open(filename, "w") as f:
        f.write(f"{n} {s_time}\n")
        for pj, dj in zip(p, d):
            f.write(f"{pj} {dj}\n")

def generate_final_instances(output_dir: str = OUTPUT_DIR, sizes: List[int] = N_SIZES):
    os.makedirs(output_dir, exist_ok=True)
    for n in sizes:
        seed =n
        
        s, p, d = gen_instance(n, S_TIME, P_MIN, P_MAX, TIGHTNESS, seed)
        filename = os.path.join(output_dir, f"in_{MY_ID}_{n}.txt") #plik typu in_N_ID.txt #TODO co grupa ustaliła? // in_ID_N // zmiana 
        save_instance(filename, n, s, p, d)

if __name__ == "__main__":
    generate_final_instances()