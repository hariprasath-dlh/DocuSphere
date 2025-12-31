const BACKEND_URL = "http://127.0.0.1:8000";

export interface EvidenceChunk {
  chunk_id: string;
  text: string;
  page: number;
  source: string;
}

export interface AnswerResponse {
  original_query: string;
  sub_queries: string[];
  answer: string;
  evidence: EvidenceChunk[];
}

// 🆕 NEW: Explicit Upload Response
export interface UploadResponse {
  status: "success" | "error";
  filename?: string;
  pages?: number;
  chunks?: number;
  message?: string;
}

/**
 * Upload PDF to backend
 * 
 * Rules for Fix:
 * 1. Use FormData
 * 2. Key MUST be "file"
 * 3. NO manual Content-Type (fetch handles it)
 */
export async function uploadPDF(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${BACKEND_URL}/upload`, {
      method: "POST",
      body: formData,
      // headers: { "Content-Type": "multipart/form-data" }, // ❌ DO NOT UNCOMMENT THIS
    });

    if (!res.ok) {
      const errorData = await res.json().catch(() => ({}));
      throw new Error(errorData.message || `Upload failed with status ${res.status}`);
    }

    const data: UploadResponse = await res.json();
    return data;

  } catch (error: any) {
    console.error("API Upload Error:", error);
    throw error;
  }
}

/**
 * Ask a question to backend
 */
export async function askQuestion(query: string): Promise<AnswerResponse> {
  const res = await fetch(`${BACKEND_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Query failed: ${res.status} ${text}`);
  }

  return await res.json();
}
