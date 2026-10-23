# deck.json 字段说明

```json
{
  "template": "../templates/finance-ruixin.pptx",   // 模板路径（相对 deck.json）
  "profile": "work/profile.json",                    // inspect_template.py 的输出
  "output": "out/deck.pptx",
  "tokens": {"primary": "#0B1F3A"},                  // 可选：覆盖自动识别的颜色/字体
  "slides": [ ... ]
}
```

`tokens` 可覆盖：`primary` `secondary` `dark` `body` `muted` `surface` `font` `font_heading` `radius`。只有自动识别错了才改。

## 每一页

| 字段 | 说明 |
|---|---|
| `from` | **必填**。复制模板的第几页（从 0 开始，见 profile.md） |
| `title` | 标题槽。写 `null` 表示删掉标题框 |
| `subtitle` | 副标题槽；模板有多个副标题框时可以写数组 |
| `number` | 序号槽（章节页的 01、内容页左上角的编号） |
| `meta` | 日期 / 汇报人槽 |
| `heading` | 目录页的「目录 / CONTENTS」，模板原文不对时改 |
| `items` | 目录条目：`["章节一", "章节二"]`；模板条目带副标题时写 `[["章节一", "一句话"], ...]` |
| `current` | 议程式章节页（profile.md 标了「议程式章节页」）：当前是第几章（从 0 开始），模板的高亮样式和竖条会移过去 |
| `tracker` | 内容页的进度标签 / 章节导航条：`{"items": ["市场概览", "竞争格局"], "current": 1}`；格子很窄，写短名；文档没分章就写 `null`（整组删掉）。模板有进度标签而 deck.json 没写时，build 会提示并保留模板原文 |
| `slots` | 直接按形状填字：`{"#12": "文字", "#13": ["第一行", "第二行"], "#14": null}`（null = 删掉） |
| `keep` | 要保留的示例形状：`["#20"]`（默认会删掉内容页的示例内容和示例字；章节页、内容页上没填的副标题和日期位也会删掉模板原文） |
| `delete` | 额外要删的形状：`["#7"]` |
| `lead` | 内容区顶部的一句话结论 |
| `conclusion` | 内容区底部的结论条 |
| `source` | 内容区底部的来源小字，如「数据来源：公司年报，示例数据」 |
| `body` | 主版式，见下 |
| `area` | 手动指定内容区 `[x, y, 宽, 高]`（英寸），覆盖自动计算 |
| `bg` | 手动指定这页底色（影响反色判断），一般不用 |
| `notes` | 演讲者备注 |
| `_why` | plan.py 留的说明，build 忽略 |

没写的槽位：示例字（标题、XXXX、请输入……）自动删除，品牌名、口号等模板原文保留。

## 复杂模板里的特殊页

| profile.md 里的标记 | 怎么写 |
|---|---|
| `hidden`（隐藏页，常是「模板使用说明」） | 不要用 |
| `quote`（模板自带的金句页） | `{"from": 11, "title": "金句", "subtitle": "—— 出处"}`；plan.py 遇到引用会自动用它 |
| 议程式章节页（章节页就是「高亮当前议题的目录」） | `{"from": 3, "items": [全部章节名], "current": 1}` |
| 段落式目录（一个文本框一段一个议题） | 和普通目录一样写 `items`，条数不受形状个数限制，编号格式沿用模板 |
| 进度标签（右上角一排 / 左侧一列） | 每个内容页写 `tracker`，见上表 |
| 标题在左侧面板里的内容页 | 和普通内容页一样写；area 已经在面板右边 |
| 内容区明显偏小的版式（带侧栏、带样机图） | plan.py 不自动用；想用就在 `from` 里指定，内容放进 area |

## 13 种版式（body.type）

```jsonc
// 卡片：2–8 张。icon 可选（engine/icons/ 里的文件名），value/unit 可选（卡片里的大数字）
{"type": "cards", "items": [{"title": "获客成本上升", "text": "单户获客成本同比上涨 22%", "icon": "coins", "value": "22", "unit": "%"}]}

// 要点：字符串或 {title, text, icon}
{"type": "bullets", "items": ["第一条", {"title": "小标题", "text": "说明"}]}

// 大数字：1–4 个；note 是下方的结论条
{"type": "stats", "items": [{"value": "1,286", "unit": "亿元", "title": "管理资产规模", "text": "同比增长 18.6%"}], "note": "一句结论"}

// 流程：2–6 步
{"type": "process", "steps": [{"title": "拆解岗位", "text": "明确 3–5 项核心胜任力", "icon": "search"}]}

// 时间线：2–6 个节点；highlight 是高亮的节点下标（默认最后一个）
{"type": "timeline", "items": [{"time": "2026年3月", "title": "质量追溯上线", "text": "全厂覆盖"}], "highlight": 3}

// 对比：左边是「旧/差」，右边是「新/好」（右边用主色强调）
{"type": "compare", "left": {"title": "过去", "items": ["..."]}, "right": {"title": "现在", "items": ["..."]}, "verdict": "一句结论"}

// 图表：kind = column | bar | line | pie | doughnut | stacked | area
// format 是数字格式：'#,##0' / '0.0' / '0"%"'；highlight 是要强调的类目下标；takeaway 是右侧结论卡
{"type": "chart", "kind": "column", "categories": ["2024", "2025"], "series": [{"name": "营收", "values": [12, 18]}],
 "format": "#,##0", "highlight": 1, "title": "可选的图表小标题",
 "takeaway": {"value": "50", "unit": "%", "title": "同比增长", "text": "一句解释"}}

// 表格：highlight_col 高亮一列；col_widths 列宽比例
{"type": "table", "header": ["方向", "目标"], "rows": [["扩面", "覆盖 120 家"]], "highlight_col": 1, "col_widths": [1, 3]}

// 金句 / 观点 / 正文
{"type": "quote", "text": "财富管理的本质，是陪客户穿越周期。", "by": "可选的出处"}
{"type": "statement", "text": "一句大字观点", "sub": "可选的补充说明", "align": "l"}
{"type": "text", "paras": ["第一段", "第二段"]}

// 图文：图片铺满一侧（自动裁切），另一侧放标题和文字/要点
{"type": "image", "path": "img/photo.jpg", "side": "left", "ratio": 0.5, "title": "标题", "text": "说明", "caption": "图片说明"}

// 左右分栏：left / right 各放一个版式
{"type": "split", "ratio": 0.58, "left": {"type": "chart", ...}, "right": {"type": "bullets", ...}}
```

## 完整的一页

```json
{
  "from": 3,
  "number": "01",
  "title": "核心指标全面达成",
  "lead": "三季度在市场波动加大的情况下，管理规模和收入都超额完成了年度节奏",
  "body": {"type": "stats", "items": [
    {"value": "1,286", "unit": "亿元", "title": "管理资产规模", "text": "同比增长 18.6%"},
    {"value": "4.2", "unit": "万户", "title": "有效客户", "text": "净增 5,300 户"}
  ]},
  "source": "示例数据",
  "notes": "完整的讲稿……"
}
```
