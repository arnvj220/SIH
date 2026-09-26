/**
 * Parameter sanitization for attack requests.
 *
 * The backend validates each attack's parameters against its declared
 * defaults and raises 400 on any unknown key. This module filters the
 * frontend's parameter dict through the attack's declared defaults so
 * we never send a key the attack doesn't support.
 *
 * Source of truth: AttackDescription.default_parameters (from GET /api/attacks).
 */
import type { AttackDescription } from "./types";

/**
 * Remove any parameter not declared in the attack's default_parameters.
 *
 * If the attack is undefined (e.g. list not loaded yet), returns {}.
 * If a value matches the type of the default, it is passed through;
 * mismatched types are dropped to avoid 400s from Pydantic.
 */
export function sanitizeParams(
  attack: AttackDescription | undefined,
  params: Record<string, unknown>
): Record<string, unknown> {
  if (!attack) return {};

  const defaults = attack.default_parameters;
  const allowed = new Set(Object.keys(defaults));
  const out: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(params)) {
    if (!allowed.has(key)) continue;

    const expected = defaults[key];
    // Type guard: only keep values whose JS type matches the default's.
    // null/undefined defaults are treated as "any type".
    if (expected === null || expected === undefined) {
      out[key] = value;
      continue;
    }
    if (typeof expected === "number" && typeof value === "number") {
      out[key] = value;
    } else if (typeof expected === "string" && typeof value === "string") {
      out[key] = value;
    } else if (typeof expected === "boolean" && typeof value === "boolean") {
      out[key] = value;
    } else if (
      typeof expected === "object" &&
      expected !== null &&
      typeof value === "object" &&
      value !== null
    ) {
      // Arrays (like revoked_verifiers) come through as objects in JS.
      out[key] = value;
    }
    // Any other type combination is dropped silently.
  }

  return out;
}

/**
 * Convenience: find the AttackDescription by name and sanitize in one call.
 */
export function sanitizeParamsForAttack(
  attacks: AttackDescription[],
  attackName: string,
  params: Record<string, unknown>
): Record<string, unknown> {
  return sanitizeParams(
    attacks.find((a) => a.name === attackName),
    params
  );
}

/**
 * Which key (if any) is safe to sweep for this attack?
 *
 * Prefers `perturbation`, then `modified_fraction`, then `intensity`.
 * Returns null if the attack has no numeric sweep parameter.
 */
export function sweepKeyFor(
  attack: AttackDescription | undefined
): string | null {
  if (!attack) return null;
  const candidates = ["perturbation", "modified_fraction", "intensity"];
  for (const c of candidates) {
    if (typeof attack.default_parameters[c] === "number") return c;
  }
  return null;
}