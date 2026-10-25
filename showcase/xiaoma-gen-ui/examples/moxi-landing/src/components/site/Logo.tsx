// 品牌标：一块墨，中间裂开一道光缝
export function Logo({ className = "" }: { className?: string }) {
  return (
    <span className={`inline-flex items-center gap-2.5 ${className}`}>
      <svg viewBox="0 0 24 24" className="size-6" aria-hidden="true">
        <rect x="2" y="2" width="20" height="20" rx="6" className="fill-foreground" />
        <path d="M13.5 4.5 L10.5 12 L13 12.5 L10.5 19.5" className="stroke-glow" strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
      <span className="text-[15px] font-semibold tracking-tight">
        墨隙 <span className="text-muted-foreground font-normal">Moxi</span>
      </span>
    </span>
  )
}
