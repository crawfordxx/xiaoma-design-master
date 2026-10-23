---
name: xiaoma-ppt
description: 把文档内容（Markdown、Word docx/doc、txt、rtf、odt、wps、html、pdf 都行）套进用户自己的 PPT 模板，生成可编辑的 .pptx：自动拆解模板（每页是封面/目录/章节/内容/结尾、哪些是可填的文字框、内容能放在哪块区域、主色辅色字体圆角），按内容形态匹配版式（数字→大数字、步骤→流程、表格→原生图表、对比→左右对比、引用→金句），所有颜色字体都取自模板，背景、母版、logo、装饰原样保留；附不用看图也能用的体检工具（溢出、出界、压字、示例字残留、对比度）。当用户要「用这个模板做 PPT」「把 md/Word/txt/文档/大纲套进公司模板」「按模板出一份汇报/路演/培训课件」「模板 + 内容 → pptx」时使用。任何能写代码、跑 Python 的模型或 agent 都能用。
---

# xiaoma-ppt

一句话：**商用 PPT 的标准是「像模板本来就长这样」：版式从模板里找，颜色字体从模板里取，内容只在模板留出的地方画。**

整套流程是确定性的脚本，模型只做三件事：读模板画像、改 deck.json、看体检结果。不能读图的模型也能走完。

## 环境

```bash
pip install python-pptx python-docx pillow lxml   # Python 3.9+
# 渲染预览、对比度检查、读 doc/rtf/odt/wps/pdf 需要 LibreOffice + poppler：
#   macOS: brew install --cask libreoffice && brew install poppler
#   Ubuntu: apt install libreoffice poppler-utils
```

下文 `E=<skill 目录>/engine`。所有脚本都有 `--help`。

## 工作流（不要跳步）

1. **拆模板**
   ```bash
   python3 $E/inspect_template.py 模板.pptx --out work/
   ```
   读 `work/profile.md`：每页的角色、槽位（`#形状id`）、内容安全区 `area`、主色辅色字体。能读图就打开 `work/template-render/sheet-1.jpg` 对照着看。
   **核对两件事**：①角色分对了没有（封面/目录/章节/内容/金句/结尾，隐藏页标 hidden 不用）；②主色是不是模板的品牌色。不对就在 deck.json 里用 `from` 指定页、用 `tokens` 改色（见 `references/deck-spec.md`）。
   真实企业模板常见的复杂结构，profile.md 会逐页标出来：隐藏的使用说明页、议程式章节页（高亮当前议题的目录）、一个文本框多段的目录、内容页的进度标签 / 章节导航条、模板自带的金句页、标题在左侧面板的内容页。每种怎么写见 `references/deck-spec.md` 的「复杂模板里的特殊页」。

2. **出草稿**
   ```bash
   python3 $E/plan.py 内容.md work/profile.json --out deck.json
   ```
   **内容不是 md 也直接传**（`内容.docx`、`内容.txt`、`.doc` `.rtf` `.odt` `.wps` `.html` `.pdf`）：plan.py 会先转成 `work/<文件名>.converted.md` 再出草稿。**先读一遍这份 md**：`#` 是封面标题、`##` 是章节、`###` 是一页，列表、表格对不对。Word 用了标题样式的基本不会错；txt、没用样式的 Word 靠「第一章」「一、」「（一）」「1.1」「1.」「•」这类编号和整段加粗来猜；PDF 只能尽力（表格、分栏会乱）。认错了就直接改这份 md，再用它重跑 plan.py。只想转不想出草稿：`python3 $E/convert.py 内容.docx --out work/content.md`。
   终端会列出每一页用了模板的哪一页、为什么选这个版式（`_why`）。匹配规则见 `references/matching.md`。

3. **逐页改 deck.json**（模型真正要动脑的一步）。对每一页问：
   - 这一页的**一个重点**是什么？`lead`（顶部一句结论）和 `conclusion`（底部结论条）有没有把它说出来？
   - 版式选得对不对？数字多就用 `stats`/`chart`，先后顺序用 `process`/`timeline`，好坏对照用 `compare`。草稿选错了就改 `body.type`。
   - 字数：上屏的字**只能从原文里删减、拆分，不能改写、扩写、编数据**；删掉的完整原文放进 `notes`（演讲者备注）。每页的字数上限见 `references/aesthetics.md`。
   - 目录条数要和章节数对上；模板目录位置不够就合并章节，或者不放目录。
   - 有进度标签的模板：每个内容页的 `tracker.items` 用 4–6 个字的短章节名，`current` 对上当前章。
   - 封面/结尾：模板原有的品牌名、口号会自动保留；要改就显式写 `title`/`subtitle`。

4. **生成**
   ```bash
   python3 $E/build.py deck.json            # → out/deck.pptx，终端会打印缩字、放不下等提示
   ```

5. **体检循环**（每一轮都跑，直到全绿）
   ```bash
   python3 $E/lint.py out/deck.pptx          # 溢出 / 出界 / 压字 / 示例字残留 / 字号 / 对比度
   python3 $E/render.py out/deck.pptx --out out/render    # 出每页 JPG 和拼图 sheet-*.jpg
   ```
   - **lint 有 ❌ 就必须修**，修法见 `references/troubleshooting.md`。⚠️ 是「字号被缩小了 / 字太多」，优先删字而不是忍着。
   - **能读图就逐张看拼图**，按 `references/aesthetics.md` 末尾的 6 项打分（模板一致、层级、密度、对齐、数据可读、页间节奏），每项 ≥ 8 才交付。
   - **不能读图的模型**：以 lint 全绿 + build 没有 ⚠️ 为准，并在交付说明里写明「未目视检查」。

## 七条硬规矩

1. **模板是唯一的设计来源。** 颜色、字体、圆角、页眉页脚、logo 全用模板的。不新增模板里没有的颜色，不换字体，不改背景。
2. **每一页都从模板复制。** 不新建空白页。封面、目录、章节、结尾一定用模板对应的那页。
3. **只在内容安全区里画。** `area` 是避开了标题、logo、页脚和背景插画的区域；要手动改 `area`，先看渲染图确认没压到东西。
4. **一页一个重点。** 每页最多一个主版式（`split` 左右各一个）。内容多就拆页，不缩字硬塞。
5. **数字要能被看见。** 关键数字用 `stats` 或图表，不埋在句子里；图表一律用原生图表（可在 PowerPoint 里改数据），不贴图片。
6. **原文不改写。** 上屏的字（包括页面标题）从原文里删减、拆分得来，不把小标题改写成自己总结的结论句；数据只能用原文里有的，查不到出处的数字不写。
7. **lint 全绿才交付。** 示例字（「标题」「XXXX」「请输入」）一个都不能留。

## 什么时候读哪份参考

| 要做的事 | 读 |
|---|---|
| md 的结构怎么对应到页、内容形态怎么对应到版式、模板的哪一页用来做什么 | `references/matching.md` |
| 审美标准：模板一致性、层级、字数上限、配色用法、目视打分表 | `references/aesthetics.md` |
| deck.json 每个字段、13 种版式各要什么数据 | `references/deck-spec.md` |
| lint 报错、模板识别不准、字体缺失、颜色不对怎么办 | `references/troubleshooting.md` |

## 交付清单

**清单全部打勾之前，不要结束回合、不要输出「最终报告」。** 中途汇报进度可以，汇报完接着干。

- [ ] `profile.md` 读过，角色和主色核对过（不对的已在 deck.json 里改）
- [ ] 内容不是 md 时，`*.converted.md` 读过，标题层级和列表核对过
- [ ] deck.json 逐页检查过：每页一个重点、版式对、字数在上限内、完整原文在 `notes`
- [ ] `build.py` 没有 ⚠️（或每条都能说明为什么可以接受）
- [ ] `lint.py` 全绿
- [ ] 渲染拼图逐张看过、6 项都 ≥ 8；不能读图的在交付说明里写明「未目视检查」
- [ ] 交付 `.pptx`，告诉用户：共几页、每章几页、哪些页用了什么版式、要改内容改 deck.json 哪里再跑一次 build
