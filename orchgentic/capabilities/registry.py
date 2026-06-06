class CapabilityRegistry:
    def __init__(self):
        self.capabilities = {
            "filesystem": ["filesystem.read", "filesystem.write"],
            "web": ["web.request"],
            "gmail": ["gmail.read", "gmail.search", "gmail.send"],
            "calendar": ["calendar.read", "calendar.write"],
            "knowledge": ["knowledge.search", "knowledge.ingest"],
            "memory": ["memory.search"],
            "datetime": ["datetime.now"],
        }

    def list(self):
        return sorted(self.capabilities.keys())

    def resolve(self, name):
        return self.capabilities.get(name.lower(), [])
