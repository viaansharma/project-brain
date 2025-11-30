Project Brain: Construction AI Assistant 

A RAG (Retrieval Augmented Generation) system designed to answer questions and extract structured data from construction specifications.

 Live Demo

Frontend: [Add your Vercel URL here]

Backend: [Add your Render URL here] (or "Run locally due to CPU embeddings")

🛠️ Tech Stack

Frontend: Next.js 14, Tailwind CSS, React Markdown

Backend: FastAPI, Python 3.12

AI/LLM: Google Gemini 2.0 Flash (via LangChain)

Embeddings: HuggingFace all-MiniLM-L6-v2 (Local/Free)

Vector DB: Pinecone (Serverless)

PDF Parsing: PyMuPDF

⚙️ Architecture Decisions

1. Ingestion Strategy

I chose PyMuPDF for parsing because it reliably extracts text from table-heavy construction documents unlike standard OCR.

Chunking: Used RecursiveCharacterTextSplitter with a chunk size of 1000 characters and 200 overlap. This large window ensures that "Door Schedules" (which span wide rows) are kept together in a single context window.

Metadata: Filenames and page numbers are preserved to ensure every AI answer provides a citation.

2. RAG Pipeline

The system uses a "Hybrid" approach for cost-efficiency:

Embeddings are generated locally using HuggingFace. This keeps the ingestion zero-cost and strictly private.

Generation uses Google's gemini-2.0-flash, which offers a massive context window suitable for reading heavy technical specs.

3. Structured Extraction

For the "Door Schedule" task, I utilized Gemini's structured output capabilities. Instead of relying on regex, the system feeds the raw text segments containing "Door", "Hardware", or "Schedule" keywords into the LLM and enforces a strict Pydantic schema (DoorSchedule) to guarantee valid JSON output for the frontend table.

 How to Run Locally

Prerequisites

Python 3.10+

Node.js 18+

API Keys for Google Gemini & Pinecone

1. Backend Setup

cd backend
python -m venv venv
source venv/bin/activate  # (Windows: venv\Scripts\activate)
pip install -r requirements.txt

# Create a .env file in /backend:
# GOOGLE_API_KEY=AIza...
# PINECONE_API_KEY=pc...
# PINECONE_INDEX_NAME=construction-index

# Run Ingestion
python ingest.py

# Start Server
uvicorn main:app --reload


2. Frontend Setup

cd frontend
npm install
# Create a .env.local file in /frontend:
# NEXT_PUBLIC_API_URL=[http://127.0.0.1:8000](http://127.0.0.1:8000)

npm run dev


🧪 Evaluation

I included a debug_chat.py and debug_pdf.py script to validate:

PDF readability (PyMuPDF verification).

Embedding dimension consistency (384 dim).

LLM connectivity checks.

📄 License

MIT