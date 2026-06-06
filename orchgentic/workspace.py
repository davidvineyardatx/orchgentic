from pathlib import Path
import textwrap

def init_workspace(path='.'):
    p=Path(path)
    for d in ['agents','tools','skills','workflows','triggers','knowledge','logs','memory','teams']:
        (p/d).mkdir(parents=True, exist_ok=True)
    def wf(rel, txt):
        f=p/rel
        if not f.exists():
            f.parent.mkdir(parents=True, exist_ok=True); f.write_text(textwrap.dedent(txt).strip()+'\n', encoding='utf-8')
    common = '''
      reasoning:
        planner: true
        reflection: true
      memory:
        enabled: true
        recent_messages: 10
        db_path: memory/orchgentic.db
      knowledge:
        enabled: true
        top_k: 5
        store: local
        db_path: memory/orchgentic.db
        collection: orchgentic_knowledge
    '''
    wf('agents/bob.yaml', f'''
    agent:
      id: bob
      name: Bob
      role: General Assistant
      description: Local development assistant powered by LM Studio.
      instructions: |
        You are Bob, a helpful local AI assistant. Use memory, knowledge, and tools when relevant.
      provider:
        type: lmstudio
        model: qwen3
      capabilities: [filesystem.read, filesystem.write, web.request, datetime.now, memory.search, knowledge.search]
      tools: [datetime.now, filesystem.read, filesystem.write, web.request, memory.search, knowledge.search]
      tool_runtime: {{enabled: true, max_iterations: 4, timeout_seconds: 90, allow_parallel: false, save_results_to_memory: false}}
      delegation: {{enabled: false, allowed_agents: [], max_depth: 2}}
    {common}
    ''')
    wf('agents/manager.yaml', f'''
    agent:
      id: manager
      name: Manager
      role: Team Orchestrator
      description: Coordinates specialist agents.
      instructions: |
        You coordinate specialist agents and synthesize their work into useful final results.
      provider:
        type: lmstudio
        model: qwen3
      capabilities: [delegate.agent, datetime.now, knowledge.search, memory.search]
      tools: [delegate.agent, datetime.now, knowledge.search, memory.search]
      tool_runtime: {{enabled: true, max_iterations: 6, timeout_seconds: 120, allow_parallel: false, save_results_to_memory: false}}
      delegation: {{enabled: true, allowed_agents: [Researcher, Writer, Reviewer], max_depth: 2}}
    {common}
    ''')
    for fn, aid, name, role, instr in [('researcher.yaml','researcher','Researcher','Research Specialist','Find and organize useful facts, context, and evidence.'),('writer.yaml','writer','Writer','Writing Specialist','Turn raw context into clear, useful writing.'),('reviewer.yaml','reviewer','Reviewer','Review Specialist','Review outputs for clarity, completeness, and risks.')]:
        wf('agents/'+fn, f'''
        agent:
          id: {aid}
          name: {name}
          role: {role}
          description: {role} for team workflows.
          instructions: |
            {instr}
          provider: {{type: lmstudio, model: qwen3}}
          capabilities: [knowledge.search, memory.search, datetime.now]
          tools: [knowledge.search, memory.search, datetime.now]
          tool_runtime: {{enabled: true, max_iterations: 4, timeout_seconds: 90, allow_parallel: false, save_results_to_memory: false}}
          delegation: {{enabled: false, allowed_agents: [], max_depth: 1}}
        {common}
        ''')
    wf('teams/contentteam.yaml', '''
    team:
      name: ContentTeam
      description: Research, write, and review content with specialist agents.
      orchestrator: Manager
      members: [Researcher, Writer, Reviewer]
      shared_context: true
      max_rounds: 3
      task: |
        Produce a clear, useful content response using the team's specialists.
    ''')
    wf('knowledge/example.txt', 'Orchgentic is a local-first Python framework for reusable agentic AI agents.')
    wf('triggers/bob_heartbeat.yaml', '''
    trigger:
      id: bob_heartbeat
      type: heartbeat
      target_agent: Bob
      enabled: true
      interval_seconds: 60
      task: |
        Check whether anything needs attention and provide a short status update.
    ''')
    wf('triggers/order_webhook.yaml', '''
    trigger:
      id: order_webhook
      type: webhook
      target_agent: Bob
      enabled: true
      path: /webhooks/orders
      task: |
        Review this incoming webhook event and summarize what action is needed.
    ''')
    wf('.env', '''
    LMSTUDIO_ENDPOINT=http://localhost:1234/v1
    LMSTUDIO_API_KEY=lm-studio
    LMSTUDIO_MODEL=qwen3
    ZILLIZ_URI=
    ZILLIZ_TOKEN=
    ZILLIZ_COLLECTION=orchgentic_knowledge
    ''')
