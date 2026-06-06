from .storage import SQLiteMemoryStorage
class MemoryManager:
    def __init__(self, db_path="memory/orchgentic.db"): self.storage = SQLiteMemoryStorage(db_path)
    def save_user_message(self, agent_id, content): self.storage.save_conversation(agent_id, "user", content)
    def save_agent_message(self, agent_id, content): self.storage.save_conversation(agent_id, "agent", content)
    def save_episode(self, agent_id, task, response, status="completed"): self.storage.save_episode(agent_id, task, response, status)
    def recent_context(self, agent_id, limit=10):
        return "\n".join([f"{role}: {content}" for _,_,role,content,_ in self.storage.recent_conversation(agent_id, limit)])
    def list_recent(self, agent_id, limit=50): return self.storage.list_conversation(agent_id, limit)
    def search(self, query, agent_id, limit=25): return self.storage.search_conversation(query, agent_id, limit)
    def clear(self, agent_id): self.storage.clear(agent_id)
