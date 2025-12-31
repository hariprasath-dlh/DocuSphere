import { uploadPDF } from "@/lib/api";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, CheckCircle2, X, FileText, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";

// ⚠️ Make sure this matches what the rest of the app expects or export it if it's the source of truth
export interface UploadedFile {
  id: string;
  name: string;
  size: number;
  status: "uploading" | "processing" | "ready" | "error";
}

interface FileUploaderProps {
  onFilesUploaded?: (files: UploadedFile[]) => void;
}

export function FileUploader({ onFilesUploaded }: FileUploaderProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);

  const onDrop = useCallback(
    async (acceptedFiles: File[]) => {
      // 1. Optimistic UI update
      const uiFiles: UploadedFile[] = acceptedFiles.map((file) => ({
        id: crypto.randomUUID(),
        name: file.name,
        size: file.size,
        status: "uploading" as UploadedFile["status"],
      }));

      setFiles((prev) => [...prev, ...uiFiles]);

      // 2. Process uploads sequentially or logically
      for (let i = 0; i < acceptedFiles.length; i++) {
        const actualFile = acceptedFiles[i];
        const uiFile = uiFiles[i];

        try {
          // Update to processing
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uiFile.id ? { ...f, status: "processing" as UploadedFile["status"] } : f
            )
          );

          // 🔹 REAL backend upload call
          const response = await uploadPDF(actualFile);

          // 🔹 CHECK RESPONSE STATUS STRICTLY
          if (response.status === "success") {
            setFiles((prev) => {
              const updated = prev.map((f) =>
                f.id === uiFile.id ? { ...f, status: "ready" as UploadedFile["status"] } : f
              );
              // Notify parent component only of ready files
              onFilesUploaded?.(updated.filter((f) => f.status === "ready"));
              return updated;
            });
          } else {
            throw new Error(response.message || "Upload failed");
          }

        } catch (err: any) {
          console.error("Upload failed for file:", uiFile.name, err);
          setErrorMessages(prev => ({ ...prev, [uiFile.id]: err.message }));
          setFiles((prev) =>
            prev.map((f) =>
              f.id === uiFile.id ? { ...f, status: "error" as UploadedFile["status"] } : f
            )
          );
        }
      }
    },
    [onFilesUploaded]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [
        ".docx",
      ],
      "application/vnd.openxmlformats-officedocument.presentationml.presentation": [
        ".pptx",
      ],
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [
        ".xlsx",
      ],
    },
  });

  const removeFile = (id: string) => {
    setFiles((prev) => {
      const updated = prev.filter((f) => f.id !== id);
      // Also update parent if a ready file is removed
      onFilesUploaded?.(updated.filter((f) => f.status === "ready"));
      return updated;
    });
  };

  const [errorMessages, setErrorMessages] = useState<Record<string, string>>({});

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const getStatusIcon = (status: UploadedFile["status"]) => {
    switch (status) {
      case "uploading":
      case "processing":
        return <Loader2 className="h-4 w-4 animate-spin text-primary" />;
      case "ready":
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case "error":
        return <X className="h-4 w-4 text-destructive" />;
    }
  };

  const getStatusText = (file: UploadedFile) => {
    switch (file.status) {
      case "uploading":
        return "Uploading…";
      case "processing":
        return "Indexing…";
      case "ready":
        return "Ready";
      case "error":
        return errorMessages[file.id] || "Failed";
    }
  };

  const rootProps = getRootProps();

  return (
    <div className="space-y-4">
      <motion.div
        className={`relative cursor-pointer rounded-xl border-2 border-dashed p-8 transition-all ${isDragActive
          ? "border-primary bg-accent/50"
          : "border-border hover:border-primary/50 hover:bg-accent/30"
          }`}
        onClick={rootProps.onClick}
        onKeyDown={rootProps.onKeyDown}
        onFocus={rootProps.onFocus}
        onBlur={rootProps.onBlur}
        tabIndex={rootProps.tabIndex}
        role={rootProps.role}
      >

        <input {...getInputProps()} />
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-accent">
            <Upload className="h-8 w-8" />
          </div>
          <div>
            <p className="text-lg font-semibold">
              {isDragActive ? "Drop files here" : "Drag & drop documents"}
            </p>
            <p className="text-sm text-muted-foreground">
              PDF, TXT, DOCX, PPTX, XLSX supported
            </p>
          </div>
        </div>
      </motion.div>

      <AnimatePresence>
        {files.map((file, index) => (
          <motion.div
            key={file.id}
            className={`flex items-center gap-3 rounded-lg border bg-card p-3 ${file.status === 'error' ? 'border-destructive/50 bg-destructive/10' : ''}`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.05 }}
          >
            <FileText className="h-5 w-5" />
            <div className="flex-1">
              <p className="truncate text-sm font-medium">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {formatFileSize(file.size)} • {getStatusText(file)}
              </p>
            </div>
            {getStatusIcon(file.status)}
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation();
                removeFile(file.id);
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
