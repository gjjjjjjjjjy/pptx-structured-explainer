#!/usr/bin/env python3
"""Render a constrained diagram JSON document into a presentation-ready SVG."""

from __future__ import annotations

import argparse
import json
import math
import unicodedata
from html import escape
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_THEME = SKILL_DIR / "assets" / "themes" / "metax-light.json"


def load_theme(spec: dict) -> dict:
    with DEFAULT_THEME.open(encoding="utf-8") as stream:
        theme = json.load(stream)
    theme.update(spec.get("theme_overrides", {}))
    return theme


def number(value, default=0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def text_units(value: str) -> float:
    units = 0.0
    for char in value:
        if unicodedata.east_asian_width(char) in {"W", "F", "A"}:
            units += 1.0
        elif char.isspace():
            units += 0.35
        else:
            units += 0.56
    return units


def wrap_text(value: str, max_units: float, max_lines: int = 4) -> list[str]:
    value = " ".join(str(value).split())
    if not value:
        return [""]
    lines = []
    current = ""
    current_units = 0.0
    for char in value:
        char_units = text_units(char)
        if current and current_units + char_units > max_units:
            lines.append(current.rstrip())
            current = char.lstrip()
            current_units = text_units(current)
            if len(lines) == max_lines - 1:
                break
        else:
            current += char
            current_units += char_units
    consumed = "".join(lines) + current
    if len(consumed) < len(value):
        remainder = value[len("".join(lines)) :]
        last = remainder[: max(1, int(max_units / 0.56) - 1)].rstrip()
        current = f"{last}…"
    lines.append(current.rstrip())
    return lines[:max_lines]


class SVG:
    def __init__(self, width: int, height: int, theme: dict):
        self.width = width
        self.height = height
        self.theme = theme
        self.parts = []
        self.parts.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img">'
        )
        self.parts.append(
            """<defs>
  <filter id="softShadow" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#172033" flood-opacity="0.10"/>
  </filter>
  <marker id="arrow" markerWidth="12" markerHeight="12" refX="10" refY="6" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L12,6 L0,12 z" fill="#94A3B8"/>
  </marker>
</defs>"""
        )
        self.rect(0, 0, width, height, fill=theme["background"], rx=0, stroke="none")

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def rect(self, x, y, width, height, *, fill, stroke="none", sw=1.5, rx=18, opacity=1, shadow=False):
        filter_attr = ' filter="url(#softShadow)"' if shadow else ""
        self.add(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{width:.1f}" height="{height:.1f}" '
            f'rx="{rx}" fill="{fill}" fill-opacity="{opacity}" stroke="{stroke}" '
            f'stroke-width="{sw}"{filter_attr}/>'
        )

    def line(self, x1, y1, x2, y2, *, stroke, sw=3, dash=None, arrow=False, opacity=1):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        arrow_attr = ' marker-end="url(#arrow)"' if arrow else ""
        self.add(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{stroke}" stroke-width="{sw}" stroke-opacity="{opacity}" '
            f'stroke-linecap="round"{dash_attr}{arrow_attr}/>'
        )

    def path(self, d: str, *, stroke, sw=3, fill="none", dash=None, arrow=False, opacity=1):
        dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
        arrow_attr = ' marker-end="url(#arrow)"' if arrow else ""
        self.add(
            f'<path d="{d}" stroke="{stroke}" stroke-width="{sw}" fill="{fill}" '
            f'stroke-opacity="{opacity}" stroke-linecap="round" stroke-linejoin="round"'
            f'{dash_attr}{arrow_attr}/>'
        )

    def circle(self, cx, cy, r, *, fill, stroke="none", sw=1.5):
        self.add(
            f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>'
        )

    def text(self, x, y, value, *, size=24, fill=None, weight=400, anchor="start", family=None, opacity=1):
        fill = fill or self.theme["text"]
        family = family or self.theme["font_family"]
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" fill-opacity="{opacity}" '
            f'font-family="{escape(family)}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}">{escape(str(value))}</text>'
        )

    def multiline(self, x, y, value, *, max_units, size=24, line_height=1.35, fill=None,
                  weight=400, anchor="start", max_lines=4):
        lines = wrap_text(value, max_units, max_lines)
        fill = fill or self.theme["text"]
        family = self.theme["font_family"]
        spans = []
        for index, line in enumerate(lines):
            dy = 0 if index == 0 else size * line_height
            spans.append(f'<tspan x="{x:.1f}" dy="{dy:.1f}">{escape(line)}</tspan>')
        self.add(
            f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{escape(family)}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">'
            + "".join(spans)
            + "</text>"
        )

    def finish(self, title: str | None = None, description: str | None = None) -> str:
        accessibility = []
        if title:
            accessibility.append(f"<title>{escape(title)}</title>")
        if description:
            accessibility.append(f"<desc>{escape(description)}</desc>")
        self.parts[1:1] = accessibility
        self.parts.append("</svg>")
        return "\n".join(self.parts)


def header(svg: SVG, spec: dict) -> float:
    svg.text(72, 76, spec.get("title", ""), size=40, weight=700)
    subtitle = spec.get("subtitle")
    if subtitle:
        svg.text(72, 116, subtitle, size=20, fill=svg.theme["muted"])
        return 160
    return 128


def tone(theme: dict, name: str) -> tuple[str, str]:
    color = theme.get(name, theme["blue"])
    pale = {
        theme["blue"]: "#EEF5FF",
        theme["green"]: "#EAF8F3",
        theme["orange"]: "#FFF6E8",
        theme["red"]: "#FDEEEE",
        theme["purple"]: "#F2EEFF",
        theme["accent"]: "#F8EEF7",
    }.get(color, theme["surface_alt"])
    return color, pale


def render_task_tree(svg: SVG, spec: dict, top: float) -> None:
    tasks = spec.get("tasks", [])
    if not tasks:
        raise ValueError("task-tree requires at least one task")
    root_w, root_h = 230, 92
    root_x, root_y = 65, top + (svg.height - top - root_h) / 2
    svg.rect(root_x, root_y, root_w, root_h, fill=svg.theme["text"], rx=24, shadow=True)
    svg.multiline(root_x + root_w / 2, root_y + 42, spec.get("root", "任务"), max_units=12,
                  size=24, fill="#FFFFFF", weight=700, anchor="middle", max_lines=2)

    available_h = svg.height - top - 70
    task_gap = 28
    task_block_h = min(250, (available_h - task_gap * (len(tasks) - 1)) / len(tasks))
    task_x, task_w = 420, 285
    item_x, item_w = 860, svg.width - 930
    for index, task in enumerate(tasks):
        block_y = top + 20 + index * (task_block_h + task_gap)
        task_h = min(96, task_block_h)
        task_y = block_y + (task_block_h - task_h) / 2
        color, pale = tone(svg.theme, task.get("tone", "blue"))
        svg.path(
            f"M {root_x + root_w} {root_y + root_h/2} "
            f"C {root_x + root_w + 70} {root_y + root_h/2}, {task_x - 80} {task_y + task_h/2}, {task_x} {task_y + task_h/2}",
            stroke=color, sw=4,
        )
        svg.rect(task_x, task_y, task_w, task_h, fill=pale, stroke=color, sw=2, rx=22)
        svg.multiline(task_x + 26, task_y + 40, task.get("title", f"任务{index+1}"), max_units=15,
                      size=25, weight=700, max_lines=2)

        items = task.get("items", [])
        if not items:
            continue
        item_gap = 18
        item_h = max(82, (task_block_h - item_gap * (len(items) - 1)) / len(items))
        first_center = block_y + item_h / 2
        last_center = block_y + (len(items) - 1) * (item_h + item_gap) + item_h / 2
        junction_x = item_x - 90
        svg.path(
            f"M {task_x + task_w} {task_y + task_h/2} C {task_x + task_w + 55} {task_y + task_h/2}, "
            f"{junction_x - 35} {(first_center + last_center)/2}, {junction_x} {(first_center + last_center)/2}",
            stroke=color, sw=4,
        )
        if len(items) > 1:
            svg.line(junction_x, first_center, junction_x, last_center, stroke=color, sw=4)
        for item_index, item in enumerate(items):
            item_y = block_y + item_index * (item_h + item_gap)
            center_y = item_y + item_h / 2
            svg.path(
                f"M {junction_x} {center_y} C {junction_x + 40} {center_y}, {item_x - 35} {center_y}, {item_x} {center_y}",
                stroke=color, sw=4,
            )
            svg.rect(item_x, item_y, item_w, item_h, fill="#FFFFFF", stroke=svg.theme["line"], sw=1.5,
                     rx=20, shadow=True)
            svg.text(item_x + 26, item_y + 34, item.get("label", "说明"), size=20, fill=color, weight=700)
            svg.multiline(item_x + 26, item_y + 68, item.get("text", ""), max_units=max(18, item_w / 24),
                          size=20, fill=svg.theme["text"], max_lines=2)


def render_flow(svg: SVG, spec: dict, top: float) -> None:
    nodes = spec.get("nodes", [])
    if not nodes:
        raise ValueError("flow requires nodes")
    horizontal = spec.get("direction", "horizontal") != "vertical"
    edge_map = {(edge.get("from"), edge.get("to")): edge for edge in spec.get("edges", [])}
    if horizontal:
        gap = 54
        usable_w = svg.width - 144 - gap * (len(nodes) - 1)
        node_w = min(280, usable_w / len(nodes))
        node_h = 180
        y = top + (svg.height - top - node_h) / 2
        positions = []
        for index, node in enumerate(nodes):
            x = 72 + index * (node_w + gap)
            positions.append((x, y))
            color, pale = tone(svg.theme, node.get("tone", ["blue", "green", "purple", "orange"][index % 4]))
            svg.rect(x, y, node_w, node_h, fill=pale, stroke=color, sw=2, rx=24, shadow=True)
            svg.circle(x + 34, y + 34, 17, fill=color)
            svg.text(x + 34, y + 41, str(index + 1), size=17, fill="#FFFFFF", weight=700, anchor="middle")
            svg.multiline(x + 28, y + 82, node.get("title", node.get("id", "")), max_units=node_w / 22,
                          size=25, weight=700, max_lines=2)
            svg.multiline(x + 28, y + 128, node.get("description", ""), max_units=node_w / 18,
                          size=18, fill=svg.theme["muted"], max_lines=2)
        for index in range(len(nodes) - 1):
            x1, y1 = positions[index]
            x2, y2 = positions[index + 1]
            svg.line(x1 + node_w + 10, y1 + node_h / 2, x2 - 12, y2 + node_h / 2,
                     stroke="#94A3B8", sw=3, arrow=True)
            edge = edge_map.get((nodes[index].get("id"), nodes[index + 1].get("id")))
            if edge and edge.get("label"):
                svg.text((x1 + node_w + x2) / 2, y1 + node_h / 2 - 18, edge["label"],
                         size=16, fill=svg.theme["muted"], anchor="middle")
    else:
        gap = 30
        node_w = min(720, svg.width - 300)
        node_h = min(112, (svg.height - top - 60 - gap * (len(nodes) - 1)) / len(nodes))
        x = (svg.width - node_w) / 2
        for index, node in enumerate(nodes):
            y = top + 15 + index * (node_h + gap)
            color, pale = tone(svg.theme, node.get("tone", "blue"))
            svg.rect(x, y, node_w, node_h, fill=pale, stroke=color, sw=2, rx=22, shadow=True)
            svg.circle(x + 42, y + node_h / 2, 18, fill=color)
            svg.text(x + 42, y + node_h / 2 + 6, str(index + 1), size=17, fill="#FFFFFF", weight=700,
                     anchor="middle")
            svg.text(x + 80, y + 42, node.get("title", ""), size=24, weight=700)
            svg.text(x + 80, y + 75, node.get("description", ""), size=18, fill=svg.theme["muted"])
            if index < len(nodes) - 1:
                svg.line(svg.width / 2, y + node_h + 5, svg.width / 2, y + node_h + gap - 7,
                         stroke="#94A3B8", sw=3, arrow=True)


def render_comparison(svg: SVG, spec: dict, top: float) -> None:
    columns = spec.get("columns", [])
    if len(columns) < 2:
        raise ValueError("comparison requires at least two columns")
    gap = 36
    column_w = (svg.width - 144 - gap * (len(columns) - 1)) / len(columns)
    card_y = top + 24
    card_h = svg.height - card_y - 62
    for index, column in enumerate(columns):
        x = 72 + index * (column_w + gap)
        color, pale = tone(svg.theme, column.get("tone", "blue"))
        svg.rect(x, card_y, column_w, card_h, fill="#FFFFFF", stroke=svg.theme["line"], rx=26, shadow=True)
        svg.rect(x, card_y, column_w, 104, fill=pale, stroke="none", rx=26)
        svg.text(x + 32, card_y + 62, column.get("title", f"方案{index+1}"), size=30, weight=700, fill=color)
        items = column.get("items", [])
        item_h = min(110, (card_h - 142) / max(1, len(items)))
        for item_index, item in enumerate(items):
            y = card_y + 132 + item_index * item_h
            svg.circle(x + 38, y + 22, 8, fill=color)
            svg.multiline(x + 60, y + 29, item, max_units=column_w / 20, size=21, max_lines=3)


def render_timeline(svg: SVG, spec: dict, top: float) -> None:
    events = spec.get("events", [])
    if not events:
        raise ValueError("timeline requires events")
    y = top + (svg.height - top) / 2
    left, right = 120, svg.width - 120
    svg.line(left, y, right, y, stroke=svg.theme["line"], sw=7)
    step = (right - left) / max(1, len(events) - 1)
    for index, event in enumerate(events):
        x = left + index * step
        color, pale = tone(svg.theme, event.get("tone", ["blue", "green", "purple", "orange"][index % 4]))
        svg.circle(x, y, 23, fill="#FFFFFF", stroke=color, sw=6)
        above = index % 2 == 0
        card_w, card_h = min(310, step * 0.8 if len(events) > 1 else 360), 145
        card_x = max(48, min(svg.width - card_w - 48, x - card_w / 2))
        card_y = y - card_h - 70 if above else y + 70
        svg.line(x, y - 28 if above else y + 28, x, card_y + card_h if above else card_y,
                 stroke=color, sw=3, dash="6 8")
        svg.rect(card_x, card_y, card_w, card_h, fill=pale, stroke=color, sw=2, rx=22)
        svg.text(card_x + 24, card_y + 45, event.get("title", ""), size=23, weight=700, fill=color)
        svg.multiline(card_x + 24, card_y + 82, event.get("description", ""), max_units=card_w / 19,
                      size=18, fill=svg.theme["muted"], max_lines=2)


def render_matrix(svg: SVG, spec: dict, top: float) -> None:
    values = spec.get("values", [])
    rows = len(values)
    columns = max((len(row) for row in values), default=0)
    if not rows or not columns:
        raise ValueError("matrix requires a non-empty values array")
    row_labels = spec.get("row_labels", [str(i + 1) for i in range(rows)])
    column_labels = spec.get("column_labels", [str(i + 1) for i in range(columns)])
    grid_size = min(580, svg.height - top - 100, svg.width * 0.48)
    cell = min(82, grid_size / max(rows, columns))
    grid_w, grid_h = columns * cell, rows * cell
    grid_x = 130
    grid_y = top + 74
    svg.text(grid_x + grid_w / 2, grid_y - 42, "Key位置", size=19, fill=svg.theme["muted"], anchor="middle")
    svg.text(54, grid_y + grid_h / 2, "Query位置", size=19, fill=svg.theme["muted"], anchor="middle")
    for column in range(columns):
        svg.text(grid_x + column * cell + cell / 2, grid_y - 12,
                 column_labels[column] if column < len(column_labels) else str(column + 1),
                 size=18, fill=svg.theme["muted"], anchor="middle")
    labels = {str(key): value for key, value in spec.get("value_labels", {}).items()}
    for row in range(rows):
        svg.text(grid_x - 22, grid_y + row * cell + cell / 2 + 6,
                 row_labels[row] if row < len(row_labels) else str(row + 1),
                 size=18, fill=svg.theme["muted"], anchor="end")
        for column in range(columns):
            value = values[row][column] if column < len(values[row]) else ""
            blocked = number(value, 0) < 0 or str(value).lower() in {"x", "false", "blocked"}
            fill = "#FDEEEE" if blocked else "#EAF8F3"
            stroke = svg.theme["red"] if blocked else svg.theme["green"]
            x, y = grid_x + column * cell, grid_y + row * cell
            svg.rect(x + 3, y + 3, cell - 6, cell - 6, fill=fill, stroke=stroke, sw=1.3, rx=12)
            value_key = str(value)
            label = labels.get(value_key, "屏蔽" if blocked else "可见")
            svg.text(x + cell / 2, y + cell / 2 + 7, label, size=16, fill=stroke, weight=700,
                     anchor="middle")

    note_x = grid_x + grid_w + 100
    note_w = svg.width - note_x - 80
    svg.rect(note_x, grid_y, note_w, min(grid_h, 360), fill=svg.theme["surface"],
             stroke=svg.theme["line"], rx=24)
    svg.text(note_x + 32, grid_y + 54, spec.get("note_title", "矩阵含义"), size=27, weight=700)
    notes = spec.get("notes", ["绿色单元格：允许当前Query读取该Key", "红色单元格：在Softmax前加入负大值"])
    for index, note in enumerate(notes):
        color = svg.theme["green"] if index == 0 else svg.theme["red"]
        y = grid_y + 108 + index * 92
        svg.circle(note_x + 38, y - 6, 9, fill=color)
        svg.multiline(note_x + 62, y, note, max_units=note_w / 20, size=20, max_lines=3)


RENDERERS = {
    "task-tree": render_task_tree,
    "flow": render_flow,
    "comparison": render_comparison,
    "timeline": render_timeline,
    "matrix": render_matrix,
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with args.input.open(encoding="utf-8") as stream:
        spec = json.load(stream)
    diagram_type = spec.get("type")
    if diagram_type not in RENDERERS:
        parser.error(f"unsupported diagram type: {diagram_type!r}; choose {', '.join(RENDERERS)}")
    canvas = spec.get("canvas", {})
    width = int(canvas.get("width", 1600))
    height = int(canvas.get("height", 900))
    if width < 640 or height < 360:
        parser.error("canvas must be at least 640x360")
    theme = load_theme(spec)
    svg = SVG(width, height, theme)
    top = header(svg, spec)
    RENDERERS[diagram_type](svg, spec, top)
    markup = svg.finish(spec.get("title"), spec.get("subtitle"))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markup, encoding="utf-8")
    print(f"type={diagram_type}")
    print(f"canvas={width}x{height}")
    print(f"output={args.output.resolve()}")


if __name__ == "__main__":
    main()
