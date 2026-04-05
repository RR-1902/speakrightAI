import { motion } from "framer-motion";
import { MessageSquareQuote, Mic2 } from "lucide-react";
import { GlassPanel } from "./GlassPanel";
import { PhonemeAccordion } from "./PhonemeAccordion";
import { ProgressPanel } from "./ProgressPanel";
import { ScoreDisplay } from "./ScoreDisplay";

export function ResultCard({ result, phonemeOpen, onTogglePhoneme }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.55 }}
    >
      <GlassPanel className="space-y-6 p-6 md:p-8">
        <ScoreDisplay
          score={result.pronunciation_score}
          grade={result.grade}
          similarityScore={result.similarity_score}
        />

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
            <div className="flex items-center gap-3">
              <Mic2 className="h-5 w-5 text-violet-100" />
              <p className="text-xs uppercase tracking-[0.35em] text-white/45">Transcribed Text</p>
            </div>
            <p className="mt-4 text-lg leading-8 text-white/92">{result.transcribed_text}</p>
          </div>

          <div className="rounded-[24px] border border-white/10 bg-white/5 p-5">
            <div className="flex items-center gap-3">
              <MessageSquareQuote className="h-5 w-5 text-violet-100" />
              <p className="text-xs uppercase tracking-[0.35em] text-white/45">Coach Feedback</p>
            </div>
            <p className="mt-4 text-lg leading-8 text-white/88">{result.feedback}</p>
          </div>
        </div>

        <PhonemeAccordion
          items={result.phoneme_analysis}
          isOpen={phonemeOpen}
          onToggle={onTogglePhoneme}
        />

        <ProgressPanel attempts={result.attempts} previousScores={result.previous_scores} />
      </GlassPanel>
    </motion.div>
  );
}
