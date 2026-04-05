import { ChevronDown, Sparkles } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

export function PhonemeAccordion({ items, isOpen, onToggle }) {
  return (
    <div className="rounded-[24px] border border-white/10 bg-white/5">
      <button
        type="button"
        onClick={onToggle}
        className="flex w-full items-center justify-between gap-4 px-5 py-4 text-left"
      >
        <div>
          <p className="text-xs uppercase tracking-[0.35em] text-white/45">Phoneme Analysis</p>
          <p className="mt-1 font-display text-lg text-white">
            Per-word pronunciation breakdown
          </p>
        </div>
        <motion.div animate={{ rotate: isOpen ? 180 : 0 }} transition={{ duration: 0.25 }}>
          <ChevronDown className="h-5 w-5 text-white/70" />
        </motion.div>
      </button>

      <AnimatePresence initial={false}>
        {isOpen ? (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.28 }}
            className="overflow-hidden"
          >
            <div className="space-y-4 border-t border-white/10 px-5 py-5">
              {items?.length ? (
                items.map((item, index) => (
                  <div
                    key={`${item.word}-${index}`}
                    className="rounded-2xl border border-white/10 bg-black/10 p-4"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      <Sparkles className="h-4 w-4 text-violet-200" />
                      <span className="font-display text-xl text-white">{item.word}</span>
                      {item.spoken_word && item.spoken_word !== item.word ? (
                        <span className="rounded-full bg-white/8 px-3 py-1 text-xs text-white/65">
                          Heard: {item.spoken_word}
                        </span>
                      ) : null}
                    </div>

                    <div className="mt-4 grid gap-4 lg:grid-cols-2">
                      <div>
                        <p className="text-xs uppercase tracking-[0.28em] text-white/45">
                          Expected phonemes
                        </p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {item.expected_phonemes?.map((phoneme, phonemeIndex) => (
                            <span
                              key={`${phoneme}-${phonemeIndex}-expected`}
                              className="rounded-full border border-white/10 bg-white/8 px-3 py-1 text-sm text-white"
                            >
                              {phoneme}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div>
                        <p className="text-xs uppercase tracking-[0.28em] text-white/45">
                          Actual phonemes
                        </p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {item.actual_phonemes?.map((phoneme, phonemeIndex) => (
                            <span
                              key={`${phoneme}-${phonemeIndex}-actual`}
                              className="rounded-full border border-fuchsia-200/20 bg-fuchsia-300/10 px-3 py-1 text-sm text-fuchsia-100"
                            >
                              {phoneme}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>

                    <div className="mt-4 space-y-2">
                      {item.issues?.map((issue, issueIndex) => (
                        <div
                          key={`${issue.issue_type}-${issueIndex}`}
                          className="rounded-xl border border-amber-200/10 bg-amber-300/8 px-4 py-3 text-sm text-white/85"
                        >
                          {issue.message}
                        </div>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="rounded-2xl border border-emerald-200/10 bg-emerald-300/8 p-4 text-sm text-emerald-100">
                  No phoneme issues detected in this attempt.
                </div>
              )}
            </div>
          </motion.div>
        ) : null}
      </AnimatePresence>
    </div>
  );
}
