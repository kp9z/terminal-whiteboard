from __future__ import annotations

import math
import os
import random
from collections.abc import Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFont

RGB = tuple[int, int, int]
Point = tuple[float, float]
Box = tuple[int, int, int, int]


@dataclass(frozen=True)
class Palette:
    """A terminal-inspired color palette."""

    bg: RGB = (13, 17, 23)  # #0d1117
    surface: RGB = (22, 27, 34)  # #161b22
    card: RGB = (18, 23, 30)
    border: RGB = (48, 54, 61)  # #30363d
    text: RGB = (201, 209, 217)  # #c9d1d9
    muted: RGB = (139, 148, 158)  # #8b949e
    blue: RGB = (88, 166, 255)  # #58a6ff
    green: RGB = (63, 185, 80)  # #3fb950
    red: RGB = (255, 101, 104)  # #ff6568
    yellow: RGB = (219, 171, 9)
    white: RGB = (246, 248, 250)


@dataclass(frozen=True)
class VisualSpec:
    """Content for a two-card contrast visual."""

    command: str
    title: str
    subtitle: str
    left_label: str
    left_title: str
    left_bullets: tuple[str, ...]
    right_label: str
    right_nodes: tuple[str, ...]
    arrow_label_top: str
    arrow_label_bottom: str
    takeaway: str
    watermark: str = "kennytrinh.com"
    footer: str = "# terminal whiteboard v0.1"


KENNY_PALETTE = Palette()

TALK_TO_AGENTS_SPEC = VisualSpec(
    command="talk-to-your-agents",
    title="Typing makes your prompts too small",
    subtitle="Voice captures the messy context agents actually need.",
    left_label="typed prompt",
    left_title='"summarize this"',
    left_bullets=("too compressed", "missing constraints", "missing tradeoffs"),
    right_label="spoken context",
    right_nodes=("what happened", "why it matters", "constraints", "tone + intent"),
    arrow_label_top="+ signal",
    arrow_label_bottom="- guessing",
    takeaway="The best prompt is often the one you would never type.",
)


class TerminalWhiteboardRenderer:
    """Draw rough terminal-whiteboard visuals.

    The renderer intentionally avoids glossy gradients and AI-art style. It uses deterministic jitter,
    monochrome terminal chrome, rough lines, and a tiny amount of texture.
    """

    def __init__(
        self,
        width: int = 1600,
        height: int = 900,
        seed: int = 77,
        palette: Palette | None = None,
    ) -> None:
        self.width = width
        self.height = height
        self.random = random.Random(seed)
        self.palette = palette or KENNY_PALETTE
        self.image = Image.new("RGB", (width, height), self.palette.bg)
        self.draw = ImageDraw.Draw(self.image)
        self.fonts = self._load_fonts()

    def _load_fonts(self) -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
        mono_candidates = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        )
        mono_bold_candidates = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        )
        mono = next((path for path in mono_candidates if os.path.exists(path)), None)
        mono_bold = next((path for path in mono_bold_candidates if os.path.exists(path)), mono)
        if not mono or not mono_bold:
            fallback = ImageFont.load_default()
            return {name: fallback for name in ("title", "sub", "label", "body", "small", "tiny", "takeaway")}
        return {
            "title": ImageFont.truetype(mono_bold, 54),
            "sub": ImageFont.truetype(mono, 28),
            "label": ImageFont.truetype(mono_bold, 30),
            "body": ImageFont.truetype(mono, 26),
            "small": ImageFont.truetype(mono, 20),
            "tiny": ImageFont.truetype(mono, 17),
            "takeaway": ImageFont.truetype(mono_bold, 31),
        }

    def add_background_texture(self) -> None:
        pix = self.image.load()
        for _ in range(9_000):
            x, y = self.random.randrange(self.width), self.random.randrange(self.height)
            r, g, b = pix[x, y]
            delta = self.random.choice([-3, -2, -1, 1, 2, 3])
            pix[x, y] = tuple(max(0, min(255, v + delta)) for v in (r, g, b))
        for x in range(80, self.width, 80):
            self.draw.line([(x, 0), (x, self.height)], fill=(17, 22, 29), width=1)
        for y in range(72, self.height, 72):
            self.draw.line([(0, y), (self.width, y)], fill=(17, 22, 29), width=1)

    def _jitter(self, points: Sequence[Point], amp: float = 2.0) -> list[Point]:
        return [(x + self.random.uniform(-amp, amp), y + self.random.uniform(-amp, amp)) for x, y in points]

    def rough_line(
        self,
        points: Sequence[Point],
        fill: RGB | None = None,
        width: int = 3,
        passes: int = 2,
        amp: float = 2.0,
    ) -> None:
        for _ in range(passes):
            self.draw.line(
                self._jitter(points, amp),
                fill=fill or self.palette.text,
                width=width,
                joint="curve",
            )

    def rough_rect(
        self,
        box: Box,
        fill: RGB | None = None,
        outline: RGB | None = None,
        width: int = 3,
        radius: int = 14,
        passes: int = 2,
    ) -> None:
        x0, y0, x1, y1 = box
        outline = outline or self.palette.border
        if fill:
            self.draw.rounded_rectangle([x0, y0, x1, y1], radius=radius, fill=fill)
        points = [
            (x0 + radius, y0),
            (x1 - radius, y0),
            (x1, y0 + radius),
            (x1, y1 - radius),
            (x1 - radius, y1),
            (x0 + radius, y1),
            (x0, y1 - radius),
            (x0, y0 + radius),
            (x0 + radius, y0),
        ]
        for _ in range(passes):
            self.rough_line(points, outline, width, 1, 2.4)

    def arrow(self, start: tuple[int, int], end: tuple[int, int], color: RGB | None = None, width: int = 4) -> None:
        color = color or self.palette.blue
        x0, y0 = start
        x1, y1 = end
        self.rough_line([(x0, y0), (x1, y1)], color, width, 2, 2.0)
        angle = math.atan2(y1 - y0, x1 - x0)
        length = 24
        for arrow_angle in (angle + math.pi * 0.82, angle - math.pi * 0.82):
            self.rough_line(
                [(x1, y1), (x1 + length * math.cos(arrow_angle), y1 + length * math.sin(arrow_angle))],
                color,
                width,
                2,
                1.5,
            )

    def text(self, xy: tuple[int, int], text: str, font_name: str = "body", fill: RGB | None = None) -> None:
        self.draw.text(xy, text, font=self.fonts[font_name], fill=fill or self.palette.text)

    def text_center(self, text: str, font_name: str, y: int, fill: RGB | None = None) -> None:
        font = self.fonts[font_name]
        bbox = self.draw.textbbox((0, 0), text, font=font)
        self.draw.text(((self.width - (bbox[2] - bbox[0])) / 2, y), text, font=font, fill=fill or self.palette.text)

    def terminal_chrome(self, title: str = "~/terminal-whiteboard", watermark: str = "terminal-whiteboard") -> None:
        p = self.palette
        self.rough_rect((70, 54, 1530, 836), fill=p.surface, outline=p.border, width=2, radius=18, passes=2)
        self.draw.ellipse([105, 82, 119, 96], fill=p.red)
        self.draw.ellipse([130, 82, 144, 96], fill=p.yellow)
        self.draw.ellipse([155, 82, 169, 96], fill=p.green)
        self.text((205, 78), title, "tiny", p.muted)
        self.text((1210, 78), watermark, "tiny", p.muted)
        self.rough_line([(95, 116), (1505, 116)], fill=p.border, width=2, passes=1, amp=1.0)

    def save(self, output: str) -> str:
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        self.image.save(output, quality=95)
        return output


def render_contrast(spec: VisualSpec, output: str, seed: int = 77, palette: Palette | None = None) -> str:
    renderer = TerminalWhiteboardRenderer(seed=seed, palette=palette)
    p = renderer.palette
    d = renderer.draw
    fonts = renderer.fonts
    renderer.add_background_texture()
    renderer.terminal_chrome(title="~/terminal-whiteboard/x-post", watermark=spec.watermark)

    prompt = "~/kennytrinh $ " if spec.watermark == "kennytrinh.com" else "~/terminal $ "
    renderer.text((130, 150), prompt, "sub", p.green)
    prompt_width = d.textbbox((0, 0), prompt, font=fonts["sub"])[2]
    renderer.text((int(130 + prompt_width), 150), spec.command, "sub", p.blue)
    renderer.text((130, 205), spec.title, "title", p.white)
    renderer.text((132, 275), spec.subtitle, "sub", p.muted)

    left = (135, 365, 685, 650)
    right = (915, 365, 1465, 650)
    renderer.rough_rect(left, fill=p.card, outline=p.border, width=3, radius=16, passes=2)
    renderer.rough_rect(right, fill=p.card, outline=p.blue, width=3, radius=16, passes=2)

    renderer.rough_rect((175, 335, 470, 388), fill=p.bg, outline=p.border, width=2, radius=10, passes=2)
    renderer.text((193, 348), spec.left_label, "label", p.muted)
    renderer.text((185, 425), spec.left_title, "body", p.text)
    renderer.rough_line([(185, 465), (635, 465)], fill=p.border, width=2, passes=1, amp=1.0)
    for index, item in enumerate(spec.left_bullets[:3]):
        y = 500 + index * 38
        renderer.text((190, y), "x", "body", p.red)
        renderer.text((230, y), item, "body", p.muted)

    renderer.rough_rect((955, 335, 1295, 388), fill=p.bg, outline=p.blue, width=2, radius=10, passes=2)
    renderer.text((973, 348), spec.right_label, "label", p.blue)
    renderer.rough_line([(1105, 455), (1195, 490), (1260, 585)], fill=(57, 66, 76), width=2, passes=1, amp=3)
    renderer.rough_line([(1115, 555), (1090, 462), (1215, 488)], fill=(57, 66, 76), width=2, passes=1, amp=3)

    node_positions = ((972, 430, p.blue), (1195, 462, p.green), (990, 540, p.green), (1215, 572, p.blue))
    for node, (x, y, color) in zip(spec.right_nodes[:4], node_positions, strict=False):
        text_width = d.textbbox((0, 0), node, font=fonts["body"])[2]
        node_box = (x - 14, y - 10, int(x + text_width + 18), y + 39)
        renderer.rough_rect(
            node_box,
            fill=p.bg,
            outline=color,
            width=2,
            radius=12,
            passes=2,
        )
        renderer.text((x, y), node, "body", p.text)

    renderer.arrow((710, 505), (890, 505), color=p.blue, width=4)
    renderer.text((738, 458), spec.arrow_label_top, "small", p.blue)
    renderer.text((734, 532), spec.arrow_label_bottom, "small", p.muted)

    renderer.rough_rect((210, 710, 1390, 775), fill=p.bg, outline=p.green, width=2, radius=14, passes=2)
    renderer.text_center(spec.takeaway, "takeaway", 728, p.white)
    renderer.rough_rect((1460, 734, 1478, 768), fill=p.green, outline=p.green, width=1, radius=2, passes=1)
    renderer.text((124, 795), spec.footer, "tiny", (87, 96, 106))
    return renderer.save(output)


def render_talk_to_agents(output: str, seed: int = 77) -> str:
    return render_contrast(TALK_TO_AGENTS_SPEC, output, seed=seed)
