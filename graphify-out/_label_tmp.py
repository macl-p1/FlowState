import sys, json
from graphify.build import build_from_json
from graphify.cluster import score_all
from graphify.analyze import god_nodes, surprising_connections, suggest_questions
from graphify.report import generate
from graphify.export import to_json
from pathlib import Path

extraction = json.loads(Path("graphify-out/.graphify_extract.json").read_text(encoding="utf-8"))
detection  = json.loads(Path("graphify-out/.graphify_detect.json").read_text(encoding="utf-8"))
analysis   = json.loads(Path("graphify-out/.graphify_analysis.json").read_text(encoding="utf-8"))

G = build_from_json(extraction, root=".", directed=False)
communities = {int(k): v for k, v in analysis["communities"].items()}
cohesion = {int(k): v for k, v in analysis["cohesion"].items()}
tokens = {"input": extraction.get("input_tokens", 0), "output": extraction.get("output_tokens", 0)}

labels = {
    0: "Tool Implementations",
    1: "Suggestions + Cross-Pollination",
    2: "Frontend Pages",
    3: "Approvals API",
    4: "Frontend Config",
    5: "Workflow Runner Errors",
    6: "Core Engine Services",
    7: "Compiler + AST",
    8: "Integrations API",
    9: "Integration Handlers",
    10: "Approval Service Models",
    11: "Workflow Schemas",
    12: "Integration Tests",
    13: "Builder Page",
    14: "History Page",
    15: "Console Page",
    16: "Workflow Schema Types",
    17: "Custom Tools API",
    18: "Integration Tool Tests",
    19: "FlowState UI Screenshots",
}
for i in range(20, max(communities.keys()) + 1):
    if i not in labels:
        labels[i] = "Community " + str(i)

questions = suggest_questions(G, communities, labels)
report = generate(G, communities, cohesion, labels, analysis["gods"], analysis["surprises"], detection, tokens, ".", suggested_questions=questions)
Path("graphify-out/GRAPH_REPORT.md").write_text(report, encoding="utf-8")
Path("graphify-out/.graphify_labels.json").write_text(json.dumps({str(k): v for k, v in labels.items()}, ensure_ascii=False), encoding="utf-8")
wrote = to_json(G, communities, "graphify-out/graph.json", community_labels=labels)
if not wrote:
    print("ERROR: refused to shrink graphify-out/graph.json (existing graph has more nodes; #479).")
print("Report updated with community labels")
