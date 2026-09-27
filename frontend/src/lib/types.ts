/** Types mirroring backend Pydantic schemas. */

export type ThreatType =
  | "NONE"
  | "FORGERY"
  | "IMPERSONATION"
  | "REPLAY"
  | "UNAUTHORIZED_VERIFICATION"
  | "CHANNEL_MANIPULATION";

export type Decision = "ACCEPT" | "REJECT" | "SUSPICIOUS";

export type Basis = "X" | "Y" | "Z";

// ── Attacks ──────────────────────────────────────────────────────────

export interface AttackDescription {
  name: string;
  threat_type: ThreatType;
  description: string;
  modes: string[];
  default_parameters: Record<string, unknown>;
}

export interface AttackRequest {
  attack_id: string;
  attack_type: string;
  seed: number;
  parameters: Record<string, unknown>;
}

export interface AttackSampleResponse {
  context_id: string;
  is_attack: boolean;
  expected_threat: ThreatType;
  role: string;
  evidence: Record<string, unknown>;
}

export interface AttackResponse {
  attack_id: string;
  attack_type: ThreatType;
  scenario_name: string;
  seed: number;
  parameters: Record<string, unknown>;
  samples: AttackSampleResponse[];
  evidence: Record<string, unknown>;
}

// ── Verification ────────────────────────────────────────────────────

export interface MeasurementRoundSchema {
  index: number;
  basis: Basis;
  expected: 0 | 1;
  observed: 0 | 1;
}

export interface VerificationRequest {
  verification_id: string;
  signature_id: string;
  signer_id: string;
  expected_signer_id: string;
  verifier_id: string;
  message_id: string;
  message_digest: string;
  signed_digest: string;
  session_id: string;
  nonce: string;
  issued_at: number;
  received_at: number;
  auth_fingerprint: string;
  measurements: MeasurementRoundSchema[];
  protocol_version: string;
  metadata: Record<string, unknown>;
}

export interface VerificationResponse {
  verification_id: string;
  decision: Decision;
  threats: ThreatType[];
  evidence: Record<string, unknown>[];
  detected: boolean;
  error_rate: number;
}

// ── Experiments ─────────────────────────────────────────────────────

export interface ExperimentRunRequest {
  attack_type: string;
  parameters: Record<string, unknown>;
  n_targets: number;
  seed: number;
  rounds: number;
  natural_error_rate: number;
}

export interface ExperimentRunResponse {
  experiment_id: string;
  config: Record<string, unknown>;
  metrics: Record<string, unknown>;
  attack_evidence: Record<string, unknown>;
  created_at?: string | null;
}

// ── Alerts ──────────────────────────────────────────────────────────

export interface Alert {
  alert_id: string;
  alert_type: string;
  severity: string;
  status: string;
  verification_id: string | null;
  attack_id: string | null;
  title: string;
  description: string | null;
  evidence: unknown;
  created_at: string | null;
  resolved_at: string | null;
}

// ── Events ──────────────────────────────────────────────────────────

export interface Event {
  event_id: string;
  event_type: string;
  context_id: string | null;
  details: Record<string, unknown>;
  created_at: string;
}

// ── Signatures / Verifications ──────────────────────────────────────

export interface SignatureSummary {
  signature_id: string;
  signer_id: string;
  message_id: string;
  session_id: string;
  protocol_version: string | null;
  created_at: string | null;
}

export interface SignatureDetail extends SignatureSummary {
  message_digest: string | null;
  quantum_evidence: Record<string, unknown>;
}

export interface VerificationSummary {
  verification_id: string;
  signature_id: string | null;
  verifier_id: string | null;
  decision: string | null;
  detected: boolean | null;
  error_rate: number | null;
  created_at: string | null;
}