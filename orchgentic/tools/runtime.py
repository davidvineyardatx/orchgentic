import asyncio
import json
from orchgentic.core.exceptions import ToolError, PermissionError
from orchgentic.tools.schemas import ToolCall, ToolResult
from orchgentic.runtime.token_estimator import estimate_tokens
import time

class ToolRuntime:
    def __init__(self, registry, allowed_tools=None, max_iterations: int = 4, timeout_seconds: int = 90, tracer=None, trace_context: dict | None = None):
        self.registry = registry
        self.allowed_tools = [tool.lower() for tool in (allowed_tools or [])]
        self.max_iterations = max_iterations
        self.timeout_seconds = timeout_seconds
        self.tracer = tracer
        self.trace_context = trace_context or {}

    def _tool_names_for_reason(self, tools: list[dict] | None = None) -> list[str]:
        names = []
        for item in tools or []:
            if isinstance(item, dict):
                name = item.get("name") or item.get("tool")
                if not name and isinstance(item.get("function"), dict):
                    name = item["function"].get("name")
                if name:
                    names.append(str(name))
        return sorted(set(names))

    def _agent_label(self) -> str:
        return self.trace_context.get("agent_name") or self.trace_context.get("agent_id") or "Agent"

    def _team_scope_label(self) -> str:
        team = self.trace_context.get("team")
        role = self.trace_context.get("team_role") or self.trace_context.get("role")
        parts = []
        if team:
            parts.append(f"team {team}")
        if role:
            parts.append(str(role))
        return " / ".join(parts)

    def _token_work_reason(self, purpose: str, *, iteration: int | None = None, tools: list[dict] | None = None) -> str:
        agent = self._agent_label()
        role = str(self.trace_context.get("team_role") or self.trace_context.get("role") or "").lower()
        task_preview = (self.trace_context.get("task_preview") or "the task").strip()
        tool_names = self._tool_names_for_reason(tools)
        tools_label = ", ".join(tool_names[:5]) if tool_names else "available tools"
        if tool_names and len(tool_names) > 5:
            tools_label += f", +{len(tool_names) - 5} more"
        iteration_suffix = f" Iteration {iteration}." if iteration is not None else ""

        if purpose == "tool_decision":
            if role == "orchestrator":
                return (
                    f"{agent} used the LLM as team orchestrator to plan member contributions and decide "
                    f"whether tools were needed for: {task_preview}.{iteration_suffix}"
                )
            if role == "synthesis":
                return (
                    f"{agent} used the LLM during team synthesis to decide whether another tool call was needed "
                    f"before producing the final response for: {task_preview}.{iteration_suffix}"
                )
            if "research" in agent.lower():
                return (
                    f"{agent} used the LLM to evaluate whether to use {tools_label} to find or verify "
                    f"data related to: {task_preview}.{iteration_suffix}"
                )
            if "writer" in agent.lower():
                return (
                    f"{agent} used the LLM to decide whether tools were needed before drafting content "
                    f"for: {task_preview}.{iteration_suffix}"
                )
            if "review" in agent.lower():
                return (
                    f"{agent} used the LLM to decide whether tools were needed before reviewing quality, clarity, "
                    f"and completeness for: {task_preview}.{iteration_suffix}"
                )
            return (
                f"{agent} used the LLM to choose the next action: call one of {tools_label} or return a final answer "
                f"for: {task_preview}.{iteration_suffix}"
            )

        if purpose == "final_answer_generation":
            return f"{agent} used the LLM to generate the final agent response for: {task_preview}."

        if purpose == "final_after_tool_limit":
            return f"{agent} used the LLM to produce the best final answer after the tool iteration limit was reached for: {task_preview}."

        return f"{agent} used the LLM for {purpose} while working on: {task_preview}."

    def _llm_trace_data(self, purpose: str, *, iteration: int | None = None, tools: list[dict] | None = None, extra: dict | None = None) -> dict:
        token_work_reason = self._token_work_reason(purpose, iteration=iteration, tools=tools)
        data = {
            **self.trace_context,
            "llm_purpose": purpose,
            "token_kind": "tokens_used",
            "token_work_reason": token_work_reason,
            "reason": token_work_reason,
            "token_count_source_reason": "estimated because provider usage metadata is not available in this runtime path",
        }
        tool_names = self._tool_names_for_reason(tools)
        if tool_names:
            data["available_tools"] = tool_names
        if iteration is not None:
            data["iteration"] = iteration
        if extra:
            data.update(extra)
        return data

    def _llm_trace_message(self, purpose: str, *, iteration: int | None = None, tools: list[dict] | None = None) -> str:
        return self._token_work_reason(purpose, iteration=iteration, tools=tools)

    def available_definitions(self):
        return self.registry.definitions(self.allowed_tools or None)

    def _strip_code_fence(self, text: str) -> str:
        cleaned = (text or "").strip()
        if "```" not in cleaned:
            return cleaned
        cleaned = cleaned.replace("```json", "```")
        parts = cleaned.split("```")
        for part in parts:
            candidate = part.strip()
            if candidate.startswith("{") and candidate.endswith("}"):
                return candidate
        return cleaned

    def _candidate_json_objects(self, text: str):
        text = self._strip_code_fence(text)
        candidates = []
        stack = []
        start = None
        in_string = False
        escape = False

        for i, char in enumerate(text):
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue

            if char == "{":
                if not stack:
                    start = i
                stack.append(char)
            elif char == "}":
                if stack:
                    stack.pop()
                    if not stack and start is not None:
                        candidates.append(text[start:i + 1])
                        start = None

        stripped = text.strip()
        if stripped.startswith("{") and stripped.endswith("}"):
            candidates.insert(0, stripped)

        seen = set()
        output = []
        for candidate in candidates:
            if candidate not in seen:
                output.append(candidate)
                seen.add(candidate)
        return output

    def parse_decision(self, text: str):
        cleaned = self._strip_code_fence(text)
        try:
            decision = json.loads(cleaned)
            if isinstance(decision, dict) and decision.get("action") in ["tool", "final"]:
                return decision
        except Exception:
            pass

        for candidate in self._candidate_json_objects(text):
            try:
                decision = json.loads(candidate)
            except Exception:
                continue
            if isinstance(decision, dict) and decision.get("action") in ["tool", "final"]:
                return decision

        return {"action": "final", "answer": text}

    async def execute_tool_call(self, call: ToolCall) -> ToolResult:
        if not call.tool_name:
            return ToolResult(False, "unknown", error="Tool name missing from tool call.")

        tool_name = call.tool_name.lower()
        if self.allowed_tools and tool_name not in self.allowed_tools:
            raise PermissionError(f"Tool not allowed for this agent: {call.tool_name}")

        tool = self.registry.get(tool_name)
        if not tool:
            raise ToolError(f"Tool not found: {call.tool_name}")

        try:
            return await asyncio.wait_for(tool.execute(**call.arguments), timeout=self.timeout_seconds)
        except Exception as exc:
            return ToolResult(False, call.tool_name, error=str(exc))

    async def run_loop(self, provider, messages: list[dict], debug: bool = False):
        observations = []
        tools = self.available_definitions()

        if not tools:
            llm_started = time.perf_counter()
            if self.tracer:
                self.tracer.event("llm.started", component="provider", name="generate", status="started", message=self._llm_trace_message("final_answer_generation"), data=self._llm_trace_data("final_answer_generation", extra={"tool_runtime": False}))
            try:
                answer = await provider.generate(messages)
            except Exception as exc:
                if self.tracer:
                    self.tracer.event(
                        "llm.failed",
                        component="provider",
                        name="generate",
                        status="failed",
                        duration_ms=round((time.perf_counter() - llm_started) * 1000, 2),
                        message=str(exc),
                        data={"error_type": type(exc).__name__, "tool_runtime": False},
                    )
                raise
            if self.tracer:
                self.tracer.event(
                    "llm.completed",
                    component="provider",
                    name="generate",
                    status="completed",
                    duration_ms=round((time.perf_counter() - llm_started) * 1000, 2),
                    input_tokens=estimate_tokens(messages),
                    output_tokens=estimate_tokens(answer),
                    token_source="estimated",
                    message=self._llm_trace_message("final_answer_generation"),
                    data=self._llm_trace_data("final_answer_generation", extra={"tool_runtime": False}),
                )
            return answer, observations

        for iteration in range(self.max_iterations):
            llm_started = time.perf_counter()
            if self.tracer:
                self.tracer.event("llm.started", component="provider", name="tool_decision", status="started", message=self._llm_trace_message("tool_decision", iteration=iteration + 1, tools=tools), data=self._llm_trace_data("tool_decision", iteration=iteration + 1, tools=tools))
            try:
                decision_text = await provider.generate_tool_decision(messages, tools, self.max_iterations)
            except Exception as exc:
                if self.tracer:
                    self.tracer.event(
                        "llm.failed",
                        component="provider",
                        name="tool_decision",
                        status="failed",
                        duration_ms=round((time.perf_counter() - llm_started) * 1000, 2),
                        message=str(exc),
                        data=self._llm_trace_data("tool_decision", iteration=iteration + 1, tools=tools, extra={"error_type": type(exc).__name__}),
                    )
                raise
            if self.tracer:
                self.tracer.event(
                    "llm.completed",
                    component="provider",
                    name="tool_decision",
                    status="completed",
                    duration_ms=round((time.perf_counter() - llm_started) * 1000, 2),
                    input_tokens=estimate_tokens(messages) + estimate_tokens(tools),
                    output_tokens=estimate_tokens(decision_text),
                    token_source="estimated",
                    message=self._llm_trace_message("tool_decision", iteration=iteration + 1, tools=tools),
                    data=self._llm_trace_data("tool_decision", iteration=iteration + 1, tools=tools),
                )
            decision = self.parse_decision(decision_text)

            if decision.get("action") == "tool":
                call = ToolCall(decision.get("tool"), decision.get("arguments", {}) or {})
                tool_started = time.perf_counter()
                if self.tracer:
                    self.tracer.event("tool.started", component="tool", name=call.tool_name, status="started", data={"iteration": iteration + 1, "arguments": call.arguments})
                try:
                    result = await self.execute_tool_call(call)
                except Exception as exc:
                    if self.tracer:
                        self.tracer.event(
                            "tool.failed",
                            component="tool",
                            name=call.tool_name,
                            status="failed",
                            duration_ms=round((time.perf_counter() - tool_started) * 1000, 2),
                            message=str(exc),
                            data={"iteration": iteration + 1, "arguments": call.arguments, "error_type": type(exc).__name__},
                        )
                    raise
                if self.tracer:
                    self.tracer.event(
                        "tool.completed" if result.success else "tool.failed",
                        component="tool",
                        name=call.tool_name,
                        status="completed" if result.success else "failed",
                        duration_ms=round((time.perf_counter() - tool_started) * 1000, 2),
                        message=result.error,
                        data={"iteration": iteration + 1, "arguments": call.arguments, "success": result.success},
                    )

                observation = {
                    "iteration": iteration + 1,
                    "tool": call.tool_name,
                    "arguments": call.arguments,
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                }
                if debug:
                    observation["raw_decision"] = decision_text
                    observation["parsed_action"] = decision

                observations.append(observation)
                messages.append({"role": "assistant", "content": decision_text})
                messages.append({
                    "role": "user",
                    "content": (
                        f"Tool observation for {call.tool_name}: "
                        f"success={result.success}; data={result.data}; error={result.error}. "
                        "Now continue. If the user request is satisfied, respond with a final answer using exactly this JSON format: "
                        '{"action":"final","answer":"your final answer"}'
                    )
                })
                continue

            if decision.get("action") == "final":
                answer = decision.get("answer", "")
                if isinstance(answer, str) and answer.strip():
                    return answer, observations
                return decision_text, observations

            return decision_text, observations

        final_messages = messages + [{
            "role": "user",
            "content": "Tool iteration limit reached. Provide the best final answer using the available observations. Do not call another tool."
        }]
        llm_started = time.perf_counter()
        if self.tracer:
            self.tracer.event("llm.started", component="provider", name="final_after_tool_limit", status="started", message=self._llm_trace_message("final_after_tool_limit"), data=self._llm_trace_data("final_after_tool_limit"))
        try:
            final_answer = await provider.generate(final_messages)
        except Exception as exc:
            if self.tracer:
                self.tracer.event(
                    "llm.failed",
                    component="provider",
                    name="final_after_tool_limit",
                    status="failed",
                    duration_ms=round((time.perf_counter() - llm_started) * 1000, 2),
                    message=str(exc),
                    data=self._llm_trace_data("final_after_tool_limit", extra={"error_type": type(exc).__name__}),
                )
            raise
        if self.tracer:
            self.tracer.event(
                "llm.completed",
                component="provider",
                name="final_after_tool_limit",
                status="completed",
                duration_ms=round((time.perf_counter() - llm_started) * 1000, 2),
                input_tokens=estimate_tokens(final_messages),
                output_tokens=estimate_tokens(final_answer),
                token_source="estimated",
                message=self._llm_trace_message("final_after_tool_limit"),
                data=self._llm_trace_data("final_after_tool_limit"),
            )
        final_decision = self.parse_decision(final_answer)
        if final_decision.get("action") == "final" and final_decision.get("answer"):
            return final_decision["answer"], observations
        return final_answer, observations
