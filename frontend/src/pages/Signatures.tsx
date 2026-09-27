import { useEffect, useState } from "react";
import { Badge } from "../components/ui/Badge";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Empty, Loading } from "../components/ui/Empty";
import { Table } from "../components/ui/Table";
import { api } from "../lib/api";
import { timestamp } from "../lib/format";
import type { SignatureDetail, SignatureSummary } from "../lib/types";
import { Page } from "../components/layout/Page";
import { invalidate } from "../lib/cache";

interface EvidenceStep {
  step: string;
  result: string;
}

function asText(value: unknown): string {
  return value === undefined || value === null ? "—" : String(value);
}

function evidenceSteps(evidence: Record<string, unknown>): EvidenceStep[] {
  const measurement = evidence.measurement_bits;
  const correction = evidence.correction_bits;
  const operator = evidence.correction_operator;
  return [
    { step: "Quantum measurement", result: measurement ? `Bits ${measurement}` : "No measurement data" },
    { step: "Correction", result: correction ? `Bits ${correction}` : "No correction data" },
    { step: "Applied operator", result: asText(operator) },
    { step: "Reproducibility seed", result: asText(evidence.seed) },
  ];
}

export function Signatures() {
  const [rows, setRows] = useState<SignatureSummary[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<SignatureDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const selectSignature = async (signatureId: string) => {
    setSelectedId(signatureId);
    setDetail(null);
    setDetailLoading(true);
    try {
      setDetail(await api.getSignature(signatureId));
    } catch (e) {
      setError(String(e));
    } finally {
      setDetailLoading(false);
    }
  };

  const refresh = async () => {
    invalidate("signatures");
    setLoading(true);
    setError(null);
    try {
      const latest = await api.listSignatures();
      setRows(latest);
      const nextId = selectedId && latest.some((row) => row.signature_id === selectedId)
        ? selectedId
        : latest[0]?.signature_id ?? null;
      if (nextId) await selectSignature(nextId);
      else {
        setSelectedId(null);
        setDetail(null);
      }
    } catch (e) {
      setError(String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const evidence = detail?.quantum_evidence ?? {};
  const state = evidence.input_state;
  const stateSize = Array.isArray(state) ? `${state.length} amplitudes` : "Not available";

  return (
    <Page
      title="Signatures"
      subtitle="Trace each generated QDS signature from signer and message identity to its digest and quantum correction evidence."
      actions={
        <Button size="sm" variant="ghost" onClick={refresh} disabled={loading}>
          {loading ? "Loading..." : "Refresh"}
        </Button>
      }
    >
      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      {loading && rows.length === 0 ? (
        <Loading label="Fetching signatures..." />
      ) : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-text">Signature registry</h2>
              <Badge tone="secondary">{rows.length} records</Badge>
            </div>
            <Table<SignatureSummary>
              rows={rows}
              rowKey={(row) => row.signature_id}
              empty="No signatures have been created yet."
              columns={[
                {
                  key: "signature",
                  header: "Signature / message",
                  render: (row) => (
                    <button
                      className={`text-left ${selectedId === row.signature_id ? "font-semibold text-primary" : "text-text hover:text-primary"}`}
                      onClick={() => selectSignature(row.signature_id)}
                    >
                      <span className="block font-mono text-xs">{row.signature_id}</span>
                      <span className="mt-0.5 block text-[11px] text-muted">Message {row.message_id}</span>
                    </button>
                  ),
                },
                {
                  key: "signer",
                  header: "Signer / session",
                  render: (row) => (
                    <span className="block text-xs text-text">
                      {row.signer_id}
                      <span className="mt-0.5 block font-mono text-[11px] text-muted">{row.session_id}</span>
                    </span>
                  ),
                },
                {
                  key: "protocol",
                  header: "Protocol",
                  render: (row) => <Badge tone="primary">{row.protocol_version ?? "Unknown"}</Badge>,
                },
                {
                  key: "created",
                  header: "Created",
                  align: "right",
                  render: (row) => <span className="text-xs text-muted">{timestamp(row.created_at)}</span>,
                },
              ]}
            />
          </div>

          <div>
            {detailLoading ? (
              <Loading label="Loading signature evidence..." />
            ) : detail ? (
              <div className="space-y-4">
                <Card title="Signature record" subtitle={detail.signature_id}>
                  <dl className="grid grid-cols-[minmax(90px,auto)_1fr] gap-x-4 gap-y-2 text-xs">
                    <dt className="text-muted">Signer</dt><dd className="font-mono text-text">{detail.signer_id}</dd>
                    <dt className="text-muted">Message</dt><dd className="font-mono text-text">{detail.message_id}</dd>
                    <dt className="text-muted">Session</dt><dd className="font-mono text-text">{detail.session_id}</dd>
                    <dt className="text-muted">Protocol</dt><dd className="text-text">{detail.protocol_version ?? "—"}</dd>
                    <dt className="text-muted">Created</dt><dd className="text-text">{timestamp(detail.created_at)}</dd>
                  </dl>
                  <div className="mt-4 border-t border-border pt-3">
                    <div className="text-[11px] font-medium text-muted">Message digest · SHA-256</div>
                    <code className="mt-1 block break-all rounded border border-border bg-bg p-2 font-mono text-[11px] text-text">
                      {detail.message_digest ?? "Not available"}
                    </code>
                  </div>
                </Card>

                <Card title="Signing evidence" subtitle="Teleportation measurement and correction record">
                  <Table<EvidenceStep>
                    rows={evidenceSteps(evidence)}
                    rowKey={(row) => row.step}
                    columns={[
                      { key: "step", header: "Step", render: (row) => <span className="text-xs text-muted">{row.step}</span> },
                      { key: "result", header: "Recorded result", render: (row) => <span className="font-mono text-xs text-text">{row.result}</span> },
                    ]}
                  />
                  <details className="mt-3">
                    <summary className="cursor-pointer text-xs text-muted">Inspect state vectors</summary>
                    <pre className="mt-2 max-h-48 overflow-auto rounded-md border border-border bg-bg p-3 text-[11px] font-mono text-muted">
                      {JSON.stringify({ stateSize, beforeCorrection: evidence.bob_state_before_correction, afterCorrection: evidence.bob_state_after_correction }, null, 2)}
                    </pre>
                  </details>
                </Card>
              </div>
            ) : (
              <Empty title="Select a signature" hint="Choose a record to inspect its digest and signing evidence." />
            )}
          </div>
        </div>
      )}
    </Page>
  );
}