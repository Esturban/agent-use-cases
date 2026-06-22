# HF Spaces Deployment Spec

## Deployment Readiness

| Demo | Function wired | OpenRouter env | Deps complete | Blockers |
|------|:---:|:---:|:---:|---------|
| Invoice Extractor | ✅ `extract_invoice` | ✅ `_client()` | ✅ (post-fix) | None |
| Resume Screener | ✅ `screen_resume` | ✅ `_client()` | ✅ (post-fix) | None |
| Contract Reviewer | ✅ `review_contract` | ✅ `_client()` | ✅ (post-fix) | None |
| Support Ticket Router | ✅ `route_and_draft` | ✅ `_client()` | ✅ (post-fix) | None |
| Lead Qualifier | ✅ `qualify` | ✅ `_client()` | ✅ (post-fix) | None |
| ReAct Agent | ✅ `run_agent` | ✅ `_client()` | ✅ (post-fix) | None |

### Pre-deployment fixes applied (same commit)

1. **README.md** — added HF Spaces YAML frontmatter (required by Spaces router).
2. **requirements.txt** — removed unused heavy deps (`langgraph`, `langchain-openai`, `langchain-core`, `python-dotenv`, `pydantic-ai`); added `pydantic>=2.0.0` (imported directly in app.py); pinned `openai>=1.40.0` (`.beta.chat.completions.parse` was added in 1.40).

---

## Space configuration

| Field | Value |
|-------|-------|
| Space ID | `Esturban/agent-use-cases` |
| SDK | `gradio` |
| Entry point | `app.py` |
| Python | `3.11` |
| Secret | `OPENROUTER_API_KEY` |

---

## Deployment steps

### 1. Install CLI

```bash
pip install huggingface_hub
```

### 2. Authenticate

```bash
huggingface-cli login
# paste your HF write token (Settings → Access Tokens)
```

### 3. Create the Space (one-time)

```bash
python - <<'EOF'
from huggingface_hub import HfApi
api = HfApi()
api.create_repo(
    repo_id="Esturban/agent-use-cases",
    repo_type="space",
    space_sdk="gradio",
    private=False,
)
print("Space created: https://huggingface.co/spaces/Esturban/agent-use-cases")
EOF
```

### 4. Upload only the files the Space needs

Upload the three files the Gradio Space requires rather than the full repo (avoids shipping 40+ example dirs and notebooks):

```bash
python - <<'EOF'
from huggingface_hub import upload_file

REPO = "Esturban/agent-use-cases"

for path in ["app.py", "requirements.txt", "README.md"]:
    upload_file(
        path_or_fileobj=path,
        path_in_repo=path,
        repo_id=REPO,
        repo_type="space",
        commit_message=f"deploy: upload {path}",
    )
    print(f"Uploaded {path}")
EOF
```

Alternatively push via git (ships the full repo — larger but simpler if you want the examples visible in the Space files tab):

```bash
git remote add hf https://huggingface.co/spaces/Esturban/agent-use-cases
git push hf dev:main
```

### 5. Set the secret

In the Space UI: **Settings → Variables and secrets → New secret**

| Name | Value |
|------|-------|
| `OPENROUTER_API_KEY` | your key from openrouter.ai |

Or via CLI:

```bash
python - <<'EOF'
from huggingface_hub import add_space_secret
add_space_secret(
    repo_id="Esturban/agent-use-cases",
    key="OPENROUTER_API_KEY",
    value="<your-key>",
)
EOF
```

### 6. Verify

Space URL: `https://huggingface.co/spaces/Esturban/agent-use-cases`

Check the **Logs** tab in the Space UI — the app starts in ~30–60s on the free CPU tier.
Cold-start expected after slimmed requirements.txt: ~25s (vs ~90s with the old heavy deps).

---

## Ongoing deploys

After any change to `app.py` or `requirements.txt`, re-run step 4 for the changed file:

```bash
python - <<'EOF'
from huggingface_hub import upload_file
upload_file("app.py", "app.py", "Esturban/agent-use-cases", repo_type="space")
EOF
```

The Space rebuilds automatically on every file push.
