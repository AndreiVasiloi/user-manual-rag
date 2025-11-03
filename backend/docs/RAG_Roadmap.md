# 🧭 RAG Learning Roadmap – Andrei Vasiloi

A structured roadmap to go from a simple manual-based RAG prototype → an evaluated, optimized, and production-ready system using **FAISS + Gemini + Python**.

---

## ✅ Phase Progress Checklist

| ✅ | Phase | Focus Area | Key Learning Tasks | Output / Milestone |
|:--:|:------|:------------|:------------------|:------------------|
| ☐ | **1. Foundations** | Core RAG concepts | - Understand “Retrieve → Augment → Generate”<br>- Implement pipeline manually with FAISS + Gemini<br>- Experiment with `chunk_size` / `overlap` values<br>- Visualize embeddings and retrieval results | 🎯 Working local RAG answering basic manual questions |
| ☐ | **2. Retrieval Quality** | Data preparation & FAISS tuning | - Clean PDF text (remove headers/footers)<br>- Use `RecursiveCharacterTextSplitter` for better chunking<br>- Test multiple embedding models (`MiniLM`, multilingual)<br>- Compare FAISS types (Flat vs IVFFlat)<br>- Save/load FAISS index to disk | 🚀 Reliable retrieval (always fetches correct manual sections) |
| ☐ | **3. Generation Control** | Prompt engineering & LLM tuning | - Design clear prompt templates for Gemini<br>- Adjust `temperature`, `max_tokens`<br>- Try reasoning prompts (“Step 1: summarize → Step 2: answer”)<br>- Compare Gemini 1.5 Flash vs Pro<br>- Add fallback when answer is missing | 💬 High-quality, factual, concise answers |
| ☐ | **4. Evaluation (RAG Triad)** | Metrics & diagnostics | - Learn Context Relevance / Faithfulness / Answer Relevance<br>- Build a small test set (5–10 Q&A pairs per manual)<br>- Measure retrieval accuracy (cosine similarity)<br>- Use an LLM-based evaluator to detect hallucinations | 📊 Notebook or dashboard showing 3 triad metrics |
| ☐ | **5. Productization** | API & UI | - Add FastAPI endpoint (`POST /ask`)<br>- Add Streamlit or React frontend for upload + chat<br>- Implement caching of FAISS and answers<br>- Add error handling + logging<br>- (Optional) simple user roles (Admin / Viewer) | 🌐 Deployable “Manual Reader Assistant” web app |
| ☐ | **6. Optimization & Research** | Scaling & advanced retrieval | - Experiment with hybrid retrieval (BM25 + FAISS)<br>- Add reranking (Cohere / Gemini Rerank)<br>- Try context compression (LangChain, DSPy)<br>- Compare vector DBs (Chroma, Milvus, Pinecone)<br>- Fine-tune embeddings on your own manuals | ⚙️ Efficient, scalable, enterprise-grade RAG system |

---

## 🗓️ Suggested Timeline

| Week | Focus | Deliverable |
|------|--------|-------------|
| **Week 1–2** | Phases 1–2 | Reliable local RAG prototype |
| **Week 3–4** | Phase 3 | Gemini prompt refinement & stable generation |
| **Week 5** | Phase 4 | Implement & visualize RAG triad metrics |
| **Week 6–7** | Phase 5 | FastAPI + frontend for upload & chat |
| **Week 8+** | Phase 6 | Advanced retrieval experiments & optimization |

---

## 💡 Practical Tips

- Keep one consistent **test manual** (e.g., De’Longhi ESAM3300) for experiments.
- Create a fixed **evaluation question set** (5–10 questions) to measure improvements.
- Track configuration changes (chunk size, top_k, model type) in a simple CSV or Notion page.
- When results degrade, identify *which metric* dropped:
  - Context Relevance → retrieval or chunking issue  
  - Faithfulness → hallucination or poor prompting  
  - Answer Relevance → question misunderstood or context incomplete

---

## 🧠 Goal

To build a **robust, explainable, and evaluable RAG system** capable of answering questions from product manuals with high accuracy — and use this project as a stepping stone toward enterprise-grade AI integrations.

---

**Author:** Andrei Vasiloi  
**Project:** Manual Reader RAG  
**Stack:** Python · FAISS · Gemini · SentenceTransformers  
**Version:** 1.0
