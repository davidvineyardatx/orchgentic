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
from orchgentic.runtime.execution_policy import classify_routing_execution_policy


class AssistantAgent:
    def __init__(self, config, provider, planner=None, reflector=None, logger=None, memory=None, knowledge=None, tool_registry=None):
        self.config=config; self.provider=provider; self.planner=planner or Planner(); self.reflector=reflector or Reflector(); self.logger=logger or RunLogger(); self.memory=memory or MemoryManager(config.memory.db_path); self.knowledge=knowledge or KnowledgeManager(provider, config.knowledge.store, config.knowledge.db_path, config.knowledge.collection); self.tool_registry=tool_registry or default_tool_registry(self.memory, self.knowledge, source_agent_config=self.config)

    def _allowed_tools(self):
        return sorted(set(list(self.config.tools or []) + [c for c in self.config.capabilities if '.' in c]))

    def _trace_context(self, identity: AgentIdentity, task: str, metadata: dict) -> dict:
        return {
            "agent_id": identity.id,
            "agent_name": identity.name,
            "agent_role": identity.role,
            "team": metadata.get("team"),
            "team_role": metadata.get("role"),
            "memory_policy": metadata.get("memory_policy"),
            "task_preview": (task or "")[:220],
        }

    def _llm_trace_message(self, identity: AgentIdentity, metadata: dict, purpose: str, task: str | None = None) -> str:
        task_preview = (task or "the task").strip()[:220]
        team = metadata.get("team")
        role = str(metadata.get("role") or "").lower()
        if team and role == "orchestrator":
            return f"{identity.name} used the LLM as team orchestrator to plan member contributions for: {task_preview}."
        if team and role == "synthesis":
            return f"{identity.name} used the LLM during team synthesis to combine member outputs into the final response for: {task_preview}."
        if "research" in identity.name.lower():
            return f"{identity.name} used the LLM to produce research-oriented output and identify verifiable information related to: {task_preview}."
        if "writer" in identity.name.lower():
            return f"{identity.name} used the LLM to draft clear content from the available context for: {task_preview}."
        if "review" in identity.name.lower():
            return f"{identity.name} used the LLM to review quality, clarity, and completeness for: {task_preview}."
        return f"{identity.name} used the LLM for {purpose} while working on: {task_preview}."

    def _llm_cost_classification(self, identity: AgentIdentity, metadata: dict, purpose: str) -> dict:
        """Classify an LLM call for Token Intelligence optimization reporting."""
        team_role = str(metadata.get("team_role") or metadata.get("role") or "").lower()
        agent_name = (identity.name or "").lower()
        if team_role == "synthesis" or purpose == "team_synthesis":
            return {
                "execution_tier": "premium_external_candidate",
                "recommended_execution_tier": "premium_external_or_configurable",
                "local_llm_eligible": False,
                "optimization_opportunity": "keep_external_or_make_configurable",
                "optimization_reason": "Final team synthesis is high-value output work; keep on an external LLM by default, but allow configuration later.",
            }
        if team_role in {"member", "researcher", "writer", "reviewer"} or any(marker in agent_name for marker in ["research", "writer", "review"]):
            return {
                "execution_tier": "local_llm_candidate",
                "recommended_execution_tier": "local_llm",
                "local_llm_eligible": True,
                "optimization_opportunity": "move_to_local_llm",
                "optimization_reason": "Team member generation/review is a strong local LLM candidate; reserve external LLMs for premium synthesis or hard reasoning.",
            }
        return {
            "execution_tier": "external_llm",
            "recommended_execution_tier": "external_llm",
            "local_llm_eligible": False,
            "optimization_opportunity": "monitor",
            "optimization_reason": "No local LLM eligibility rule matched this LLM call yet.",
        }

    async def run(self, task, *, show_plan=False, debug=False, reflection=True, metadata=None, tracer=None):
        run=RunState(run_id=(tracer.run_id if tracer and tracer.run_id else str(uuid.uuid4())), status=RunStatus.RUNNING); identity=AgentIdentity(self.config.id,self.config.name,self.config.role,self.config.description); metadata=metadata or {}
        agent_started = time.perf_counter()
        trace_context = self._trace_context(identity, task, metadata)
        llm_cost_classification = self._llm_cost_classification(identity, metadata, 'final_answer_generation')
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
            execution_policy_decision = classify_routing_execution_policy(
                task,
                self.config,
                escalation=preflight.escalation,
            )
            self.logger.write(run.run_id, 'EXECUTION_POLICY', execution_policy_decision)
            if tracer:
                tracer.event(
                    'execution_policy.classified',
                    component='policy',
                    name=execution_policy_decision.get('policy_action'),
                    status='completed',
                    message=execution_policy_decision.get('reason'),
                    data=execution_policy_decision,
                    token_source='not_applicable',
                )
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
            tool_decision_policy = str(metadata.get('tool_decision_policy') or '').lower()
            skip_tool_decision = tool_decision_policy == 'skip'
            if tracer and skip_tool_decision:
                skipped_iterations = metadata.get('estimated_tool_decision_iterations_saved') or 1
                try:
                    skipped_iterations = max(1, int(skipped_iterations))
                except Exception:
                    skipped_iterations = 1
                base_tool_decision_estimate = estimate_tokens(messages) + 300
                routing_event_name = metadata.get('tool_decision_policy_event_name') or 'deterministic_tool_decision_policy'
                tracer.event(
                    'routing.bypassed',
                    component='routing',
                    name=routing_event_name,
                    status='completed',
                    message='Team role policy skipped external LLM tool-decision planning.',
                    estimated_tokens_saved=base_tool_decision_estimate * skipped_iterations,
                    token_source='estimated',
                    data={
                        **trace_context,
                        'routing_mode': routing_event_name,
                        'savings_reason': 'team_role_policy_bypassed_tool_decision_llm',
                        'reason': metadata.get('tool_decision_policy_reason') or 'Tool-decision LLM call skipped by team role policy.',
                        'local_llm_eligible': True,
                        'external_llm_avoided': True,
                        'tool_decision_policy': tool_decision_policy,
                        'estimated_tool_decision_iterations_saved': skipped_iterations,
                        'estimated_tokens_saved_per_iteration': base_tool_decision_estimate,
                    },
                )
            if self.config.tool_runtime.enabled and not skip_tool_decision:
                runtime=ToolRuntime(
                    self.tool_registry,
                    allowed_tools=self._allowed_tools(),
                    max_iterations=self.config.tool_runtime.max_iterations,
                    timeout_seconds=self.config.tool_runtime.timeout_seconds,
                    tracer=tracer,
                    trace_context=trace_context,
                )
                answer, tool_observations = await runtime.run_loop(self.provider,messages,debug=debug)
                if tool_observations: self.logger.write(run.run_id,'TOOL_OBSERVATIONS',tool_observations)
            else:
                llm_started = time.perf_counter()
                if tracer:
                    tracer.event(
                        'llm.started',
                        component='provider',
                        name=getattr(self.provider, '__class__', type(self.provider)).__name__,
                        status='started',
                        message=self._llm_trace_message(identity, metadata, 'final_answer_generation', task),
                        data={
                            **trace_context,
                            'provider': getattr(self.config.provider, 'type', None),
                            'model': getattr(self.config.provider, 'model', None),
                            'llm_purpose': 'final_answer_generation',
                            'token_work_reason': self._llm_trace_message(identity, metadata, 'final_answer_generation', task),
                            'reason': self._llm_trace_message(identity, metadata, 'final_answer_generation', task),
                            'token_kind': 'tokens_used',
                            'token_count_source_reason': 'estimated because provider usage metadata is not available in this runtime path',
                            **llm_cost_classification,
                        },
                    )
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
                        message=self._llm_trace_message(identity, metadata, 'final_answer_generation', task),
                        data={
                            **trace_context,
                            'model': getattr(self.config.provider, 'model', None),
                            'provider': getattr(self.config.provider, 'type', None),
                            'llm_purpose': 'final_answer_generation',
                            'token_work_reason': self._llm_trace_message(identity, metadata, 'final_answer_generation', task),
                            'reason': self._llm_trace_message(identity, metadata, 'final_answer_generation', task),
                            'token_kind': 'tokens_used',
                            'token_count_source_reason': 'estimated because provider usage metadata is not available in this runtime path',
                            **llm_cost_classification,
                        },
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
