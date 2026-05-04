import subprocess
import sys
import os
import re

def parse_summary_line(line: str) -> dict:
    match = re.search(
        r'n = (\w+), limit t: ([\d.]+), faktyczny t algorytmu: ([\d.]+), timeout: (\w+)', 
        line
    )
    if match:
        return {
            'n': match.group(1),
            'limit_t': float(match.group(2)),
            'measured_t': float(match.group(3)),
            'timeout': match.group(4)
        }
    return None

def run_all_instances(alg_id: str, inst_id: str, algorithm_path: str):
    
    INSTANCE_DIR = "./instancje"
    OUTPUT_DIR = "./pliki_wynikowe"
    VER_TIME_SCRIPT = "ver_time.py"
    
    REPORT_FILE = f"times_{alg_id}_on_{inst_id}.csv"

    if not os.path.exists(INSTANCE_DIR):
        print(f"BŁĄD: folder instancji '{INSTANCE_DIR}' nie istnieje")
        sys.exit(1)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    sizes = range(50, 501, 50)
    
    full_alg_path_parts = algorithm_path.split()
    base_command = ["python", VER_TIME_SCRIPT] + full_alg_path_parts
    
    results = []
    print(f"Algorytm: {alg_id} ({algorithm_path})")
    print(f"Instancje: {inst_id}")
    print(f"Raport: {REPORT_FILE}\n")

    for n in sizes:
        time_limit = n / 10.0
        instance_file = os.path.join(INSTANCE_DIR, f"in_{inst_id}_{n}.txt")
        output_file = os.path.join(OUTPUT_DIR, f"out_{alg_id}_on_{inst_id}_{n}.txt")
        
        if not os.path.exists(instance_file):
            print(f"Pomięto n={n}: Nie znaleziono pliku instancji: {instance_file}")
            continue

        command = base_command + [instance_file, output_file, str(time_limit)]
        
        print(f"start n={n} (limit: {time_limit:.1f}s)")

        try:
            result = subprocess.run(
                command, 
                capture_output=True,
                text=True,
                check=False 
            )
            
            summary_line = None
            print(result.stdout.strip()) # Pokaż cały output z ver_time
            
            for line in result.stdout.splitlines():
                if "faktyczny t algorytmu:" in line:
                    summary_line = line
                    break
            
            if result.returncode != 0 and not summary_line:
                print("Wystąpił błąd w ver_time.py lub w solverze !!!")
                print(result.stderr)
            
            summary = parse_summary_line(summary_line) if summary_line else None
            
            if summary:
                results.append(summary)
            else:
                print(f"Nie można sparsować wyniku dla n={n} (sprawdź stdout/stderr weryfikatora)")
            
        except FileNotFoundError:
            print(f"Błąd: Nie znaleziono skryptu {VER_TIME_SCRIPT} lub '{full_alg_path_parts[0]}'.")
            sys.exit(1)
        
    if results:
        with open(REPORT_FILE, 'w') as f:
            f.write("n;limit_t;zmierzone_t;timeout\n")
            for res in results:
                f.write(f"{res['n']};{res['limit_t']:.2f};{res['measured_t']:.4f};{res['timeout']}\n")
        print(f"\nWyniki czasowe zapisano do pliku: {REPORT_FILE}")
        
        print("\nFaktyczne czasy algorytmu (do skopiowania)")
        for res in results:
            print(f"{res['measured_t']:.4f}")
            
    else:
        print("\nBrak wyników do zapisania.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Błąd: Nieprawidłowa liczba argumentów.")
        print("Użycie: python run_tests.py <indeks_algorytmu> <indeks_instancji> \"<program_do_testowania>\"")   #python run_tests.py 155830 123456 "python 155830.py" (moj alg, instance 123456, moj alg)
        sys.exit(1)

    alg_id = sys.argv[1]
    inst_id = sys.argv[2] 
    algorithm_path = sys.argv[3]
    
    run_all_instances(alg_id, inst_id, algorithm_path)