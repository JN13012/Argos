import type { KeyboardEvent } from "react";

/** Keep Tab inside the dialog instead of sending it to the browser chrome. */
export function containDialogFocus(
  event: KeyboardEvent<HTMLDialogElement>,
): void {
  if (event.key !== "Tab") return;
  const controls = [
    ...event.currentTarget.querySelectorAll<HTMLElement>(
      'a[href], button:not(:disabled), input:not(:disabled), select:not(:disabled), textarea:not(:disabled), [tabindex]:not([tabindex="-1"])',
    ),
  ].filter((node) => node.getClientRects().length > 0 && node.tabIndex >= 0);
  const first = controls[0];
  const last = controls.at(-1);
  if (!first || !last) return;
  if (
    event.shiftKey &&
    (document.activeElement === first ||
      document.activeElement === event.currentTarget)
  ) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}
