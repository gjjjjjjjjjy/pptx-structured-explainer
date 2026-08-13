# pptx-structured-explainer

一个用于设计、修改和验证**专业知识讲解型 PowerPoint** 的 Skill，可用于 Claude Code 和 Codex。

它解决的是这样一类问题：内容本身没错，但讲解链条断裂、术语突然出现、结论没有证据，或者整页被做成一张图片导致无法编辑和检索。本 Skill 强制先确认受众与知识结构，再确认模板和 Markdown 文稿，最后才生成可编辑的 PPT，并对结构、视觉、媒体内嵌和可移植性做完整 QA。

## 主要能力

- 从主题、Markdown、文档、代码仓库或现有 PPT 设计演示文稿
- 按照由浅入深的知识依赖组织内容（概念先于机制、指标定义先于结果表、正确性先于性能）
- 在专业术语首次出现时就近解释；缩写必须同时给出展开形式和释义
- 先确认统一 SVG 风格，再批量制作图示
- 优先使用 PowerPoint 原生文字、形状、表格和图表，保持内容可编辑
- 检查外部媒体链接、本地路径泄漏和缺失资源
- 支持现有 PPT 的结构盘点、局部修改和可移植性验证

## 安装

### Claude Code

Skill 目录放到下面任一位置即可被自动发现：

| 位置 | 作用范围 |
| --- | --- |
| `~/.claude/skills/pptx-structured-explainer/` | 个人全局，所有项目可用 |
| `<项目>/.claude/skills/pptx-structured-explainer/` | 仅该项目，可随仓库提交共享 |

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/gjjjjjjjjjy/pptx-structured-explainer.git \
  ~/.claude/skills/pptx-structured-explainer
```

安装后用 `/pptx-structured-explainer` 调用，或直接描述任务让 Claude 自行匹配（`SKILL.md` 的 `description` 字段决定匹配时机）。用 `/doctor` 可确认 Skill 已被加载。

### Codex

将本目录安装到 Codex 的 Skills 目录，`agents/openai.yaml` 提供显示名称和默认提示词。

## 使用方式

安装后直接描述任务即可，Skill 会引导完成确认流程：

```text
把这份实验手册整理成一套由浅入深、术语解释清晰的课件。
```

```text
盘点这个 PPT 的讲解链条，指出术语突兀、顺序错乱和整页图片的问题。
```

```text
这几页的文字被做成了图片，改回可编辑的原生文本，其他页不要动。
```

处理现有 PPT 时，Skill 会先盘点结构并报告问题，在你确认修改边界后才动手；引入新视觉系统时先做一页样例，通过后再批量应用。

## 依赖

| 用途 | 依赖 |
| --- | --- |
| 读写 `.pptx` | Claude Code 内置的 `pptx` skill，或其他 PPTX 工具链 |
| `inventory_pptx.py` | `python-pptx` |
| `audit_media.py` | `defusedxml` |
| 渲染检查（推荐） | Microsoft PowerPoint，或 LibreOffice |

```bash
pip install python-pptx defusedxml
```

中文课件建议用 Microsoft PowerPoint 做最终渲染检查，字体替换和中文排版问题在其他渲染器上不一定能复现。

## 辅助脚本

```bash
# 逐页结构盘点：标题、可编辑文本数、图片、表格、备注、版式
python scripts/inventory_pptx.py deck.pptx
python scripts/inventory_pptx.py deck.pptx --json

# 媒体审计：外链、本地路径泄漏、缺失关系目标
python scripts/audit_media.py deck.pptx
```

`audit_media.py` 通过时打印 `PASS`，发现问题时打印 `FAIL` 并以非零状态退出，可直接用于 CI 或提交前检查。

## 目录结构

```text
pptx-structured-explainer/
├── SKILL.md                        # 主流程与核心约束
├── agents/
│   └── openai.yaml                 # Codex 界面配置
├── references/
│   ├── content-and-language.md     # 大纲、标题、术语、语言与深度要求
│   ├── existing-deck-workflow.md   # 现有 PPT 的盘点与安全修改流程
│   ├── qa-and-portability.md       # 内容/结构/视觉/媒体/可移植性检查清单
│   ├── svg-and-layout.md           # SVG 风格、版面与图示规范
│   └── template-and-format.md      # 模板检查与交付格式确认
└── scripts/
    ├── audit_media.py
    └── inventory_pptx.py
```

`SKILL.md` 是入口，`references/` 按需加载——不必一次读完。

## License

本项目采用 [MIT License](LICENSE)。
