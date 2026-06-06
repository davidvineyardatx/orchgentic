from pathlib import Path
from datetime import datetime
class RunLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir); self.log_dir.mkdir(parents=True, exist_ok=True)
    def write(self, run_id, section, content):
        with open(self.log_dir / f"run_{run_id}.log", "a", encoding="utf-8") as f:
            f.write(f"\n[{datetime.utcnow().isoformat()}] {section}\n{str(content).rstrip()}\n")
