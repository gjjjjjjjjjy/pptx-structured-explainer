# pptx-structured-explainer

一个用于设计、修改和验证专业知识讲解型 PowerPoint 的 Codex Skill。

它强调先确认受众、知识结构、模板和 Markdown 文稿，再统一 SVG 视觉风格并生成可编辑的 PPT。对于已有演示文稿，会先理解原有内容和讲解链条，并在确认范围内修改，保留用户已有的图表、模板和媒体。

## 主要能力

- 从主题、Markdown、文档、代码仓库或现有 PPT 设计演示文稿
- 按照由浅入深的知识依赖组织内容
- 在专业术语首次出现时就近解释必要概念
- 先确认统一 SVG 风格，再批量制作图示
- 优先使用 PowerPoint 原生文字、形状、表格和图表，保持内容可编辑
- 检查外部媒体链接、本地路径泄漏和缺失资源
- 支持现有 PPT 的结构盘点、局部修改和可移植性验证
- 可在没有平台专用 PPT Skill 时，使用 Python 与 LibreOffice 完成跨平台检查和渲染
- 强制区分源文件缺陷与渲染器兼容问题，避免把漏渲染误判为页面内容缺失
- 检查教学课件的“概念—代码—命令—结果—验收”实验闭环
- 安装后自带 PPTX 结构读取、可编辑创建、文字替换、渲染和媒体检查工具

## 目录结构

```text
pptx-structured-explainer/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── content-and-language.md
│   ├── existing-deck-workflow.md
│   ├── qa-and-portability.md
│   ├── svg-and-layout.md
│   ├── template-and-format.md
│   ├── toolchain.md
│   └── pptx-operations.md
├── requirements.txt
├── examples/
│   └── minimal-deck.json
└── scripts/
    ├── audit_media.py
    ├── check_environment.py
    ├── create_pptx.py
    ├── inventory_pptx.py
    ├── make_contact_sheet.py
    ├── replace_text.py
    └── render_pptx.py
```

## 使用方式

将本目录安装到 Codex 的 Skills 目录，或在支持本地 Skill 的工作环境中引用。典型请求：

```text
使用 $pptx-structured-explainer 将我的主题或现有 PPT 整理成由浅入深、术语解释清晰的演示文稿。
```

处理 `.pptx` 文件时，优先使用当前智能体环境提供的专业 PPT 工具。如果没有，可安装公开依赖：

```bash
python -m pip install -r requirements.txt
```

跨平台渲染脚本还需要安装 LibreOffice。完整工具选择与能力边界见 `references/toolchain.md`。

没有平台专用 PPT Skill 时，可直接使用仓库内的操作脚本：

```bash
python scripts/check_environment.py
python scripts/create_pptx.py deck.json --output deck.pptx
python scripts/replace_text.py source.pptx replacements.json --output reviewed.pptx
python scripts/render_pptx.py reviewed.pptx --output-dir rendered
```

详细 JSON 格式和安全边界见 `references/pptx-operations.md`。

## License

本项目采用 [MIT License](LICENSE)。
