export default function PlaceholderPage({ name }: { name: string }) {
  return (
    <div className="bg-panel border border-border rounded-md p-8 text-center text-faint">
      <p className="font-medium text-ink mb-1">{name}</p>
      <p className="text-sm">
        Not yet migrated to the new app shell — still live at its original page for now. Today is the reference implementation; this tab is next.
      </p>
    </div>
  );
}
