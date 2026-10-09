import { useEffect, useRef, useState } from "react";
import { Button } from "../../components/Button";
import { Icon } from "../../components/Icon";
import { containDialogFocus } from "../../components/dialog-focus";
import { ChatMessages } from "./ChatMessages";
import type { ChatMessage } from "./ChatMessages";
import { ChatComposer, MAX_QUESTION_LENGTH } from "./ChatComposer";
import { localReply } from "./local-reply";
import type { ChatContext } from "./local-reply";
import "./ChatPanel.css";

interface ChatPanelProps {
  context: ChatContext;
  focusRequest: number;
  expanded: boolean;
  onExpandedChange(expanded: boolean): void;
  initiallyOpen?: boolean;
}

const MAX_MESSAGES = 42;
const suggestions = [
  {
    label: "Résumer la mission",
    question: "Résumer la mission",
    icon: "target",
  },
  {
    label: "Constats à examiner",
    question: "Constats à revoir",
    icon: "clipboard",
  },
  {
    label: "Retrouver les preuves",
    question: "Voir les preuves",
    icon: "folder",
  },
] as const;

export function ChatPanel({
  context,
  focusRequest,
  expanded,
  onExpandedChange,
  initiallyOpen = false,
}: ChatPanelProps) {
  const [open, setOpen] = useState(initiallyOpen);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<readonly ChatMessage[]>([]);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const panelRef = useRef<HTMLElement>(null);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const expandButtonRef = useRef<HTMLButtonElement>(null);
  const wasExpandedRef = useRef(false);

  useEffect(() => {
    if (focusRequest === 0) return;
    setOpen(true);
    panelRef.current?.scrollIntoView({ block: "nearest" });
    inputRef.current?.focus({ preventScroll: true });
  }, [focusRequest]);

  useEffect(() => {
    if (expanded) {
      setOpen(true);
      if (!dialogRef.current?.open) dialogRef.current?.showModal();
      inputRef.current?.focus({ preventScroll: true });
    } else if (wasExpandedRef.current) {
      dialogRef.current?.close();
      expandButtonRef.current?.focus({ preventScroll: true });
    }
    wasExpandedRef.current = expanded;
  }, [expanded]);

  function askMission(question: string) {
    const text = question.trim().slice(0, MAX_QUESTION_LENGTH);
    if (!text) return;
    setOpen(true);
    setMessages((current) => {
      const nextId = (current.at(-1)?.id ?? 0) + 1;
      const timestamp = new Date();
      return [
        ...current,
        { id: nextId, author: "Vous" as const, text, timestamp },
        {
          id: nextId + 1,
          author: "Argos" as const,
          text: localReply(text, context),
          timestamp,
        },
      ].slice(-MAX_MESSAGES);
    });
    setDraft("");
    inputRef.current?.focus({ preventScroll: true });
  }

  const surface = (
    <>
      <div className="panel-heading chat-heading">
        <div className="panel-heading-label">
          <span className="chat-mark">
            <Icon name="chat" />
          </span>
          <h2 id="chat-title">Argos Chat</h2>
        </div>
        <div className="chat-actions">
          {!expanded && (
            <Button
              variant="quiet"
              id="chat-toggle"
              aria-expanded={open}
              aria-controls="chat-content"
              onClick={() => setOpen(!open)}
            >
              {open ? "Réduire la conversation" : "Ouvrir la conversation"}
              <Icon name="chevron" />
            </Button>
          )}
          <button
            type="button"
            ref={expandButtonRef}
            className="button button--icon"
            id="chat-expand"
            aria-expanded={expanded}
            aria-label={
              expanded
                ? "Réduire le panneau de chat"
                : "Agrandir le panneau de chat"
            }
            onClick={() => onExpandedChange(!expanded)}
          >
            <Icon name={expanded ? "close" : "expand"} />
          </button>
        </div>
      </div>
      <div className="chat-content" id="chat-content" hidden={!open}>
        <div className="chat-introduction">
          <Icon name="folder" />
          <span>Contexte : {context.assessment.mission.title}</span>
        </div>
        <ChatMessages messages={messages} open={open} />
        <div className="chat-suggestions">
          {suggestions.map((item) => (
            <Button
              key={item.question}
              onClick={() => askMission(item.question)}
            >
              <Icon name={item.icon} />
              {item.label}
            </Button>
          ))}
        </div>
      </div>
      <ChatComposer
        draft={draft}
        inputRef={inputRef}
        onDraftChange={setDraft}
        onSubmit={askMission}
      />
    </>
  );

  return (
    <>
      {!expanded && (
        <section
          ref={panelRef}
          className={`panel chat-panel ${open ? "open" : ""}`}
          id="chat-panel"
          aria-labelledby="chat-title"
        >
          {surface}
        </section>
      )}
      <dialog
        ref={dialogRef}
        id="chat-dialog"
        className="panel chat-panel chat-dialog"
        aria-labelledby="chat-title"
        onKeyDown={containDialogFocus}
        onCancel={(event) => {
          event.preventDefault();
          onExpandedChange(false);
        }}
        onClose={() => onExpandedChange(false)}
      >
        {expanded && surface}
      </dialog>
    </>
  );
}
