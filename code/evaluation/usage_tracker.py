import csv
import json
from pathlib import Path
from datetime import datetime

class UsageTracker:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.log_file = self.base_dir / "evaluation" / "usage_log.csv"
        self.report_file = self.base_dir / "evaluation" / "usage_report.md"
        
        if not self.log_file.exists():
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp", "request_id", "agent", "model", 
                    "input_tokens", "output_tokens", "estimated_cost_cents"
                ])
                
    def log(self, request_id: str, agent: str, model: str, input_tokens: int, output_tokens: int, cost_cents: float = 0.0):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.utcnow().isoformat(), request_id, agent, model,
                input_tokens, output_tokens, cost_cents
            ])
            
    def generate_report(self):
        if not self.log_file.exists():
            return
            
        total_calls = 0
        total_input = 0
        total_output = 0
        agents = {}
        
        with open(self.log_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                total_calls += 1
                i_tok = int(row["input_tokens"])
                o_tok = int(row["output_tokens"])
                total_input += i_tok
                total_output += o_tok
                
                agent = row["agent"]
                if agent not in agents:
                    agents[agent] = 0
                agents[agent] += (i_tok + o_tok)
                
        md = [
            "# AI Usage Report\n",
            f"- **Total API Calls**: {total_calls}",
            f"- **Total Input Tokens**: {total_input}",
            f"- **Total Output Tokens**: {total_output}",
            f"- **Total Tokens**: {total_input + total_output}\n",
            "## By Agent"
        ]
        
        for k, v in agents.items():
            md.append(f"- **{k}**: {v} tokens")
            
        with open(self.report_file, 'w') as f:
            f.write("\n".join(md))
            
        print(f"Generated {self.report_file}")
