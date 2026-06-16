# agent-use-cases

Small, self-contained agent examples. Each `examples/{N}-{slug}/` is one lesson,
built in 4 legible commits (scaffold -> tools -> workflow -> entry) so the git
history itself reads as a course.

## Layout

```
AGENTS.md                  # the teaching loop + 4-phase commit protocol
examples/_queue/ideas.json # backlog of lessons
examples/{N}-{slug}/       # one example each
Makefile                   # make lint / make fix
```

## Run an example

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your OPENAI_API_KEY
python examples/1-basic-react-agent/main.py
```

See `AGENTS.md` for how new examples get added.
