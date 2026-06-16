# agent-use-cases -- Teaching Workspace

**Purpose:** Build small, self-contained agent examples. Each example is one lesson.
**Autonomy:** Teaching loop -- pick next queue item, scaffold in 4 commits, mark done.

---

## Session Start Protocol

1. **Check queue** -- pick the next `pending` item by priority:
   ```bash
   python3 -c "
   import json
   q = json.load(open('examples/_queue/ideas.json'))['queue']
   for i in q:
       print(f'  {i[\"id\"]:3}  [{i[\"status\"]:9}]  {i[\"priority\"]:6}  {i[\"slug\"]}')
   "
   ```

2. **Check deps** -- if the example needs a new package, add it first in its own commit:
   `pip install <dep> && pip freeze > requirements.txt`
   then `git commit -m "chore(deps): add <dep>"`.

3. **Scaffold** -- follow the 4-phase commit protocol below.

4. **Mark done** -- set the item's `status` to `"done"` in `examples/_queue/ideas.json`.

---

## 4-Phase Commit Protocol

Every example is exactly these 4 commits. No combining phases.

| Phase | Files | Commit message |
|-------|-------|----------------|
| 1 scaffold | dir + empty stubs | `chore(examples): scaffold {slug} -- directory and stub files` |
| 2 tools | `src/tools.py` | `feat(examples/{slug}): add tools -- {one-line}` |
| 3 workflow | `src/workflow.py` | `feat(examples/{slug}): add workflow -- {one-line}` |
| 4 entry | `main.py` + `README.md` | `feat(examples/{slug}): add main and README -- {one-line}` |

**Hard limits:** under 150 total lines across all files. README is 3-5 lines.

---

## Example Structure

```
examples/{N}-{slug}/
├── main.py          # entry: load_dotenv(), if __name__ == "__main__"
├── README.md        # 3-5 lines + run command
└── src/
    ├── __init__.py  # empty
    ├── tools.py     # @tool functions
    └── workflow.py  # create_workflow() -> compiled graph
```

Mirror `examples/1-basic-react-agent/` exactly.

---

## Rules (hard constraints)

- NEVER add `Co-Authored-By` lines to commits
- NEVER commit `AGENTS.md` changes alongside example commits -- keep them separate
- Add a dep in its own commit before using it
- `main.py` always calls `load_dotenv()` and has an `if __name__ == "__main__":` block
- No speculative code, no extra features, no TODO comments

---

## Key Paths

| Path | What |
|------|------|
| `examples/_queue/ideas.json` | Teaching loop queue |
| `examples/{N}-{slug}/` | Individual examples |
| `requirements.txt` | Pinned deps |
| `Makefile` | `make lint` / `make fix` over `examples/` |
