import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { Send, User, Bot, Loader2, LogOut } from "lucide-react";
import ReactMarkdown from "react-markdown"; // 1. Added this import
import "./Chat.css";

const API_URL = "https://ai-agent-1c6j.onrender.com";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId] = useState(
    `session_${Math.random().toString(36).slice(2, 9)}`
  );

  const navigate = useNavigate();
  const scrollRef = useRef(null);

  // 2. Added Security: Redirect to login if no token
  useEffect(() => {
    if (!localStorage.getItem("token")) {
      navigate("/login");
    }
  }, [navigate]);

  /* Auto scroll */
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/home");
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await axios.post(API_URL, {
        message: userMessage.content,
        conversation_id: conversationId,
      });

      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.data.response },
      ]);
    } catch (err) {
      console.error("Chat API Error:", err);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "⚠️ Unable to connect to the AI planner.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      {/* Navbar */}
      <div className="chat-navbar">
        <div className="chat-brand">
          <div className="chat-logo">GP</div>
          <h2 className="chat-title">Goal Planner</h2>
        </div>

        <button className="logout-btn" onClick={handleLogout}>
          <LogOut size={18} /> Logout
        </button>
      </div>

      {/* Chat Area */}
      <div className="chat-body">
        {messages.length === 0 && (
          <div className="chat-welcome">
            <h3>Welcome 👋</h3>
            <p>What goal would you like to plan today?</p>
          </div>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`message-row ${msg.role}`}>
            <div className={`message-card ${msg.role}`}>
              <div className={`avatar ${msg.role}`}>
                {msg.role === "user" ? <User size={18} /> : <Bot size={18} />}
              </div>

              {/* 3. Updated this Bubble to render Markdown Points */}
              <div className={`message-bubble ${msg.role}`}>
                {msg.role === "assistant" ? (
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                ) : (
                  msg.content
                )}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="chat-loading">
            <Loader2 size={16} className="spin" />
            AI is thinking...
          </div>
        )}

        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="chat-input-wrapper">
        <form className="chat-form" onSubmit={handleSendMessage}>
          <input
            className="chat-input"
            placeholder="Type your goal..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />

          <button
            className="send-btn"
            type="submit"
            disabled={isLoading}
          >
            <Send size={20} />
          </button>
        </form>
      </div>
    </div>
  );
}
