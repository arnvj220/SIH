import { useEffect, useState } from "react";
import clsx from "clsx";
import { api } from "../../lib/api";

type Status = "unknown" | "online" | "offline";

export function StatusPill() {
  const [status, setStatus] = useState<Status>("unknown");

  useEffect(() => {
    let cancelled = false;

    const check = async () => {
      try {
        await api.health();
        if (!cancelled) setStatus("online");
      } catch {
        if (!cancelled) setStatus("offline");
      }
    };

    check();
    const t = setInterval(check, 10_000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, []);

  return (
    <span
      className={clsx(
        "flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] font-medium",
        status === "online" &&
          "border-success/30 bg-success/10 text-success",
        status === "offline" && "border-danger/30 bg-danger/10 text-danger",
        status === "unknown" && "border-border bg-bg text-muted"
      )}
      title={
        status === "online"
          ? "Backend reachable"
          : status === "offline"
            ? "Backend not responding"
            : "Checking backend…"
      }
    >
      <span
        className={clsx(
          "h-1.5 w-1.5 rounded-full",
          status === "online" && "bg-success",
          status === "offline" && "bg-danger",
          status === "unknown" && "bg-muted"
        )}
      />
      {status === "online"
        ? "Connected"
        : status === "offline"
          ? "Offline"
          : "…"}
    </span>
  );
}