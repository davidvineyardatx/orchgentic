from pydantic import BaseModel, Field
class ProviderConfig(BaseModel):
    type: str = "lmstudio"
    model: str = "qwen3"
class ReasoningConfig(BaseModel):
    planner: bool = True
    reflection: bool = True
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
