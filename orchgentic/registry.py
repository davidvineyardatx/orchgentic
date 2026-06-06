class Registry:
    def __init__(self):
        self.items = {}

    def register(self, name: str, obj):
        self.items[name.lower()] = obj

    def get(self, name: str):
        return self.items.get(name.lower())

    def list(self):
        return sorted(self.items.keys())
