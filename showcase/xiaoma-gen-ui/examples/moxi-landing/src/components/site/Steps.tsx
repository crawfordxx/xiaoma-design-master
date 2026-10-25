import { motion, useScroll, useTransform } from "motion/react"
import { useRef } from "react"
import { steps } from "@/content"

// 三步流程：左侧进度线随滚动填满
export function Steps() {
  const ref = useRef<HTMLOListElement>(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start 75%", "end 55%"] })
  const fill = useTransform(scrollYProgress, [0, 1], [0, 1])

  return (
    <section id="how" className="scroll-mt-24 border-t border-border bg-surface/40">
      <div className="mx-auto grid max-w-6xl gap-14 px-5 py-24 md:grid-cols-[0.9fr_1.1fr] md:px-8 md:py-32">
        <div className="md:sticky md:top-32 md:self-start">
          <p className="font-mono text-sm tracking-widest text-glow">{steps.eyebrow}</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-balance md:text-5xl">{steps.title}</h2>
        </div>

        <div className="relative">
          <div className="absolute top-2 bottom-2 left-[11px] w-px bg-border md:left-[15px]" aria-hidden="true" />
          <motion.div
            style={{ scaleY: fill }}
            className="absolute top-2 bottom-2 left-[11px] w-px origin-top bg-glow md:left-[15px]"
            aria-hidden="true"
          />
          <ol ref={ref} className="relative space-y-12 pl-10 md:pl-14">
          {steps.items.map((s) => (
            <li key={s.n} className="relative">
              <span className="absolute top-1 -left-10 grid size-6 place-items-center rounded-full border border-glow/50 bg-background md:-left-14 md:size-8">
                <span className="size-1.5 rounded-full bg-glow" />
              </span>
              <p className="font-mono text-sm text-muted-foreground">{s.n}</p>
              <h3 className="mt-1 text-2xl font-semibold tracking-tight">{s.title}</h3>
              <p className="mt-2 max-w-xl leading-relaxed text-muted-foreground">{s.body}</p>
            </li>
          ))}
          </ol>
        </div>
      </div>
    </section>
  )
}
