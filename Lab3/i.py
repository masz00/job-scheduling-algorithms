import os
import sys


INSTANCES_DIR = "instancje"


class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def load_and_analyze(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        n = int(lines[0])
        
        # Parsowanie P i R
        p_matrix = [] 
        r_list = []
        for i in range(n):
            parts = list(map(int, lines[1 + i].split()))
            p_matrix.append(parts[:4])
            r_list.append(parts[4])

        # Parsowanie S (tylko suma)
        s_values = []
        for line in lines[1 + n:]:
            s_values.extend(map(int, line.split()))
        total_setup = sum(s_values)

      
        
        # Bottleneck Ratio
        mach_load = [0]*4
        total_p = 0
        for p in p_matrix:
            for m in range(4):
                mach_load[m] += p[m]
                total_p += p[m]
        
        avg_mach_load = sum(mach_load) / 4
        max_mach_load = max(mach_load)
        bot_idx = mach_load.index(max_mach_load) + 1
        bot_ratio = max_mach_load / avg_mach_load if avg_mach_load > 0 else 1.0

        # Setup Percentage
        # (Średni setup) / (Średni czas zadania)
        avg_s = total_setup / (n * (n - 1)) if n > 1 else 0
        avg_job = total_p / n if n > 0 else 1
        setup_pct = (avg_s / avg_job) * 100

        # Release Date Spread
        max_r = max(r_list)
        

        r_spread = max_r / max_mach_load if max_mach_load > 0 else 0
        

        # Strategiua
        
        strategy = "NEH Standard"
        color = Colors.GREEN
        
        # TSP dominuje wszystko inne Jezeli setupy sa > 20%
        if setup_pct > 20.0:
            strategy = "TSP / Clustering"
            color = Colors.RED
        
        # Jesli zadania przychodza rzadko, musisz brac to co jest dostępne (sort r_j)
        elif r_spread > 0.8:
            strategy = "Release Priority"
            color = Colors.CYAN
            
        # Jesli nie głodzenie, to czy wąskie gardło?
        # Jesli jedna maszyna zatyka, sortujemy pod nią
        elif bot_ratio > 1.25:
            strategy = f"Bottleneck (M{bot_idx})"
            color = Colors.YELLOW
            
        elif setup_pct > 12.0:
            strategy = "NEH + Setup Lookahead"
            color = Colors.BLUE
            
        return {
            'n': n,
            'bot': bot_ratio,
            'bot_idx': bot_idx,
            'setup': setup_pct,
            'r_spread': r_spread,
            'col': color
        }

    except Exception as e:
        return None

def main():
    if not os.path.exists(INSTANCES_DIR):
        print(f"Brak folderu {INSTANCES_DIR}")
        return

    files = [f for f in os.listdir(INSTANCES_DIR) if f.startswith("in_") and f.endswith(".txt")]
    
    def sort_key(fname):
        parts = fname.replace(".txt", "").split("_")
        try:
            student_id = int(parts[1])
            n = int(parts[2])
            return (student_id, n)
        except:
            return (0, 0)
            
    files.sort(key=sort_key)

    print(f"{'PLIK':<25} | {'N':<4} | {'BOT RATIO':<10} | {'SETUP %':<8} | {'R SPREAD':<8}")
    print("-" * 90)

    prev_id = None

    for fname in files:
        curr_id = fname.split('_')[1] if len(fname.split('_')) > 1 else ""
        if prev_id is not None and curr_id != prev_id:
            print("-" * 90)
        prev_id = curr_id

        path = os.path.join(INSTANCES_DIR, fname)
        res = load_and_analyze(path)
        
        if res:
            bot_str = f"{res['bot']:.2f} (M{res['bot_idx']})"
            setup_str = f"{res['setup']:.1f}%"
            r_str = f"{res['r_spread']:.2f}"
            
            print(f"{fname:<25} | {res['n']:<4} | {bot_str:<10} | {setup_str:<8} | {r_str:<8}")

if __name__ == "__main__":
    main()


"""
LIK                      | N    | BOT RATIO  | SETUP %  | R SPREAD
------------------------------------------------------------------------------------------
in_151893_50.txt          | 50   | 1.04 (M1)  | 13.1%    | 0.09    
in_151893_100.txt         | 100  | 1.06 (M4)  | 13.0%    | 0.04    
in_151893_150.txt         | 150  | 1.06 (M3)  | 12.7%    | 0.03    
in_151893_200.txt         | 200  | 1.01 (M3)  | 13.4%    | 0.02    
in_151893_250.txt         | 250  | 1.02 (M4)  | 13.1%    | 0.02    
in_151893_300.txt         | 300  | 1.03 (M4)  | 13.3%    | 0.02    
in_151893_350.txt         | 350  | 1.03 (M2)  | 13.0%    | 0.01    
in_151893_400.txt         | 400  | 1.03 (M4)  | 13.1%    | 0.01    
in_151893_450.txt         | 450  | 1.01 (M2)  | 12.9%    | 0.01    
in_151893_500.txt         | 500  | 1.03 (M2)  | 13.2%    | 0.01    
------------------------------------------------------------------------------------------
in_155275_50.txt          | 50   | 1.04 (M2)  | 14.0%    | 0.13    
in_155275_100.txt         | 100  | 1.03 (M1)  | 12.4%    | 0.06    
in_155275_150.txt         | 150  | 1.04 (M2)  | 12.9%    | 0.05    
in_155275_200.txt         | 200  | 1.03 (M1)  | 13.6%    | 0.04
in_155275_250.txt         | 250  | 1.04 (M1)  | 12.8%    | 0.03    
in_155275_300.txt         | 300  | 1.05 (M3)  | 14.3%    | 0.03    
in_155275_350.txt         | 350  | 1.03 (M1)  | 14.0%    | 0.02    
in_155275_400.txt         | 400  | 1.03 (M3)  | 13.3%    | 0.02    
in_155275_450.txt         | 450  | 1.04 (M1)  | 14.1%    | 0.02    
in_155275_500.txt         | 500  | 1.03 (M3)  | 13.6%    | 0.02    
------------------------------------------------------------------------------------------
in_155829_50.txt          | 50   | 1.09 (M3)  | 13.4%    | 0.10
in_155829_100.txt         | 100  | 1.07 (M2)  | 12.7%    | 0.10    
in_155829_150.txt         | 150  | 1.06 (M3)  | 13.0%    | 0.08    
in_155829_200.txt         | 200  | 1.04 (M1)  | 13.2%    | 0.09    
in_155829_250.txt         | 250  | 1.02 (M1)  | 13.2%    | 0.09    
in_155829_300.txt         | 300  | 1.03 (M1)  | 13.2%    | 0.10    
in_155829_350.txt         | 350  | 1.04 (M3)  | 12.9%    | 0.09    
in_155829_400.txt         | 400  | 1.01 (M3)  | 13.1%    | 0.09    
in_155829_450.txt         | 450  | 1.02 (M1)  | 13.1%    | 0.09    
in_155829_500.txt         | 500  | 1.04 (M2)  | 13.1%    | 0.09    
------------------------------------------------------------------------------------------
in_155830_50.txt          | 50   | 2.17 (M2)  | 9.6%     | 0.52
in_155830_100.txt         | 100  | 2.02 (M2)  | 10.1%    | 0.59    
in_155830_150.txt         | 150  | 2.10 (M2)  | 9.9%     | 0.56    
in_155830_200.txt         | 200  | 2.11 (M2)  | 10.0%    | 0.57    
in_155830_250.txt         | 250  | 2.09 (M2)  | 10.0%    | 0.57    
in_155830_300.txt         | 300  | 2.03 (M2)  | 10.2%    | 0.60    
in_155830_350.txt         | 350  | 2.06 (M2)  | 10.1%    | 0.59    
in_155830_400.txt         | 400  | 2.09 (M2)  | 10.0%    | 0.57    
in_155830_450.txt         | 450  | 2.04 (M2)  | 10.2%    | 0.60    
in_155830_500.txt         | 500  | 2.07 (M2)  | 10.0%    | 0.58    
------------------------------------------------------------------------------------------
in_155863_50.txt          | 50   | 1.03 (M4)  | 6.0%     | 0.37
in_155863_100.txt         | 100  | 1.04 (M3)  | 6.2%     | 0.19    
in_155863_150.txt         | 150  | 1.02 (M2)  | 6.2%     | 0.13    
in_155863_200.txt         | 200  | 1.05 (M3)  | 6.1%     | 0.09    
in_155863_250.txt         | 250  | 1.03 (M2)  | 6.2%     | 0.08    
in_155863_300.txt         | 300  | 1.06 (M1)  | 6.2%     | 0.06    
in_155863_350.txt         | 350  | 1.05 (M3)  | 6.0%     | 0.05    
in_155863_400.txt         | 400  | 1.05 (M3)  | 6.4%     | 0.05    
in_155863_450.txt         | 450  | 1.03 (M3)  | 6.3%     | 0.04    
in_155863_500.txt         | 500  | 1.03 (M4)  | 6.2%     | 0.04    
------------------------------------------------------------------------------------------
in_155883_50.txt          | 50   | 1.06 (M1)  | 15.2%    | 0.15    
in_155883_100.txt         | 100  | 1.06 (M1)  | 14.8%    | 0.07    
in_155883_150.txt         | 150  | 1.03 (M2)  | 15.2%    | 0.05    
in_155883_200.txt         | 200  | 1.04 (M4)  | 14.3%    | 0.04    
in_155883_250.txt         | 250  | 1.03 (M3)  | 15.4%    | 0.03    
in_155883_300.txt         | 300  | 1.06 (M1)  | 14.8%    | 0.02    
in_155883_350.txt         | 350  | 1.02 (M3)  | 15.0%    | 0.02    
in_155883_400.txt         | 400  | 1.03 (M3)  | 14.6%    | 0.02    
in_155883_450.txt         | 450  | 1.04 (M1)  | 14.4%    | 0.02    
in_155883_500.txt         | 500  | 1.02 (M1)  | 14.5%    | 0.02    
------------------------------------------------------------------------------------------
in_155888_50.txt          | 50   | 1.08 (M1)  | 19.8%    | 0.09    
in_155888_100.txt         | 100  | 1.03 (M4)  | 18.1%    | 0.04
in_155888_150.txt         | 150  | 1.02 (M4)  | 18.5%    | 0.03    
in_155888_200.txt         | 200  | 1.06 (M2)  | 19.3%    | 0.02    
in_155888_250.txt         | 250  | 1.04 (M1)  | 19.1%    | 0.02    
in_155888_300.txt         | 300  | 1.06 (M2)  | 19.0%    | 0.01    
in_155888_350.txt         | 350  | 1.02 (M3)  | 18.9%    | 0.01    
in_155888_400.txt         | 400  | 1.03 (M3)  | 19.5%    | 0.01    
in_155888_450.txt         | 450  | 1.05 (M2)  | 19.5%    | 0.01    
in_155888_500.txt         | 500  | 1.04 (M4)  | 19.1%    | 0.01    
------------------------------------------------------------------------------------------
in_155972_50.txt          | 50   | 1.06 (M3)  | 6.4%     | 0.93    
in_155972_100.txt         | 100  | 1.04 (M1)  | 6.3%     | 0.93    
in_155972_150.txt         | 150  | 1.03 (M2)  | 6.2%     | 0.95    
in_155972_200.txt         | 200  | 1.01 (M4)  | 6.1%     | 0.95    
in_155972_250.txt         | 250  | 1.01 (M1)  | 6.4%     | 0.98    
in_155972_300.txt         | 300  | 1.01 (M4)  | 6.3%     | 0.98    
in_155972_350.txt         | 350  | 1.02 (M4)  | 6.3%     | 0.99    
in_155972_400.txt         | 400  | 1.04 (M1)  | 6.3%     | 0.96    
in_155972_450.txt         | 450  | 1.02 (M1)  | 6.2%     | 0.97    
in_155972_500.txt         | 500  | 1.03 (M4)  | 6.3%     | 0.97    
------------------------------------------------------------------------------------------
in_155989_50.txt          | 50   | 1.18 (M2)  | 14.2%    | 1.23    
in_155989_100.txt         | 100  | 1.09 (M3)  | 13.7%    | 1.45    
in_155989_150.txt         | 150  | 1.16 (M4)  | 15.2%    | 1.38
in_155989_200.txt         | 200  | 1.08 (M1)  | 15.6%    | 1.48    
in_155989_250.txt         | 250  | 1.18 (M3)  | 14.8%    | 1.36    
in_155989_300.txt         | 300  | 1.16 (M3)  | 14.7%    | 1.37    
in_155989_350.txt         | 350  | 1.07 (M3)  | 13.5%    | 1.50    
in_155989_400.txt         | 400  | 1.11 (M1)  | 14.4%    | 1.44    
in_155989_450.txt         | 450  | 1.12 (M1)  | 15.2%    | 1.42    
in_155989_500.txt         | 500  | 1.17 (M2)  | 14.8%    | 1.36    
------------------------------------------------------------------------------------------
in_156014_50.txt          | 50   | 1.07 (M2)  | 5.1%     | 0.72
in_156014_100.txt         | 100  | 1.04 (M2)  | 4.7%     | 0.69    
in_156014_150.txt         | 150  | 1.03 (M3)  | 4.8%     | 0.71    
in_156014_200.txt         | 200  | 1.05 (M4)  | 4.7%     | 0.68    
in_156014_250.txt         | 250  | 1.03 (M1)  | 4.7%     | 0.70    
in_156014_300.txt         | 300  | 1.04 (M1)  | 4.9%     | 0.71    
in_156014_350.txt         | 350  | 1.01 (M3)  | 4.8%     | 0.72    
in_156014_400.txt         | 400  | 1.05 (M4)  | 4.9%     | 0.70    
in_156014_450.txt         | 450  | 1.02 (M2)  | 4.8%     | 0.71    
in_156014_500.txt         | 500  | 1.02 (M3)  | 4.7%     | 0.70    
------------------------------------------------------------------------------------------
in_156935_50.txt          | 50   | 1.03 (M3)  | 51.6%    | 0.44
in_156935_100.txt         | 100  | 1.11 (M4)  | 52.9%    | 0.41    
in_156935_150.txt         | 150  | 1.05 (M1)  | 49.4%    | 0.41    
in_156935_200.txt         | 200  | 1.06 (M2)  | 49.2%    | 0.41    
in_156935_250.txt         | 250  | 1.01 (M1)  | 49.9%    | 0.44    
in_156935_300.txt         | 300  | 1.02 (M3)  | 50.8%    | 0.44    
in_156935_350.txt         | 350  | 1.03 (M3)  | 50.5%    | 0.43    
in_156935_400.txt         | 400  | 1.02 (M3)  | 50.5%    | 0.44    
in_156935_450.txt         | 450  | 1.04 (M2)  | 50.7%    | 0.43    
in_156935_500.txt         | 500  | 1.01 (M4)  | 49.7%    | 0.43    
------------------------------------------------------------------------------------------
in_159087_50.txt          | 50   | 1.12 (M4)  | 2.7%     | 0.01    
in_159087_100.txt         | 100  | 1.01 (M4)  | 2.6%     | 0.01
in_159087_150.txt         | 150  | 1.04 (M2)  | 2.6%     | 0.01    
in_159087_200.txt         | 200  | 1.03 (M2)  | 2.7%     | 0.01    
in_159087_250.txt         | 250  | 1.05 (M2)  | 2.7%     | 0.01    
in_159087_300.txt         | 300  | 1.05 (M1)  | 2.7%     | 0.01    
in_159087_350.txt         | 350  | 1.02 (M1)  | 2.8%     | 0.01    
in_159087_400.txt         | 400  | 1.01 (M4)  | 2.8%     | 0.01    
in_159087_450.txt         | 450  | 1.02 (M1)  | 2.7%     | 0.01    
in_159087_500.txt         | 500  | 1.05 (M2)  | 2.7%     | 0.01    
"""