import sys
import os
import re
from typing import Tuple, List, Dict

def load_instance(filename: str) -> Tuple[int, int, Dict[int, Dict[str, int]]]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 2:
            raise ValueError("plik instacji musi mieć min 2 linie")

        n_str, s_str = lines[0].split()
        n, s = int(n_str), int(s_str)
        
        if len(lines) - 1 != n:
            raise ValueError(f"liczba linii zadań ({len(lines)-1}) nie zgadza się z zadeklarowanym n={n}")

        tasks: Dict[int, Dict[str, int]] = {}
        for i in range(1, n + 1):
            p_str, d_str = lines[i].split()
            tasks[i] = {'p': int(p_str), 'd': int(d_str)}

        return n, s, tasks
    except Exception as e:
        sys.exit(f"błąd wczytywania instancji {filename}: {e}")

def load_solution(filename: str) -> Tuple[int, int, List[List[int]]]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if len(lines) < 2:
            raise ValueError("Plik wynikowy musi mieć min 2 linie")

        criterion_value = int(lines[0])
        k = int(lines[1])
        
        batches: List[List[int]] = []
        if k > 0 and len(lines) >= 3:
             batches = [list(map(int, line.split())) for line in lines[2:2+k]]
        
        if len(batches) != k:
            print(f"bład: zadeklarowane k={k} nie zgadza się z liczbą wczytanych partii {len(batches)}")
            
        return criterion_value, k, batches
    except Exception as e:
        print(f"błąd wczytywania rozwiązania {filename}: {e}")
        return -1, -1, []

def calculate_criterion(n: int, s: int, tasks: Dict[int, Dict[str, int]], batches: List[List[int]]) -> int:
    total_tardiness = 0
    current_time = 0
    
    all_tasks_in_batches = set()
    total_tasks_count = 0

    for batch in batches:
        if not batch: continue 
        
        batch_time = 0
        for j in batch:
            if j not in tasks:
                print(f"błąd: zadanie {j} jest w partii, ale nie ma go w pliku instancji")
                return -999999 #TODO zmienic pozniej na errora, teraz do testow zeby zwrocilio liczbe jest 0-99999
            batch_time += tasks[j]['p']
            all_tasks_in_batches.add(j)
            total_tasks_count += 1
            
        completion_time = current_time + batch_time
        current_time = completion_time + s

        for j in batch:
            tardiness = max(0, completion_time - tasks[j]['d'])
            total_tardiness += tardiness

    if len(all_tasks_in_batches) != n or total_tasks_count != n:
         print(f"błąd: liczba zadań w instancji (n={n}) nie zgadza się z liczbą unikalnych zadań w partiach ({len(all_tasks_in_batches)})")
         return -99999 #TODO zmienić jw.

    return total_tardiness

def analyze_and_report(instance_student_id: str, solution_student_id: str):


    INSTANCE_DIR = "./instancje"
    OUTPUT_DIR = "./pliki_wynikowe"
    REPORT_FILE = f"report_{instance_student_id}_vs_{solution_student_id}.csv"
    
    print(f"Weryfikacja: Instancje={instance_student_id}, Wyniki={solution_student_id}")
    
    sizes = range(50, 501, 50)
    results = []

    for n in sizes:
        instance_file = os.path.join(INSTANCE_DIR, f"in_{instance_student_id}_{n}.txt")
        solution_file = os.path.join(OUTPUT_DIR, f"out_{solution_student_id}_{n}.txt")

        if not os.path.exists(instance_file):
            print(f"Brak pliku instancji: {instance_file}")
            continue
        if not os.path.exists(solution_file):
            print(f"Brak pliku wynikowego: {solution_file}")
            continue

        try:
            n_inst, s, tasks_dict_raw = load_instance(instance_file)
            if n != n_inst:
                print(f"Konflikt N: Nazwa pliku ({n}) vs zawartość ({n_inst})")

            criterion_file, k, batches = load_solution(solution_file)
            
            if criterion_file == -1: 
                criterion_calc = -1
                poprawnosc = "bład wczytania"
            else:
                criterion_calc = calculate_criterion(n_inst, s, tasks_dict_raw, batches)
                poprawnosc = "TAK" if criterion_calc == criterion_file else "NIE"
            
            results.append({
                'n': n,
                'opoznienie_z_pliku': criterion_file,
                'opoznienie_przeliczone': criterion_calc,
                'czy_poprawne': poprawnosc
            })

            if poprawnosc == "NIE":
                print(f"bład: wartość z pliku: {criterion_file}, Wartość obliczona: {criterion_calc}")
            elif poprawnosc == "TAK":
                print(f"{criterion_calc}")

        except Exception as e:
            print(f"blad podczas przetwarzania N={n}: {e}")
            results.append({
                'n': n, 'opoznienie_z_pliku': 'ERROR', 'opoznienie_przeliczone': 'ERROR', 'czy_poprawne': 'ERROR'
            })

    if results:
        with open(REPORT_FILE, 'w', encoding='utf-8') as f:
            f.write("n;opoznienie_z_pliku_out;opoznienie_przeliczone_ver_sol;czy_poprawne\n")
            for res in results:
                f.write(f"{res['n']};{res['opoznienie_z_pliku']};{res['opoznienie_przeliczone']};{res['czy_poprawne']}\n")
        print(f"\nRaport porównawczy zapisano do pliku: {REPORT_FILE}")
    else:
        print("\nBrak wyników do zapisania.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Użycie: python analyze_results_v2.py <ID_studenta_instancji> <ID_studenta_wyniku>") #python .\analyze_results_v2.py 156014 155830 instancje 014, wynikowe 830
        sys.exit(1)

    instance_student_id = sys.argv[1]
    solution_student_id = sys.argv[2]
    
    analyze_and_report(instance_student_id, solution_student_id)
