import { useState, useEffect } from "react";
import MarkdownBlock from "./MarkdownBlock";

// Used as a Collapsible's child -- Collapsible only mounts its children once
// opened, so this fetches lazily on first expand rather than loading every
// report section up front on page load.
export default function ReportSection({ fetcher }: { fetcher: () => Promise<{ text: string; as_of?: string }> }) {
  const [text, setText] = useState<string | null>(null);
  const [asOf, setAsOf] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    fetcher()
      .then((r) => {
        if (cancelled) return;
        setText(r.text);
        setAsOf(r.as_of || "");
      })
      .catch((e) => !cancelled && setError(e instanceof Error ? e.message : String(e)));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error) return <p className="text-sm text-down py-2">Failed to load: {error}</p>;
  if (text === null) return <p className="text-faint italic text-sm py-4">Loading…</p>;
  return (
    <div className="pt-3">
      {asOf && <p className="text-[11px] text-faint mb-2">as of {asOf}</p>}
      <MarkdownBlock text={text} />
    </div>
  );
}
