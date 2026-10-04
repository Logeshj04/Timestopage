import { describe, expect, it } from "vitest";
import { currentShiftCode, todayProductionDateInput } from "../utils/datetime";

describe("production date helpers", () => {
  it("uses previous calendar date for Shift C after midnight", () => {
    const moment = new Date("2026-08-28T19:30:00.000Z");
    expect(currentShiftCode(moment)).toBe("C");
    expect(todayProductionDateInput(moment)).toBe("2026-08-28");
  });
});
