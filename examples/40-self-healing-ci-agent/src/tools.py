"""
Tool definitions and implementations for the self-healing CI agent.

Each function represents a real action the agent can take:
  - apply_dependency_fix  — install or upgrade a Python package
  - apply_env_fix         — set an environment variable in the CI context
  - apply_code_patch      — apply a described code change to a file
  - run_tests             — run the CI test suite and observe results

TOOL_DEFINITIONS is the list of OpenAI function-calling dicts passed to the API.
TOOL_MAP maps function name -> callable for dispatch in the tool loop.

State (_applied_fixes) is reset at the start of each run() call via reset_state()
so scenarios remain independent when main.py runs multiple scenarios in sequence.
"""
from __future__ import annotations

# ---------------------------------------------------------------------------
# Mutable simulation state — reset per run() call
# ---------------------------------------------------------------------------
_applied_fixes: list[dict] = []


def reset_state() -> None:
    """Reset simulation state. Call once at the start of every run() invocation."""
    global _applied_fixes
    _applied_fixes = []


# ---------------------------------------------------------------------------
# Tool implementations
# ---------------------------------------------------------------------------


def apply_dependency_fix(package: str, version: str | None = None) -> dict:
    """Install or upgrade a Python package. Returns success + message."""
    fix = {"type": "dependency", "package": package, "version": version}
    _applied_fixes.append(fix)
    ver_str = f"=={version}" if version else " (latest)"
    return {
        "success": True,
        "message": f"Installed {package}{ver_str}",
        "fix": fix,
    }


def apply_env_fix(key: str, value: str) -> dict:
    """Set an environment variable in the CI context."""
    fix = {"type": "env", "key": key, "value": value}
    _applied_fixes.append(fix)
    return {
        "success": True,
        "message": f"Set {key}={value}",
        "fix": fix,
    }


def apply_code_patch(file_path: str, description: str) -> dict:
    """Apply a described code change to a file."""
    fix = {"type": "code_patch", "file": file_path, "description": description}
    _applied_fixes.append(fix)
    return {
        "success": True,
        "message": f"Patched {file_path}: {description}",
        "fix": fix,
    }


def run_tests(filter_pattern: str | None = None) -> dict:
    """Run the CI test suite. Returns passed, exit_code, output.

    Simulation rules:
      - Tests pass if at least one dependency fix has been applied (Scenario A).
      - Tests always fail for flaky/timeout errors — no tool call resolves them
        (Scenario B).
    """
    dep_fixes = [f for f in _applied_fixes if f["type"] == "dependency"]
    if dep_fixes:
        pattern_note = f" (filter: {filter_pattern})" if filter_pattern else ""
        return {
            "passed": True,
            "exit_code": 0,
            "output": (
                f"pytest{pattern_note}: 42 passed in 3.2s "
                f"(after installing {dep_fixes[-1]['package']})"
            ),
        }
    return {
        "passed": False,
        "exit_code": 1,
        "output": "ERROR: Connection timed out after 30s. Tests did not complete.",
    }


# ---------------------------------------------------------------------------
# OpenAI tool definitions
# ---------------------------------------------------------------------------

TOOL_DEFINITIONS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "apply_dependency_fix",
            "description": (
                "Install or upgrade a Python package in the CI environment. "
                "Use this when the failure is caused by a missing or incompatible package."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "package": {
                        "type": "string",
                        "description": "The package name to install (e.g. 'requests').",
                    },
                    "version": {
                        "type": "string",
                        "description": (
                            "Exact version to pin (e.g. '2.31.0'). "
                            "Omit to install the latest available version."
                        ),
                    },
                },
                "required": ["package"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_env_fix",
            "description": (
                "Set an environment variable in the CI context. "
                "Use this when the failure is caused by a missing or incorrect env var."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {
                        "type": "string",
                        "description": "The environment variable name (e.g. 'DATABASE_URL').",
                    },
                    "value": {
                        "type": "string",
                        "description": "The value to set.",
                    },
                },
                "required": ["key", "value"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "apply_code_patch",
            "description": (
                "Apply a described code change to a source file. "
                "Use this when the failure is caused by a syntax error or bad import."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to patch (e.g. 'src/client.py').",
                    },
                    "description": {
                        "type": "string",
                        "description": (
                            "Human-readable description of the change to apply "
                            "(e.g. 'Replace `import requests` with "
                            "`from requests import Session`)."
                        ),
                    },
                },
                "required": ["file_path", "description"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_tests",
            "description": (
                "Run the CI test suite and observe the results. "
                "Always call this after applying a fix to check if the failure is resolved. "
                "Stop calling tools if this returns passed=true."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "filter_pattern": {
                        "type": "string",
                        "description": (
                            "Optional pytest -k expression to run a subset of tests "
                            "(e.g. 'test_auth'). Omit to run the full suite."
                        ),
                    },
                },
                "required": [],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
]

# ---------------------------------------------------------------------------
# Dispatch map
# ---------------------------------------------------------------------------

TOOL_MAP: dict[str, object] = {
    "apply_dependency_fix": apply_dependency_fix,
    "apply_env_fix": apply_env_fix,
    "apply_code_patch": apply_code_patch,
    "run_tests": run_tests,
}
