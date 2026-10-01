import json
from graphify.detect import detect
from pathlib import Path
result = detect(Path("."))
Path("graphify-out/.graphify_detect.json").write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
print(f"total_files={result['total_files']} total_words={result.get('total_words',0)}")
for cat, files in result.get("files", {}).items():
    print(f"  {cat}: {len(files)} files")
skipped = result.get("skipped_sensitive", [])
if skipped:
    print(f"skipped_sensitive={len(skipped)}: {skipped[:5]}")
