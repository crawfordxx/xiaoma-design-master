// 全站文案集中放这里，组件只管排版
export const nav = {
  links: [
    { label: "功能", href: "#features" },
    { label: "工作方式", href: "#how" },
    { label: "常见问题", href: "#faq" },
  ],
  cta: "免费试用",
}

export const hero = {
  badge: "新 · 一次并读 200 篇文献",
  title: ["把两百篇论文，", "读成一页结论。"],
  sub: "墨隙替你通读、比对，并标出每一句结论的出处。你只需要判断，不需要翻找。",
  primary: "免费试用 14 天",
  secondary: "看 90 秒演示",
  note: "无需信用卡 · 支持 PDF / Word / 网页链接",
}

export const demoCard = {
  question: "远程协作对研发团队的产出有什么影响？",
  sources: 186,
  findings: [
    { text: "短期交付速度与线下团队基本持平", cites: [3, 17, 42] },
    { text: "跨组的新想法数量随时间下降", cites: [8, 51] },
    { text: "两类研究对「沟通成本」的结论相反，已并排列出", cites: [22, 96], conflict: true },
  ],
  // 悬停引用编号时显示的原文摘录（演示数据，文献均为虚构）
  snippets: {
    3: "Allen 2024 · 第 5 页：迭代周期在迁移后两个季度内无显著变化。",
    17: "Chen 等 2023 · 第 9 页：远程组的按期交付率为 91%，对照组为 93%。",
    42: "Ortiz 2022 · 第 3 页：交付速度差异在统计上不显著。",
    8: "Field 2024 · 第 12 页：跨团队提案数自第 6 个月起持续下降。",
    51: "Survey R&D 2023 · 第 7 页：跨组共创会议频次下降约三分之一。",
    22: "Kim 2023 · 第 4 页：沟通成本较线下上升，主要来自会议时长。",
    96: "Novak 2024 · 第 15 页：控制团队规模后，沟通成本无显著差异。",
  } as Record<number, string>,
}

export const facts = [
  { value: "200", unit: "篇", label: "单次并读上限" },
  { value: "每一句", unit: "", label: "结论都带出处" },
  { value: "3", unit: "种", label: "导出格式" },
  { value: "0", unit: "", label: "上传到第三方的原文" },
]

export const bento = {
  eyebrow: "功能",
  title: "读文献最累的部分，交给它",
  read: {
    title: "通读并比对",
    body: "拖进一整个文件夹，墨隙逐篇读完，把相同问题的回答对齐到一张表里。",
    files: [
      { name: "Allen_2024_remote_teams.pdf", progress: 1 },
      { name: "Chen_et_al_2023.pdf", progress: 1 },
      { name: "Field_study_collab.pdf", progress: 0.72 },
      { name: "Survey_RnD_output.pdf", progress: 0.38 },
    ],
  },
  cite: {
    title: "每句都有出处",
    body: "点一下编号，直接跳到原文那一段。",
    sentence: "跨组的新想法数量随时间下降",
    snippet: "…第 6 个月起，跨团队提案数较基线下降 …",
  },
  conflict: {
    title: "冲突不抹平",
    body: "文献结论相反时，并排列出，不替你挑。",
    a: "研究 A：沟通成本上升",
    b: "研究 B：无显著变化",
  },
  ask: {
    title: "追问到原文",
    q: "这个结论的样本量多大？",
    a: "三项研究合计 1,240 人，最小的一项只有 38 人 [51]。",
  },
  export: { title: "一页纸导出", formats: ["Markdown", "Word", "LaTeX"] },
  local: { title: "原文只留在你这", body: "文献在本地解析，不上传给第三方。" },
}

export const steps = {
  eyebrow: "工作方式",
  title: "三步，从一堆 PDF 到一页纸",
  items: [
    { n: "01", title: "放进文献", body: "PDF、Word、网页链接都行。一次最多 200 篇，也可以接着往同一个项目里加。" },
    { n: "02", title: "问一个具体的问题", body: "问得越具体，结论越干净。墨隙会先告诉你哪些文献真的回答了这个问题。" },
    { n: "03", title: "拿到带出处的一页纸", body: "结论、分歧、证据强弱一页列清。每一句都能点回原文，方便你逐条核对。" },
  ],
}

export const faq = {
  eyebrow: "常见问题",
  items: [
    { q: "它会编造结论吗？", a: "每一句结论都必须挂在原文段落上；找不到出处的句子不会出现在结论卡里。" },
    { q: "支持中文文献吗？", a: "支持中英文混排的文献集，结论用你提问的语言输出。" },
    { q: "我的文献会被拿去训练吗？", a: "不会。原文在本地解析，只有你选择分享的结论卡会离开你的电脑。" },
  ],
}

export const finalCta = {
  title: "下一篇综述，从一页纸开始。",
  body: "14 天免费试用，到期不自动扣费。",
  button: "免费试用",
}

export const footer = {
  note: "本页是 xiaoma-gen-ui 生成的示例站点，产品、数据与引用均为虚构。",
  links: ["隐私", "条款", "联系我们"],
}
