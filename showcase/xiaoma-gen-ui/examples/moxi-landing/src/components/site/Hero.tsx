import { motion } from "motion/react"
import { ArrowRight, Play, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { hero } from "@/content"
import { DemoCard } from "./DemoCard"

const rise = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 120, damping: 20 } },
} as const

export function Hero() {
  return (
    <section id="top" className="relative overflow-hidden pt-28 pb-20 md:pt-36 md:pb-28 lg:flex lg:min-h-[100svh] lg:items-center lg:py-24">
      <LightSeam />
      <motion.div
        initial="hidden"
        animate="show"
        transition={{ staggerChildren: 0.08 }}
        className="relative mx-auto grid w-full max-w-6xl items-center gap-14 px-5 md:px-8 lg:grid-cols-[1.05fr_1fr] lg:gap-12"
      >
        <div>
          <motion.div variants={rise}>
            <Badge variant="outline" className="h-8 gap-1.5 rounded-full border-glow/30 px-3 text-glow">
              <Sparkles className="size-3.5" aria-hidden="true" />
              {hero.badge}
            </Badge>
          </motion.div>
          <motion.h1
            variants={rise}
            className="mt-6 text-[2.6rem] leading-[1.12] font-semibold tracking-tight text-balance md:text-6xl md:leading-[1.08] xl:text-7xl"
          >
            {hero.title[0]}
            <br />
            <span className="text-glow">{hero.title[1]}</span>
          </motion.h1>
          <motion.p variants={rise} className="mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground">
            {hero.sub}
          </motion.p>
          <motion.div variants={rise} className="mt-9 flex flex-col gap-3 sm:flex-row">
            <Button size="lg" className="h-12 gap-2 rounded-full px-6 text-base font-semibold">
              {hero.primary}
              <ArrowRight data-icon="inline-end" aria-hidden="true" />
            </Button>
            <Button size="lg" variant="outline" className="h-12 gap-2 rounded-full px-6 text-base">
              <Play data-icon="inline-start" aria-hidden="true" />
              {hero.secondary}
            </Button>
          </motion.div>
          <motion.p variants={rise} className="mt-4 text-sm text-muted-foreground">
            {hero.note}
          </motion.p>
        </div>
        <motion.div variants={rise}>
          <DemoCard />
        </motion.div>
      </motion.div>
    </section>
  )
}

// 记忆点：墨色里裂开一道光缝，一团光沿缝缓缓下行，穿过结论卡背后
function LightSeam() {
  return (
    <div className="pointer-events-none absolute inset-0" aria-hidden="true">
      <div className="absolute top-[-15%] hidden h-[130%] w-[3px] -rotate-[14deg] md:left-[66%] md:block lg:left-[71%]">
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-glow/70 to-transparent" />
        <motion.div
          className="absolute inset-x-[-1px] h-40 rounded-full bg-gradient-to-b from-transparent via-glow to-transparent shadow-[0_0_28px_8px_var(--glow)]"
          initial={{ top: "-20%" }}
          animate={{ top: "110%" }}
          transition={{ duration: 5.5, repeat: Infinity, ease: "easeInOut", repeatDelay: 1.2 }}
        />
      </div>
      <motion.div
        className="absolute top-[-15%] left-[94%] md:left-[66%] h-[130%] w-56 -translate-x-1/2 -rotate-[14deg] bg-glow/12 blur-3xl lg:left-[71%]"
        animate={{ opacity: [0.55, 1, 0.55] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  )
}
