import { expect, it } from "vitest";
import { appendActivity } from "./activity";
import type { ActivityEvent } from "./activity";

it("retains the latest 100 session events with monotonic ids without mutating the old list", () => {
  let events: readonly ActivityEvent[] = [];
  const input = {
    type: "mission",
    text: "Dossier consulté.",
    reference: "MIS-001",
  } as const;
  const initial = appendActivity(events, input);
  events = initial;
  for (let i = 0; i < 110; i++) events = appendActivity(events, input);
  expect(initial).toHaveLength(1);
  expect(events).toHaveLength(100);
  expect(events[0]?.id).toBe(12);
  expect(events.at(-1)?.id).toBe(111);
});
