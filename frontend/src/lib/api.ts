
import type {
  Alert,
  AttackDescription,
  AttackRequest,
  AttackResponse,
  Event,
  ExperimentRunRequest,
  ExperimentRunResponse,
  SignatureSummary,
  SignatureDetail,
  VerificationRequest,
  VerificationResponse,
  VerificationSummary,
} from "./types";
import { cached, invalidate } from "./cache";

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";

class ApiError extends Error {
  constructor(public status: number, public body: unknown, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(
  method: string,
  path: string,
  body?: unknown
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers: body !== undefined ? { "Content-Type": "application/json" } : {},
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  const text = await res.text();
  const data = text ? safeParse(text) : null;

  if (!res.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? (data as { detail: unknown }).detail
        : res.statusText;
    throw new ApiError(res.status, data, `HTTP ${res.status}: ${detail}`);
  }

  return data as T;
}

function safeParse(text: string): unknown {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export const api = {
  health: () => request<{ status: string }>("GET", "/health"),

  listAttacks: () =>
    cached("attacks", 60_000, () =>
      request<AttackDescription[]>("GET", "/api/attacks")
    ),

  executeAttack: (attack: AttackRequest, target: VerificationRequest) =>
    request<AttackResponse>("POST", "/api/attacks/execute", { attack, target }),

  verify: (body: VerificationRequest) =>
    request<VerificationResponse>("POST", "/api/verification", body),

  listVerifications: () =>
    cached("verifications", 15_000, () =>
      request<VerificationSummary[]>("GET", "/api/verifications")
    ),

  listSignatures: () =>
    cached("signatures", 15_000, () =>
      request<SignatureSummary[]>("GET", "/api/signatures")
    ),

  getSignature: (id: string) =>
    request<SignatureDetail>("GET", `/api/signatures/${id}`),

  listExperiments: () =>
  cached("experiments", 15_000, () =>
    request<ExperimentRunResponse[]>("GET", "/api/experiments")
  ),

  getExperiment: (id: string) =>
    request<ExperimentRunResponse>("GET", `/api/experiments/${id}`),

  runExperiment: (body: ExperimentRunRequest) =>
    request<ExperimentRunResponse>("POST", "/api/experiments/run", body).then(
      (res) => {
        invalidate("experiments");
        return res;
      }
    ),

  listAlerts: () =>
    cached("alerts", 15_000, () =>
      request<Alert[]>("GET", "/api/alerts")
    ),

  getAlert: (id: string) =>
    request<Alert>("GET", `/api/alerts/${id}`),

  resolveAlert: (id: string) =>
    request<Alert>("POST", `/api/alerts/${id}/resolve`).then((res) => {
      invalidate("alerts");
      return res;
    }),

  listEvents: () =>
    cached("events", 15_000, () =>
      request<Event[]>("GET", "/api/events")
    ),

  createEvent: (body: {
    event_type: string;
    context_id?: string | null;
    details?: Record<string, unknown>;
  }) =>
    request<Event>("POST", "/api/events", body).then((res) => {
      invalidate("events");
      return res;
    }),

  clearEvents: () =>
    request<void>("DELETE", "/api/events").then(() => invalidate("events")),

  seedDemo: () =>
    request<{
      signatures_created: number;
      verifications_created: number;
      alerts_created: number;
    }>("POST", "/api/seed/demo").then((res) => {
      // Seed writes to every collection — bust every cached resource.
      invalidate("signatures");
      invalidate("verifications");
      invalidate("alerts");
      invalidate("events");
      invalidate("experiments");
      return res;
    }),
};

export { ApiError };