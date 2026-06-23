from pydantic import BaseModel, Field
class ProviderConfig(BaseModel):
    type: str = "lmstudio"
    model: str = "qwen3"
class EscalationConfig(BaseModel):
    enabled: bool = True
    min_confidence: float = 0.52

class ReasoningConfig(BaseModel):
    planner: bool = True
    reflection: bool = True
    local_reasoner: bool = True
    confidence_scoring: bool = True
    confidence_high_threshold: float = 0.78
    confidence_low_threshold: float = 0.52
    escalation: EscalationConfig = Field(default_factory=EscalationConfig)

class WorkflowRoutingConfig(BaseModel):
    enabled: bool = True
    multi_step_threshold: float = 0.80

class EventRoutingConfig(BaseModel):
    enabled: bool = True
    autonomous_events_require_policy_checks: bool = True

class PolicyRoutingConfig(BaseModel):
    enabled: bool = True
    block_disabled_tools_before_llm: bool = True
    hold_confirmation_tools_before_llm: bool = True

class RoutingConfig(BaseModel):
    workflow: WorkflowRoutingConfig = Field(default_factory=WorkflowRoutingConfig)
    event: EventRoutingConfig = Field(default_factory=EventRoutingConfig)
    policy: PolicyRoutingConfig = Field(default_factory=PolicyRoutingConfig)

class DeterministicExecutionConfig(BaseModel):
    enabled: bool = True

class LocalReasoningExecutionConfig(BaseModel):
    enabled: bool = True

class LocalLLMExecutionConfig(BaseModel):
    enabled: bool = False
    eligible_for: list[str] = Field(
        default_factory=lambda: [
            "classification",
            "routing",
            "summarization",
            "review",
        ]
    )

class ExternalLLMExecutionConfig(BaseModel):
    enabled: bool = True
    require_for: list[str] = Field(
        default_factory=lambda: [
            "complex_generation",
            "high_uncertainty_reasoning",
        ]
    )

class PremiumModelExecutionConfig(BaseModel):
    enabled: bool = True
    require_for: list[str] = Field(
        default_factory=lambda: [
            "final_synthesis",
            "executive_output",
            "high_quality_final",
        ]
    )

class ExecutionPolicyConfig(BaseModel):
    enabled: bool = True
    default_mode: str = "external_llm_when_needed"
    deterministic: DeterministicExecutionConfig = Field(default_factory=DeterministicExecutionConfig)
    local_reasoning: LocalReasoningExecutionConfig = Field(default_factory=LocalReasoningExecutionConfig)
    local_llm: LocalLLMExecutionConfig = Field(default_factory=LocalLLMExecutionConfig)
    external_llm: ExternalLLMExecutionConfig = Field(default_factory=ExternalLLMExecutionConfig)
    premium_model: PremiumModelExecutionConfig = Field(default_factory=PremiumModelExecutionConfig)

class MemoryConfig(BaseModel):
    enabled: bool = True
    recent_messages: int = 10
    db_path: str = "memory/orchgentic.db"
class KnowledgeConfig(BaseModel):
    enabled: bool = True
    top_k: int = 5
    store: str = "local"
    db_path: str = "memory/orchgentic.db"
    collection: str = "orchgentic_knowledge"
class ToolRuntimeConfig(BaseModel):
    enabled: bool = True
    max_iterations: int = 4
    timeout_seconds: int = 90
    allow_parallel: bool = False
    save_results_to_memory: bool = False
class DelegationConfig(BaseModel):
    enabled: bool = False
    allowed_agents: list[str] = Field(default_factory=list)
    max_depth: int = 2
class AgentConfig(BaseModel):
    id: str
    name: str
    role: str = "Assistant"
    description: str = ""
    timezone: str = "UTC"
    locale: str = "en-US"
    instructions: str = "Help the user complete the task."
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    capabilities: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    tool_runtime: ToolRuntimeConfig = Field(default_factory=ToolRuntimeConfig)
    delegation: DelegationConfig = Field(default_factory=DelegationConfig)
    reasoning: ReasoningConfig = Field(default_factory=ReasoningConfig)
    routing: RoutingConfig = Field(default_factory=RoutingConfig)
    execution_policy: ExecutionPolicyConfig = Field(default_factory=ExecutionPolicyConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    knowledge: KnowledgeConfig = Field(default_factory=KnowledgeConfig)
    gmail: dict = Field(default_factory=dict)
    tool_policies: dict = Field(default_factory=dict)
class TriggerConfig(BaseModel):
    id: str
    type: str
    target_agent: str
    enabled: bool = True
    task: str
    interval_seconds: int = 60
    path: str | None = None
class TeamConfig(BaseModel):
    name: str
    description: str = ""
    timezone: str = "UTC"
    locale: str = "en-US"
    orchestrator: str
    members: list[str] = Field(default_factory=list)
    shared_context: bool = True
    max_rounds: int = 3
    task: str = "Coordinate the team to complete the requested task."
    execution_policy: ExecutionPolicyConfig = Field(default_factory=ExecutionPolicyConfig)
