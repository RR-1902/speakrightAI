export function GlassPanel({ children, className = "" }) {
  return (
    <div
      className={`rounded-[28px] border border-white/15 bg-white/10 shadow-glass backdrop-blur-2xl ${className}`}
    >
      {children}
    </div>
  );
}
