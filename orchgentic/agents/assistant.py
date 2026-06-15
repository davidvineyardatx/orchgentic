import uuid
import time
from orchgentic.core.enums import RunStatus
from orchgentic.core.models import AgentIdentity, RunState
from orchgentic.planning.planner import Planner
from orchgentic.reflection.reflector import Reflector
from orchgentic.logging.run_logger import RunLogger
from orchgentic.memory.manager import MemoryManager
from orchgentic.knowledge.manager import KnowledgeManager
from orchgentic.tools.registry import default_tool_registry
from orchgentic.tools.runtime import ToolRuntime
from orchgentic.core.reasoning.runtime_hooks import preflight_reasoning
from orchgentic.runtime.token_estimator import estimate_tokens


class AssistantAgent:
    def __init__(self, config, provider, planner=None, reflector=None, logger=None, memory=None, knowledge=None, tool_registry=None):
        self.config=config; self.provider=provider; self.planner=planner or Planner(); self.reflector=reflector or Reflector(); self.logger=logger or RunLogger(); self.memory=memory or MemoryManager(config.memory.db_path); self.knowledge=knowledge or KnowledgeManager(provider, config.knowledge.store, config.knowledge.db_path, config.knowledge.collection); self.tool_registry=tool_registry or default_tool_registry(self.memory, self.knowledge, source_agent_config=self.config)

    def _allowed_tools(self):
        return sorted(set(list(self.config.tools or []) + [c for c in self.config.capabilities if '.' in c]))

    async def run(self, task, *, show_plan=False, debug=False, reflection=True, metadata=None, tracer=None):
        run=RunState(run_id=(tracer.run_id if tracer and tracer.run_id else str(uuid.uuid4())), status=RunStatus.RUNNING); identity=AgentIdentity(self.config.id,self.config.name,self.config.role,self.config.description); metadata=metadata or {}
        agent_started = time.perf_counter()
        if tracer:
            tracer.event(
                'agent.started',
                component='agent',
                name=identity.name,
                status='started',
                message='Agent execution started.',
                data={'agent_id': identity.id, 'role': identity.role, 'metadata': metadata},
            )
        try:
            self.logger.write(run.run_id,'TASK',task)
            if metadata: self.logger.write(run.run_id,'METADATA',metadata)
            config_map = self.config.model_dump() if hasattr(self.config, 'model_dump') else self.config.dict()
            reasoning_started = time.perf_counter()
            preflight = preflight_reasoning(task, agent_config=config_map, available_tools=self._allowed_tools())
            if tracer:
                tracer.event(
                    'reasoning.completed',
                    component='reasoning',
                    name='preflight_reasoning',
                    status='completed',
                    message='Local reasoning completed.',
                    duration_ms=round((time.perf_counter() - reasoning_started) * 1000, 2),
                    data={
                        'local_decision': preflight.local_result.decision.value,
                        'local_confidence': preflight.local_result.confidence,
                        'confidence_score': preflight.confidence.score,
                        'confidence_band': preflight.confidence.band.value,
                        'escalation_action': preflight.escalation.action.value,
                        'escalation_reason': preflight.escalation.reason,
                        'suggested_tools': preflight.local_result.suggested_tools,
                    },
                    token_source='not_applicable',
                )
            self.logger.write(run.run_id,'PREFLIGHT_REASONING',{
                'local_decision': preflight.local_result.decision.value,
                'local_confidence': preflight.local_result.confidence,
                'confidence_score': preflight.confidence.score,
                'confidence_band': preflight.confidence.band.value,
                'escalation_action': preflight.escalation.action.value,
                'escalation_reason': preflight.escalation.reason,
                'suggested_tools': preflight.local_result.suggested_tools,
            })
            if preflight.local_result.local_answer and not preflight.escalation.should_call_llm:
                answer = preflight.local_result.local_answer
                self.logger.write(run.run_id,'ANSWER',answer)
                if tracer:
                    tracer.event(
                        'agent.completed',
                        component='agent',
                        name=identity.name,
                        status='completed',
                        message='Agent completed with local answer.',
                        duration_ms=round((time.perf_counter() - agent_started) * 1000, 2),
                        data={'local_answer': True},
                    )
                run.complete()
                return answer
            if preflight.escalation.action.value == 'stop_with_error':
                raise RuntimeError(preflight.escalation.reason)
            # Team orchestration prompts already carry explicit shared context.
            # Pulling unrelated historical memory into team roles/synthesis can contaminate final outputs.
            use_memory_context = self.config.memory.enabled and not metadata.get('team')
            memory_context = self.memory.recent_context(identity.id,self.config.memory.recent_messages) if use_memory_context else ''
            if memory_context:
                self.logger.write(run.run_id,'MEMORY_CONTEXT',memory_context)
                if tracer:
                    tracer.event('memory.context_loaded', component='memory', name=identity.id, status='completed', data={'tokens_estimated': estimate_tokens(memory_context)}, token_source='estimated')
            knowledge_started = time.perf_counter()
            knowledge_context = await self.knowledge.context_for_query(task,self.config.knowledge.top_k) if self.config.knowledge.enabled else ''
            if knowledge_context:
                self.logger.write(run.run_id,'KNOWLEDGE_CONTEXT',knowledge_context)
                if tracer:
                    tracer.event(
                        'knowledge.context_loaded',
                        component='knowledge',
                        name='knowledge.search',
                        status='completed',
                        duration_ms=round((time.perf_counter() - knowledge_started) * 1000, 2),
                        data={'tokens_estimated': estimate_tokens(knowledge_context), 'top_k': self.config.knowledge.top_k},
                        token_source='estimated',
                    )
            plan_started = time.perf_counter()
            plan = await self.planner.create_plan(task) if self.config.reasoning.planner else None
            if plan:
                run.planner_steps=len(plan.steps); self.logger.write(run.run_id,'PLAN',plan.to_text())
                if tracer:
                    tracer.event(
                        'planning.completed',
                        component='planning',
                        name='planner',
                        status='completed',
                        duration_ms=round((time.perf_counter() - plan_started) * 1000, 2),
                        data={'steps': len(plan.steps)},
                    )
            system=f"You are {identity.name}, a {identity.role}.\n{self.config.instructions}\nAnswer clearly and helpfully."
            if memory_context: system += '\n\nRecent memory:\n' + memory_context
            if knowledge_context: system += '\n\nRelevant knowledge:\n' + knowledge_context
            if metadata: system += '\n\nTrigger/context metadata:\n' + str(metadata)
            if plan: system += '\n\nPlan:\n' + plan.to_text()
            messages=[{'role':'system','content':system},{'role':'user','content':task}]
            tool_observations=[]
            if self.config.tool_runtime.enabled:
                runtime=ToolRuntime(self.tool_registry, allowed_tools=self._allowed_tools(), max_iterations=self.config.tool_runtime.max_iterations, timeout_seconds=self.config.tool_runtime.timeout_seconds, tracer=tracer)
                answer, tool_observations = await runtime.run_loop(self.provider,messages,debug=debug)
                if tool_observations: self.logger.write(run.run_id,'TOOL_OBSERVATIONS',tool_observations)
            else:
                llm_started = time.perf_counter()
                if tracer:
                    tracer.event('llm.started', component='provider', name=getattr(self.provider, '__class__', type(self.provider)).__name__, status='started', data={'provider': getattr(self.config.provider, 'type', None), 'model': getattr(self.config.provider, 'model', None)})
                answer = await self.provider.generate(messages)
                if tracer:
                    tracer.event(
                        'llm.completed',
                        component='provider',
                        name=getattr(self.config.provider, 'type', None),
                        status='completed',
                        duration_ms=round((time.perf_counter() - llm_started) * 1000, 2),
                        input_tokens=estimate_tokens(messages),
                        output_tokens=estimate_tokens(answer),
                        token_source='estimated',
                        data={'model': getattr(self.config.provider, 'model', None)},
                    )
            self.logger.write(run.run_id,'ANSWER',answer)
            ref=None
            if reflection and self.config.reasoning.reflection:
                reflection_started = time.perf_counter()
                ref=await self.reflector.reflect(task,answer); run.reflection_count += 1; self.logger.write(run.run_id,'REFLECTION',ref.to_text())
                if tracer:
                    tracer.event(
                        'reflection.completed',
                        component='reflection',
                        name='reflector',
                        status='completed',
                        duration_ms=round((time.perf_counter() - reflection_started) * 1000, 2),
                        data={'reflection_count': run.reflection_count},
                    )
            if self.config.memory.enabled:
                self.memory.save_user_message(identity.id,task); self.memory.save_agent_message(identity.id,answer); self.memory.save_episode(identity.id,task,answer)
                if self.config.tool_runtime.save_results_to_memory and tool_observations: self.memory.save_agent_message(identity.id, f'Tool observations: {tool_observations}')
            run.complete()
            if tracer:
                tracer.event(
                    'agent.completed',
                    component='agent',
                    name=identity.name,
                    status='completed',
                    message='Agent execution completed.',
                    duration_ms=round((time.perf_counter() - agent_started) * 1000, 2),
                    data={'planner_steps': run.planner_steps, 'reflection_count': run.reflection_count, 'tool_observations': len(tool_observations)},
                )
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
        except Exception as exc:
            run.fail()
            if tracer:
                tracer.event(
                    'agent.failed',
                    component='agent',
                    name=identity.name,
                    status='failed',
                    message=str(exc),
                    duration_ms=round((time.perf_counter() - agent_started) * 1000, 2),
                    data={'error_type': type(exc).__name__},
                )
            raise
