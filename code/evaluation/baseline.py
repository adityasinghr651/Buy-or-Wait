import time
import json
import csv
from collections import Counter
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "code"))

from main import run_pipeline

def generate_baseline():
    print("Running pipeline for baseline metrics...")
    start = time.time()
    run_pipeline()
    end = time.time()
    
    execution_time = end - start
    
    output_file = BASE_DIR / "output.csv"
    
    status_counts = Counter()
    method_counts = Counter()
    
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    for row in rows:
        status_counts[row["affordability_status"]] += 1
        method_counts[row["recommended_payment_method"]] += 1
        
    metrics = {
        "execution_time_seconds": round(execution_time, 2),
        "total_requests": len(rows),
        "status_distribution": dict(status_counts),
        "method_distribution": dict(method_counts)
    }
    
    out_path = BASE_DIR / "evaluation" / "baseline_metrics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(metrics, f, indent=2)
        
    print(f"Baseline generated: {out_path}")
    print(json.dumps(metrics, indent=2))

if __name__ == "__main__":
    generate_baseline()
