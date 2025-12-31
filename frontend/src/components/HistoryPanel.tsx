import { motion, AnimatePresence } from "framer-motion";
import { History, ChevronRight, Clock, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { Answer } from "./AnswerDisplay";

interface HistoryPanelProps {
  history: Answer[];
  onSelectItem: (answer: Answer) => void;
  onClearHistory: () => void;
  isOpen: boolean;
  onToggle: () => void;
}

export function HistoryPanel({
  history,
  onSelectItem,
  onClearHistory,
  isOpen,
  onToggle,
}: HistoryPanelProps) {
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);

    if (minutes < 1) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <>
      {/* Toggle Button */}
      <motion.button
        onClick={onToggle}
        className="fixed left-0 top-1/2 -translate-y-1/2 z-40 flex items-center gap-1 rounded-r-lg border border-l-0 border-border bg-card px-2 py-3 shadow-soft hover:bg-accent transition-colors"
        whileHover={{ x: 4 }}
      >
        <History className="h-4 w-4 text-primary" />
        <ChevronRight
          className={`h-4 w-4 text-muted-foreground transition-transform ${
            isOpen ? "rotate-180" : ""
          }`}
        />
      </motion.button>

      {/* Overlay */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            className="fixed inset-0 bg-foreground/10 backdrop-blur-sm z-40 lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onToggle}
          />
        )}
      </AnimatePresence>

      {/* Panel */}
      <AnimatePresence>
        {isOpen && (
          <motion.aside
            className="fixed left-0 top-0 bottom-0 w-80 max-w-[85vw] z-50 border-r border-border bg-card shadow-xl flex flex-col"
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
          >
            {/* Header */}
            <div className="flex items-center justify-between border-b border-border px-4 py-4">
              <div className="flex items-center gap-2">
                <History className="h-5 w-5 text-primary" />
                <h2 className="font-semibold text-foreground">Query History</h2>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={onClearHistory}
                className="text-muted-foreground hover:text-destructive"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>

            {/* History List */}
            <div className="flex-1 overflow-y-auto p-3">
              {history.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-40 text-center">
                  <Clock className="h-10 w-10 text-muted-foreground/50 mb-3" />
                  <p className="text-sm text-muted-foreground">No queries yet</p>
                  <p className="text-xs text-muted-foreground/70">
                    Your query history will appear here
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {history.map((item, index) => (
                    <motion.button
                      key={item.id}
                      className="w-full text-left rounded-lg border border-border bg-card p-3 hover:bg-accent/50 hover:border-primary/30 transition-all"
                      onClick={() => onSelectItem(item)}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      whileHover={{ scale: 1.02 }}
                    >
                      <p className="text-sm font-medium text-foreground line-clamp-2">
                        {item.query}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1 flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatTime(item.timestamp)}
                      </p>
                    </motion.button>
                  ))}
                </div>
              )}
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </>
  );
}
