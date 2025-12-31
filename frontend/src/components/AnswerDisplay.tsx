import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import { ChevronDown, ChevronUp, FileText, Quote, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Citation {
  source: string;
  page: number;
  text: string;
  chunk_id: string;
}

interface Answer {
  id: string;
  query: string;
  content: string;
  citations: Citation[];
  timestamp: Date;
}

interface AnswerDisplayProps {
  answer: Answer;
}

export function AnswerDisplay({ answer }: AnswerDisplayProps) {
  const [showChunks, setShowChunks] = useState(false);

  return (
    <motion.div
      className="rounded-xl border border-border bg-card shadow-card overflow-hidden"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="border-b border-border bg-accent/30 px-6 py-4">
        <div className="flex items-start gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary shadow-glow">
            <Sparkles className="h-5 w-5 text-primary-foreground" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">Your question</p>
            <p className="text-foreground font-semibold">{answer.query}</p>
          </div>
        </div>
      </div>

      {/* Answer Content */}
      <div className="px-6 py-5">
        <div className="prose prose-sm max-w-none text-foreground prose-headings:text-foreground prose-strong:text-foreground prose-code:text-primary prose-code:bg-accent prose-code:px-1 prose-code:py-0.5 prose-code:rounded">
          <ReactMarkdown>{answer.content}</ReactMarkdown>
        </div>
      </div>

      {/* Citations */}
      {answer.citations.length > 0 && (
        <div className="border-t border-border px-6 py-4">
          <p className="text-sm font-semibold text-foreground mb-3 flex items-center gap-2">
            <Quote className="h-4 w-4 text-primary" />
            Evidence & Sources ({answer.citations.length})
          </p>
          <div className="space-y-2">
            {answer.citations.map((citation, index) => (
              <motion.div
                key={citation.chunk_id + index}
                className="flex items-start gap-3 rounded-lg border border-border/50 bg-accent/30 p-3"
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <div className="flex flex-col items-center justify-center min-w-[24px]">
                  <span className="text-xs font-bold text-muted-foreground">[{citation.chunk_id.substring(0, 4)}]</span>
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-foreground truncate">
                    {citation.source} <span className="text-muted-foreground">• Page {citation.page}</span>
                  </p>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2 italic">"{citation.text}"</p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mt-4">
            <Button
              variant="ghost"
              size="sm"
              className="w-full text-xs text-muted-foreground hover:text-foreground"
              onClick={() => setShowChunks(!showChunks)}
            >
              {showChunks ? "Hide Full Evidence" : "View Full Evidence Text"}
            </Button>
          </div>
        </div>
      )}

      {/* Chunk Viewer Toggle */}
      <AnimatePresence>
        {showChunks && (
          <motion.div
            className="border-t border-border bg-muted/30 px-6 py-4"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="space-y-3 max-h-80 overflow-y-auto">
              {answer.citations.map((chunk, index) => (
                <motion.div
                  key={index}
                  className="rounded-lg border border-border bg-card p-4"
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <p className="text-xs font-semibold text-primary mb-2">
                    ID: {chunk.chunk_id} • Page {chunk.page}
                  </p>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {chunk.text}
                  </p>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export type { Answer, Citation };
