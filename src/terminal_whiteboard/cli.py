from __future__ import annotations

import argparse
from pathlib import Path

from terminal_whiteboard.renderer import VisualSpec, render_contrast, render_sample


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate rough terminal-style whiteboard visuals for technical posts."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample = subparsers.add_parser("sample", help="Render the built-in repo/agent workflow example.")
    sample.add_argument("--output", "-o", default="examples/agent-visual-workflow.png")
    sample.add_argument("--seed", type=int, default=77)

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
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "sample":
        output = Path(args.output)
        render_sample(str(output), seed=args.seed)
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

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
