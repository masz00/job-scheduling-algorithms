import subprocess
import os
import sys
from typing import List, Tuple

N_SIZES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
INST_DIR = "instancje"
SOL_DIR = "pliki_wynikowe"
VERIFIER_SCRIPT = "ver_sol.py"


def verify_solution(inst_file: str, sol_file: str) -> Tuple[bool, str]:

    try:
        result = subprocess.run(
            ['python', VERIFIER_SCRIPT, inst_file, sol_file],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace', 
            timeout=5.0
        )
        
        output = result.stdout.strip()
        

        if result.returncode == 0 and output and output.isdigit():
            return True, output
        else:

            if result.stderr:
                return False, result.stderr.split('\n')[0][:100]
            else:
                return False, output[:100] if output else "Nieznany błąd"
                
    except subprocess.TimeoutExpired:
        return False, "Timeout weryfikacji"
    except Exception as e:
        return False, str(e)[:100]


def collect_results(alg_id: str, inst_id: str) -> List[Tuple[int, bool, str]]:

    results = []
    

    print(f"Algorytm: {alg_id:<27}")
    print(f"Instancje: {inst_id:<26}\n")
    
    for n in N_SIZES:
        inst_file = os.path.join(INST_DIR, f"in_{inst_id}_{n}.txt")
        sol_file = os.path.join(SOL_DIR, f"out_{alg_id}_{n}.txt")
        
        if not os.path.exists(inst_file):
            print(f"n={n:>4} │  BRAK INSTANCJI")
            results.append((n, False, "BRAK_INSTANCJI"))
            continue
        
        if not os.path.exists(sol_file):
            print(f"n={n:>4} │  BRAK ROZWIĄZANIA")
            results.append((n, False, "BRAK_ROZWIĄZANIA"))
            continue
        
        success, value = verify_solution(inst_file, sol_file)
        
        if success:
            print(f"n={n:>4} │  OK    │ Koszt: {value}")
            results.append((n, True, value))
        else:
            print(f"n={n:>4} │  BŁĄD  │ {value}")
            results.append((n, False, value))
    
    return results


def print_csv_output(results: List[Tuple[int, bool, str]]) -> None:
    for _, success, value in results:
        print(f"{value}")


def print_summary(results: List[Tuple[int, bool, str]]) -> None:

    success_count = sum(1 for _, s, _ in results if s)
    total_count = len(results)
    print()
    print(f"\nPodsumowanie: {success_count}/{total_count}\n")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie: python analyze_results.py <alg_id> <inst_id>")
        print("Przykład: python analyze_results.py 155830 155989")
        sys.exit(1)
    
    alg_id = sys.argv[1]
    inst_id = sys.argv[2]
    
    if not os.path.exists(VERIFIER_SCRIPT):
        print(f"Błąd: Nie znaleziono {VERIFIER_SCRIPT}")
        sys.exit(1)
    
    if not os.path.exists(INST_DIR):
        print(f"Błąd: Nie znaleziono katalogu {INST_DIR}")
        sys.exit(1)
    
    if not os.path.exists(SOL_DIR):
        print(f"Błąd: Nie znaleziono katalogu {SOL_DIR}")
        sys.exit(1)
    
    results = collect_results(alg_id, inst_id)
    
    print_summary(results)
    print_csv_output(results)