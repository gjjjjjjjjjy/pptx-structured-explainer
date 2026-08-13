# Structured Diagram Specification

## Contents

1. Common fields
2. Task tree
3. Flow
4. Comparison
5. Timeline
6. Matrix
7. Theme overrides

## Common fields

Every JSON document accepts:

```json
{
  "type": "flow",
  "title": "Diagram title",
  "subtitle": "Optional one-line context",
  "canvas": {"width": 1600, "height": 900},
  "theme": "metax-light"
}
```

Use a 1600×900 canvas for 16:9 slides. Keep labels concise; let the renderer wrap descriptions. Do not provide coordinates in structured mode.

## Task tree

```json
{
  "type": "task-tree",
  "title": "实验任务",
  "root": "C500推理实验",
  "tasks": [
    {
      "title": "任务1（必做）",
      "tone": "blue",
      "items": [
        {"label": "任务说明", "text": "完成Cache与No Cache对照"},
        {"label": "验收标准", "text": "输出一致并记录性能指标"}
      ]
    }
  ]
}
```

## Flow

```json
{
  "type": "flow",
  "title": "推理执行路径",
  "direction": "horizontal",
  "nodes": [
    {"id": "a", "title": "Prompt", "description": "输入Token"},
    {"id": "b", "title": "Prefill", "description": "写入历史K/V"},
    {"id": "c", "title": "Decode", "description": "逐Token生成"}
  ],
  "edges": [
    {"from": "a", "to": "b"},
    {"from": "b", "to": "c", "label": "复用Cache"}
  ]
}
```

Structured flow uses the listed node order. Edges should normally connect adjacent nodes; choose custom mode for complex cross-links.

## Comparison

```json
{
  "type": "comparison",
  "title": "Cache与No Cache",
  "columns": [
    {"title": "No Cache", "tone": "orange", "items": ["完整序列Forward", "重复计算历史K/V"]},
    {"title": "Cache", "tone": "green", "items": ["单Token Decode", "读取并追加历史K/V"]}
  ]
}
```

## Timeline

```json
{
  "type": "timeline",
  "title": "一次生成请求",
  "events": [
    {"title": "Prompt进入", "description": "请求开始"},
    {"title": "首Token", "description": "TTFT结束"},
    {"title": "连续Decode", "description": "按TPOT逐Token输出"}
  ]
}
```

## Matrix

```json
{
  "type": "matrix",
  "title": "Causal Mask",
  "row_labels": ["Q1", "Q2", "Q3"],
  "column_labels": ["K1", "K2", "K3"],
  "values": [[0, -1, -1], [0, 0, -1], [0, 0, 0]],
  "value_labels": {"0": "可见", "-1": "屏蔽"}
}
```

Use structured matrix for stable educational grids. Use custom mode when the matrix must connect to Softmax, tokens, formulas, or a decode timeline.

## Theme overrides

Use a bundled theme name or override only semantic tokens:

```json
{
  "theme_overrides": {
    "accent": "#8A1C7C",
    "success": "#168A68",
    "warning": "#F59E0B"
  }
}
```

Do not ask weak models to define every font, stroke, radius, or spacing value.
