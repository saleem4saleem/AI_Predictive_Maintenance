export function LoadingSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div className="skeleton-stack" aria-label="Loading">
      {Array.from({ length: rows }).map((_, index) => (
        <div className="skeleton-line" key={index} />
      ))}
    </div>
  );
}
