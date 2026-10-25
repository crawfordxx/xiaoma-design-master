import { motion } from "motion/react"
import { FileStack, GitCompareArrows, Search } from "lucide-react"
import { demoCard } from "@/content"

// Hero 里的产品示意：一张带出处的结论卡
export function DemoCard() {
  return (
    <div className="relative rounded-2xl bg-gradient-to-b from-glow/40 via-border to-transparent p-px">
      <div className="rounded-2xl bg-surface/95 p-5 backdrop-blur md:p-8">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border pb-4">
          <div className="flex min-w-0 items-center gap-2.5 text-sm text-muted-foreground">
            <Search className="size-4 shrink-0" aria-hidden="true" />
            <span className="truncate text-foreground">{demoCard.question}</span>
          </div>
          <div className="flex items-center gap-2 font-mono text-xs text-muted-foreground">
            <FileStack className="size-3.5" aria-hidden="true" />
            已读 {demoCard.sources} 篇 · 演示数据
          </div>
        </div>
        <ol className="@container mt-5 space-y-3">
          {demoCard.findings.map((f, i) => (
            <motion.li
              key={f.text}
              initial={{ opacity: 0, x: -12 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-40px" }}
              transition={{ delay: 0.15 * i, type: "spring", stiffness: 140, damping: 22 }}
              className={`relative flex flex-col gap-3 rounded-xl border p-4 @xl:flex-row @xl:items-center @xl:justify-between ${
                f.conflict ? "border-glow/35 bg-glow/5" : "border-border bg-card/60"
              }`}
            >
              <div className="flex items-start gap-3">
                <span className="mt-0.5 font-mono text-sm text-muted-foreground">{String(i + 1).padStart(2, "0")}</span>
                <span className="text-[15px] leading-relaxed">
                  {f.conflict && <GitCompareArrows className="mr-1.5 inline size-4 text-glow" aria-label="存在分歧" />}
                  {f.text}
                </span>
              </div>
              <div className="flex shrink-0 gap-1.5 pl-8 @xl:pl-0">
                {f.cites.map((c) => (
                  <CiteChip key={c} id={c} snippet={demoCard.snippets[c]} />
                ))}
              </div>
            </motion.li>
          ))}
        </ol>
      </div>
    </div>
  )
}

// 引用编号：悬停或键盘聚焦时，在这一行上方弹出原文摘录，演示「每句都有出处」
function CiteChip({ id, snippet }: { id: number; snippet: string }) {
  const tipId = `cite-${id}`
  return (
    <span className="group/cite">
      <button
        type="button"
        aria-describedby={tipId}
        className="min-h-11 min-w-11 rounded-md px-1 font-mono text-xs text-cite outline-none @xl:min-h-0 @xl:min-w-0 [&>span]:transition-colors"
      >
        <span className="inline-block rounded-md border border-cite/30 bg-cite/10 px-2 py-0.5 group-hover/cite:border-cite/70 group-hover/cite:bg-cite/20 group-focus-within/cite:border-cite/70 group-focus-within/cite:bg-cite/20">
          [{id}]
        </span>
      </button>
      <span
        id={tipId}
        role="tooltip"
        className="pointer-events-none invisible absolute inset-x-3 bottom-full z-20 mb-2 translate-y-1 rounded-lg border border-cite/30 bg-popover px-3 py-2 text-left text-xs leading-relaxed text-popover-foreground opacity-0 shadow-xl transition-all duration-200 group-focus-within/cite:visible group-focus-within/cite:translate-y-0 group-focus-within/cite:opacity-100 group-hover/cite:visible group-hover/cite:translate-y-0 group-hover/cite:opacity-100 motion-reduce:transition-none"
      >
        {snippet}
      </span>
    </span>
  )
}
