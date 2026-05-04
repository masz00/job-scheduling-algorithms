import sys
import subprocess
import time
import os
import shutil

def print_summary(n, time_limit, elapsed_time, timeout=False):

    try:
        n_str = n.split('_')[-1].split('.')[0]
        n_val = int(n_str)
    except Exception:
        n_val = "N/A"

    timeout_status = "TAK" if timeout else "NIE"
    
    # output: test dla: n = {n}, limit t:{limit_t}, faktyczny t algorytmu: {t policzone}    przy zmianie, zmienić w run_tests.py
    print(f"test dla: n = {n_val}, limit t: {time_limit:.2f}, faktyczny t algorytmu: {elapsed_time:.4f}, timeout: {timeout_status}")

def verify_time(executable_and_args, instance_file, solution_file, time_limit):
    exe_path = executable_and_args[0]
    if not shutil.which(exe_path) and not os.path.exists(exe_path) and exe_path.lower() != 'python':
        print(f"Plik wykonywalny/skrypt '{exe_path}' nie istnieje lub nie jest w PATH.")
        return

    command = executable_and_args + [instance_file, solution_file, str(time_limit)] 
    start_time = time.perf_counter()
    
    instance_name_only = os.path.basename(instance_file)

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=time_limit + 1.0 # Daj 1s marginesu dla subprocess, solver ma swój ścisły limit
        )
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        
        if result.returncode != 0:
            print(f"Program zakończył się z błędem (kod: {result.returncode})")
            print("--- STDOUT ---")
            print(result.stdout)
            print("--- STDERR ---")
            print(result.stderr)
        
        print_summary(instance_name_only, time_limit, elapsed_time, False)

    except subprocess.TimeoutExpired:
        elapsed_time = time.perf_counter() - start_time
        print(f"przekroczono limit czasu ({time_limit} s)")
        print(f"Czas działania: {elapsed_time:.4f} s")
        
        print_summary(instance_name_only, time_limit, elapsed_time, True)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Użycie: python ver_time.py <p_wykonywalny> <p_instancji> <p_wynikowy> <limit_czasu_s>") # python ver_time.py python 155830.py in_155830_50.txt out_50_test.txt 5
        sys.exit(1)
        
    instance_file = sys.argv[-3]
    solution_file = sys.argv[-2]
    try:
        time_limit = float(sys.argv[-1])
    except ValueError:
        print("Błąd:ostatni argumnt (limit czasu) should be convertable to float (być liczbą)") #
        sys.exit(1)
    except Exception as e:
        print(f"wystąpił inny bład: {e}")

    executable_and_args = sys.argv[1:-3]

    verify_time(executable_and_args, instance_file, solution_file, time_limit)