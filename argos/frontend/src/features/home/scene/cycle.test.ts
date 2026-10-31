import { describe, expect, it } from "vitest";
import { CYCLE_SECONDS, cycleAt } from "./cycle";

describe("homepage scene choreography", () => {
  it("keeps the globe alone at the beginning and before looping", () => {
    expect(cycleAt(0)).toEqual({ phase: "osint", red: 0, blue: 0 });
    expect(cycleAt(40)).toEqual({ phase: "osint", red: 0, blue: 0 });
    expect(cycleAt(CYCLE_SECONDS)).toEqual(cycleAt(0));
  });

  it("introduces each mascot gradually and never overlaps their full presence", () => {
    expect(cycleAt(12).red).toBe(0);
    expect(cycleAt(13.5).red).toBeCloseTo(0.5);
    expect(cycleAt(16).red).toBe(1);
    expect(cycleAt(22).red).toBeCloseTo(0.5);
    expect(cycleAt(24).red).toBe(0);
    expect(cycleAt(24).blue).toBe(0);
    expect(cycleAt(25.5).blue).toBeCloseTo(0.5);
    expect(cycleAt(29).blue).toBe(1);
    expect(cycleAt(36).blue).toBe(0);
    for (let time = 0; time < 2 * CYCLE_SECONDS; time += 0.125) {
      const state = cycleAt(time);
      expect(state.red).toBeGreaterThanOrEqual(0);
      expect(state.red).toBeLessThanOrEqual(1);
      expect(state.blue).toBeGreaterThanOrEqual(0);
      expect(state.blue).toBeLessThanOrEqual(1);
      expect(state.red * state.blue).toBe(0);
    }
  });
});
