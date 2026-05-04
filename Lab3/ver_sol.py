import sys
from typing import Tuple, List, Dict, Set

def load_instance(filename: str) -> Tuple[int, List[Dict], List[List[int]]]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            raw_lines = f.readlines()

        lines = [line.strip() for line in raw_lines if line.strip()]

        if not lines:
            raise ValueError("Plik instancji jest pusty")

        try:
            n = int(lines[0])
            if n <= 0:
                raise ValueError(f"Liczba zadań n musi być > 0, otrzymano: {n}")
        except ValueError:
            raise ValueError(f"Pierwsza linia musi być liczbą całkowitą. Otrzymano: '{lines[0]}'")

        expected_lines_count = 1 + n + n
        if len(lines) < expected_lines_count:
            raise ValueError(f"Za mało linii w pliku. Oczekiwano {expected_lines_count} (n={n}), jest {len(lines)}")

        jobs = []
        for i in range(n):
            line_idx = 1 + i
            content = lines[line_idx]
            parts = content.split()
            
            if len(parts) != 5:
                raise ValueError(f"Błąd w linii {line_idx+1} (zadanie {i+1}): Oczekiwano 5 liczb, otrzymano {len(parts)}")
            
            try:
                vals = list(map(int, parts))
            except ValueError:
                raise ValueError(f"Błąd w linii {line_idx+1}: Wartości muszą być liczbami całkowitymi, otrzymano: '{content}'")

            if any(p <= 0 for p in vals[:4]):
                raise ValueError(f"Błąd w linii {line_idx+1}: Czasy procesowania muszą być dodatnie, otrzymano: {vals[:4]}")
            if vals[4] < 0:
                raise ValueError(f"Błąd w linii {line_idx+1}: Czas dostępności r nie może być ujemny, otrzymano: {vals[4]}")

            jobs.append({
                'id': i + 1,
                'p': vals[:4],
                'r': vals[4]
            })

        s_matrix = []
        start_matrix_line = 1 + n
        
        for i in range(n):
            line_idx = start_matrix_line + i
            content = lines[line_idx]
            parts = content.split()

            if len(parts) != n:
                raise ValueError(f"Błąd macierzy S (wiersz {i+1}, linia pliku {line_idx+1}): Oczekiwano {n} wartości, otrzymano {len(parts)}")

            try:
                row = list(map(int, parts))
            except ValueError:
                raise ValueError(f"Błąd macierzy S (wiersz {i+1}): Wartości muszą być liczbami całkowitymi, otrzymano: {content}")

            if any(val < 0 for val in row):
                 raise ValueError(f"Błąd macierzy S (wiersz {i+1}): Czasy przezbrojeń nie mogą być ujemne")

            if row[i] != 0:
                 raise ValueError(f"Błąd macierzy S: Wartość na przekątnej S[{i+1}][{i+1}] musi wynosić 0, otrzymano: {row[i]}")

            s_matrix.append(row)

        return n, jobs, s_matrix

    except Exception as e:
        print(f"Błąd instancji: {e}")
        sys.exit(1)


def load_solution(filename: str, expected_n: int) -> Tuple[int, List[int]]:
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) != 2:
            print(f"Błąd rozwiązania: Oczekiwano 2 linii, otrzymano {len(lines)}")
            sys.exit(1)

        try:
            cmax = int(lines[0])
            if cmax < 0:
                print(f"Błąd rozwiązania: Wartość Cmax nie może być ujemna ({cmax})")
                sys.exit(1)
        except ValueError:
            print(f"Błąd rozwiązania: Pierwsza linia musi być liczbą całkowitą, otrzymano: '{lines[0]}'")
            sys.exit(1)

        try:
            sequence = list(map(int, lines[1].split()))
        except ValueError:
            print(f"Błąd rozwiązania: Druga linia musi zawierać ciąg liczb całkowitych, otrzymano: {lines[1]}")
            sys.exit(1)

        task_ids = sequence
        sys_exit_end = False
        if len(task_ids) != expected_n:
            print(f"Błąd rozwiązania: Nieprawidłowa liczba zadań w sekwencji, oczekiwano: {expected_n}, otrzymano:  {len(task_ids)}")
            sys_exit_end = True

        received_set = set(task_ids)
        expected_set = set(range(1, expected_n + 1))

        if len(received_set) != len(task_ids):
            duplicates = {}
            for t in task_ids:
                duplicates[t] = duplicates.get(t, 0) + 1
            dup_list = [k for k, v in duplicates.items() if v > 1]
            print(f"Błąd rozwiązania: Znaleziono zduplikowane zadania: {sorted(dup_list)}")
            sys_exit_end = True

        if received_set != expected_set:
            missing = expected_set - received_set
            extra = received_set - expected_set
            
            if missing:
                print(f"Błąd rozwiązania: Brakujące zadania: {sorted(list(missing))}")
            if extra:
                print(f"Błąd rozwiązania: Zadania spoza zakresu: {sorted(list(extra))}")
            sys_exit_end = True
        if sys_exit_end:
            sys.exit(1)

        return cmax, sequence

    except FileNotFoundError:
        print(f"Błąd: Nie znaleziono pliku rozwiązania: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Błąd wczytywania rozwiązania: {e}")
        sys.exit(1)


def calculate_real_cmax(n: int, jobs: List[Dict], s_matrix: List[List[int]], sequence: List[int]) -> int:

    job_map = {j['id']: j for j in jobs}
    
    machine_avail_time = [0] * 4 
    
    prev_job_idx = None

    for job_id in sequence:
        curr_job = job_map[job_id]
        curr_job_idx = job_id - 1
        
        setup_time = 0
        if prev_job_idx is not None:
            setup_time = s_matrix[prev_job_idx][curr_job_idx]
        
        job_ready_time = curr_job['r']
        
        for m in range(4):
            machine_ready_for_work = machine_avail_time[m] + setup_time
            start_time = max(machine_ready_for_work, job_ready_time)
            duration = curr_job['p'][m]
            finish_time = start_time + duration
            machine_avail_time[m] = finish_time
            job_ready_time = finish_time

        prev_job_idx = curr_job_idx

    return machine_avail_time[3]


def main():
    if len(sys.argv) != 3:
        print("Użycie: python ver_sol.py <plik_instancji> <plik_rozwiązania>")
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]

    n, jobs, s_matrix = load_instance(instance_file)
    sol_cmax, sequence = load_solution(solution_file, n)
    real_cmax = calculate_real_cmax(n, jobs, s_matrix, sequence)

    if real_cmax != sol_cmax:
        print(f"Błąd CMAX, obliczona wartość: {real_cmax} jest różna z wartością z pliku: {sol_cmax}")
        sys.exit(1)
    print(real_cmax)

if __name__ == "__main__":
    main()