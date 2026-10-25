import { motion } from "motion/react"
import type { ReactNode } from "react"
import { FileDown, FileText, GitCompareArrows, Link2, Lock, MessageSquareText } from "lucide-react"
import { bento } from "@/content"

function Cell({ className = "", children }: { className?: string; children: ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-60px" }}
      whileHover={{ y: -4 }}
      transition={{ type: "spring", stiffness: 160, damping: 22 }}
      className={`group relative overflow-hidden rounded-2xl border border-border bg-card p-6 md:p-7 ${className}`}
    >
      {children}
    </motion.div>
  )
}

function CellTitle({ icon, children }: { icon: ReactNode; children: ReactNode }) {
  return (
    <h3 className="flex items-center gap-2 text-lg font-semibold tracking-tight">
      <span className="text-glow">{icon}</span>
      {children}
    </h3>
  )
}

export function Bento() {
  const { read, cite, conflict, ask } = bento
  return (
    <section id="features" className="mx-auto max-w-6xl scroll-mt-24 px-5 py-24 md:px-8 md:py-32">
      <p className="font-mono text-sm tracking-widest text-glow">{bento.eyebrow}</p>
      <h2 className="mt-3 max-w-2xl text-3xl font-semibold tracking-tight text-balance md:text-5xl">{bento.title}</h2>

      <div className="mt-12 grid gap-4 md:grid-cols-6 md:grid-rows-[auto_auto_auto]">
        <Cell className="md:col-span-4 md:row-span-2">
          <CellTitle icon={<FileText className="size-5" aria-hidden="true" />}>{read.title}</CellTitle>
          <p className="mt-2 max-w-md text-muted-foreground">{read.body}</p>
          <ul className="mt-8 space-y-3">
            {read.files.map((f, i) => (
              <li key={f.name} className="rounded-xl border border-border bg-surface px-4 py-3">
                <div className="flex items-center justify-between gap-4 font-mono text-xs">
                  <span className="truncate text-foreground">{f.name}</span>
                  <span className="shrink-0 text-muted-foreground">{f.progress === 1 ? "已读完" : `${Math.round(f.progress * 100)}%`}</span>
                </div>
                <div className="mt-2.5 h-1 overflow-hidden rounded-full bg-muted">
                  <motion.div
                    className="h-full origin-left rounded-full bg-glow"
                    initial={{ scaleX: 0 }}
                    whileInView={{ scaleX: f.progress }}
                    viewport={{ once: true }}
                    transition={{ duration: 1.1, delay: 0.12 * i, ease: [0.22, 1, 0.36, 1] }}
                  />
                </div>
              </li>
            ))}
          </ul>
        </Cell>

        <Cell className="md:col-span-2">
          <CellTitle icon={<Link2 className="size-5" aria-hidden="true" />}>{cite.title}</CellTitle>
          <p className="mt-2 text-sm text-muted-foreground">{cite.body}</p>
          <p className="mt-6 leading-relaxed">
            {cite.sentence}
            <span className="ml-1.5 rounded-md border border-cite/30 bg-cite/10 px-1.5 py-0.5 font-mono text-xs text-cite">[51]</span>
          </p>
          <p className="mt-3 border-l-2 border-cite/50 pl-3 text-sm text-muted-foreground">{cite.snippet}</p>
        </Cell>

        <Cell className="md:col-span-2">
          <CellTitle icon={<GitCompareArrows className="size-5" aria-hidden="true" />}>{conflict.title}</CellTitle>
          <p className="mt-2 text-sm text-muted-foreground">{conflict.body}</p>
          <div className="mt-6 grid grid-cols-2 gap-2 text-sm">
            <span className="rounded-lg border border-border bg-surface p-3">{conflict.a}</span>
            <span className="rounded-lg border border-glow/35 bg-glow/5 p-3">{conflict.b}</span>
          </div>
        </Cell>

        <Cell className="md:col-span-3">
          <CellTitle icon={<MessageSquareText className="size-5" aria-hidden="true" />}>{ask.title}</CellTitle>
          <div className="mt-6 space-y-3 text-sm">
            <p className="ml-auto w-fit max-w-[85%] rounded-2xl rounded-br-md bg-secondary px-4 py-2.5">{ask.q}</p>
            <p className="w-fit max-w-[90%] rounded-2xl rounded-bl-md border border-border bg-surface px-4 py-2.5 leading-relaxed">{ask.a}</p>
          </div>
        </Cell>

        <Cell className="md:col-span-3">
          <div className="grid h-full gap-6 sm:grid-cols-2">
            <div>
              <CellTitle icon={<FileDown className="size-5" aria-hidden="true" />}>{bento.export.title}</CellTitle>
              <ul className="mt-4 flex flex-wrap gap-2">
                {bento.export.formats.map((x) => (
                  <li key={x} className="rounded-full border border-border px-3 py-1 font-mono text-xs text-muted-foreground">
                    {x}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <CellTitle icon={<Lock className="size-5" aria-hidden="true" />}>{bento.local.title}</CellTitle>
              <p className="mt-2 text-sm text-muted-foreground">{bento.local.body}</p>
            </div>
          </div>
        </Cell>
      </div>
    </section>
  )
}
