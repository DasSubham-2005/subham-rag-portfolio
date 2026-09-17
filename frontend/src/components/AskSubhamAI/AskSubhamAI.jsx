import { useEffect, useRef, useState } from "react";
import { Bot, Send, X, Sparkles } from "lucide-react";
import { api } from "../../api";
import "./AskSubhamAI.css";

const INITIAL_MESSAGE = {
  role: "bot",
  text: "Hi! 👋 I'm Subham's portfolio AI. Ask me about his projects, skills, education or experience.",
};

export default function AskSubhamAI() {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([INITIAL_MESSAGE]);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "end",
    });
  }, [messages, loading]);

  async function send(text = q) {
    const question = text.trim();

    if (!question || loading) return;

    setQ("");

    setMessages((current) => [
      ...current,
      {
        role: "user",
        text: question,
      },
    ]);

    setLoading(true);

    try {
      const result = await api("/api/assistant", {
        method: "POST",
        body: {
          question,
        },
      });

      const answer =
        result?.answer?.trim() ||
        "I could not find that information in the portfolio knowledge base.";

      setMessages((current) => [
        ...current,
        {
          role: "bot",
          text: answer,
        },
      ]);
    } catch (error) {
      console.error("Ask Subham AI error:", error);

      setMessages((current) => [
        ...current,
        {
          role: "bot",
          text: "The AI assistant is currently unavailable. Please try again later.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(event) {
    event.preventDefault();
    send();
  }

  function handleQuickQuestion(question) {
    send(question);
  }

  return (
    <>
      {!open && (
        <button
          className="ai-launch"
          onClick={() => setOpen(true)}
          aria-label="Open Talk to Subham AI"
        >
          <Bot />

          <span>
            <b>Talk to Subham AI ✨</b>
            <small>RAG-powered portfolio assistant ✨</small>
          </span>
        </button>
      )}

      {open && (
        <section className="ai-chat" aria-label="Talk to Subham AI chat">
          <header>
            <div className="ai-icon">
              <Sparkles />
            </div>

            <div>
              <b>Talk to Subham AI</b>
              <small>RAG-powered portfolio assistant ✨</small>
            </div>

            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close Talk to Subham AI"
            >
              <X />
            </button>
          </header>

          <div className="ai-messages">
            {messages.map((message, index) => (
              <div
                key={`${message.role}-${index}`}
                className={`ai-msg ${message.role}`}
              >
                {message.text}
              </div>
            ))}

            {loading && <div className="ai-msg bot">Thinking…</div>}
            <div ref={messagesEndRef} />
          </div>

          <div className="quick">
            <button
              type="button"
              disabled={loading}
              onClick={() => handleQuickQuestion("Who is Subham Das?")}
            >
              Who is Subham?
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => handleQuickQuestion("What projects has he built?")}
            >
              Projects
            </button>

            <button
              type="button"
              disabled={loading}
              onClick={() => handleQuickQuestion("What are his skills?")}
            >
              Skills
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            <input
              value={q}
              onChange={(event) => setQ(event.target.value)}
              placeholder="Ask about Subham…"
              disabled={loading}
              autoComplete="off"
              aria-label="Ask a question about Subham"
            />

            <button
              type="submit"
              disabled={loading || !q.trim()}
              aria-label="Send question"
            >
              <Send />
            </button>
          </form>
        </section>
      )}
    </>
  );
}
