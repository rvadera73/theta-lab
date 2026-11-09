import { useState, ReactNode } from "react";

export default function Collapsible({
  title,
  badge,
  defaultOpen = false,
  children,
}: {
  title: string;
  badge?: ReactNode;
  defaultOpen?: boolean;
  children: ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <section className="bg-panel border border-border rounded-md mb-3 overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2.5 text-left hover:bg-panelAlt/60 transition-colors"
      >
        <span className="flex items-center gap-2">
          <span className="text-[13px] font-semibold text-ink">{title}</span>
          {badge}
        </span>
        <span className="text-faint text-[11px]">{open ? "▴ collapse" : "▾ expand"}</span>
      </button>
      {open && <div className="px-4 pb-4 border-t border-border">{children}</div>}
    </section>
  );
}
