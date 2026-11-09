import { marked } from "marked";
import { useMemo } from "react";

// Report sections (Sector Heat, Risk & Macro, Framework status, Quarterly
// Direction, India's full report) are hand/report-authored markdown, not
// structured data -- rendering it is genuinely the right call here rather
// than re-parsing it into components, same choice the legacy *.html pages
// already made with marked.js from a CDN script tag. Bundled via npm here
// instead so Vite controls the version or lazily-executed arbitrary script
// we don't bundle isn't loaded at runtime.
export default function MarkdownBlock({ text }: { text: string }) {
  const html = useMemo(() => marked.parse(text || "_No content._", { async: false }) as string, [text]);
  return <div className="rendered-md text-[13px] text-ink/90" dangerouslySetInnerHTML={{ __html: html }} />;
}
