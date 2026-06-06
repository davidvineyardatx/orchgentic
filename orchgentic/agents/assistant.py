import uuid
from orchgentic.core.enums import RunStatus
from orchgentic.core.models import AgentIdentity, RunState
from orchgentic.planning.planner import Planner
from orchgentic.reflection.reflector import Reflector
from orchgentic.logging.run_logger import RunLogger
from orchgentic.memory.manager import MemoryManager
from orchgentic.knowledge.manager import KnowledgeManager
from orchgentic.tools.registry import default_tool_registry
from orchgentic.tools.runtime import ToolRuntime
class AssistantAgent:
    def __init__(self, config, provider, planner=None, reflector=None, logger=None, memory=None, knowledge=None, tool_registry=None):
        self.config=config; self.provider=provider; self.planner=planner or Planner(); self.reflector=reflector or Reflector(); self.logger=logger or RunLogger(); self.memory=memory or MemoryManager(config.memory.db_path); self.knowledge=knowledge or KnowledgeManager(provider, config.knowledge.store, config.knowledge.db_path, config.knowledge.collection); self.tool_registry=tool_registry or default_tool_registry(self.memory, self.knowledge, source_agent_config=self.config)
    def _allowed_tools(self):
        return sorted(set(list(self.config.tools or []) + [c for c in self.config.capabilities if '.' in c]))
    async def run(self, task, *, show_plan=False, debug=False, reflection=True, metadata=None):
        run=RunState(run_id=str(uuid.uuid4()), status=RunStatus.RUNNING); identity=AgentIdentity(self.config.id,self.config.name,self.config.role,self.config.description); metadata=metadata or {}
        self.logger.write(run.run_id,'TASK',task)
        if metadata: self.logger.write(run.run_id,'METADATA',metadata)
        memory_context = self.memory.recent_context(identity.id,self.config.memory.recent_messages) if self.config.memory.enabled else ''
        if memory_context: self.logger.write(run.run_id,'MEMORY_CONTEXT',memory_context)
        knowledge_context = await self.knowledge.context_for_query(task,self.config.knowledge.top_k) if self.config.knowledge.enabled else ''
        if knowledge_context: self.logger.write(run.run_id,'KNOWLEDGE_CONTEXT',knowledge_context)
        plan = await self.planner.create_plan(task) if self.config.reasoning.planner else None
        if plan: run.planner_steps=len(plan.steps); self.logger.write(run.run_id,'PLAN',plan.to_text())
        system=f"You are {identity.name}, a {identity.role}.\n{self.config.instructions}\nAnswer clearly and helpfully."
        if memory_context: system += '\n\nRecent memory:\n' + memory_context
        if knowledge_context: system += '\n\nRelevant knowledge:\n' + knowledge_context
        if metadata: system += '\n\nTrigger/context metadata:\n' + str(metadata)
        if plan: system += '\n\nPlan:\n' + plan.to_text()
        messages=[{'role':'system','content':system},{'role':'user','content':task}]
        tool_observations=[]
        if self.config.tool_runtime.enabled:
            runtime=ToolRuntime(self.tool_registry, allowed_tools=self._allowed_tools(), max_iterations=self.config.tool_runtime.max_iterations, timeout_seconds=self.config.tool_runtime.timeout_seconds)
            answer, tool_observations = await runtime.run_loop(self.provider,messages,debug=debug)
            if tool_observations: self.logger.write(run.run_id,'TOOL_OBSERVATIONS',tool_observations)
        else:
            answer = await self.provider.generate(messages)
        self.logger.write(run.run_id,'ANSWER',answer)
        ref=None
        if reflection and self.config.reasoning.reflection:
            ref=await self.reflector.reflect(task,answer); run.reflection_count += 1; self.logger.write(run.run_id,'REFLECTION',ref.to_text())
        if self.config.memory.enabled:
            self.memory.save_user_message(identity.id,task); self.memory.save_agent_message(identity.id,answer); self.memory.save_episode(identity.id,task,answer)
            if self.config.tool_runtime.save_results_to_memory and tool_observations: self.memory.save_agent_message(identity.id, f'Tool observations: {tool_observations}')
        run.complete()
        if debug:
            parts=[f'RUN ID\n{run.run_id}']
            if memory_context: parts.append(f'MEMORY\n{memory_context}')
            if knowledge_context: parts.append(f'KNOWLEDGE\n{knowledge_context}')
            if plan: parts.append(f'PLAN\n{plan.to_text()}')
            if tool_observations: parts.append(f'TOOLS\n{tool_observations}')
            parts.append(f'ANSWER\n{answer}')
            if ref: parts.append(f'REFLECTION\n{ref.to_text()}')
            return '\n\n'.join(parts)
        if show_plan and plan: return f'PLAN\n{plan.to_text()}\n\nANSWER\n{answer}'
        return answer
