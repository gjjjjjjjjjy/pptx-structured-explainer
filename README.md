# pptx-structured-explainer

一个用于设计、修改和验证**专业知识讲解型 PowerPoint** 的 Skill，可用于 Claude Code 和 Codex。

它支持两条工作流：

- **从零制作**——给一个主题、一份文档或一个代码仓库，依次确认受众与知识结构、模板与交付格式、幻灯片标题、Markdown 文稿、统一 SVG 风格，然后批量生成可编辑的 PPT。
- **修改现有 PPT**——先盘点结构并重建讲解链条，报告术语突兀、顺序错乱、证据缺失、整页图片等问题，在你确认修改边界后才动手，保留其余页面和你已有的图表、模板与媒体。

两条路径都以同一套要求收尾：内容由浅入深、术语首次出现即解释、正文保持可编辑、媒体全部内嵌，并通过结构、视觉、媒体和可移植性 QA。

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

安装后直接描述任务即可，Skill 会引导完成确认流程。

**从零制作**（可以从主题、Markdown、文档或代码仓库出发）：

```text
就这个主题做一套课件，讲清楚原理和验证方法。
```

```text
把这份文档整理成一套由浅入深、术语解释清晰的课件。
```

```text
按这个代码仓库的实现，做一套讲清楚执行路径的技术分享 PPT。
```

**修改现有 PPT：**

```text
盘点这个 PPT 的讲解链条，指出术语突兀、顺序错乱和整页图片的问题。
```

```text
这几页的文字被做成了图片，改回可编辑的原生文本，其他页不要动。
```

从零制作时，Skill 会依次确认目的与受众、大纲与核心知识点、模板与交付格式、幻灯片标题、Markdown 文稿、SVG 风格样例，然后才批量生成图示并构建 PPT——除非你明确要求跳过某个确认环节，否则不会直接开始生成。修改现有 PPT 时，会先盘点并报告问题，在你确认修改边界后才动手，且只改确认范围内的内容。两种情况下，引入新视觉系统都是先做一页样例，通过后再批量应用。

## 依赖

| 用途 | 依赖 |
| --- | --- |
| 读取、编辑、渲染、校验 `.pptx` | 另行安装的 `pptx` skill |
| `inventory_pptx.py` | `python-pptx` |
| `audit_media.py` | `defusedxml` |
| 最终渲染检查 | Microsoft PowerPoint（可用时） |

```bash
pip install python-pptx defusedxml
```

本 Skill 只负责内容设计与确认流程，所有 PowerPoint 的读写、渲染和校验操作都交给 `pptx` skill 完成。渲染检查优先使用 Microsoft PowerPoint，中文排版、GIF、SVG 和动画在其他渲染器上不一定能如实复现。

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
