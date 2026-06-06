from .models import Plan, PlanStep
class Planner:
    async def create_plan(self, task):
        return Plan(task, [
            PlanStep("step_1", "Understand the request."),
            PlanStep("step_2", "Use available memory/context."),
            PlanStep("step_3", "Generate and review the response.")
        ])
