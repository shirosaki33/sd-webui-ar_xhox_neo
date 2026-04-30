from __future__ import annotations

from math import gcd
from pathlib import Path
from typing import Iterable, List, Tuple

import gradio as gr
import modules.scripts as scripts

try:
    from modules.ui_components import ToolButton
except Exception:
    ToolButton = gr.Button

EXT_DIR = Path(scripts.basedir())

DEFAULT_SD15 = [
    "512*512 # 1:1",
    "512*768 # 2:3",
    "768*512 # 3:2",
    "768*1024 # 3:4",
    "1024*768 # 4:3",
    "1024*1024 # 1:1",
]

DEFAULT_SDXL = [
    "704*1408", "704*1344", "768*1344", "768*1280", "832*1216", "832*1152",
    "896*1152", "896*1088", "960*1088", "960*1024", "1024*960", "1088*960",
    "1088*896", "1152*896", "1152*832", "1216*832", "1280*768", "1344*768",
    "1344*704", "1408*704", "1472*704", "1536*640", "1600*640", "1664*576",
]

DEFAULT_CUSTOM = [
    "#1024*1024 # Example. Remove # to enable.",
    "640*480", "480*640", "1280*720", "720*1280", "1920*1080", "1080*1920",
]

DEFAULTS = {
    "SD15": DEFAULT_SD15,
    "SDXL": DEFAULT_SDXL,
    "Custom": DEFAULT_CUSTOM,
}


def ratio_label(width: int, height: int) -> str:
    common = {
        (768, 1366): (9, 16),
        (1366, 768): (16, 9),
        (1564, 670): (21, 9),
    }
    rw, rh = common.get((width, height), (None, None))
    if rw is None:
        d = gcd(width, height) or 1
        rw, rh = width // d, height // d
    return f"{width}x{height} | {rw}:{rh}"


def ensure_resolution_file(kind: str) -> Path:
    path = EXT_DIR / f"{kind}_resolutions.txt"
    if not path.exists():
        path.write_text("\n".join(DEFAULTS[kind]) + "\n", encoding="utf-8")
    return path


def parse_resolution_line(line: str):
    raw = line.strip()
    if not raw or raw.startswith("#") or "*" not in raw:
        return None
    value, _, comment = raw.partition("#")
    width_s, sep, height_s = value.partition("*")
    if sep != "*":
        return None
    try:
        width = int(width_s.strip())
        height = int(height_s.strip())
    except ValueError:
        print(f"[sd-webui-ar-neo] Skipping invalid resolution line: {line.rstrip()}")
        return None
    if width <= 0 or height <= 0:
        return None
    return width, height, comment.strip()


def read_resolutions(kind: str) -> List[Tuple[int, int, str]]:
    path = ensure_resolution_file(kind)
    out: List[Tuple[int, int, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        parsed = parse_resolution_line(line)
        if parsed:
            out.append(parsed)
    return out


def reduced_ratio_text(width, height) -> str:
    try:
        width = int(float(width or 0))
        height = int(float(height or 0))
    except Exception:
        return "Aspect Ratio: **-**"
    if width <= 0 or height <= 0:
        return "Aspect Ratio: **-**"
    d = gcd(width, height) or 1
    return f"Aspect Ratio: **{width // d}:{height // d}**"


def solve_height(width2, width1, height1):
    try:
        return round(float(width2) / (float(width1) / float(height1)))
    except Exception:
        return 0


def solve_width(height2, width1, height1):
    try:
        return round(float(height2) * (float(width1) / float(height1)))
    except Exception:
        return 0


class AspectRatioNeoScript(scripts.Script):
    def title(self):
        return "Aspect Ratio picker Neo"

    def show(self, is_img2img):
        return scripts.AlwaysVisible

    def _button(self, tab: str, width: int, height: int, comment: str = ""):
        label = ratio_label(width, height)
        elem_id = f"arx_btn_{tab}_{width}_{height}"
        return gr.Button(
            value=label,
            elem_id=elem_id,
            elem_classes=["arx-resolution-button"],
            tooltip=comment or f"Set {width} x {height}",
            variant="secondary",
            size="sm",
        )

    def _render_group(self, tab: str, title: str, kind: str, cols: int = 6):
        gr.Markdown(f"**{title}**")
        resolutions = read_resolutions(kind)
        for i in range(0, len(resolutions), cols):
            with gr.Row(elem_classes=["arx-resolution-row"]):
                for width, height, comment in resolutions[i:i + cols]:
                    self._button(tab, width, height, comment)

    def ui(self, is_img2img):
        tab = "img2img" if is_img2img else "txt2img"
        with gr.Accordion(open=True, label=self.title(), elem_id=f"arx_{tab}_container"):
            self._render_group(tab, "SD1.5 resolutions", "SD15")
            self._render_group(tab, "SDXL base resolutions", "SDXL")
            with gr.Accordion(open=False, label="Custom resolutions"):
                self._render_group(tab, "Custom", "Custom")

            with gr.Accordion(open=False, label="Aspect Ratio Calculator", elem_id=f"arx_calc_{tab}"):
                with gr.Row():
                    with gr.Column(min_width=120):
                        width1 = gr.Number(label="Width 1", value=1024, precision=0)
                        height1 = gr.Number(label="Height 1", value=1024, precision=0)
                    with gr.Column(min_width=120):
                        width2 = gr.Number(label="Width 2", value=0, precision=0)
                        height2 = gr.Number(label="Height 2", value=0, precision=0)
                    ratio = gr.Markdown(value="Aspect Ratio: **1:1**")
                with gr.Row():
                    get_current = gr.Button("⬇️ Get current", elem_id=f"arx_get_current_{tab}", size="sm")
                    swap = gr.Button("⇅ Swap", size="sm")
                    calc_h = gr.Button("Calculate Height", size="sm")
                    calc_w = gr.Button("Calculate Width", size="sm")
                    apply = gr.Button("Apply", elem_id=f"arx_apply_calc_{tab}", size="sm")

                swap.click(lambda w1, h1, w2, h2: (h1, w1, h2, w2), [width1, height1, width2, height2], [width1, height1, width2, height2])
                calc_h.click(solve_height, [width2, width1, height1], [height2])
                calc_w.click(solve_width, [height2, width1, height1], [width2])
                width1.change(reduced_ratio_text, [width1, height1], [ratio])
                height1.change(reduced_ratio_text, [width1, height1], [ratio])

        return []
