import type { RefObject } from "react";
import { Button } from "../../components/Button";
import { Icon } from "../../components/Icon";

export const MAX_QUESTION_LENGTH = 500;

interface ChatComposerProps {
  draft: string;
  inputRef: RefObject<HTMLTextAreaElement | null>;
  onDraftChange(draft: string): void;
  onSubmit(question: string): void;
}

export function ChatComposer({
  draft,
  inputRef,
  onDraftChange,
  onSubmit,
}: ChatComposerProps) {
  return (
    <div className="chat-footer">
      <form
        className="chat-form"
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit(draft);
        }}
      >
        <label className="sr-only" htmlFor="chat-input">
          Question sur la mission
        </label>
        <textarea
          ref={inputRef}
          id="chat-input"
          rows={1}
          maxLength={MAX_QUESTION_LENGTH}
          placeholder="Une question sur le dossier…"
          value={draft}
          onChange={(event) => onDraftChange(event.target.value)}
          onKeyDown={(event) => {
            if (
              event.key === "Enter" &&
              !event.shiftKey &&
              !event.nativeEvent.isComposing
            ) {
              event.preventDefault();
              onSubmit(draft);
            }
          }}
        />
        <Button
          variant="icon"
          className="send-button"
          id="chat-send"
          type="submit"
          aria-label="Envoyer le message"
          disabled={!draft.trim()}
        >
          <Icon name="send" />
        </Button>
      </form>
      <p className="chat-privacy">
        <Icon name="lock" />
        Les messages restent dans ce navigateur.
      </p>
    </div>
  );
}
