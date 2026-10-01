---
source_file: "backend/app/agents/compiler.py"
type: "code"
community: "Compiler + AST"
location: "L41"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Compiler__AST
---

# _make_node_executor()

## Connections
- [[dot-compile()]] - `calls` [EXTRACTED]
- [[Create an async node executor function for LangGraph.]] - `rationale_for` [EXTRACTED]
- [[ExecutionStatus]] - `uses` [INFERRED]
- [[SafeEvalError]] - `uses` [INFERRED]
- [[StepExecution]] - `calls` [EXTRACTED]
- [[StepStatus]] - `uses` [INFERRED]
- [[compiler.py]] - `contains` [EXTRACTED]
- [[execute()]] - `indirect_call` [INFERRED]
- [[safe_eval()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Compiler__AST