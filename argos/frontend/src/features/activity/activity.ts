export type ActivityType = "mission" | "review" | "report";
export type ActivityFilter = "all" | ActivityType;

export interface ActivityEvent {
  readonly id: number;
  readonly timestamp: Date;
  readonly type: ActivityType;
  readonly text: string;
  readonly reference: string;
}

export interface ActivityInput {
  readonly type: ActivityType;
  readonly text: string;
  readonly reference: string;
}

export const activityLabels: Record<ActivityType, string> = {
  mission: "MISSION",
  review: "CONSTAT",
  report: "RAPPORT",
};

export const MAX_ACTIVITY_EVENTS = 100;
export const COLLAPSED_ACTIVITY_EVENTS = 3;

export function appendActivity(
  events: readonly ActivityEvent[],
  input: ActivityInput,
): readonly ActivityEvent[] {
  const last = events.at(-1);
  return [
    ...events,
    { ...input, id: (last?.id ?? 0) + 1, timestamp: new Date() },
  ].slice(-MAX_ACTIVITY_EVENTS);
}

export const formatTime = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
  second: "2-digit",
});
