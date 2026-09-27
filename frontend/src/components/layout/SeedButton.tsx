import { useState } from "react";
// import { Button } from "../ui/Button";
// import { api } from "../../lib/api";

export function SeedButton() {
  // const [busy, setBusy] = useState(false);
  const [toast] = useState<string | null>(null);

  // const seed = async () => {
  //   setBusy(true);
  //   setToast(null);
  //   try {
  //     const res = await api.seedDemo();
  //     setToast(
  //       `Seeded ${res.signatures_created} sigs · ${res.verifications_created} verifs · ${res.alerts_created} alerts`
  //     );
  //     setTimeout(() => setToast(null), 6000);
  //   } catch (e) {
  //     setToast(`Seed failed: ${String(e)}`);
  //     setTimeout(() => setToast(null), 6000);
  //   } finally {
  //     setBusy(false);
  //   }
  // };

  return (
    <div className="relative">
      {/* <Button size="sm" variant="ghost" onClick={seed} disabled={busy}>
        {busy ? "Seeding…" : "Seed demo data"}
      </Button> */}
      {toast && (
        <div className="absolute right-0 top-full mt-2 z-30 w-max max-w-[320px] rounded-md border border-border bg-surface px-3 py-2 text-[11px] text-muted shadow-lg">
          {toast}
        </div>
      )}
    </div>
  );
}