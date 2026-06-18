from pathlib import Path

from terminal_whiteboard.renderer import (
    TALK_TO_AGENTS_SPEC,
    VisualSpec,
    render_contrast,
    render_talk_to_agents,
)


def assert_png(path: Path) -> None:
    assert path.exists()
    assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_sample_render_creates_png(tmp_path: Path) -> None:
    output = tmp_path / "sample.png"
    assert render_talk_to_agents(str(output), seed=1) == str(output)
    assert_png(output)


def test_contrast_render_creates_png(tmp_path: Path) -> None:
    output = tmp_path / "contrast.png"
    spec = VisualSpec(
        command="test",
        title="Small prompts lose context",
        subtitle="A terminal-whiteboard test visual.",
        left_label="thin prompt",
        left_title='"do this"',
        left_bullets=("missing why", "missing taste", "missing constraints"),
        right_label="rich prompt",
        right_nodes=("context", "constraints", "tradeoffs", "tone"),
        arrow_label_top="+ signal",
        arrow_label_bottom="- guessing",
        takeaway="Better context makes the agent less random.",
    )
    assert render_contrast(spec, str(output), seed=2) == str(output)
    assert_png(output)


def test_builtin_spec_has_kenny_watermark() -> None:
    assert TALK_TO_AGENTS_SPEC.watermark == "kennytrinh.com"
