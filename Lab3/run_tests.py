import subprocess
import os
import sys
import time
from typing import List, Tuple


N_SIZES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
INST_DIR = "instancje"
SOL_DIR = "pliki_wynikowe"


def run_solver(alg_name: str, alg_cmd: str, inst_id: str, n: int, time_limit: float) -> Tuple[bool, float]:

    inst_file = os.path.join(INST_DIR, f"in_{inst_id}_{n}.txt")
    sol_file = os.path.join(SOL_DIR, f"out_{alg_name}_{n}.txt")
    
    if not os.path.exists(inst_file):
        print(f"Brak pliku: {inst_file}", file=sys.stderr)
        return False, 0.0
    
    cmd = alg_cmd.split() + [inst_file, sol_file, str(time_limit)]
    
    start = time.perf_counter()
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, 
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        stdout, stderr = process.communicate(timeout=time_limit + 2.0)
        
        if stderr:
            print(stderr, end='')
            
        elapsed = time.perf_counter() - start
        success = (process.returncode == 0 and os.path.exists(sol_file))
        
        return success, elapsed
        
    except subprocess.TimeoutExpired:
        elapsed = time.perf_counter() - start
        return False, elapsed
    except Exception as e:
        print(f"   Błąd: {e}", file=sys.stderr)
        return False, 0.0


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Użycie: python run_tests.py <alg_name> <inst_id> <alg_cmd>") #python run_tests.py 155830 155830 "python 155830.py"
        sys.exit(1)
    
    alg_name = sys.argv[1]
    inst_id = sys.argv[2]
    alg_cmd = sys.argv[3]
    
    print(f"Algorytm: {alg_name:<29}")
    print(f"Instancje: {inst_id:<28}")
    print(f"Plik:   {alg_cmd:<28}\n")
    
    
    results: List[Tuple[int, str, float]] = []
    
    for n in N_SIZES:
        time_limit = n / 10.0
        
        print(f"test n={n:<3} (limit: {time_limit:.1f}s)  ", end=" ", flush=True)
        

        success, elapsed = run_solver(alg_name, alg_cmd, inst_id, n, time_limit)
        
        if success:
            print(f" ({elapsed:.2f}s)")
            results.append((n, "OK", elapsed))
        else:
            print(f" ({elapsed:.2f}s)")
            results.append((n, "FAIL", elapsed))
    


    
    ok_count = sum(1 for _, status, _ in results if status == "OK")
    
    for n, status, elapsed in results:
        time_str = f"{elapsed:.2f}".replace('.', ',')
        print(f"{time_str}")
    