import type { ReactNode } from "react";

interface Column<T> {
  key: string;
  header: ReactNode;
  align?: "left" | "right";
  render: (row: T) => ReactNode;
}

interface TableProps<T> {
  columns: Column<T>[];
  rows: T[];
  empty?: ReactNode;
  rowKey: (row: T, idx: number) => string;
}

export function Table<T>({ columns, rows, empty, rowKey }: TableProps<T>) {
  if (rows.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-border bg-surface px-4 py-8 text-center text-sm text-muted">
        {empty ?? "No rows."}
      </div>
    );
  }
  return (
    <div className="overflow-auto rounded-md border border-border bg-surface">
      <table className="w-full bg-surface text-sm">
        <thead className="bg-bg">
          <tr>
            {columns.map((c) => (
              <th
                key={c.key}
                className={`border-b border-border bg-bg px-2 py-1.5 text-xs font-semibold uppercase tracking-wider text-muted sm:px-3 sm:py-2 ${
                  c.align === "right" ? "text-right" : "text-left"
                }`}
              >
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr
              key={rowKey(row, i)}
              className="border-t border-border bg-surface hover:bg-bg/60"
            >
              {columns.map((c) => (
                <td
                  key={c.key}
                  className={`px-2 py-1.5 sm:px-3 sm:py-2 ${
                    c.align === "right" ? "text-right font-mono" : ""
                  }`}
                >
                  {c.render(row)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}