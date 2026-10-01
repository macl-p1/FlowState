---
type: community
cohesion: 0.09
members: 32
---

# Compiler + AST

**Cohesion:** 0.09 - loosely connected
**Members:** 32 nodes

## Members
- [[dot-__init__()_14]] - code - backend/app/agents/compiler.py
- [[dot-__init__()_15]] - code - backend/app/engine/runner.py
- [[dot-compile()]] - code - backend/app/agents/compiler.py
- [[AST]] - code
- [[Any_8]] - code
- [[BaseModel_7]] - code
- [[CompilationError]] - code - backend/app/agents/compiler.py
- [[Compiles a validated Workflow into an executable LangGraph StateGraph.]] - rationale - backend/app/agents/compiler.py
- [[Convert a Workflow into an executable LangGraph. Returns a CompiledWorkflow…]] - rationale - backend/app/agents/compiler.py
- [[Create an async node executor function for LangGraph.]] - rationale - backend/app/agents/compiler.py
- [[Exception_4]] - code
- [[Exception_5]] - code
- [[Raised when an expression contains unsafe operations.]] - rationale - backend/app/utils/safe_eval.py
- [[Raised when workflow cannot be compiled.]] - rationale - backend/app/agents/compiler.py
- [[Record of a single node execution.]] - rationale - backend/app/schemas/execution.py
- [[Recursively evaluate an AST node against a context dict.]] - rationale - backend/app/utils/safe_eval.py
- [[Safe expression evaluator using Python AST. Replaces eval() for condition node…]] - rationale - backend/app/utils/safe_eval.py
- [[SafeEvalError]] - code - backend/app/utils/safe_eval.py
- [[Safely evaluate a Python expression against a context dict. Args expression A…]] - rationale - backend/app/utils/safe_eval.py
- [[Session_9]] - code
- [[StepExecution]] - code - backend/app/schemas/execution.py
- [[Workflow Compiler — converts validated Workflow JSON into executable LangGraph.]] - rationale - backend/app/agents/compiler.py
- [[WorkflowCompiler]] - code - backend/app/agents/compiler.py
- [[_eval_node()]] - code - backend/app/utils/safe_eval.py
- [[_make_node_executor()]] - code - backend/app/agents/compiler.py
- [[compiler.py]] - code - backend/app/agents/compiler.py
- [[execute()]] - code - backend/app/agents/compiler.py
- [[langgraph_checkpoint_memory]] - concept
- [[langgraph_graph]] - concept
- [[operator]] - concept
- [[safe_eval()]] - code - backend/app/utils/safe_eval.py
- [[safe_eval.py]] - code - backend/app/utils/safe_eval.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Compiler__AST
SORT file.name ASC
```

## Connections to other communities
- 16 edges to [[_COMMUNITY_Core Engine Services]]
- 11 edges to [[_COMMUNITY_Workflow Runner Errors]]
- 4 edges to [[_COMMUNITY_Community 36]]
- 3 edges to [[_COMMUNITY_Workflow Schemas]]
- 2 edges to [[_COMMUNITY_Community 49]]
- 1 edge to [[_COMMUNITY_Approval Service Models]]
- 1 edge to [[_COMMUNITY_Community 50]]
- 1 edge to [[_COMMUNITY_Workflow Schema Types]]
- 1 edge to [[_COMMUNITY_Community 35]]
- 1 edge to [[_COMMUNITY_Community 21]]

## Top bridge nodes
- [[compiler.py]] - degree 24, connects to 8 communities
- [[WorkflowCompiler]] - degree 11, connects to 4 communities
- [[StepExecution]] - degree 11, connects to 3 communities
- [[safe_eval()]] - degree 9, connects to 2 communities
- [[SafeEvalError]] - degree 8, connects to 2 communities