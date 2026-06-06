from .models import ReflectionResult
class Reflector:
    async def reflect(self, task, answer):
        if not answer or not answer.strip(): return ReflectionResult(False, 0.1, ["Answer was empty."])
        return ReflectionResult(True, 0.9, [])
