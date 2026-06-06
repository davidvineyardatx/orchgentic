from pathlib import Path
import sqlite3
from datetime import datetime
class SQLiteMemoryStorage:
    def __init__(self, db_path="memory/orchgentic.db"):
        self.db_path = Path(db_path); self.db_path.parent.mkdir(parents=True, exist_ok=True); self._init()
    def _connect(self): return sqlite3.connect(self.db_path)
    def _init(self):
        with self._connect() as c:
            c.execute("CREATE TABLE IF NOT EXISTS conversation_memory(id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, role TEXT, content TEXT, timestamp TEXT)")
            c.execute("CREATE TABLE IF NOT EXISTS episodic_memory(id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id TEXT, task TEXT, response TEXT, status TEXT, timestamp TEXT)")
            c.commit()
    def save_conversation(self, agent_id, role, content):
        with self._connect() as c:
            c.execute("INSERT INTO conversation_memory(agent_id,role,content,timestamp) VALUES(?,?,?,?)", (agent_id, role, content, datetime.utcnow().isoformat())); c.commit()
    def recent_conversation(self, agent_id, limit=10):
        with self._connect() as c:
            rows=c.execute("SELECT id,agent_id,role,content,timestamp FROM conversation_memory WHERE agent_id=? ORDER BY id DESC LIMIT ?", (agent_id, limit)).fetchall()
        return list(reversed(rows))
    def list_conversation(self, agent_id, limit=50):
        with self._connect() as c:
            return c.execute("SELECT id,agent_id,role,content,timestamp FROM conversation_memory WHERE agent_id=? ORDER BY id DESC LIMIT ?", (agent_id, limit)).fetchall()
    def search_conversation(self, query, agent_id, limit=25):
        with self._connect() as c:
            return c.execute("SELECT id,agent_id,role,content,timestamp FROM conversation_memory WHERE agent_id=? AND content LIKE ? ORDER BY id DESC LIMIT ?", (agent_id, f'%{query}%', limit)).fetchall()
    def save_episode(self, agent_id, task, response, status):
        with self._connect() as c:
            c.execute("INSERT INTO episodic_memory(agent_id,task,response,status,timestamp) VALUES(?,?,?,?,?)", (agent_id, task, response, status, datetime.utcnow().isoformat())); c.commit()
    def clear(self, agent_id):
        with self._connect() as c:
            c.execute("DELETE FROM conversation_memory WHERE agent_id=?", (agent_id,)); c.execute("DELETE FROM episodic_memory WHERE agent_id=?", (agent_id,)); c.commit()
