import sys
from typing import Tuple, List, Dict

def load_instance(filename: str) -> Tuple[int, Dict[int, Dict[str, int]]]:

    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 1:
            print(f"Błąd instancji: plik jest pusty")
            sys.exit(1)

        try:
            n = int(lines[0])
            if n <= 0:
                print(f"Błąd instancji: n musi być > 0, otrzymano n={n}")
                sys.exit(1)
        except ValueError:
            print(f"Błąd instancji: pierwsza linia powinna być liczbą całkowitą n, otrzymano: '{lines[0]}'")
            sys.exit(1)

        if len(lines) - 1 != n:
            print(f"Błąd instancji: Liczba zadań w pliku ({len(lines)-1}) != zadeklarowane n={n}")
            sys.exit(1)

        tasks: Dict[int, Dict[str, int]] = {}
        for i in range(1, n + 1):
            line_num = i
            parts = lines[i].split()

            if len(parts) != 3:
                print(f"Błąd instancji (linia {line_num+1}, zadanie {i}):Oczekiwano 3 wartości (p r w), otrzymano {len(parts)}: {parts}")
                sys.exit(1)

            try:
                p = int(parts[0])
                r = int(parts[1])
                w = int(parts[2])
            except ValueError as e:
                print(f"Błąd instancji (linia {line_num+1}, zadanie {i}): wartości muszą być liczbami całkowitymi, otrzymano: {parts}")
                sys.exit(1)

            errors = []
            if p <= 0:
                errors.append(f"p={p} musi być > 0")
            if r < 0:
                errors.append(f"r={r} musi być ≥ 0")
            if w <= 0:
                errors.append(f"w={w} musi być > 0)")

            if errors:
                print(f"Błąd instancji (linia {line_num+1}, zadanie {i}): nieprawidłowe wartości:")
                for err in errors:
                    print(f"  - {err}")
                sys.exit(1)

            tasks[i] = {'p': p, 'r': r, 'w': w}

        return n, tasks

    except FileNotFoundError:
        print(f"BŁĄD: Nie znaleziono pliku instancji: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Błąd inny plik:{filename} bład: {e}")
        sys.exit(1)


def load_solution(filename: str, expected_n: int) -> Tuple[int, List[List[int]]]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f]

        while lines and not lines[-1]:
            lines.pop()

        if len(lines) < 5:
            print(f"Błąd rozwiązania: oczekiwano 5 linii, otrzymano {len(lines)}")
            sys.exit(1)
        try:
            criterion_value = int(lines[0])
            if criterion_value < 0:
                print(f"Błąd rozwiązania: wartość kryterium nie może być ujemna, otrzymano: {criterion_value}")
                sys.exit(1)
        except ValueError:
            print(f"Błąd rozwiązania: wartość kryterium musi być liczbą całkowitą, otrzymano: '{lines[0]}'")
            sys.exit(1)

        machines: List[List[int]] = []
        for i in range(1, 5):
            machine_num = i
            if i < len(lines) and lines[i]:
                try:
                    sequence = list(map(int, lines[i].split()))
                    machines.append(sequence)
                except ValueError as e:
                    print(f"Błąd rozwiązania: (linia {i+1} - (maszyna {machine_num}):Numery zadań muszą być liczbami całkowitymi")
                    print(f"Otrzymano: '{lines[i]}")
                    sys.exit(1)
            else:
                machines.append([])

        all_tasks = [task for seq in machines for task in seq]

        if len(all_tasks) != expected_n:
            print(f"Błąd rozwiązania: Łączna liczba zadań ({len(all_tasks)}) != oczekiwana ({expected_n})")
            print(f"Podział na maszyny: {[len(m) for m in machines]}")
            sys.exit(1)

        if len(set(all_tasks)) != len(all_tasks):
            duplicates = [t for t in set(all_tasks) if all_tasks.count(t) > 1]
            print(f"Błąd rozwiązania: zduplikowane zadania: {sorted(duplicates)}")
            sys.exit(1)

        expected_task_set = set(range(1, expected_n + 1))
        solution_task_set = set(all_tasks)

        if expected_task_set != solution_task_set:
            missing = expected_task_set - solution_task_set
            extra = solution_task_set - expected_task_set

            if missing:
                print(f"Błąd rozwiązania: brakujące zadania/e: {sorted(missing)}")
            if extra:
                print(f"Bład rozwiązania: nadmiarowe zadania/e: {sorted(extra)}")
            sys.exit(1)

        return criterion_value, machines

    except FileNotFoundError:
        print(f"Błąd rozwiązania: nie znaleziono pliku rozwiązania: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Błąd rozwiązania: niestandardowe blad pliku:{filename} bład: {e}")
        sys.exit(1)


def calculate_criterion(tasks: Dict[int, Dict[str, int]], machines: List[List[int]]) -> int:
    total_weighted_flow_time = 0

    for machine_id, machine_sequence in enumerate(machines, start=1):
        current_time = 0

        for job_id in machine_sequence:
            job = tasks[job_id]
            p_j = job['p']
            r_j = job['r']
            w_j = job['w']

            start_time = max(r_j, current_time)
            completion_time_Cj = start_time + p_j
            flow_time_Fj = completion_time_Cj - r_j
            total_weighted_flow_time += w_j * flow_time_Fj
            current_time = completion_time_Cj

    return total_weighted_flow_time


def verify_solution(instance_file: str, solution_file: str) -> None:
    n, tasks = load_instance(instance_file)
    criterion_file, machines = load_solution(solution_file, n)
    calculated_criterion = calculate_criterion(tasks, machines)

    diff = abs(calculated_criterion - criterion_file)

    if diff == 0:
        print(f"{calculated_criterion}")
    else:
        print(f"Błąd wartości kryterium, wartość z pliku: {criterion_file}, obliczona wartość: {calculated_criterion}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3: #python ver_sol.py in_155830_50.txt out_155830_50.txt
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]
    verify_solution(instance_file, solution_file)