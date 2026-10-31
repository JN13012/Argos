export type ScenePhase = "osint" | "red" | "blue";

export const CYCLE_SECONDS = 48;

function smoothstep(start: number, end: number, value: number): number {
  const x = Math.max(0, Math.min(1, (value - start) / (end - start)));
  return x * x * (3 - 2 * x);
}

// The last twelve seconds leave the globe alone before the next cycle.
export function cycleAt(seconds: number) {
  const time = ((seconds % CYCLE_SECONDS) + CYCLE_SECONDS) % CYCLE_SECONDS;
  const red = smoothstep(12, 15, time) * (1 - smoothstep(20, 24, time));
  const blue = smoothstep(24, 27, time) * (1 - smoothstep(32, 36, time));
  const phase: ScenePhase =
    time < 12 ? "osint" : time < 24 ? "red" : time < 36 ? "blue" : "osint";
  return { phase, red, blue };
}
