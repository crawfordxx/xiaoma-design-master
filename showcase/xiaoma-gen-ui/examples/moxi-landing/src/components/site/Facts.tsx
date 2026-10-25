import { facts } from "@/content"

// 产品规格条：只写功能事实，不写编造的用户数
export function Facts() {
  return (
    <section aria-label="产品规格" className="border-y border-border bg-surface/50">
      <dl className="mx-auto grid max-w-6xl grid-cols-2 gap-y-8 px-5 py-10 md:grid-cols-4 md:px-8">
        {facts.map((f) => (
          <div key={f.label} className="flex flex-col gap-1 border-l border-border pl-5">
            <dt className="order-2 text-sm text-muted-foreground">{f.label}</dt>
            <dd className="order-1 text-3xl font-semibold tracking-tight md:text-4xl">
              {f.value}
              {f.unit && <span className="ml-1 text-lg text-muted-foreground">{f.unit}</span>}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  )
}
