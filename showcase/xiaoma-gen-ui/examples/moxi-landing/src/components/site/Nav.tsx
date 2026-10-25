import { motion, useScroll, useTransform } from "motion/react"
import { Button } from "@/components/ui/button"
import { nav } from "@/content"
import { Logo } from "./Logo"

export function Nav() {
  const { scrollY } = useScroll()
  // 滚动后导航底色渐显，首屏保持通透
  const opacity = useTransform(scrollY, [0, 120], [0, 1])

  return (
    <header className="fixed inset-x-0 top-0 z-50">
      <motion.div
        style={{ opacity }}
        className="absolute inset-0 border-b border-border bg-background/80 backdrop-blur-md"
        aria-hidden="true"
      />
      <nav className="relative mx-auto flex h-16 max-w-6xl items-center justify-between px-5 md:px-8" aria-label="主导航">
        <a href="#top" aria-label="墨隙 Moxi 首页" className="inline-flex min-h-11 items-center">
          <Logo />
        </a>
        <ul className="hidden items-center gap-4 text-sm text-muted-foreground md:flex">
          {nav.links.map((l) => (
            <li key={l.href}>
              <a href={l.href} className="inline-flex min-h-11 min-w-11 items-center justify-center px-2 transition-colors hover:text-foreground">
                {l.label}
              </a>
            </li>
          ))}
        </ul>
        <Button size="lg" className="h-11 rounded-full px-5 font-semibold">
          {nav.cta}
        </Button>
      </nav>
    </header>
  )
}
