# list_imports.py
import ast, glob

modules = set()
for fn in glob.glob("**/*.py", recursive=True):
    try:
        with open(fn, "r", encoding="utf-8", errors="ignore") as f:
            tree = ast.parse(f.read(), filename=fn)
    except Exception:
        # skip files we can't even parse
        continue

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                modules.add(n.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module.split(".")[0])

print("\n".join(sorted(modules)))
