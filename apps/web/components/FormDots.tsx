export default function FormDots({ results }: { results: number[] }) {
  return (
    <div className="flex items-center gap-1">
      {results.map((val, idx) => (
        <span
          key={`${val}-${idx}`}
          className={`h-2.5 w-2.5 rounded-full ${val > 0 ? "bg-wave" : val < 0 ? "bg-coral" : "bg-slate/40"}`}
        />
      ))}
    </div>
  );
}
