# 🤖 ai-hr-assistant

An intelligent HR assistant chatbot that allows users to search, explore, and query employee resources using natural language.
---

## 🎯 Objective

> Help HR teams query employee data such as:
- "Find Python developers with 3+ years experience"
- "Who has worked on healthcare projects?"
- "Suggest people for a React Native project"
- "What is Brian Berry’s email?"

---

## 🔍 Features

- ✅ Semantic search using SentenceTransformer embeddings
- ✅ FAISS-based vector index for fast retrieval
- ✅ Smart prompting with local LLM (**Mistral via Ollama**)
- ✅ Direct contact info retrieval (e.g., email, phone, department)
- ✅ Robust edge case handling (gibberish, missing names, empty queries)
- ✅ Dynamic top-K query interpretation (e.g., “show 5 employees”)
- ✅ Full **Streamlit chatbot UI** with:
  - Chat history memory
  - Load More / pagination
  - Assistant greeting and status display
  - Clear chat button

---

## 🧠 Architecture

```
Streamlit UI → FastAPI (/chat)
             → Embedding (MiniLM)
             → FAISS similarity search
             → Prompt context + Ollama (Mistral)
             ← Suggested candidates & explanation
```

- **LLM**: Mistral 7B via [Ollama](https://ollama.com)
- **Embedding Model**: all-MiniLM-L6-v2
- **Database**: In-memory JSON + FAISS
- **Backend**: FastAPI
- **Frontend**: Streamlit (chat interface)

---

## ⚙️ Setup & Run

### 1. Clone the project
```bash
git clone [https://github.com/yourusername/hr-chatbot.git](https://github.com/adhiljaseem/ai-hr-assistant.git)
cd ai-hr-assistant
```

### 2. Set up the environment
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Pull LLM (Ollama)
```bash
ollama pull mistral
```

### 4. Build FAISS index
```bash
python build_index.py
```

### 5. Start backend
```bash
uvicorn chatbot:app --reload
```

### 6. Start frontend
```bash
streamlit run app.py
```

---

## 📡 API Endpoints

### `POST /chat`
Accepts natural language queries.

```json
{ "query": "Find React developers with 5 years of experience" }
```

Returns:
- `response`: Suggested matches with reasoning
- `matches`: List of structured employee profiles

---

### `GET /employees/search`
Filter employees with structured queries.

Supported filters:
- `skill`, `role`, `location`, `status`
- `min_experience`, `project`, `department`, `language`, `certification`, `availability`

---

## 👨‍💻 My Role & Work

As part of the assessment, I built and implemented:

✅ **Streamlit Chat UI**  
- Persistent chat memory  
- Paginated employee display  
- Clean UX with assistant intro and sidebar actions  

✅ **Edge Case Handling**  
- Gibberish detection  
- Empty queries  
- Personal info queries without a name  
- FAISS fallback for zero matches  

✅ **Prompt Engineering**  
- Custom prompts tailored to employee data  
- Local response generation with Mistral  
- Structured fallback responses

✅ **Dataset + Indexing**  
- 60+ realistic employee records  
- Metadata formatting & FAISS embedding  
- Query interpretation (e.g., "give me 10 names")

✅ **FastAPI Backend**  
- REST endpoints `/chat` and `/employees/search`  
- Embedding + vector search pipeline  
- Ollama integration

---

## 💡 AI Assistance

While I independently designed and implemented the system, I used:

| Tool      | Used For                       |
|-----------|--------------------------------|
| ChatGPT   | Prompt design, code scaffolding, edge cases |
| Ollama    | Local LLM inference (Mistral 7B) |
| SentenceTransformers | Semantic query embedding |
| FAISS     | Vector similarity search       |

All AI-assisted code was reviewed, edited, and integrated manually.

---

## 📸 Screenshots
![image](https://github.com/user-attachments/assets/40f2a3bd-b396-41a1-a14b-703b8611207f)


## 📁 Project Structure

```
├── app.py               # Streamlit UI
├── chatbot.py           # FastAPI backend
├── build_index.py       # FAISS index generation
├── employee_metadata.json
├── employee_index.faiss
├── requirements.txt
└── README.md
```

---
