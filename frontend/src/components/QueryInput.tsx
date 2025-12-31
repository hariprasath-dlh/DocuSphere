import { useState } from "react";
import { motion } from "framer-motion";
import { Send, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

interface QueryInputProps {
  onSubmit: (query: string) => Promise<void>;
  isLoading?: boolean;
  disabled?: boolean;
  placeholder?: string;
}

export function QueryInput({
  onSubmit,
  isLoading = false,
  disabled = false,
  placeholder = "Ask DocuSphere anything about your documents..."
}: QueryInputProps) {
  const [query, setQuery] = useState("");

  const handleSubmit = async () => {
    if (!query.trim() || isLoading || disabled) return;

    await onSubmit(query.trim());
    setQuery("");
  };

  const handleKeyDown = async (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      await handleSubmit();
    }
  };

  return (
    <motion.div
      className="relative"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className={`rounded-xl border border-border bg-card p-1 shadow-soft transition-shadow focus-within:shadow-glow focus-within:border-primary/50 ${disabled ? 'opacity-60 cursor-not-allowed' : ''}`}>
        <Textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className="min-h-[100px] resize-none border-0 bg-transparent text-foreground placeholder:text-muted-foreground focus-visible:ring-0 focus-visible:ring-offset-0 disabled:cursor-not-allowed"
          disabled={isLoading || disabled}
        />

        <div className="flex items-center justify-between px-2 pb-2">
          <p className="text-xs text-muted-foreground">
            Press Enter to send • Shift+Enter for new line
          </p>

          <Button
            onClick={handleSubmit}
            disabled={!query.trim() || isLoading || disabled}
            variant="hero"
            size="lg"
            className="gap-2"
          >
            {isLoading ? (
              <>
                <motion.div
                  animate={{ rotate: 360 }}
                  transition={{
                    duration: 1,
                    repeat: Infinity,
                    ease: "linear",
                  }}
                >
                  <Sparkles className="h-4 w-4" />
                </motion.div>
                Thinking...
              </>
            ) : (
              <>
                <Send className="h-4 w-4" />
                Ask DocuSphere
              </>
            )}
          </Button>
        </div>
      </div>
    </motion.div>
  );
}
