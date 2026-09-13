import csv
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_FILE = BASE_DIR / "output.csv"
REQUESTS_FILE = BASE_DIR / "requests.csv"
AUDIT_OUTPUT = BASE_DIR / "evaluation" / "output_audit.md"

def run_audit():
    if not OUTPUT_FILE.exists():
        print(f"File not found: {OUTPUT_FILE}")
        sys.exit(1)
        
    requests = {}
    with open(REQUESTS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        for r in reader:
            requests[r["request_id"]] = Decimal(r["requested_amount"])
            
    status_counts = Counter()
    method_counts = Counter()
    
    contradictions = 0
    safe_amount_ratios = []
    
    with open(OUTPUT_FILE, 'r') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        
    if not rows:
        print("output.csv is empty")
        sys.exit(1)
        
    for row in rows:
        req_id = row["request_id"]
        safe_amt = Decimal(row["amount_safe_to_pay"])
        status = row["affordability_status"]
        method = row["recommended_payment_method"]
        
        status_counts[status] += 1
        method_counts[method] += 1
        
        req_amt = requests.get(req_id)
        if req_amt:
            if safe_amt > req_amt:
                contradictions += 1
            ratio = float(safe_amt / req_amt)
            safe_amount_ratios.append(ratio)
            
        # Contradiction checks
        if status == "affordable_now" and method != "full_payment":
            contradictions += 1
        if status == "not_affordable" and method != "not_recommended":
            contradictions += 1
            
    # Generate MD
    md = [
        "# Output.csv Audit Report\n",
        "## Distributions",
        "### Affordability Status",
    ]
    for k, v in status_counts.items():
        md.append(f"- **{k}**: {v} ({v/len(rows)*100:.1f}%)")
        
    md.append("\n### Payment Method")
    for k, v in method_counts.items():
        md.append(f"- **{k}**: {v} ({v/len(rows)*100:.1f}%)")
        
    md.append("\n## Mathematical Consistency")
    md.append(f"- **Total Contradictions**: {contradictions}")
    
    if safe_amount_ratios:
        avg_ratio = sum(safe_amount_ratios) / len(safe_amount_ratios)
        md.append(f"- **Average Safe Amount Ratio**: {avg_ratio*100:.1f}% of requested amount")
        
    AUDIT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(AUDIT_OUTPUT, 'w') as f:
        f.write("\n".join(md))
        
    print(f"Audit complete. Wrote {AUDIT_OUTPUT}")

if __name__ == "__main__":
    run_audit()
