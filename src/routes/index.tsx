import { createFileRoute } from "@tanstack/react-router";
import { ViderHeader } from "@/components/ViderHeader";
import { ViderHero } from "@/components/ViderHero";
import { ViderFeatures } from "@/components/ViderFeatures";
import { ViderFooter } from "@/components/ViderFooter";

export const Route = createFileRoute("/")({
  component: Index,
  head: () => ({
    meta: [
      { title: "VIDER — Chat With Clarity" },
      { name: "description", content: "Trợ lý AI thông minh, nhanh chóng và đa năng. Trải nghiệm hội thoại mượt mà với công nghệ tiên tiến nhất." },
      { property: "og:title", content: "VIDER — Chat With Clarity" },
      { property: "og:description", content: "Trợ lý AI thông minh, nhanh chóng và đa năng." },
    ],
  }),
});

function Index() {
  return (
    <div className="min-h-screen">
      <ViderHeader />
      <ViderHero />
      <ViderFeatures />
      <ViderFooter />
    </div>
  );
}
