Project Brain 🧠 - Construction Intelligence AI

A RAG-based LLM application that helps construction teams find information and extract schedules from PDF documents instantly.

Live Demo: https://project-brain-puce.vercel.app
(Login with: testingcheckuser1234@gmail.com)

🚀 Features

Q&A Chat: Ask natural language questions about construction specs.

Source Citations: Every answer links back to the specific PDF page.

Structured Extraction: Automatically generates a "Door Schedule" JSON table from messy text.

Evaluation Pipeline: Includes a script to verify accuracy.

🛠 Tech Stack

Frontend: React, Tailwind CSS (Deployed on Vercel)

Backend: FastAPI, Python (Deployed on Render)

AI Engine: Google Gemini Pro 2.0 (via LangChain)

Vector DB: Pinecone (Serverless)

🏃‍♂️ How to Run Locally

Backend

Navigate to backend: cd backend

Install dependencies: pip install -r requirements.txt

Set up .env file:

GOOGLE_API_KEY=your_key
PINECONE_API_KEY=your_key
PINECONE_INDEX_NAME=construction-index


Run server: uvicorn main:app --reload

Frontend

Navigate to frontend: cd frontend

Install dependencies: npm install

Set up .env:

NEXT_PUBLIC_API_URL=https://project-brain-yzjp.onrender.com


Run app: npm start

🧠 Design Decisions

Chunking & Indexing

I used RecursiveCharacterTextSplitter with a chunk size of 1000 tokens and 200 overlap. This ensures that context (like table headers) is preserved across chunks.

RAG Pipeline

Query Analysis: The user query is embedded using GoogleGenerativeAIEmbeddings.

Retrieval: We fetch the top 3 most relevant chunks from Pinecone.

Generation: We pass the context + prompt to Gemini-2.0-Flash to generate a concise answer with citations.

Structured Extraction

For the "Door Schedule" task, I used a specific prompt engineering strategy to force the LLM to output valid JSON (doors: []), which is then parsed and displayed as a React Table.