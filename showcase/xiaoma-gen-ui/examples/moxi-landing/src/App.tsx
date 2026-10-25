import { MotionConfig } from "motion/react"
import { Bento } from "@/components/site/Bento"
import { Faq, FinalCta, Footer } from "@/components/site/Closing"
import { Facts } from "@/components/site/Facts"
import { Hero } from "@/components/site/Hero"
import { Nav } from "@/components/site/Nav"
import { Steps } from "@/components/site/Steps"

export default function App() {
  return (
    // reducedMotion="user"：系统开了「减少动态效果」时自动关掉位移动画
    <MotionConfig reducedMotion="user">
      <Nav />
      <main>
        <Hero />
        <Facts />
        <Bento />
        <Steps />
        <Faq />
        <FinalCta />
      </main>
      <Footer />
    </MotionConfig>
  )
}
