from __future__ import annotations

import math
import os
import random
from collections.abc import Sequence
from dataclasses import dataclass

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
    watermark: str = "terminal-whiteboard"
    footer: str = "# terminal whiteboard v0.1"


@dataclass(frozen=True)
class DialogSpec:
    """Content for a dialog-only contrast visual.

    This layout is platform-portable: panels fill or slightly bleed past the
    canvas edges so viewers mostly see dialog surfaces, not an empty dark
    background. Keep important text inside crop-safe inner boxes.
    """

    title: str
    subtitle: str
    left_title: str
    left_lines: tuple[str, ...]
    center_title: str
    center_subtitle: str
    right_title: str
    right_lines: tuple[str, ...]
    takeaway_top: str
    takeaway_bottom: str
    watermark: str = "terminal-whiteboard"


DEFAULT_PALETTE = Palette()

TERMINAL_WHITEBOARD_SPEC = VisualSpec(
    command="render-agent-visual",
    title="Agents need visuals, not design chores",
    subtitle="Turn structured ideas into terminal-whiteboard PNGs from a CLI.",
    left_label="manual design",
    left_title='"open a design tool"',
    left_bullets=("slow iteration", "inconsistent style", "hard to automate"),
    right_label="agent workflow",
    right_nodes=("post idea", "visual spec", "renderer", "png output"),
    arrow_label_top="+ structure",
    arrow_label_bottom="- design drag",
    takeaway="A good agent tool turns intent into a reusable artifact.",
    watermark="terminal-whiteboard",
    footer="# built by an agent, for agents",
)

DIALOG_ONLY_SPEC = DialogSpec(
    title="Smart model ≠ useful AI",
    subtitle="Useful AI comes from the layer around it.",
    left_title="MODEL ONLY",
    left_lines=("clever demo", "forgets context"),
    center_title="MODEL",
    center_subtitle="replaceable",
    right_title="OPERATING LAYER",
    right_lines=("access", "memory", "judgment"),
    takeaway_top="Not a leaderboard problem.",
    takeaway_bottom="A system design problem.",
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
        self.palette = palette or DEFAULT_PALETTE
        self.image = Image.new("RGB", (width, height), self.palette.bg)
        self.draw = ImageDraw.Draw(self.image)
        self.font_paths = self._load_font_paths()
        self.fonts = self._load_fonts()

    def _load_font_paths(self) -> dict[str, str | None]:
        mono_candidates = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        )
        mono_bold_candidates = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/System/Library/Fonts/Menlo.ttc",
        )
        hand_candidates = (
            os.path.expanduser("~/.fonts/kira/Caveat[wght].ttf"),
            "/usr/share/fonts/truetype/google-fonts/Caveat-Regular.ttf",
            "/System/Library/Fonts/Supplemental/MarkerFelt.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        )
        return {
            "mono": next((path for path in mono_candidates if os.path.exists(path)), None),
            "mono_bold": next((path for path in mono_bold_candidates if os.path.exists(path)), None),
            "hand": next((path for path in hand_candidates if os.path.exists(path)), None),
        }

    def _load_fonts(self) -> dict[str, ImageFont.FreeTypeFont | ImageFont.ImageFont]:
        mono = self.font_paths["mono"]
        mono_bold = self.font_paths["mono_bold"] or mono
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

    def floating_rect(
        self,
        box: Box,
        fill: RGB,
        outline: RGB | None = None,
        width: int = 3,
        radius: int = 24,
        shadow_offset: tuple[int, int] = (12, 16),
    ) -> None:
        """Draw a lifted rough card with a soft shadow."""

        x0, y0, x1, y1 = box
        shadow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        dx, dy = shadow_offset
        shadow_draw.rounded_rectangle([x0 + dx, y0 + dy, x1 + dx, y1 + dy], radius=radius, fill=(0, 0, 0, 120))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        self.image = Image.alpha_composite(self.image.convert("RGBA"), shadow).convert("RGB")
        self.draw = ImageDraw.Draw(self.image)
        self.rough_rect(box, fill=fill, outline=outline, width=width, radius=radius, passes=2)
        self.rough_line([(x0 + 26, y0 + 10), (x1 - 26, y0 + 10)], fill=(38, 52, 66), width=2, passes=1, amp=0.7)

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

    def fit_font(
        self,
        text: str,
        box: Box,
        max_size: int,
        min_size: int = 18,
        *,
        font_path: str | None = None,
        pad: int = 16,
    ) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        """Return the largest font that fits text inside box.

        Raises ValueError instead of silently overflowing. Agents can use this as
        an automated text-fit guard before sharing generated assets.
        """

        x0, y0, x1, y1 = box
        available_width = (x1 - x0) - 2 * pad
        available_height = (y1 - y0) - 2 * pad
        if available_width <= 0 or available_height <= 0:
            raise ValueError(f"Box is too small for padding: box={box}, pad={pad}")

        path = font_path or self.font_paths.get("mono")
        for size in range(max_size, min_size - 1, -2):
            font = ImageFont.truetype(path, size) if path else ImageFont.load_default()
            bbox = self.draw.textbbox((0, 0), text, font=font)
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
            if width <= available_width and height <= available_height:
                return font
        raise ValueError(f"Text does not fit: {text!r} in {box} with pad={pad}")

    def text_center_in_box(
        self,
        box: Box,
        text: str,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
        fill: RGB | None = None,
    ) -> None:
        x0, y0, x1, y1 = box
        bbox = self.draw.textbbox((0, 0), text, font=font)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        self.draw.text(
            ((x0 + x1 - width) / 2 - bbox[0], (y0 + y1 - height) / 2 - bbox[1]),
            text,
            font=font,
            fill=fill or self.palette.text,
        )

    def text_left_in_box(
        self,
        box: Box,
        text: str,
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
        fill: RGB | None = None,
        pad: int = 0,
    ) -> None:
        x0, y0, _x1, y1 = box
        bbox = self.draw.textbbox((0, 0), text, font=font)
        height = bbox[3] - bbox[1]
        self.draw.text(
            (x0 + pad - bbox[0], y0 + (y1 - y0 - height) / 2 - bbox[1]),
            text,
            font=font,
            fill=fill or self.palette.text,
        )

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

    prompt = "~/terminal $ "
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


def render_dialog_only(spec: DialogSpec, output: str, seed: int = 77, palette: Palette | None = None) -> str:
    renderer = TerminalWhiteboardRenderer(seed=seed, palette=palette)
    p = renderer.palette
    hand = renderer.font_paths["hand"]
    renderer.image = Image.new("RGB", (renderer.width, renderer.height), (24, 34, 49))
    renderer.draw = ImageDraw.Draw(renderer.image)

    header_fill = (24, 34, 49)
    left_fill = (35, 23, 27)
    center_fill = (16, 32, 51)
    right_fill = (16, 34, 25)
    footer_fill = (23, 32, 43)

    renderer.rough_rect((-8, -8, 1608, 270), fill=header_fill, outline=p.border, width=3, radius=30, passes=2)
    renderer.draw.ellipse([42, 38, 61, 57], fill=p.red)
    renderer.draw.ellipse([76, 38, 95, 57], fill=p.yellow)
    renderer.draw.ellipse([110, 38, 129, 57], fill=p.green)
    renderer.text((1350, 36), spec.watermark, "tiny", p.muted)

    renderer.text_center_in_box(
        (70, 88, 1530, 192),
        spec.title,
        renderer.fit_font(spec.title, (70, 88, 1530, 192), 96, 54, font_path=hand, pad=0),
        p.white,
    )
    renderer.text_center_in_box(
        (70, 185, 1530, 250),
        spec.subtitle,
        renderer.fit_font(spec.subtitle, (70, 185, 1530, 250), 48, 30, font_path=hand, pad=0),
        p.muted,
    )

    renderer.floating_rect((-18, 300, 545, 690), fill=left_fill, outline=p.red, width=4, radius=34)
    renderer.text_center_in_box(
        (40, 335, 510, 455),
        spec.left_title,
        renderer.fit_font(spec.left_title, (40, 335, 510, 455), 68, 34, font_path=hand, pad=14),
        p.red,
    )
    for line, box in zip(spec.left_lines[:2], ((55, 498, 500, 565), (55, 580, 500, 655)), strict=False):
        renderer.text_center_in_box(box, line, renderer.fit_font(line, box, 52, 28, font_path=hand, pad=8), p.muted)

    renderer.floating_rect((620, 388, 980, 600), fill=center_fill, outline=p.blue, width=4, radius=28)
    renderer.text_center_in_box(
        (655, 420, 945, 515),
        spec.center_title,
        renderer.fit_font(spec.center_title, (655, 420, 945, 515), 74, 38, font_path=hand, pad=10),
        p.blue,
    )
    renderer.text_center_in_box(
        (655, 515, 945, 582),
        spec.center_subtitle,
        renderer.fit_font(spec.center_subtitle, (655, 515, 945, 582), 44, 24, font_path=hand, pad=4),
        p.muted,
    )

    renderer.floating_rect((1055, 282, 1618, 704), fill=right_fill, outline=p.green, width=4, radius=36)
    renderer.text_center_in_box(
        (1088, 320, 1568, 435),
        spec.right_title,
        renderer.fit_font(spec.right_title, (1088, 320, 1568, 435), 62, 38, font_path=hand, pad=20),
        p.green,
    )
    for line, y in zip(spec.right_lines[:3], (486, 566, 646), strict=False):
        renderer.draw.ellipse([1110, y + 16, 1129, y + 35], fill=p.blue)
        box = (1162, y, 1560, y + 62)
        renderer.text_left_in_box(box, line, renderer.fit_font(line, box, 54, 34, font_path=hand, pad=0), p.white)

    renderer.arrow((548, 500), (616, 500), color=p.red, width=5)
    renderer.arrow((984, 500), (1052, 500), color=p.green, width=6)

    renderer.floating_rect((-8, 728, 1608, 908), fill=footer_fill, outline=p.border, width=3, radius=30)
    renderer.text_center_in_box(
        (80, 748, 1520, 815),
        spec.takeaway_top,
        renderer.fit_font(spec.takeaway_top, (80, 748, 1520, 815), 60, 38, font_path=hand, pad=0),
        p.blue,
    )
    renderer.text_center_in_box(
        (80, 810, 1520, 878),
        spec.takeaway_bottom,
        renderer.fit_font(spec.takeaway_bottom, (80, 810, 1520, 878), 60, 38, font_path=hand, pad=0),
        p.green,
    )

    return renderer.save(output)


def render_sample(output: str, seed: int = 77) -> str:
    return render_contrast(TERMINAL_WHITEBOARD_SPEC, output, seed=seed)


def render_dialog_sample(output: str, seed: int = 77) -> str:
    return render_dialog_only(DIALOG_ONLY_SPEC, output, seed=seed)
