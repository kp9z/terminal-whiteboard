# terminal-whiteboard

Generate rough terminal-style whiteboard visuals for technical posts, docs, explainers, and AI-agent workflows.

**Built by an agent, for agents.** The default look is a **dark terminal whiteboard**: mono typography, rough boxes/arrows, GitHub-ish dark colors, and compact labels that read well on X.

![Agent visual workflow example](examples/agent-visual-workflow.png)

## About

`terminal-whiteboard` is a small Python/uv tool for turning technical ideas into rough terminal-style visuals. It is designed to be **agent-friendly**: structured inputs, deterministic seeds, CLI-first rendering, and outputs that agents can attach to posts/docs without opening a design tool.

The project is also an experiment in agent-built tooling: a visual system created by an AI assistant to help other agents produce less generic, more readable technical visuals.

## Why

Most AI-generated social visuals look glossy, generic, or illegible. `terminal-whiteboard` is meant for builder-native visuals that feel closer to a sketch in a terminal than a Canva template.

## Install for development

This project uses [`uv`](https://docs.astral.sh/uv/), not pip.

```bash
uv sync --dev
```

## Usage

Render the built-in sample:

```bash
uv run terminal-whiteboard sample --output examples/agent-visual-workflow.png
```

Render a custom contrast visual:

```bash
uv run terminal-whiteboard contrast \
  --command-name "render-agent-visual" \
  --title "Agents need visuals, not design chores" \
  --subtitle "Turn structured ideas into terminal-whiteboard PNGs from a CLI." \
  --left-label "manual design" \
  --left-title '"open a design tool"' \
  --left-bullet "slow iteration" \
  --left-bullet "inconsistent style" \
  --left-bullet "hard to automate" \
  --right-label "agent workflow" \
  --right-node "post idea" \
  --right-node "visual spec" \
  --right-node "renderer" \
  --right-node "png output" \
  --arrow-top "+ structure" \
  --arrow-bottom "- design drag" \
  --takeaway "A good agent tool turns intent into a reusable artifact." \
  --watermark "terminal-whiteboard" \
  --output outputs/custom.png
```

Render a dialog-only / panel-first visual for platform-portable social posts:

```bash
uv run terminal-whiteboard dialog-sample --output examples/dialog-only-operating-layer.png

uv run terminal-whiteboard dialog \
  --title "Smart model ≠ useful AI" \
  --subtitle "Useful AI comes from the layer around it." \
  --left-title "MODEL ONLY" \
  --left-line "clever demo" \
  --left-line "forgets context" \
  --center-title "MODEL" \
  --center-subtitle "replaceable" \
  --right-title "OPERATING LAYER" \
  --right-line "access" \
  --right-line "memory" \
  --right-line "judgment" \
  --takeaway-top "Not a leaderboard problem." \
  --takeaway-bottom "A system design problem." \
  --output outputs/dialog.png
```

The dialog renderer deliberately lets panels push to the canvas edges so the image is mostly dialog surfaces, not black background. It also measures text bounding boxes and raises an error instead of exporting text that overflows.

## Agent-friendly usage

Agents can call the CLI with structured fields, use deterministic seeds for repeatable output, and attach the generated PNG directly to a post, README, issue, or docs page. No browser, canvas, or design-tool session required.

## Development

```bash
uv run pytest
uv run ruff check .
uv run terminal-whiteboard sample --output /tmp/talk-to-your-agents.png
```

## Design principles

- dark terminal surface or dialog-first panel surfaces
- mono-first typography, with optional readable handwritten labels when available
- rough hand-drawn shapes, not glossy AI art
- blue/green accents, red only for negative marks
- one idea per visual
- short labels over paragraph text
- automated text-fit checks before export
- watermark is quiet, not logo-heavy

## Status

Early alpha. Current templates:

- two-card contrast visual
- dialog-only / panel-first visual

Planned templates:

- flow diagrams
- stacked frameworks
- quote cards
- node maps
- Excalidraw/SVG export
