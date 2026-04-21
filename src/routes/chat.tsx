import { createFileRoute } from "@tanstack/react-router";
import { ChatInterface } from "@/components/ChatInterface";

export const Route = createFileRoute("/chat")({
  component: ChatPage,
  head: () => ({
    meta: [
      { title: "VIDER — Chat" },
      { name: "description", content: "Trò chuyện với VIDER — trợ lý AI thông minh." },
      { property: "og:title", content: "VIDER — Chat" },
    ],
  }),
});

function ChatPage() {
  return <ChatInterface />;
}
