from __future__ import annotations

import argparse
from pathlib import Path

from terminal_whiteboard.renderer import (
    DialogSpec,
    InBodyFlowSpec,
    VisualSpec,
    render_contrast,
    render_dialog_only,
    render_dialog_sample,
    render_in_body_flow,
    render_in_body_flow_sample,
    render_sample,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate rough terminal-style whiteboard visuals for technical posts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample = subparsers.add_parser("sample", help="Render the built-in repo/agent workflow example.")
    sample.add_argument("--output", "-o", default="examples/agent-visual-workflow.png")
    sample.add_argument("--seed", type=int, default=77)

    dialog_sample = subparsers.add_parser(
        "dialog-sample",
        help="Render the built-in dialog-only / panel-first example.",
    )
    dialog_sample.add_argument("--output", "-o", default="examples/dialog-only-operating-layer.png")
    dialog_sample.add_argument("--seed", type=int, default=77)

    in_body_sample = subparsers.add_parser(
        "in-body-flow-sample",
        help="Render the built-in cleaner in-body article flow example.",
    )
    in_body_sample.add_argument("--output", "-o", default="examples/in-body-flow.png")
    in_body_sample.add_argument("--seed", type=int, default=77)

    in_body_flow = subparsers.add_parser(
        "in-body-flow",
        help="Render a cleaner in-body article diagram with two vertical flows.",
    )
    in_body_flow.add_argument("--title", default="Two different flows")
    in_body_flow.add_argument("--subtitle", required=True)
    in_body_flow.add_argument("--left-label", required=True)
    in_body_flow.add_argument("--left-step", action="append", default=[], help="Repeat up to four times.")
    in_body_flow.add_argument("--right-label", required=True)
    in_body_flow.add_argument("--right-step", action="append", default=[], help="Repeat up to four times.")
    in_body_flow.add_argument("--center-badge-top", default="less writing tax")
    in_body_flow.add_argument("--center-badge-bottom", default="more context kept")
    in_body_flow.add_argument("--takeaway", required=True)
    in_body_flow.add_argument("--watermark", default="terminal-whiteboard")
    in_body_flow.add_argument("--output", "-o", default="outputs/in-body-flow.png")
    in_body_flow.add_argument("--seed", type=int, default=77)

    contrast = subparsers.add_parser("contrast", help="Render a two-card contrast visual.")
    contrast.add_argument("--title", required=True)
    contrast.add_argument("--subtitle", required=True)
    contrast.add_argument("--left-label", default="old way")
    contrast.add_argument("--left-title", required=True)
    contrast.add_argument("--left-bullet", action="append", default=[], help="Repeat up to three times.")
    contrast.add_argument("--right-label", default="better way")
    contrast.add_argument("--right-node", action="append", default=[], help="Repeat up to four times.")
    contrast.add_argument("--takeaway", required=True)
    contrast.add_argument("--command-name", default="contrast")
    contrast.add_argument("--arrow-top", default="+ signal")
    contrast.add_argument("--arrow-bottom", default="- noise")
    contrast.add_argument("--watermark", default="terminal-whiteboard")
    contrast.add_argument("--output", "-o", default="outputs/contrast.png")
    contrast.add_argument("--seed", type=int, default=77)

    dialog = subparsers.add_parser(
        "dialog",
        help="Render a platform-portable dialog-only visual with edge-filling panels.",
    )
    dialog.add_argument("--title", required=True)
    dialog.add_argument("--subtitle", required=True)
    dialog.add_argument("--left-title", required=True)
    dialog.add_argument("--left-line", action="append", default=[], help="Repeat up to two times.")
    dialog.add_argument("--center-title", default="MODEL")
    dialog.add_argument("--center-subtitle", default="replaceable")
    dialog.add_argument("--right-title", required=True)
    dialog.add_argument("--right-line", action="append", default=[], help="Repeat up to three times.")
    dialog.add_argument("--takeaway-top", required=True)
    dialog.add_argument("--takeaway-bottom", required=True)
    dialog.add_argument("--watermark", default="terminal-whiteboard")
    dialog.add_argument("--output", "-o", default="outputs/dialog.png")
    dialog.add_argument("--seed", type=int, default=77)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "sample":
        output = Path(args.output)
        render_sample(str(output), seed=args.seed)
        print(output)
        return 0

    if args.command == "dialog-sample":
        output = Path(args.output)
        render_dialog_sample(str(output), seed=args.seed)
        print(output)
        return 0

    if args.command == "in-body-flow-sample":
        output = Path(args.output)
        render_in_body_flow_sample(str(output), seed=args.seed)
        print(output)
        return 0

    if args.command == "in-body-flow":
        spec = InBodyFlowSpec(
            title=args.title,
            subtitle=args.subtitle,
            left_label=args.left_label,
            left_steps=tuple(args.left_step[:4] or ["idea", "draft", "edit", "publish"]),
            right_label=args.right_label,
            right_steps=tuple(args.right_step[:4] or ["thought", "conversation", "framework", "artifact"]),
            center_badge_top=args.center_badge_top,
            center_badge_bottom=args.center_badge_bottom,
            takeaway=args.takeaway,
            watermark=args.watermark,
        )
        output = Path(args.output)
        render_in_body_flow(spec, str(output), seed=args.seed)
        print(output)
        return 0

    if args.command == "contrast":
        spec = VisualSpec(
            command=args.command_name,
            title=args.title,
            subtitle=args.subtitle,
            left_label=args.left_label,
            left_title=args.left_title,
            left_bullets=tuple(args.left_bullet[:3] or ["too vague", "missing context", "hard to act on"]),
            right_label=args.right_label,
            right_nodes=tuple(args.right_node[:4] or ["context", "constraints", "tradeoffs", "intent"]),
            arrow_label_top=args.arrow_top,
            arrow_label_bottom=args.arrow_bottom,
            takeaway=args.takeaway,
            watermark=args.watermark,
        )
        output = Path(args.output)
        render_contrast(spec, str(output), seed=args.seed)
        print(output)
        return 0

    if args.command == "dialog":
        spec = DialogSpec(
            title=args.title,
            subtitle=args.subtitle,
            left_title=args.left_title,
            left_lines=tuple(args.left_line[:2] or ["clever demo", "forgets context"]),
            center_title=args.center_title,
            center_subtitle=args.center_subtitle,
            right_title=args.right_title,
            right_lines=tuple(args.right_line[:3] or ["access", "memory", "judgment"]),
            takeaway_top=args.takeaway_top,
            takeaway_bottom=args.takeaway_bottom,
            watermark=args.watermark,
        )
        output = Path(args.output)
        render_dialog_only(spec, str(output), seed=args.seed)
        print(output)
        return 0

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
