import { useState } from "react";
import { motion } from "framer-motion";
import { FileText, Zap, Shield, Search } from "lucide-react";

import { askQuestion } from "@/lib/api";
import { Navbar } from "@/components/Navbar";
import { FileUploader, type UploadedFile } from "@/components/FileUploader";
import { QueryInput } from "@/components/QueryInput";
import { AnswerDisplay, type Answer, type Citation } from "@/components/AnswerDisplay";
import { HistoryPanel } from "@/components/HistoryPanel";

const features = [
  {
    icon: FileText,
    title: "Multi-Format Support",
    description: "Upload PDF, TXT, and DOCX documents seamlessly",
  },
  {
    icon: Search,
    title: "Intelligent Retrieval",
    description: "Advanced RAG technology for precise answers",
  },
  {
    icon: Shield,
    title: "Transparent Citations",
    description: "Every answer backed by source references",
  },
  {
    icon: Zap,
    title: "Fast Processing",
    description: "Get answers in seconds, not minutes",
  },
];

export default function Index() {
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [answers, setAnswers] = useState<Answer[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<Answer | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [historyOpen, setHistoryOpen] = useState(false);

  // ✅ REAL BACKEND QUERY (FIXED)
  const handleQuery = async (query: string) => {
    setIsLoading(true);
    try {
      const data = await askQuestion(query);

      // Backend now returns a flat list of evidence
      const allChunks = data.evidence;

      // Deduplicate chunks by ID (Standard safety check)
      const seenChunks = new Set();
      const uniqueCitations: Citation[] = [];

      allChunks.forEach(chunk => {
        if (!seenChunks.has(chunk.chunk_id)) {
          seenChunks.add(chunk.chunk_id);
          uniqueCitations.push({
            chunk_id: chunk.chunk_id,
            text: chunk.text,
            page: chunk.page,
            source: chunk.source
          });
        }
      });

      const newAnswer: Answer = {
        id: crypto.randomUUID(),
        query: data.original_query,
        content: data.answer,
        citations: uniqueCitations,
        timestamp: new Date(),
      };

      setAnswers((prev) => [newAnswer, ...prev]);
      setSelectedAnswer(newAnswer);
    } catch (error) {
      console.error("Query failed:", error);
      // Optional: Add toast notification here
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectFromHistory = (answer: Answer) => {
    setSelectedAnswer(answer);
    setHistoryOpen(false);
  };

  const clearHistory = () => {
    setAnswers([]);
    setSelectedAnswer(null);
  };

  const hasUploads = uploadedFiles.length > 0;

  return (
    <div className="min-h-screen bg-background">
      <Navbar />

      <HistoryPanel
        history={answers}
        onSelectItem={handleSelectFromHistory}
        onClearHistory={clearHistory}
        isOpen={historyOpen}
        onToggle={() => setHistoryOpen(!historyOpen)}
      />

      <main className="container mx-auto px-4 py-8 md:py-12">
        {/* Hero */}
        <motion.section
          className="text-center mb-12"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <motion.div
            className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-accent px-4 py-1.5 text-sm font-medium mb-6"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
          >
            <Zap className="h-4 w-4 text-primary" />
            Powered by Advanced RAG Technology
          </motion.div>

          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Ask Questions, Get{" "}
            <span className="text-gradient">Intelligent Answers</span>
          </h1>

          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Upload your documents and let DocuSphere find answers with
            transparent citations.
          </p>
        </motion.section>

        {/* Features */}
        <motion.section className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className="rounded-xl border bg-card p-4 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-accent mx-auto mb-3">
                <feature.icon className="h-5 w-5 text-primary" />
              </div>
              <h3 className="font-semibold text-sm">{feature.title}</h3>
              <p className="text-xs text-muted-foreground">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.section>

        {/* Main Grid */}
        <div className="grid lg:grid-cols-2 gap-8">
          <div className="space-y-6">
            <section>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                Upload Documents
              </h2>
              <FileUploader onFilesUploaded={setUploadedFiles} />
            </section>

            <section>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Search className="h-5 w-5 text-primary" />
                Ask a Question
              </h2>
              <QueryInput
                onSubmit={handleQuery}
                isLoading={isLoading}
                disabled={!hasUploads}
                placeholder={hasUploads ? "Ask DocuSphere anything about your documents..." : "Please upload a document to start asking questions."}
              />
              {!hasUploads && (
                <p className="text-xs text-muted-foreground mt-2 ml-1 text-red-400">
                  * You must upload a document before querying.
                </p>
              )}
            </section>
          </div>

          <section>
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Zap className="h-5 w-5 text-primary" />
              Answer
            </h2>

            {selectedAnswer ? (
              <AnswerDisplay answer={selectedAnswer} />
            ) : (
              <div className="rounded-xl border border-dashed p-12 text-center">
                <Search className="h-8 w-8 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Your answers will appear here
                </p>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}
