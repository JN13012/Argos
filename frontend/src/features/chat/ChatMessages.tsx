import { useEffect, useRef } from "react";
import { Icon } from "../../components/Icon";
import { formatTime } from "../activity/activity";

export interface ChatMessage {
  readonly id: number;
  readonly author: "Vous" | "Argos";
  readonly text: string;
  readonly timestamp: Date;
}

export function ChatMessages({
  messages,
  open,
}: {
  messages: readonly ChatMessage[];
  open: boolean;
}) {
  const containerRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const container = containerRef.current;
    if (container && open) container.scrollTop = container.scrollHeight;
  }, [messages, open]);

  return (
    <div
      className="chat-messages"
      id="chat-messages"
      ref={containerRef}
      role="log"
      aria-label="Conversation avec Argos"
      aria-live="polite"
      aria-relevant="additions"
    >
      {!messages.length && (
        <>
          <div className="message assistant-message">
            <span className="message-avatar">
              <Icon name="eye-shield" />
            </span>
            <div className="message-bubble">
              <span className="message-author">ARGOS</span>
              <p>Bonjour, bienvenue dans votre espace de travail.</p>
              <p>
                Je peux vous présenter la mission, les constats et les preuves
                de cette démonstration.
              </p>
              <span className="message-time">Démo locale</span>
            </div>
          </div>
          <div className="chat-day-divider">
            <span>EXPLORER LA DÉMONSTRATION</span>
          </div>
        </>
      )}
      {messages.map((message) => (
        <div
          className={`message ${message.author === "Vous" ? "user" : "assistant"}-message`}
          key={message.id}
        >
          {message.author === "Argos" && (
            <span className="message-avatar">
              <Icon name="eye-shield" />
            </span>
          )}
          <div className="message-bubble">
            <span className="message-author">{message.author}</span>
            <p>{message.text}</p>
            <time
              className="message-time"
              dateTime={message.timestamp.toISOString()}
            >
              {formatTime.format(message.timestamp)}
            </time>
          </div>
        </div>
      ))}
    </div>
  );
}
