# pptx-structured-explainer

一套用于设计、修改和验证**专业知识讲解型 PowerPoint** 的 Skills，可用于 Claude Code 和 Codex。仓库包含三个可一起安装的能力：

- `pptx-structured-explainer`：理解主题、组织知识链条、确认大纲和文稿、统一视觉语言；
- `pptx-operator`：读取、创建、编辑、渲染并校验 `.pptx` / `.potx` 文件；
- `svg-diagram-engine`：弱模型用结构化 JSON 稳定出图，强模型用 Custom / Hybrid 模式精绘，并统一完成 SVG 校验与 PNG 预览。

它支持两条工作流：

- **从零制作**——给一个主题、一份文档或一个代码仓库，依次确认受众与知识结构、模板与交付格式、幻灯片标题、Markdown 文稿、统一 SVG 风格，然后批量生成可编辑的 PPT。
- **修改现有 PPT**——先盘点结构并重建讲解链条，报告术语突兀、顺序错乱、证据缺失、整页图片等问题，在你确认修改边界后才动手，保留其余页面和你已有的图表、模板与媒体。

两条路径都以同一套要求收尾：内容由浅入深、术语首次出现即解释、正文保持可编辑、媒体全部内嵌，并通过结构、视觉、媒体和可移植性 QA。

## 主要能力

- 从主题、Markdown、文档、代码仓库或现有 PPT 设计演示文稿
- 按照由浅入深的知识依赖组织内容（概念先于机制、指标定义先于结果表、正确性先于性能）
- 在专业术语首次出现时就近解释；缩写必须同时给出展开形式和释义
- 根据模板、操作系统和目标渲染后端自动选择中文标题/正文字体，不把 Arial 当作中文字体
- 先让用户选择 Structured、Hybrid、Custom 或逐图选择，再确认统一 SVG 风格并批量制作图示
- 优先使用 PowerPoint 原生文字、形状、表格和图表，保持内容可编辑
- 检查外部媒体链接、本地路径泄漏和缺失资源
- 支持现有 PPT 的结构盘点、局部修改和可移植性验证
- 一次安装内容设计、PPT 文件操作和 SVG 图示 Skill

## 安装

先克隆仓库，再运行安装器。安装器会同时安装 `pptx-structured-explainer`、`pptx-operator` 和 `svg-diagram-engine`：

```bash
git clone https://github.com/gjjjjjjjjjy/pptx-structured-explainer.git
cd pptx-structured-explainer
python install.py --target both --install-deps
```

可选目标：

```bash
# 只安装到 Claude Code
python install.py --target claude --install-deps

# 只安装到 Codex
python install.py --target codex --install-deps

# 先查看安装位置，不写文件
python install.py --target both --dry-run
```

默认安装位置：

| 平台 | 目录 |
| --- | --- |
| Claude Code | `~/.claude/skills/` |
| Codex | `${CODEX_HOME:-~/.codex}/skills/` |

如果目标目录已经存在，安装器默认停止，避免静默覆盖。确认更新时使用 `--force`；旧版本会移动到 Skills 目录同级的 `skills-backups/<时间戳>/`，避免备份被 Codex 或 Claude Code 误识别为可用 Skill，然后再写入新版本。

`--install-deps` 会把 `python-pptx`、`defusedxml`、`Pillow`、`PyMuPDF` 和 `fontTools` 安装到运行安装器的 Python 环境。若环境已经统一管理这些依赖，可以去掉该参数，只安装 Skills。

安装后可以调用 `/pptx-structured-explainer` 或 `$pptx-structured-explainer` 进入内容设计流程；实际操作文件时会配合 `pptx-operator`，复杂图示会配合 `svg-diagram-engine`。也可以直接描述任务，由 `description` 自动匹配。

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
| 读取、编辑、渲染、校验 `.pptx` | 仓库内置的 `pptx-operator` Skill |
| 稳定或精细生成 SVG | 仓库内置的 `svg-diagram-engine` Skill |
| `inventory_pptx.py` | `python-pptx` |
| `audit_media.py` | `defusedxml` |
| 中文字体策略与渲染器字体检查 | `fontTools` |
| 自动渲染预览 | macOS 优先使用 Microsoft PowerPoint，否则使用 LibreOffice；PNG 转换使用 Poppler 或 PyMuPDF |
| 最终兼容性检查 | Microsoft PowerPoint（可用时） |

```bash
pip install python-pptx defusedxml Pillow PyMuPDF fontTools
```

`pptx-operator` 的自动渲染入口先生成 PDF，再转成逐页 PNG 和联系表。macOS 检测到 Microsoft PowerPoint 时优先使用它，否则回退到 LibreOffice。中文排版、GIF、SVG、动画和音视频在 LibreOffice 中可能与 PowerPoint 不完全一致，因此包含这些能力时仍应使用 Microsoft PowerPoint 做最终检查。

## 辅助脚本

```bash
# 逐页结构盘点：标题、可编辑文本数、图片、表格、备注、版式
python scripts/inventory_pptx.py deck.pptx
python scripts/inventory_pptx.py deck.pptx --json

# 媒体审计：外链、本地路径泄漏、缺失关系目标
python scripts/audit_media.py deck.pptx

# 完整 PPT 操作工具位于配套 Skill
python companion/pptx-operator/scripts/validate_pptx.py deck.pptx
python companion/pptx-operator/scripts/font_policy.py \
  --template deck.pptx --renderer libreoffice
python companion/pptx-operator/scripts/apply_cjk_fonts.py \
  deck.pptx deck-cjk.pptx --template deck.pptx --renderer libreoffice
python companion/pptx-operator/scripts/audit_pptx_fonts.py \
  deck-cjk.pptx --libreoffice-safe --strict
python companion/pptx-operator/scripts/render_pptx.py deck-cjk.pptx \
  --output-dir rendered
```

字体策略以目标渲染器实际可见的字体为准。若独立打包的 LibreOffice 看不到系统中文字体，命令会在生成前明确失败，并提示安装或配置 `Noto Sans CJK SC`，而不是继续依赖 Arial 回退并输出缺字页面。

`audit_media.py` 通过时打印 `PASS`，发现问题时打印 `FAIL` 并以非零状态退出，可直接用于 CI 或提交前检查。

SVG 图示可独立运行：

```bash
# 弱模型：JSON 规范 → 稳定 SVG
python companion/svg-diagram-engine/scripts/diagram_render.py \
  companion/svg-diagram-engine/assets/examples/task-tree.json task-tree.svg

# 所有模式共用：校验 → PNG 预览
python companion/svg-diagram-engine/scripts/svg_validate.py task-tree.svg --strict
python companion/svg-diagram-engine/scripts/svg_render.py task-tree.svg task-tree.png
```

仓库同时提供绘图模式选择图以及 Structured、Hybrid、Custom 三种样张，位于 `companion/svg-diagram-engine/assets/examples/`。Skill 可以先展示选择图，再由用户决定整套统一模式或逐图选择。

PNG 预览不启动浏览器，依次尝试 `resvg`、`rsvg-convert`、Sharp 和 CairoSVG；找到第一个可用后端即使用。Codex 可直接发现其运行时内置的 Sharp，Claude Code 也可使用当前项目或 `NODE_PATH` 中的 Sharp。SVG 源文件始终保留为最终矢量资产。

若 Claude Code 环境没有上述后端，可在项目中执行 `npm install sharp`，然后用 `--backend sharp` 固定渲染后端；这条路径不依赖 Chrome、Chromium 或浏览器自动化。

## 目录结构

```text
pptx-structured-explainer/
├── install.py                      # 同时安装三个 Skills
├── requirements.txt               # PPT 操作脚本的 Python 依赖
├── SKILL.md                        # 主流程与核心约束
├── agents/
│   └── openai.yaml                 # Codex 界面配置
├── references/
│   ├── content-and-language.md     # 大纲、标题、术语、语言与深度要求
│   ├── existing-deck-workflow.md   # 现有 PPT 的盘点与安全修改流程
│   ├── qa-and-portability.md       # 内容/结构/视觉/媒体/可移植性检查清单
│   ├── svg-and-layout.md           # SVG 风格、版面与图示规范
│   └── template-and-format.md      # 模板检查与交付格式确认
├── scripts/
│   ├── audit_media.py
│   └── inventory_pptx.py
└── companion/
    ├── pptx-operator/
    │   ├── SKILL.md                # PPT 文件操作流程
    │   ├── agents/openai.yaml
    │   ├── references/
    │   │   └── font-compatibility.md
    │   └── scripts/
    │       ├── inventory_pptx.py
    │       ├── audit_media.py
    │       ├── font_policy.py
    │       ├── apply_cjk_fonts.py
    │       ├── audit_pptx_fonts.py
    │       ├── validate_pptx.py
    │       └── render_pptx.py
    └── svg-diagram-engine/
        ├── SKILL.md                # 稳定出图与精绘流程
        ├── references/             # JSON 规范与 Custom 模式规则
        ├── assets/                 # 主题和示例
        └── scripts/
            ├── diagram_render.py
            ├── svg_validate.py
            ├── svg_render.py
            └── svg_contact_sheet.py
```

三个 `SKILL.md` 分别负责内容设计、PPT 文件操作与 SVG 图示生成，`references/` 按需加载。仓库中的实现均采用 MIT License，不包含或复制其他专有 PPT Skill 的代码。

## License

本项目采用 [MIT License](LICENSE)。
