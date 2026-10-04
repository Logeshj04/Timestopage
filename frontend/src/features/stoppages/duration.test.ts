import { describe, expect, it } from "vitest";
import { z } from "zod";

const schema = z.object({
  duration_minutes: z.coerce.number().int().gt(0, "Duration must be greater than 0 minutes."),
});

describe("stoppage duration validation", () => {
  it("rejects zero and negative values", () => {
    expect(schema.safeParse({ duration_minutes: 0 }).success).toBe(false);
    expect(schema.safeParse({ duration_minutes: -5 }).success).toBe(false);
  });

  it("accepts positive minutes", () => {
    expect(schema.parse({ duration_minutes: 15 })).toEqual({ duration_minutes: 15 });
  });
});
