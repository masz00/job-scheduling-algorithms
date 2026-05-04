
import subprocess
import os
import sys
from typing import List, Tuple


N_SIZES = [50, 100, 150, 200, 250, 300, 350, 400, 450, 500]
INST_DIR = "instancje"
SOL_DIR = "pliki_wynikowe"
VERIFIER_SCRIPT = "ver_sol.py"


def parse_verifier_output(output: str) -> Tuple[str, str]:
    lines = output.strip().split('\n')
    file_value = None
    computed_value = None

    for line in lines:
        if "Wartość z pliku:" in line:
            file_value = line.split(":")[-1].strip()
        elif "Obliczona wartość:" in line:
            computed_value = line.split(":")[-1].strip()
    return file_value or "-", computed_value or "-"

def verify_results(alg_id: str, inst_id: str) -> List[Tuple[int, str, bool, str, str]]:
    results = []
    print(f"  Algorytm: {alg_id}")
    print(f"  Instancje: {inst_id}\n")
    
    for n in N_SIZES:
        inst_file = os.path.join(INST_DIR, f"in_{inst_id}_{n}.txt")
        sol_file = os.path.join(SOL_DIR, f"out_{alg_id}_on_{inst_id}_{n}.txt")

        if not os.path.exists(inst_file):
            print(f"n={n:<3} | BRAK PLIKU INSTANCJI: {inst_file}")
            results.append((n, "BRAK INSTANCJI", False, "-", "-"))
            continue

        if not os.path.exists(sol_file):
            print(f"n={n:<3} | BRAK PLIKU ROZWIĄZANIA: {sol_file}")
            results.append((n, "BRAK ROZWIĄZANIA", False, "-", "-"))
            continue
            
        try:
            result = subprocess.run(
                ['python', VERIFIER_SCRIPT, inst_file, sol_file],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
        except FileNotFoundError:
             print(f"FATAL: Nie znaleziono skryptu '{VERIFIER_SCRIPT}'.")
             sys.exit(1)

        output = result.stdout.strip()

        if result.returncode == 0 and output.isdigit():
            print(f"n={n:<3} | OK        | Koszt: {output}")
            results.append((n, output, True, output, output))
        else:
            file_val, comp_val = parse_verifier_output(output)
            print(f"n={n:<3} | BŁĄD!     | Z pliku: {file_val}, Obliczono: {comp_val}")
            full_error = output if (file_val == '-' and comp_val == '-') else f"Błąd (Plik: {file_val}, Obliczono: {comp_val})"
            results.append((n, full_error, False, file_val, comp_val))

    return results

def print_summary_for_spreadsheet(results: List[Tuple[int, str, bool, str, str]]) -> None:
    for n, output, is_success, file_val, comp_val in results:
        if is_success:
            print(f"{comp_val}") 
        elif comp_val != "-":
            print(f"{comp_val}")
        else:
            print("ERROR")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Użycie: python analyze_results.py <indeks_algorytmu> <indeks_instancji>")   #python analyze_results.py 155830 155989  (moj alg inna instancja)
        sys.exit(1)
        
    alg_id_to_check = sys.argv[1]
    inst_id_to_check = sys.argv[2]
    
    results = verify_results(alg_id_to_check, inst_id_to_check)
    print_summary_for_spreadsheet(results)