import { useEffect, useRef } from "react";
import type { ReactNode } from "react";
import { Button } from "./Button";
import { Icon } from "./Icon";
import { containDialogFocus } from "./dialog-focus";

interface ModalProps {
  id: string;
  title: string;
  eyebrow?: string;
  open: boolean;
  onClose(): void;
  closeLabel: string;
  children: ReactNode;
  className?: string;
}

/** Native dialog provides focus containment, background inertness and Escape handling. */
export function Modal({
  id,
  title,
  eyebrow,
  open,
  onClose,
  closeLabel,
  children,
  className = "",
}: ModalProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (!dialog) return;
    if (open && !dialog.open) dialog.showModal();
    if (!open && dialog.open) dialog.close();
  }, [open]);

  return (
    <dialog
      ref={dialogRef}
      id={id}
      className={`modal ${className}`}
      aria-labelledby={`${id}-title`}
      onKeyDown={containDialogFocus}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
      onClose={onClose}
      onClick={(event) => {
        if (event.target !== event.currentTarget) return;
        const bounds = event.currentTarget.getBoundingClientRect();
        if (
          event.clientX < bounds.left ||
          event.clientX > bounds.right ||
          event.clientY < bounds.top ||
          event.clientY > bounds.bottom
        )
          onClose();
      }}
    >
      <div className="modal-heading">
        <div>
          {eyebrow && <span className="eyebrow">{eyebrow}</span>}
          <h2 id={`${id}-title`}>{title}</h2>
        </div>
        <Button variant="icon" aria-label={closeLabel} onClick={onClose}>
          <Icon name="close" />
        </Button>
      </div>
      {children}
    </dialog>
  );
}
