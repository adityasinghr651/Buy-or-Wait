import sys
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR / "code"))

import config
# Override requests file to run on sample_requests
config.REQUESTS_FILE = BASE_DIR / "sample_requests.csv"
config.OUTPUT_FILE = BASE_DIR / "evaluation" / "sample_output.csv"

from main import run_pipeline

def run_scoring():
    print("Running pipeline on sample_requests.csv...")
    run_pipeline()
    
    ground_truth_file = BASE_DIR / "sample_requests.csv"
    output_file = config.OUTPUT_FILE
    
    truth = {}
    with open(ground_truth_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            truth[row["request_id"]] = row
            
    outputs = {}
    with open(output_file, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            outputs[row["request_id"]] = row
            
    fields = [
        "affordability_status",
        "recommended_payment_method",
        "earliest_date_for_full_payment"
    ]
    
    scores = {f: {"correct": 0, "total": 0} for f in fields}
    
    for req_id, true_row in truth.items():
        if req_id not in outputs:
            continue
            
        out_row = outputs[req_id]
        
        for f in fields:
            scores[f]["total"] += 1
            out_val = str(out_row[f]).strip()
            true_val = str(true_row[f]).strip()
            if out_val == true_val:
                scores[f]["correct"] += 1
            else:
                print(f"[{req_id}] Mismatch in {f}: Expected '{true_val}', Got '{out_val}'")
                
    # Output report
    print("\n=== SCORING REPORT (Against sample_requests.csv) ===")
    for f in fields:
        correct = scores[f]["correct"]
        total = scores[f]["total"]
        if total > 0:
            print(f"{f}: {correct}/{total} ({correct/total*100:.1f}%)")

if __name__ == "__main__":
    run_scoring()
