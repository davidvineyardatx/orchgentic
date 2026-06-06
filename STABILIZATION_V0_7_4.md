# v0.7.4 Tool Parser / Continuation Hotfix

Fixes a runtime issue where models such as `llama-3.3-70b-versatile` may return prose plus JSON tool calls.

Before:

```text
To find out what day it is, I'll call the datetime.now tool.

{"action":"tool","tool":"datetime.now","arguments":{}}
```

The runtime could treat the whole response as final text.

Now the runtime extracts embedded JSON action objects, executes the tool, reinjects the observation, and continues until a final answer is produced.

## Test

```bash
orch run Bob --debug
```

Prompt:

```text
Using datetime.now tell me what day it is
```
