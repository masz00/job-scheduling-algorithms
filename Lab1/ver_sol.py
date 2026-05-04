import sys
from typing import Tuple, List, Dict

def load_instance(filename: str) -> Tuple[int, int, Dict[int, Dict[str, int]]]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if len(lines) < 2:
            raise ValueError("plik instacji min 2 linie")

        n, s = map(int, lines[0].split())
        if len(lines) - 1 != n:
            raise ValueError(f"liczba linii zadań ({len(lines)-1}) nie zgadza się z n={n}")

        tasks: Dict[int, Dict[str, int]] = {}
        for i in range(1, n + 1):
            p, d = map(int, lines[i].split())
            tasks[i] = {'p': p, 'd': d}

        return n, s, tasks
    except Exception as e:
        sys.exit(f"Błąd wczytywania instancji: {e}")

def load_solution(filename: str, expected_n: int) -> Tuple[int, int, List[List[int]]]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if len(lines) < 3:
            raise ValueError("wyjsciowy min 3 linie")

        criterion_value = int(lines[0])
        k = int(lines[1])
        batches: List[List[int]] = [list(map(int, line.split())) for line in lines[2:]]

        if k != len(batches):
            raise ValueError(f"liczba batchy zadeklaraowana != faktynczna liczba -> k={k}, len(batches)={len(batches)}")

        all_tasks = [t for b in batches for t in b]
        if len(all_tasks) > expected_n:
            raise ValueError(f"za dużo tasków")

        if len(set(all_tasks)) != expected_n:
            raise ValueError("za mała liczba/duplikacja")

        if not all(1 <= t <= expected_n for t in all_tasks):
            raise ValueError("task poza zakresem")

        return criterion_value, k, batches
    except Exception as e:
        sys.exit(f"Złe rozwiązanie -> {e}")

def calculate_criterion(s: int, tasks: Dict[int, Dict[str, int]], batches: List[List[int]]) -> int:
    total_tardiness = 0
    current_time = 0

    for batch in batches:

        batch_time = sum(tasks[j]['p'] for j in batch)
        completion_time = current_time + batch_time
        current_time = completion_time + s

        for j in batch:
            tardiness = max(0,completion_time - tasks[j]['d'])
            total_tardiness += tardiness

    return total_tardiness

def verify_solution(instance_file: str, solution_file: str) -> None:

    n, s, tasks = load_instance(instance_file)
    criterion_file, k, batches = load_solution(solution_file, n)

    calc = calculate_criterion(s, tasks, batches)
    diff = abs(calc - criterion_file)

    if diff == 0:
        print(f"Brak bledu")
    else:
        print(f"{calc}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("python ver_sol.py <p_instancji> <p_rozwiazania>")
        sys.exit(1)

    instance_file, solution_file = sys.argv[1], sys.argv[2]
    verify_solution(instance_file, solution_file)
# if __name__ == "__main__":
#     index = 155271
#     sizes = range(50, 550, 50)
#
#     for size in sizes:
#         instance_file = f'./instancje/in_{index}_{size}.txt'
#         solution_file = f'./pliki_wynikowe/out_{size}.txt'
#
#         verify_solution(instance_file, solution_file)