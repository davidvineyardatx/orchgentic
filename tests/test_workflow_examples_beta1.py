from __future__ import annotations

from pathlib import Path

import yaml


EXAMPLE_DIR = Path("examples/workflows")

REQUIRED_TOP_LEVEL_FIELDS = {
    "id",
    "name",
    "version",
    "trigger",
    "runtime",
    "steps",
}

SUPPORTED_TRIGGER_TYPES = {"manual", "heartbeat", "webhook"}
SUPPORTED_RUNTIME_MODES = {"sequential"}
SUPPORTED_STEP_TYPES = {"agent", "team", "tool"}


def _load_examples() -> list[tuple[Path, dict]]:
    assert EXAMPLE_DIR.exists(), "examples/workflows directory is missing"

    loaded: list[tuple[Path, dict]] = []
    for path in sorted(EXAMPLE_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        loaded.append((path, data))

    assert loaded, "no workflow examples found"
    return loaded


def test_workflow_examples_include_required_contract_fields() -> None:
    for path, data in _load_examples():
        missing = REQUIRED_TOP_LEVEL_FIELDS - set(data)
        assert not missing, f"{path} missing required fields: {sorted(missing)}"


def test_workflow_example_triggers_are_supported() -> None:
    for path, data in _load_examples():
        trigger_type = data["trigger"]["type"]
        assert trigger_type in SUPPORTED_TRIGGER_TYPES, (
            f"{path} uses unsupported trigger type {trigger_type!r}"
        )


def test_workflow_example_runtime_is_beta1_supported() -> None:
    for path, data in _load_examples():
        runtime = data["runtime"]
        assert runtime["mode"] in SUPPORTED_RUNTIME_MODES
        assert runtime.get("save_trace") is True
        assert runtime.get("fail_fast") is True
        assert isinstance(runtime.get("max_steps"), int)
        assert isinstance(runtime.get("timeout_seconds"), int)


def test_workflow_example_steps_are_valid_and_unique() -> None:
    for path, data in _load_examples():
        step_ids = []
        for step in data["steps"]:
            assert "id" in step, f"{path} has a step without id"
            assert "type" in step, f"{path} step {step.get('id')} missing type"
            assert step["type"] in SUPPORTED_STEP_TYPES
            step_ids.append(step["id"])

            if step["type"] == "agent":
                assert "agent" in step
                assert "prompt" in step
            elif step["type"] == "team":
                assert "team" in step
                assert "prompt" in step
            elif step["type"] == "tool":
                assert "tool" in step
                assert "with" in step

        assert len(step_ids) == len(set(step_ids)), f"{path} has duplicate step ids"


def test_workflow_examples_define_final_output() -> None:
    for path, data in _load_examples():
        outputs = data.get("outputs", {})
        assert "final" in outputs, f"{path} missing outputs.final"
        assert "from" in outputs["final"], f"{path} missing outputs.final.from"
