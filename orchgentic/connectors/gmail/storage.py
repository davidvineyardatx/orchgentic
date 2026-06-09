from pathlib import Path
import json, shutil
BASE_DIR = Path.home() / ".orchgentic" / "oauth" / "gmail"
def _safe(name="default"): return (name or "default").strip().replace("/","-").replace("\\","-")
def connection_dir(name="default"):
    p=BASE_DIR/_safe(name); p.mkdir(parents=True,exist_ok=True); return p
def token_path(name="default"): return connection_dir(name)/"token.json"
def credentials_path(name="default"): return connection_dir(name)/"credentials.json"
def account_path(name="default"): return connection_dir(name)/"account.json"
def list_connections():
    return sorted([p.name for p in BASE_DIR.iterdir() if p.is_dir()]) if BASE_DIR.exists() else []
def save_account(name,email,scopes):
    account_path(name).write_text(json.dumps({"name":name,"email":email,"scopes":scopes},indent=2),encoding="utf-8")
def read_account(name):
    p=account_path(name)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
def delete_connection(name):
    p=BASE_DIR/_safe(name)
    if p.exists(): shutil.rmtree(p); return True
    return False
