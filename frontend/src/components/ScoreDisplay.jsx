import { motion } from "framer-motion";

const gradeStyles = {
  Excellent: "text-emerald-300",
  Good: "text-sky-300",
  "Needs Improvement": "text-amber-300",
  Poor: "text-rose-300",
};

export function ScoreDisplay({ score, grade, similarityScore }) {
  const progress = Math.max(0, Math.min(100, score ?? 0));
  const gradeClass = gradeStyles[grade] ?? "text-white";

  return (
    <div className="grid gap-6 md:grid-cols-[220px_1fr]">
      <motion.div
        initial={{ opacity: 0, scale: 0.92 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="relative flex aspect-square items-center justify-center self-start rounded-full border border-white/15 bg-white/5 p-5 shadow-glow"
      >
        <div
          className="absolute inset-3 rounded-full"
          style={{
            background: `conic-gradient(from 180deg, rgba(212,116,255,0.95) 0deg, rgba(132,92,255,0.95) ${
              progress * 3.6
            }deg, rgba(255,255,255,0.08) ${progress * 3.6}deg 360deg)`,
          }}
        />
        <div className="relative flex h-full w-full flex-col items-center justify-center rounded-full bg-[#12081d]/90 text-center">
          <span className="font-display text-5xl font-semibold text-white">{score}</span>
          <span className="mt-2 text-xs uppercase tracking-[0.35em] text-white/50">Score</span>
        </div>
      </motion.div>

      <div className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <span className="rounded-full border border-white/10 bg-white/8 px-4 py-2 text-xs uppercase tracking-[0.3em] text-white/70">
            Pronunciation Grade
          </span>
          <span className={`font-display text-3xl font-semibold ${gradeClass}`}>{grade}</span>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm text-white/70">
            <span>Backend similarity</span>
            <span>{Math.round((similarityScore ?? 0) * 100)}%</span>
          </div>
          <div className="h-3 overflow-hidden rounded-full bg-white/10">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${Math.round((similarityScore ?? 0) * 100)}%` }}
              transition={{ duration: 0.7, ease: "easeOut" }}
              className="h-full rounded-full bg-gradient-to-r from-fuchsia-400 via-violet-300 to-sky-300 shadow-button"
            />
          </div>
        </div>
      </div>
    </div>
  );
}
