# Changelog

Notable changes to the curriculum. Releases are date-tagged (`vYYYY.MM.DD.N`) and cut
automatically on merge to `main` (`.github/workflows/release.yml`), with auto-generated notes.

The format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## Unreleased

### Added
- `GUIDELINES.md` — teaching guidelines: how to learn the curriculum, how to adapt a use case, and the contributor build protocol.
- This changelog.

## Curriculum (current state)

- **27 worked use-case examples**, beginner → advanced (see [`CATALOG.md`](./CATALOG.md)).
- Patterns taught: structured output, schema validation + retry, prompt rubrics, conditional
  routing, long-context extraction, multi-agent delegation, tool loops, and multi-provider fan-out.
- Each example: runnable `main.py` with 2+ sample inputs, a `README.md`, and a Colab workbook
  with a starter exercise.
