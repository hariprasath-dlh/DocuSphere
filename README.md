# DocuSphere – Offline Intent-Aware RAG System

DocuSphere is a fully offline, intent-aware Retrieval-Augmented Generation (RAG) system that allows users to upload documents and ask natural language questions with high accuracy.

Unlike traditional RAG systems, DocuSphere understands user intent, handles spelling and grammar mistakes, and performs precise data extraction without hallucinations.

---

## 🚀 Key Features

- Fully Offline AI (No APIs, No Internet)
- Intent-Aware Query Understanding
- Hybrid RAG (Semantic Search + Rule-Based Extraction)
- Accurate Extraction of:
  - LinkedIn URLs
  - Email addresses
  - Phone numbers
- Supports document uploads (PDF, DOCX, TXT)
- Clean and minimal UI
- High-precision answers (no vector IDs exposed)

---

## 🧠 How It Works

1. User uploads a document
2. Query is normalized (handles spelling & grammar errors)
3. Intent is detected (LIST, EXTRACT, EXPLAIN, GENERAL)
4. Relevant content is filtered from the vector store
5. Based on intent:
   - **Regex Extraction** for links/emails (100% accuracy)
   - **LLM Generation** for explanations and summaries

---

## 🛠️ Tech Stack

**Frontend**
- React
- TypeScript
- Vite
- Tailwind CSS

**Backend**
- Python
- FastAPI
- FAISS (Vector Store)

**AI**
- Offline LLM via Ollama
- Sentence Transformers for embeddings

---

## 📂 Project Structure

# DocuSphere – Offline Intent-Aware RAG System

DocuSphere is a fully offline, intent-aware Retrieval-Augmented Generation (RAG) system that allows users to upload documents and ask natural language questions with high accuracy.

Unlike traditional RAG systems, DocuSphere understands user intent, handles spelling and grammar mistakes, and performs precise data extraction without hallucinations.

---

## 🚀 Key Features

- Fully Offline AI (No APIs, No Internet)
- Intent-Aware Query Understanding
- Hybrid RAG (Semantic Search + Rule-Based Extraction)
- Accurate Extraction of:
  - LinkedIn URLs
  - Email addresses
  - Phone numbers
- Supports document uploads (PDF, DOCX, TXT)
- Clean and minimal UI
- High-precision answers (no vector IDs exposed)

---

## 🧠 How It Works

1. User uploads a document
2. Query is normalized (handles spelling & grammar errors)
3. Intent is detected (LIST, EXTRACT, EXPLAIN, GENERAL)
4. Relevant content is filtered from the vector store
5. Based on intent:
   - **Regex Extraction** for links/emails (100% accuracy)
   - **LLM Generation** for explanations and summaries

---

## 🛠️ Tech Stack

**Frontend**
- React
- TypeScript
- Vite
- Tailwind CSS

**Backend**
- Python
- FastAPI
- FAISS (Vector Store)

**AI**
- Offline LLM via Ollama
- Sentence Transformers for embeddings

---
```
## 📂 Project Structure

DocuSphere/
├── backend/
│ ├── intent_normalizer.py
│ ├── output_mode.py
│ ├── retrieval.py
│ ├── llm.py
│ ├── main.py
│ └── verify_logic.py
│
├── frontend/
│ ├── src/
│ └── public/
│
├── package.json
└── README.md

```
