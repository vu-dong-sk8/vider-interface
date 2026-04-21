import { Link } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { ArrowRight, Zap } from "lucide-react";
import { motion } from "framer-motion";

export function ViderHero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden vider-gradient">
      {/* Diagonal stripe pattern overlay */}
      <div className="absolute inset-0 vider-stripe opacity-60" />

      {/* Accent line decorations */}
      <div className="absolute top-1/4 left-0 w-32 h-[2px] bg-vider-accent opacity-60" />
      <div className="absolute bottom-1/3 right-0 w-48 h-[2px] bg-vider-accent opacity-40" />
      <div className="absolute top-1/2 right-12 w-[2px] h-24 bg-vider-accent opacity-30" />

      <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
        {/* Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-white/10 bg-white/5 text-sm text-white/70 mb-8"
        >
          <Zap className="w-3.5 h-3.5 text-vider-accent" />
          <span className="text-label">AI-Powered Assistant</span>
        </motion.div>

        {/* Main heading */}
        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-display text-5xl sm:text-7xl md:text-8xl lg:text-9xl text-white mb-6"
        >
          CHAT WITH
          <br />
          <span className="relative">
            CLARITY
            <span className="absolute -bottom-2 left-0 w-full h-1 vider-accent-gradient rounded-full" />
          </span>
          <span className="text-vider-accent">.</span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className="text-lg md:text-xl text-white/60 max-w-2xl mx-auto mb-10 font-light leading-relaxed"
        >
          Trợ lý AI thông minh, nhanh chóng và đa năng. Trải nghiệm hội thoại mượt mà
          với công nghệ tiên tiến nhất.
        </motion.p>

        {/* CTAs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.45 }}
          className="flex flex-col sm:flex-row items-center justify-center gap-4"
        >
          <Link to="/chat">
            <Button variant="accent" size="lg" className="text-base px-8 py-6 gap-2">
              Bắt đầu ngay
              <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
          <a href="#features">
            <Button variant="heroOutline" size="lg" className="text-base px-8 py-6 border-white/20 text-white hover:bg-white hover:text-black">
              Tìm hiểu thêm
            </Button>
          </a>
        </motion.div>

        {/* Stats row */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="mt-20 grid grid-cols-3 gap-8 max-w-lg mx-auto"
        >
          {[
            { value: "99.9%", label: "Uptime" },
            { value: "<1s", label: "Phản hồi" },
            { value: "50+", label: "Ngôn ngữ" },
          ].map((stat) => (
            <div key={stat.label} className="text-center">
              <div className="text-display text-2xl md:text-3xl text-white">{stat.value}</div>
              <div className="text-label text-white/40 mt-1">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
