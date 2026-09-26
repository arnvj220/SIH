import { useEffect, useState } from "react";
import { Table } from "../components/ui/Table";
import { api } from "../lib/api";
import { timestamp } from "../lib/format";
import type { SignatureSummary } from "../lib/types";

export function Signatures() {
  const [rows, setRows] = useState<SignatureSummary[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api.listSignatures().then(setRows).catch((e) => setError(String(e)));
  }, []);

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <header className="mb-6">
        <h1 className="text-xl font-semibold text-text">Signatures</h1>
        <p className="mt-1 text-sm text-muted">
          QDS signatures created by the signing service.
        </p>
      </header>

      {error && (
        <div className="mb-4 rounded-md border border-danger/40 bg-danger/10 px-4 py-2 text-sm text-danger">
          {error}
        </div>
      )}

      <Table<SignatureSummary>
        rows={rows}
        rowKey={(r, i) => r.signature_id ?? `sig-${i}`}
        empty="No signatures yet."
        columns={[
          {
            key: "id",
            header: "Signature ID",
            render: (r) => <span className="font-mono text-xs">{r.signature_id}</span>,
          },
          {
            key: "signer",
            header: "Signer",
            render: (r) => <span className="font-mono text-xs">{r.signer_id}</span>,
          },
          {
            key: "session",
            header: "Session",
            render: (r) => <span className="font-mono text-xs">{r.session_id}</span>,
          },
          {
            key: "protocol",
            header: "Protocol",
            render: (r) => <span className="text-xs text-muted">{r.protocol_version ?? "—"}</span>,
          },
          {
            key: "created",
            header: "Created",
            align: "right",
            render: (r) => <span className="text-xs text-muted">{timestamp(r.created_at)}</span>,
          },
        ]}
      />
    </div>
  );
}