import { ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { faq, finalCta, footer } from "@/content"
import { Logo } from "./Logo"

export function Faq() {
  return (
    <section id="faq" className="mx-auto max-w-3xl scroll-mt-24 px-5 py-24 md:px-8">
      <p className="font-mono text-sm tracking-widest text-glow">{faq.eyebrow}</p>
      <div className="mt-8 divide-y divide-border border-y border-border">
        {faq.items.map((item) => (
          <details key={item.q} className="group py-5">
            <summary className="flex min-h-11 cursor-pointer list-none items-center justify-between gap-6 text-lg font-medium">
              {item.q}
              <span className="text-2xl leading-none text-muted-foreground transition-transform group-open:rotate-45" aria-hidden="true">
                +
              </span>
            </summary>
            <p className="mt-3 leading-relaxed text-muted-foreground">{item.a}</p>
          </details>
        ))}
      </div>
    </section>
  )
}

export function FinalCta() {
  return (
    <section className="relative overflow-hidden border-t border-border">
      <div className="absolute inset-x-0 -top-24 mx-auto h-64 max-w-2xl rounded-full bg-glow/15 blur-3xl" aria-hidden="true" />
      <div className="relative mx-auto max-w-6xl px-5 py-24 text-center md:px-8 md:py-32">
        <h2 className="text-3xl font-semibold tracking-tight text-balance md:text-6xl">{finalCta.title}</h2>
        <p className="mt-5 text-muted-foreground">{finalCta.body}</p>
        <Button size="lg" className="mt-9 h-12 gap-2 rounded-full px-7 text-base font-semibold">
          {finalCta.button}
          <ArrowRight data-icon="inline-end" aria-hidden="true" />
        </Button>
      </div>
    </section>
  )
}

export function Footer() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto flex max-w-6xl flex-col gap-6 px-5 py-10 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between md:px-8">
        <Logo />
        <p>{footer.note}</p>
        <ul className="-mx-2 flex gap-2">
          {footer.links.map((l) => (
            <li key={l}>
              <a href="#top" className="inline-flex min-h-11 min-w-11 items-center justify-center px-2 hover:text-foreground">
                {l}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </footer>
  )
}
