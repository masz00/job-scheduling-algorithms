import sys
import time
import random
import copy
from typing import List, Dict, Tuple


TaskDict = Dict[int, Dict[str, int]]
MachineSchedules = List[List[int]]


def load_instance(filename: str) -> Tuple[int, TaskDict]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if len(lines) < 1:
            raise ValueError("Plik instancji jest pusty")

        n = int(lines[0])
        if len(lines) - 1 != n:
            raise ValueError(f"Liczba zadań w pliku ({len(lines)-1}) != zadeklarowane n={n}")

        tasks: TaskDict = {}
        for i in range(1, n + 1):
            parts = lines[i].split()
            if len(parts) != 3:
                raise ValueError(f"Linia {i+1}: Oczekiwano 3 wartości, otrzymano {len(parts)}")
            
            p = int(parts[0])
            r = int(parts[1])
            w = int(parts[2])
            tasks[i] = {'p': p, 'r': r, 'w': w}

        return n, tasks
    except Exception as e:
        print(f"Błąd wczytywania instancji: {e}", file=sys.stderr)
        sys.exit(1)


def save_solution(filename: str, criterion_value: int, schedules: MachineSchedules):
    try:
        with open(filename, 'w') as f:
            f.write(str(criterion_value) + '\n')
            for machine_seq in schedules:
                f.write(' '.join(map(str, machine_seq)) + '\n')
            for _ in range(4 - len(schedules)):
                f.write('\n')
    except Exception as e:
        print(f"Błąd zapisu rozwiązania: {e}", file=sys.stderr)
        sys.exit(1)


def calculate_total_cost(tasks: TaskDict, machine_schedules: MachineSchedules) -> int:
    total_weighted_flow_time = 0

    for machine_sequence in machine_schedules:
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


def calculate_machine_cost(tasks: TaskDict, machine_sequence: List[int]) -> int:
    cost = 0
    current_time = 0
    for job_id in machine_sequence:
        job = tasks[job_id]
        p_j = job['p']
        r_j = job['r']
        w_j = job['w']
        
        start_time = max(r_j, current_time)
        completion_time = start_time + p_j
        flow_time = completion_time - r_j
        
        cost += w_j * flow_time
        current_time = completion_time
    
    return cost


def get_initial_solution(tasks: TaskDict, m_machines: int = 4) -> MachineSchedules:
    
    jobs_list = []
    for job_id, details in tasks.items():
        p, r, w = details['p'], details['r'], details['w']
        wspt_ratio = (p / w) if w > 0 else p 
        jobs_list.append((job_id, p, r, w, wspt_ratio))

    jobs_list.sort(key=lambda x: x[4])

    schedules: MachineSchedules = [[] for _ in range(m_machines)]
    machine_free_time = [0] * m_machines

    for job_id, p_j, r_j, w_j, _ in jobs_list:
        best_machine_idx = 0
        min_free_time = machine_free_time[0]
        
        for m_idx in range(1, m_machines):
            if machine_free_time[m_idx] < min_free_time:
                min_free_time = machine_free_time[m_idx]
                best_machine_idx = m_idx
        
        start_time = max(r_j, min_free_time)
        completion_time = start_time + p_j
        
        machine_free_time[best_machine_idx] = completion_time
        schedules[best_machine_idx].append(job_id)
        
    return schedules


def random_local_search_unlimited(tasks: TaskDict, 
                                 current_solution: MachineSchedules,
                                 global_start: float,
                                 time_limit: float) -> Tuple[MachineSchedules, int]:

    current_cost = calculate_total_cost(tasks, current_solution)
    best_solution = copy.deepcopy(current_solution)
    best_cost = current_cost
    
    attempts = 0
    no_improve_since_best = 0
    
    while (time.time() - global_start) < time_limit:
        attempts += 1
        if random.random() < 0.7:
            nonempty_machines = [m for m in range(4) if current_solution[m]]
            
            if len(nonempty_machines) >= 2:
                m_from = random.choice(nonempty_machines)
                m_to = random.choice([m for m in range(4) if m != m_from])
                
                if current_solution[m_from]:
                    task_idx = random.randint(0, len(current_solution[m_from]) - 1)
                    task_id = current_solution[m_from][task_idx]
                    
                    # Oblicz zmianę kosztu (tylko dla obu maszyn)
                    old_cost_m_from = calculate_machine_cost(tasks, current_solution[m_from])
                    old_cost_m_to = calculate_machine_cost(tasks, current_solution[m_to])
                    
                    # Stwórz nowe harmonogramy
                    new_m_from = current_solution[m_from][:task_idx] + current_solution[m_from][task_idx+1:]
                    new_m_to = current_solution[m_to] + [task_id]
                    
                    new_cost_m_from = calculate_machine_cost(tasks, new_m_from)
                    new_cost_m_to = calculate_machine_cost(tasks, new_m_to)
                    
                    delta = (new_cost_m_from - old_cost_m_from) + (new_cost_m_to - old_cost_m_to)
                    new_total_cost = current_cost + delta
                    
                    if new_total_cost < current_cost:
                        current_solution[m_from] = new_m_from
                        current_solution[m_to] = new_m_to
                        current_cost = new_total_cost
                        no_improve_since_best = 0
                        
                        if new_total_cost < best_cost:
                            best_cost = new_total_cost
                            best_solution = copy.deepcopy(current_solution)
                    else:
                        no_improve_since_best += 1
        else:
            
            machines_with_tasks = [m for m in range(4) if len(current_solution[m]) >= 2]
            
            if machines_with_tasks:
                m_idx = random.choice(machines_with_tasks)
                i = random.randint(0, len(current_solution[m_idx]) - 1)
                j = random.randint(0, len(current_solution[m_idx]) - 1)
                
                if i != j:
                    old_cost = calculate_machine_cost(tasks, current_solution[m_idx])
                    
                    # Swap
                    current_solution[m_idx][i], current_solution[m_idx][j] = \
                        current_solution[m_idx][j], current_solution[m_idx][i]
                    
                    new_cost = calculate_machine_cost(tasks, current_solution[m_idx])
                    delta = new_cost - old_cost
                    new_total_cost = current_cost + delta
                    
                    if new_total_cost < current_cost:
                        current_cost = new_total_cost
                        no_improve_since_best = 0
                        
                        if new_total_cost < best_cost:
                            best_cost = new_total_cost
                            best_solution = copy.deepcopy(current_solution)
                    else:
                        # Swap back
                        current_solution[m_idx][i], current_solution[m_idx][j] = \
                            current_solution[m_idx][j], current_solution[m_idx][i]
                        no_improve_since_best += 1
        
        # Nie wychodzę z LS - pracuj do końca czasu!
        # Ale jeśli nie ma żadnej poprawy od 100+ prób, perturbuj
        if no_improve_since_best > 100:
            break
    
    return best_solution, best_cost


def perturbation_fast(tasks: TaskDict, 
                      solution: MachineSchedules,
                      perturbation_strength: int = 2) -> MachineSchedules:
    """Szybka perturbacja."""
    perturbed = copy.deepcopy(solution)
    
    all_tasks_positions = []
    for m_idx in range(4):
        for task_idx in range(len(perturbed[m_idx])):
            all_tasks_positions.append((m_idx, task_idx))
    
    num_to_remove = min(perturbation_strength, len(all_tasks_positions))
    if num_to_remove == 0:
        return perturbed
    
    positions_to_remove = random.sample(all_tasks_positions, num_to_remove)
    
    removed_tasks = []
    for m_idx, task_idx in sorted(positions_to_remove, key=lambda x: (x[0], -x[1])):
        removed_tasks.append(perturbed[m_idx].pop(task_idx))
    
    machine_free_time = [0] * 4
    
    for m_idx in range(4):
        current_time = 0
        for job_id in perturbed[m_idx]:
            r_j = tasks[job_id]['r']
            p_j = tasks[job_id]['p']
            start_time = max(r_j, current_time)
            current_time = start_time + p_j
        machine_free_time[m_idx] = current_time
    
    for job_id in removed_tasks:
        best_m = min(range(4), 
                    key=lambda m: max(tasks[job_id]['r'], machine_free_time[m]))
        perturbed[best_m].append(job_id)
        start_time = max(tasks[job_id]['r'], machine_free_time[best_m])
        machine_free_time[best_m] = start_time + tasks[job_id]['p']
    
    return perturbed


def solve_with_ils(n: int, tasks: TaskDict, time_limit: float) -> Tuple[int, MachineSchedules]:
    """
    ILS: Pracuje przez CAŁY dostępny czas, zostawiając 0.5s luzu.
    """
    global_start_time = time.time()
    
    TIME_BUFFER = 0.5  # Lusz 0.5s
    effective_time_limit = time_limit - TIME_BUFFER
    
    # Inicjalizacja
    best_solution = get_initial_solution(tasks)
    best_cost = calculate_total_cost(tasks, best_solution)
    
    current_solution = copy.deepcopy(best_solution)
    current_cost = best_cost
    
    iteration = 0
    
    # GŁÓWNA PĘTLA: pracuj do końca czasu
    while (time.time() - global_start_time) < effective_time_limit:
        elapsed = time.time() - global_start_time
        remaining = effective_time_limit - elapsed
        
        if remaining < 0.05:
            break
        
        # Daj CAŁEMU LS dostępny czas (minus mały zapas na perturbację)
        ls_time_budget = remaining - 0.01
        
        ls_solution, ls_cost = random_local_search_unlimited(
            tasks, 
            current_solution,
            global_start_time,
            global_start_time + ls_time_budget
        )
        
        # Aktualizuj najlepsze
        if ls_cost < best_cost:
            best_cost = ls_cost
            best_solution = copy.deepcopy(ls_solution)
        
        current_solution = copy.deepcopy(ls_solution)
        current_cost = ls_cost
        
        # Perturbacja na koniec
        perturbation_strength = 2
        current_solution = perturbation_fast(tasks, current_solution, perturbation_strength)
        current_cost = calculate_total_cost(tasks, current_solution)
        
        iteration += 1
    
    return best_cost, best_solution


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Użycie: python 155830.py <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]
    
    try:
        time_limit_s = float(sys.argv[3])
    except ValueError:
        print("Błąd: limit czasu musi być liczbą.", file=sys.stderr)
        sys.exit(1)

    n, tasks = load_instance(instance_file)
    criterion_value, schedules = solve_with_ils(n, tasks, time_limit_s)
    save_solution(solution_file, criterion_value, schedules)