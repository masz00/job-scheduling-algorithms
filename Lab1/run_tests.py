import subprocess
import sys
import os
import re

def parse_summary_line(line: str) -> dict:
    #Parsuje linię podsumowania z ver_time.py
    
    # Oczekiwany format: test dla: n = 50, limit t: 5.00, faktyczny t algorytmu: 0.0012, timeout: NIE
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

def run_all_instances(student_index: str, algorithm_path: str):
    
    INSTANCE_DIR = "./instancje"
    OUTPUT_DIR = "./pliki_wynikowe"
    VER_TIME_SCRIPT = "ver_time.py"
    REPORT_FILE = f"times_{student_index}.csv"

    if not os.path.exists(INSTANCE_DIR):
        print(f"error: folder instancji '{INSTANCE_DIR}' nie istnieje")
        sys.exit(1)
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    sizes = range(50, 501, 50)
    
    full_alg_path_parts = algorithm_path.split()
    base_command = ["python", VER_TIME_SCRIPT] + full_alg_path_parts
    
    results = []
    print(f"Indeks: {student_index}, algorytm.exe: {algorithm_path}\n ")

    for n in sizes:
        time_limit = n / 10.0
        instance_file = os.path.join(INSTANCE_DIR, f"in_{student_index}_{n}.txt")
        output_file = os.path.join(OUTPUT_DIR, f"out_{student_index}_{n}.txt")
        
        if not os.path.exists(instance_file):
            print(f"Pomięto: Nie znaleziono pliku instancji: {instance_file}")
            continue

        command = base_command + [instance_file, output_file, str(time_limit)]
        

        try:
            result = subprocess.run(
                command, 
                capture_output=True,
                text=True,
                check=False # Nie rzuca wyjątku, jeśli ver_time się wywaliło???????????????????????
            )
            
            #zgarnia linie podsumowania z ver_time.py
            summary_line = None
            for line in result.stdout.splitlines():
                if "faktyczny t algorytmu:" in line:   #UWAZAC NA ZMIANE SYNTAX W ver_time.py
                    summary_line = line
                    break
            
            summary = parse_summary_line(summary_line) if summary_line else None
            
            if summary:
                results.append(summary)
            else:
                print("Nie można sparsować wyniku (sprawdź stdout/stderr weryfikatora)")
                print(f"Kod wyjścia ver_time.py: {result.returncode}")
                
        except FileNotFoundError:
            print(f"Błąd: Nie znaleziono skryptu {VER_TIME_SCRIPT} lub '{full_alg_path_parts[0]}'.")
            sys.exit(1)
        
    if results:
        with open(REPORT_FILE, 'w') as f:
            f.write("n;limit_t;zmierzone_t;timeout\n")
            for res in results:
                f.write(f"{res['n']};{res['limit_t']:.2f};{res['measured_t']:.4f};{res['timeout']}\n")
        print(f"zapisano do pliku: {REPORT_FILE}")
    else:
        print("Brak wyników do zapisania.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie: python run_tests.py <indeks_studenta> \"<program_do_testowania>\"")   #przykład python run_tests.py 155830 "algorithm.exe"  
        sys.exit(1)

    student_index = sys.argv[1]
    algorithm_path = sys.argv[2] 
    
    run_all_instances(student_index, algorithm_path)