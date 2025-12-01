Project Brain 🧠 - Construction Intelligence AI

A RAG-based LLM application that allows construction teams to query project documents and extract structured schedules instantly.

Live Demo: https://project-brain-puce.vercel.app
(Login credential: testingcheckuser1234@gmail.com)

🚀 Features

Q&A Chat: Ask natural language questions about construction specs (e.g., "What is the fire rating for door D-101?").

Source Citations: Every answer links back to the specific PDF page to prevent hallucinations.

Structured Extraction: Automatically extracts messy data into a clean "Door Schedule" table.

Robust Error Handling: Handles API rate limits and connection issues gracefully.

🛠 Tech Stack

Frontend: Next.js 14, Tailwind CSS (Deployed on Vercel)

Backend: FastAPI, Python 3.10+ (Deployed on Render)

AI Engine: Google Gemini 2.0 Flash (via LangChain)

Embeddings: Google Text-Embedding-004 (768 dimensions)

Vector DB: Pinecone (Serverless)

🏃‍♂️ How to Run Locally

1. Backend Setup

cd backend
pip install -r requirements.txt

# Create a .env file with:
# GOOGLE_API_KEY=...
# PINECONE_API_KEY=...
# PINECONE_INDEX_NAME=construction-index

uvicorn main:app --reload


2. Frontend Setup

cd frontend
npm install

# Create a .env.local file with:
# NEXT_PUBLIC_API_URL=http://localhost:8000

npm run dev


🧠 Design Decisions

1. Ingestion & Chunking

I implemented a custom ingestion script (backend/ingest.py) that uses PyPDFDirectoryLoader.

Chunking Strategy: I used RecursiveCharacterTextSplitter with a chunk size of 1000 tokens and an overlap of 200 tokens. This large chunk size ensures that tables (like door schedules) are not split in the middle, preserving the context for the LLM.

2. RAG Pipeline

Retrieval: The system embeds the user query using text-embedding-004 and queries Pinecone for the top 3 most relevant matches (k=3).

Generation: The context is passed to Gemini-2.0-Flash with a strict system prompt to only answer based on the provided context.

Citations: Metadata from Pinecone (filename/page) is preserved and sent to the frontend for display.

3. Structured Extraction

For the "Door Schedule" task, I used a specific extraction prompt that instructs the LLM to ignore conversational text and output raw JSON matching a predefined schema ({ doors: [...] }). This allows the frontend to reliably render the data as a UI table.

✅ Evaluation

An evaluation script (backend/evaluate.py) is included to run automated test queries against the API and log the latency/accuracy of responses.