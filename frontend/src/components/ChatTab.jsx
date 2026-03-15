import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Image as ImageIcon } from "lucide-react";
import { sendChatMessage, getImageUrl } from "../api";
import "./ChatTab.css";

function ChatTab({ hasAnalysis }) {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hello! I am your patent analysis assistant. Upload and analyze your IDF and PR documents, then ask me anything about the key features, prior art mapping, or patentability.",
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || isLoading || !hasAnalysis) return;

    const userMsg = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const result = await sendChatMessage(trimmed);
      const assistantMsg = {
        role: "assistant",
        content: result.answer,
        sources: result.sources || [],
        images: result.images || [],
        intent: result.intent,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errMsg =
        err.message && err.message.toLowerCase().includes("run analysis")
          ? "Please run the analysis first before using the chat."
          : "Sorry, something went wrong. Please try again.";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: errMsg },
      ]);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-container">
      {!hasAnalysis && (
        <div className="chat-no-analysis-banner">
          ⚠️ Upload your IDF &amp; PR documents and run analysis first to enable the AI chat.
        </div>
      )}
      <div className="chat-messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-avatar">
              {msg.role === "assistant" ? (
                <Bot size={16} />
              ) : (
                <User size={16} />
              )}
            </div>
            <div className="message-bubble">
              <div className="message-content">{msg.content}</div>
              {msg.images && msg.images.length > 0 && (
                <div className="message-images">
                  {msg.images.map((imgPath, j) => {
                    const parts = imgPath.replace(/\\/g, "/").split("/");
                    const docType = parts[parts.length - 2] || "DOC";
                    const filename = parts[parts.length - 1];
                    return (
                      <div key={j} className="chat-image-wrapper">
                        <img
                          src={getImageUrl(docType, filename)}
                          alt="Related figure"
                          className="chat-image"
                        />
                        <div className="image-label">
                          <ImageIcon size={10} />
                          {filename}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
              {msg.sources && msg.sources.length > 0 && (
                <div className="message-sources">
                  {msg.sources.map((s, j) => (
                    <span key={j} className="source-tag">
                      {s.doc_type} — {s.section}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">
              <Bot size={16} />
            </div>
            <div className="message-bubble">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-area">
        <textarea
          ref={inputRef}
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            hasAnalysis
              ? "Ask about key features, prior art, or patentability..."
              : "Run analysis first to enable patent-specific Q&A..."
          }
          rows={1}
          id="chat-input"
          disabled={!hasAnalysis}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={isLoading || !input.trim() || !hasAnalysis}
          id="send-btn"
          title={!hasAnalysis ? "Run analysis first to enable chat" : "Send message"}
        >
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}

export default ChatTab;
