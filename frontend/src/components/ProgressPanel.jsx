import { motion } from "framer-motion";
import { TrendingUp } from "lucide-react";

export function ProgressPanel({ attempts, previousScores }) {
  const maxScore = Math.max(...(previousScores?.length ? previousScores : [100]));

  return (
    <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
      <div className="flex items-center gap-3">
        <div className="rounded-2xl bg-white/10 p-3">
          <TrendingUp className="h-5 w-5 text-violet-100" />
        </div>
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-white/45">Progress</p>
          <p className="font-display text-xl text-white">{attempts} total attempts</p>
        </div>
      </div>

      <div className="mt-5 flex items-end gap-3 overflow-x-auto pb-2">
        {previousScores?.map((score, index) => (
          <div key={`${score}-${index}`} className="min-w-[60px] flex-1">
            <div className="mb-2 text-center text-xs text-white/45">#{index + 1}</div>
            <motion.div
              initial={{ height: 0 }}
              animate={{ height: `${Math.max((score / maxScore) * 160, 18)}px` }}
              transition={{ duration: 0.5, delay: index * 0.05 }}
              className="flex items-end justify-center rounded-t-[20px] bg-gradient-to-t from-fuchsia-500 via-violet-400 to-cyan-300 px-2 pb-3 shadow-button"
            >
              <span className="font-display text-lg text-white">{score}</span>
            </motion.div>
          </div>
        ))}
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {previousScores?.map((score, index) => (
          <span
            key={`chip-${score}-${index}`}
            className="rounded-full border border-white/10 bg-white/8 px-3 py-1 text-sm text-white/80"
          >
            Attempt {index + 1}: {score}
          </span>
        ))}
      </div>
    </div>
  );
}
