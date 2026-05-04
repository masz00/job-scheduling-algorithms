import sys
import subprocess
import time
import os


def print_summary(n_str: str, time_limit: float, elapsed_time: float, timeout: bool = False):
    try:
        n_val = n_str.split('_')[-1].split('.')[0]
        n_val = int(n_val)
    except (ValueError, IndexError):
        n_val = "N/A"

    timeout_status = "TAK" if timeout else "NIE"
    print(f"n = {n_val:4} | limit: {time_limit:6.2f}s | faktyczny: {elapsed_time:8.4f}s | timeout: {timeout_status}")


def verify_time(executable_and_args, instance_file: str, solution_file: str, time_limit: float):
    exe_path = executable_and_args[0]
    
    if exe_path.lower() == 'python':
        if len(executable_and_args) < 2:
            print(f"Błąd: Dla Python podaj plik skryptu jako drugi argument")
            return
    elif not (os.path.exists(exe_path) or os.path.exists(exe_path + '.exe')):
        if not os.path.exists(exe_path):
            print(f"Błąd: Nie znaleziono pliku {exe_path}")
            return

    # Prepare command
    command = list(executable_and_args) + [instance_file, solution_file, str(time_limit)]
    instance_name_only = os.path.basename(instance_file)

    # Run with timeout
    start_time = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=time_limit + 2.0,
            encoding='utf-8',
            errors='replace'
        )
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time

        if result.returncode != 0:
            print(f"Program zakończył się z błędem (kod: {result.returncode})")
            if result.stderr:
                print("--- STDERR ---")
                print(result.stderr[:500])  # Limit output
            if result.stdout:
                print("--- STDOUT ---")
                print(result.stdout[:500])

        print_summary(instance_name_only, time_limit, elapsed_time, False)

    except subprocess.TimeoutExpired:
        elapsed_time = time.perf_counter() - start_time
        print(f"Przekroczono limit czasu ({time_limit}s)")
        print_summary(instance_name_only, time_limit, elapsed_time, True)

    except Exception as e:
        elapsed_time = time.perf_counter() - start_time
        print(f"Błąd podczas uruchamiania: {e}")
        print_summary(instance_name_only, time_limit, elapsed_time, False)


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Użycie: python ver_time.py <program> [args...] <plik_instancji> <plik_wynikowy> <limit_czasu_s>")
        print("Przykład 1: python ver_time.py python 155830.py in_155830_50.txt out_50_test.txt 5")
        print("Przykład 2: python ver_time.py ./solver in_155830_50.txt out_50_test.txt 5")
        sys.exit(1)

    # Parse arguments
    instance_file = sys.argv[-3]
    solution_file = sys.argv[-2]
    
    try:
        time_limit = float(sys.argv[-1])
        if time_limit <= 0:
            raise ValueError("Limit czasu musi być > 0")
    except ValueError as e:
        print(f"Błąd: Ostatni argument (limit czasu) musi być liczbą dodatnią. Otrzymano: {sys.argv[-1]}")
        sys.exit(1)

    executable_and_args = sys.argv[1:-3]

    if not os.path.exists(instance_file):
        print(f"Błąd: Nie znaleziono pliku instancji: {instance_file}")
        sys.exit(1)

    verify_time(executable_and_args, instance_file, solution_file, time_limit)