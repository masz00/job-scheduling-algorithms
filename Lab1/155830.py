import sys
import time
import random
import copy
import math
from typing import List, Dict, Tuple

Task = Tuple[int, int, int] 

def load_instance(filename: str) -> Tuple[int, int, List[Task]]:
    try:
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines:
            raise ValueError("plik instancji jest pusty")

        n, s = map(int, lines[0].split())
        
        tasks: List[Task] = []
        for i, line in enumerate(lines[1:], start=1):
            if not line: continue
            p, d = map(int, line.split())
            tasks.append((i, p, d)) 

        if len(tasks) != n:
             raise ValueError(f"liczba zadań w pliku ({len(tasks)}) nie zgadza się z zadeklarowanym n={n}")

        return n, s, tasks
    except Exception as e:
        sys.exit(f"błąd wczytywania instancji: {e}")


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


def run_rcl(s: int, initial_tasks: List[Task], alpha: float) -> List[List[int]]:

    batches: List[List[int]] = []
    current_batch: List[int] = []
    current_time = 0
    current_batch_total_P = 0 
    
    remaining_tasks: List[Task] = list(initial_tasks)
    
    while remaining_tasks:
        if not remaining_tasks: break
        
        d_min = min(task[2] for task in remaining_tasks)
        rcl_threshold = d_min * (1.0 + alpha)
        rcl = [task for task in remaining_tasks if task[2] <= rcl_threshold]
        
        if not rcl:
             rcl = remaining_tasks 
             
        chosen_task = random.choice(rcl)  #TODO zastanowić się czy wag nie dac jak bedze czas w testach
        remaining_tasks.remove(chosen_task)
        
        j_index, p_j, d_j = chosen_task
        hypothetical_completion_time = current_time + current_batch_total_P + p_j 
        
        if not current_batch or hypothetical_completion_time <= d_j: 
            current_batch.append(j_index)
            current_batch_total_P += p_j
        else:
            batches.append(current_batch)     #TODO docelowo lepsza logika liczenia 
            current_time = (current_time + current_batch_total_P) + s

            current_batch = [j_index]
            current_batch_total_P = p_j
            
    if current_batch:
        batches.append(current_batch)
        
    return batches


def run_sa(initial_batches: List[List[int]],s: int, tasks_dict: Dict[int, Dict[str, int]], global_start_time: float, total_time_limit: float) -> Tuple[int, List[List[int]]]:

    best_criterion = calculate_criterion(s, tasks_dict, initial_batches)
    current_batches = copy.deepcopy(initial_batches)
    best_batches = copy.deepcopy(initial_batches)
    current_criterion = best_criterion
    
    T_start = max(1.0, float(best_criterion) * 0.05)  #TODO dostroić parametry
    T_end = 0.01
    cooling_factor = 0.9995 
    
    T = T_start
    iters_since_last_check = 0
    
    while True:
        iters_since_last_check += 1
        
        if iters_since_last_check >= 500:
            iters_since_last_check = 0
            if (time.time() - global_start_time) >= total_time_limit:
                break
        
        if T <= T_end:
            if (time.time() - global_start_time) < (total_time_limit - 0.5):# zapas na 1/2s
                T = T_start * 0.1
                current_batches = copy.deepcopy(best_batches) 
                current_criterion = best_criterion
            else:
                break
        
        candidate_batches = copy.deepcopy(current_batches)
        
        possible_moves = []
        if len(candidate_batches) >= 2:
            possible_moves.extend(['move', 'swap', 'merge'])
        if any(len(b) > 1 for b in candidate_batches):
            possible_moves.append('split')
            
        if not possible_moves:
            continue
            
        move = random.choice(possible_moves)

        try:
            if move == 'move':
                idx_from, idx_to = random.sample(range(len(candidate_batches)), 2)
                if not candidate_batches[idx_from]: continue
                task_idx = random.randrange(len(candidate_batches[idx_from]))
                task_id = candidate_batches[idx_from].pop(task_idx)
                candidate_batches[idx_to].append(task_id)
                
            elif move == 'swap':
                idx1, idx2 = random.sample(range(len(candidate_batches)), 2)
                if not candidate_batches[idx1] or not candidate_batches[idx2]: continue
                task_idx1 = random.randrange(len(candidate_batches[idx1]))
                task_idx2 = random.randrange(len(candidate_batches[idx2]))
                task1, task2 = candidate_batches[idx1][task_idx1], candidate_batches[idx2][task_idx2]
                candidate_batches[idx1][task_idx1], candidate_batches[idx2][task_idx2] = task2, task1

            elif move == 'split':
                possible_to_split = [i for i, b in enumerate(candidate_batches) if len(b) > 1]
                if not possible_to_split: continue
                idx_to_split = random.choice(possible_to_split)
                task_idx = random.randrange(len(candidate_batches[idx_to_split]))
                task_id = candidate_batches[idx_to_split].pop(task_idx)
                candidate_batches.append([task_id])

            elif move == 'merge':
                idx1, idx2 = random.sample(range(len(candidate_batches)), 2)
                candidate_batches[idx1].extend(candidate_batches[idx2])
                candidate_batches.pop(idx2)

            candidate_batches = [b for b in candidate_batches if b]
            candidate_criterion = calculate_criterion(s, tasks_dict, candidate_batches)

            delta = candidate_criterion - current_criterion
            
            if delta < 0:
                current_criterion = candidate_criterion
                current_batches = candidate_batches
                if candidate_criterion < best_criterion:
                    best_criterion = candidate_criterion
                    best_batches = copy.deepcopy(candidate_batches)
            elif math.exp(-delta / T) > random.random():
                current_criterion = candidate_criterion
                current_batches = candidate_batches
            
            T *= cooling_factor
                
        except (ValueError, IndexError):
            continue 
    return best_criterion, best_batches


def solve(n: int, s: int, tasks: List[Task]) -> Tuple[int, List[List[int]]]:

    total_time_limit = (n / 10.0) - 0.5 
    start_time_solve = time.time()

    tasks_dict = {task[0]: {'p': task[1], 'd': task[2]} for task in tasks}

    alpha = 0.1 #Faza konstrukcyjna TODO jak bedzie czas na zmiane, raczej nie powinno znaczaco wplynac jesli pozniej SA
    
    initial_batches = run_rcl(s, tasks, alpha)
    
    best_criterion, best_batches = run_sa(
        initial_batches, s, tasks_dict, 
        start_time_solve, 
        total_time_limit
    )
    return best_criterion, best_batches


def save_solution(filename: str, criterion_value: int, batches: List[List[int]]):
    try:
        final_batches = [b for b in batches if b]
        with open(filename, 'w') as f:
            f.write(str(criterion_value) + '\n') 
            f.write(str(len(final_batches)) + '\n') 
            for batch in final_batches:
                f.write(' '.join(map(str, batch)) + '\n') 
    except Exception as e:
        sys.exit(f"błąd zapisu rozwiązania: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Użycie: python 155830.py <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        sys.exit(1)

    instance_file = sys.argv[1]
    solution_file = sys.argv[2]
    
    try:
        time_limit_s = float(sys.argv[3])
    except ValueError:
        sys.exit("błąd:ostatni argument (limit czasu) should be convertable to float (być liczbą)") #
    n, s, tasks = load_instance(instance_file)
    criterion_value, batches = solve(n, s, tasks) 
    save_solution(solution_file, criterion_value, batches)
