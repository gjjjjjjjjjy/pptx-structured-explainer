# Chinese Font Compatibility

## Selection order

1. Read the template theme's major/minor East Asian fonts and its `Hans` supplemental fonts.
2. Keep a template font only when it is visible to the target rendering backend.
3. Otherwise select a visible Simplified Chinese font for the current platform and renderer.
4. If no reliable CJK font exists, stop and request installation/configuration of `Noto Sans CJK SC` or another approved font. Never fall back to Arial for Han text.

Preferred system candidates:

- macOS: `PingFang SC`, `Hiragino Sans GB`, `Heiti SC`;
- Windows: `Microsoft YaHei`, `DengXian`, `SimHei`;
- Linux/LibreOffice: `Noto Sans CJK SC`, `Noto Sans SC`, `Source Han Sans SC`, `WenQuanYi Micro Hei`.

Use the template's major East Asian font for titles and minor East Asian font for body text when both are renderer-visible. Keep Arial, Calibri, or another approved Latin font only for Latin-only runs.

“Installed on the operating system” and “visible to the renderer” are not always equivalent. A self-contained LibreOffice runtime may use only its private font directory. The policy command therefore accepts `--renderer system|powerpoint|libreoffice` and stops when the chosen backend cannot see a CJK font.

## Native PowerPoint requirement

Reading a PPTX extracts Unicode and does not require the font. Rendering does. PowerPoint-compatible mixed-script runs may declare separate Latin and East Asian typefaces:

```xml
<a:rPr lang="zh-CN">
  <a:latin typeface="Arial"/>
  <a:ea typeface="Microsoft YaHei"/>
</a:rPr>
```

The actual `a:ea` value must come from template/renderer selection. For LibreOffice compatibility, split mixed text into separate runs. A Han run must use the selected CJK font in both declarations:

```xml
<a:rPr lang="zh-CN">
  <a:latin typeface="Noto Sans CJK SC"/>
  <a:ea typeface="Noto Sans CJK SC"/>
</a:rPr>
```

Its adjacent Latin-only run may use Arial. Do not assume LibreOffice will substitute Chinese glyphs for an Arial-only run. This failure can leave a mixed-language title showing only its English words.

## Tools

```bash
python scripts/font_policy.py --template template.pptx --renderer libreoffice --json
python scripts/apply_cjk_fonts.py input.pptx output.pptx \
  --template template.pptx --renderer libreoffice
python scripts/audit_pptx_fonts.py output.pptx --libreoffice-safe --strict
python scripts/render_pptx.py output.pptx --output-dir rendered --backend libreoffice
```

`apply_cjk_fonts.py` works on a copy, splits mixed-script runs, preserves the Latin font for Latin text, and assigns explicit CJK fonts to Han runs in slides, charts, and diagram data. Validate and render the output after patching. If font policy fails for the renderer, do not run the patch or render steps.
