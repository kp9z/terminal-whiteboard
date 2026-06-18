from pathlib import Path

from terminal_whiteboard.renderer import (
    DIALOG_ONLY_SPEC,
    HOOK_SPEC,
    IN_BODY_FLOW_SPEC,
    TERMINAL_WHITEBOARD_SPEC,
    DialogSpec,
    HookSpec,
    InBodyFlowSpec,
    VisualSpec,
    render_contrast,
    render_dialog_only,
    render_dialog_sample,
    render_hook,
    render_hook_sample,
    render_in_body_flow,
    render_in_body_flow_sample,
    render_sample,
)


def assert_png(path: Path) -> None:
    assert path.exists()
    assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n")


def test_sample_render_creates_repo_focused_png(tmp_path: Path) -> None:
    output = tmp_path / "sample.png"
    assert render_sample(str(output), seed=1) == str(output)
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


def test_dialog_sample_render_creates_png(tmp_path: Path) -> None:
    output = tmp_path / "dialog-sample.png"
    assert render_dialog_sample(str(output), seed=3) == str(output)
    assert_png(output)


def test_in_body_flow_sample_render_creates_png(tmp_path: Path) -> None:
    output = tmp_path / "in-body-flow-sample.png"
    assert render_in_body_flow_sample(str(output), seed=5) == str(output)
    assert_png(output)


def test_hook_sample_render_creates_png(tmp_path: Path) -> None:
    output = tmp_path / "hook-sample.png"
    assert render_hook_sample(str(output), seed=5) == str(output)
    assert_png(output)


def test_hook_render_rejects_overlong_phrases(tmp_path: Path) -> None:
    output = tmp_path / "hook-too-long.png"
    spec = HookSpec(phrase="THIS HOOK HAS TOO MANY WORDS TO BE TASTEFUL")
    try:
        render_hook(spec, str(output), seed=5)
    except ValueError as exc:
        assert "Hook phrase" in str(exc)
    else:
        raise AssertionError("Expected hook renderer to reject overlong phrase")


def test_in_body_flow_render_creates_png(tmp_path: Path) -> None:
    output = tmp_path / "in-body-flow.png"
    spec = InBodyFlowSpec(
        title="Two different flows",
        subtitle="The artifact matters less than preserving the thought.",
        left_label="content flow",
        left_steps=("idea", "draft", "edit", "publish"),
        right_label="interview flow",
        right_steps=("thought", "conversation", "framework", "artifact"),
        center_badge_top="less writing tax",
        center_badge_bottom="more context kept",
        takeaway="value = less thought lost",
    )
    assert render_in_body_flow(spec, str(output), seed=6) == str(output)
    assert_png(output)


def test_rough_rect_uses_intermediate_points_for_excalidraw_like_edges() -> None:
    from terminal_whiteboard.renderer import TerminalWhiteboardRenderer

    renderer = TerminalWhiteboardRenderer(seed=5)
    calls: list[int] = []

    def record_points(points, fill=None, width=3, passes=2, amp=2.0):  # noqa: ANN001, ANN202
        calls.append(len(points))

    renderer.rough_line = record_points  # type: ignore[method-assign]
    renderer.rough_rect((10, 20, 310, 220), radius=24, passes=2)

    assert calls
    assert min(calls) > 20


def test_dialog_render_fails_when_text_cannot_fit(tmp_path: Path) -> None:
    output = tmp_path / "dialog-too-long.png"
    spec = DialogSpec(
        title="Smart model != useful AI",
        subtitle="Useful AI comes from the layer around it.",
        left_title="MODEL ONLY",
        left_lines=("clever demo", "forgets context"),
        center_title="MODEL",
        center_subtitle="replaceable",
        right_title="THIS TITLE IS INTENTIONALLY FAR TOO LONG FOR THE PANEL",
        right_lines=("access", "memory", "judgment"),
        takeaway_top="Not a leaderboard problem.",
        takeaway_bottom="A system design problem.",
    )
    try:
        render_dialog_only(spec, str(output), seed=4)
    except ValueError as exc:
        assert "Text does not fit" in str(exc)
    else:
        raise AssertionError("Expected text-fit guard to reject overflowing dialog text")


def test_builtin_specs_have_generic_watermark() -> None:
    assert TERMINAL_WHITEBOARD_SPEC.watermark == "terminal-whiteboard"
    assert DIALOG_ONLY_SPEC.watermark == "terminal-whiteboard"
    assert IN_BODY_FLOW_SPEC.watermark == "terminal-whiteboard"
    assert HOOK_SPEC.watermark == "terminal-whiteboard"
