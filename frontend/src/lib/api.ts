/**
 * Typed fetch wrapper for the QDS backend.
 *
 * Reads VITE_API_BASE from the environment. In dev, Vite proxies /api
 * to http://localhost:8000, so the default empty string works.
 */
import type {
  Alert,
  AttackDescription,
  AttackRequest,
  AttackResponse,
  Event,
  ExperimentRunRequest,
  ExperimentRunResponse,
  SignatureSummary,
  VerificationRequest,
  VerificationResponse,
  VerificationSummary,
} from "./types";

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
  // Health
  health: () => request<{ status: string }>("GET", "/health"),

  // Attacks
  listAttacks: () => request<AttackDescription[]>("GET", "/api/attacks"),

  executeAttack: (attack: AttackRequest, target: VerificationRequest) =>
    request<AttackResponse>("POST", "/api/attacks/execute", { attack, target }),

  // Verification
  verify: (body: VerificationRequest) =>
    request<VerificationResponse>("POST", "/api/verification", body),

  listVerifications: () =>
    request<VerificationSummary[]>("GET", "/api/verifications"),

  // Signatures
  listSignatures: () =>
    request<SignatureSummary[]>("GET", "/api/signatures"),

  // Experiments
  listExperiments: () =>
    request<ExperimentRunResponse[]>("GET", "/api/experiments"),

  getExperiment: (id: string) =>
    request<ExperimentRunResponse>("GET", `/api/experiments/${id}`),

  runExperiment: (body: ExperimentRunRequest) =>
    request<ExperimentRunResponse>("POST", "/api/experiments/run", body),

  // Alerts
  listAlerts: () => request<Alert[]>("GET", "/api/alerts"),
  getAlert: (id: string) => request<Alert>("GET", `/api/alerts/${id}`),
  resolveAlert: (id: string) =>
    request<Alert>("POST", `/api/alerts/${id}/resolve`),

  // Events
  listEvents: () => request<Event[]>("GET", "/api/events"),
  createEvent: (body: {
    event_type: string;
    context_id?: string | null;
    details?: Record<string, unknown>;
  }) => request<Event>("POST", "/api/events", body),
  clearEvents: () => request<void>("DELETE", "/api/events"),
};

export { ApiError };