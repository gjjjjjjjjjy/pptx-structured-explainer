# Chinese Font Compatibility

## Selection order

1. Read the template theme's major/minor East Asian fonts and its `Hans` supplemental fonts.
2. Keep a template font only when it is visible to the target rendering backend and has verified terms permitting free commercial use and redistribution.
3. Otherwise use `Source Han Sans SC` as the default Chinese title and body family when it is visible to the target renderer.
4. Use `Source Han Serif SC` only when the confirmed template or visual direction requires a serif/Song-style Chinese face; do not mix it into ordinary sans-serif body text by default.
5. If the Source Han family is unavailable, select a renderer-visible fallback. If no reliable CJK font exists, stop and request installation/configuration. Never fall back to Arial for Han text.

Verified open-license fallback candidates after `Source Han Sans SC`:

- macOS, Windows, and Linux/LibreOffice: `Noto Sans CJK SC` or `Noto Sans SC`.

Do not treat platform fonts such as Arial, Calibri, PingFang SC, Microsoft YaHei, DengXian, SimSun, or SimHei as redistributable merely because they are installed. Under this skill's conservative policy, an unverified family is replaced with `Source Han Sans SC`. Additional families may be added only after recording authoritative license evidence that explicitly permits commercial use and redistribution.

Use the template's major East Asian font for titles and minor East Asian font for body text only when both are renderer-visible and license-approved. With no compliant template font, use `Source Han Sans SC` for Chinese and Latin title/body text; express hierarchy through size and weight.

“Installed on the operating system” and “visible to the renderer” are not always equivalent. A self-contained LibreOffice runtime may use only its private font directory. The policy command therefore accepts `--renderer system|powerpoint|libreoffice` and stops when the chosen backend cannot see a CJK font.

On Windows, inspect both HKLM/HKCU font registrations and the system/user font directories. Treat localized and English family names as aliases: `微软雅黑` ↔ `Microsoft YaHei`, `等线` ↔ `DengXian`, `宋体` ↔ `SimSun`, and `黑体` ↔ `SimHei`. This lets a Chinese template theme match the same installed font regardless of the Windows display language.

## Native PowerPoint requirement

Reading a PPTX extracts Unicode and does not require the font. Rendering does. PowerPoint-compatible mixed-script runs may declare separate Latin and East Asian typefaces. The following common system-font example explains OOXML but is non-compliant with this skill's redistribution policy and must not be delivered unchanged:

```xml
<a:rPr lang="zh-CN">
  <a:latin typeface="Arial"/>
  <a:ea typeface="Microsoft YaHei"/>
</a:rPr>
```

The actual `a:ea` value must come from template/renderer selection. For LibreOffice compatibility, split mixed text into separate runs. A Han run must use the selected CJK font in both declarations:

```xml
<a:rPr lang="zh-CN">
  <a:latin typeface="Source Han Sans SC"/>
  <a:ea typeface="Source Han Sans SC"/>
</a:rPr>
```

Its adjacent Latin-only run must also use a verified family such as `Source Han Sans SC`, `IBM Plex Sans`, or `Inter`. Do not assume LibreOffice will substitute Chinese glyphs for an Arial-only run. This failure can leave a mixed-language title showing only its English words.

## Tools

```bash
python scripts/font_policy.py --template template.pptx --renderer libreoffice --json
python scripts/apply_cjk_fonts.py input.pptx output.pptx \
  --template template.pptx --renderer libreoffice
python scripts/audit_pptx_fonts.py output.pptx --libreoffice-safe --strict
python scripts/audit_font_licenses.py output.pptx --strict
python scripts/render_pptx.py output.pptx --output-dir rendered --backend libreoffice
```

`apply_cjk_fonts.py` works on a copy, splits mixed-script runs, replaces Latin and Chinese text fonts with the selected approved families, and assigns explicit CJK fonts to Han runs in slides, notes, charts, and diagram data. Validate and render the output after patching. If font policy fails for the renderer, do not run the patch or render steps.
