import { FileText, Mail, GraduationCap, Lightbulb, Bot, Shield, Gauge, Globe } from "lucide-react";
import { motion } from "framer-motion";

const prompts = [
  { icon: FileText, title: "Tóm tắt tài liệu", desc: "Rút gọn nội dung dài thành ý chính" },
  { icon: Mail, title: "Viết email chuyên nghiệp", desc: "Soạn email chỉnh chu trong tích tắc" },
  { icon: GraduationCap, title: "Hỗ trợ học tập", desc: "Giải đáp thắc mắc mọi lĩnh vực" },
  { icon: Lightbulb, title: "Phân tích ý tưởng", desc: "Đánh giá và phát triển sáng tạo" },
];

const features = [
  { icon: Bot, title: "AI Thông Minh", desc: "Mô hình ngôn ngữ tiên tiến nhất" },
  { icon: Shield, title: "Bảo Mật", desc: "Dữ liệu được mã hoá end-to-end" },
  { icon: Gauge, title: "Siêu Nhanh", desc: "Phản hồi dưới 1 giây" },
  { icon: Globe, title: "Đa Ngôn Ngữ", desc: "Hỗ trợ hơn 50 ngôn ngữ" },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4 } },
};

export function ViderFeatures() {
  return (
    <section id="features" className="py-24 md:py-32 bg-background">
      <div className="max-w-7xl mx-auto px-6">
        {/* Section header */}
        <div className="mb-16">
          <p className="text-label text-vider-accent mb-3">Khám phá</p>
          <h2 className="text-display text-3xl md:text-5xl text-foreground">
            BẮT ĐẦU VỚI
            <br />
            VIDER<span className="text-vider-accent">.</span>
          </h2>
        </div>

        {/* Suggested prompts grid */}
        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-24"
        >
          {prompts.map((p) => (
            <motion.div
              key={p.title}
              variants={item}
              className="group relative bg-surface-sunken border border-border rounded-lg p-6 cursor-pointer hover:bg-card hover:border-foreground/20 transition-all duration-300 vider-shadow hover:vider-shadow-lg"
            >
              <div className="w-10 h-10 rounded-md bg-foreground flex items-center justify-center mb-4 group-hover:bg-vider-accent transition-colors duration-300">
                <p.icon className="w-5 h-5 text-background group-hover:text-vider-accent-foreground transition-colors duration-300" />
              </div>
              <h3 className="font-semibold text-foreground mb-1">{p.title}</h3>
              <p className="text-sm text-muted-foreground">{p.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Features grid */}
        <div className="mb-16">
          <p className="text-label text-muted-foreground mb-3">Tính năng</p>
          <h2 className="text-display text-3xl md:text-5xl text-foreground">
            ĐƯỢC XÂY DỰNG
            <br />
            CHO HIỆU SUẤT<span className="text-vider-accent">.</span>
          </h2>
        </div>

        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {features.map((f) => (
            <motion.div
              key={f.title}
              variants={item}
              className="border border-border rounded-lg p-6 hover:border-foreground/20 transition-all duration-300"
            >
              <f.icon className="w-6 h-6 text-foreground mb-4" />
              <h3 className="text-label text-foreground mb-2">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
