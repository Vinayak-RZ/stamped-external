from pathlib import Path
root = Path(__file__).resolve().parents[1]
code = (root / "scripts/build-industry-decks.py").read_text(encoding="utf-8")
code = code.replace('ROOT = Path("/workspace")', f'ROOT = Path(r"{root}")')
exec(compile(code, "build-industry-decks.py", "exec"))
