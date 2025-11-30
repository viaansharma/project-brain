import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# 1. Load Environment Variables
load_dotenv()
app = FastAPI()

# 2. Check Keys
google_key = os.getenv("GOOGLE_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

# --- ROBUST DATA MODEL (Everything Optional + String) ---
class DoorItem(BaseModel):
    mark: Optional[str] = Field(description="Door mark number, e.g., D-101")
    location: Optional[str] = Field(description="Room name or location")
    width_mm: Optional[str] = Field(description="Width (as text)")
    height_mm: Optional[str] = Field(description="Height (as text)")
    fire_rating: Optional[str] = Field(description="Fire rating")
    material: Optional[str] = Field(description="Door material")

class DoorSchedule(BaseModel):
    doors: List[DoorItem]

# 3. Setup Models
print("⏳ Loading Local Embeddings (MiniLM)...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

print(f"⏳ Connecting to Pinecone Index: {index_name}...")
vectorstore = PineconeVectorStore(
    index_name=index_name, 
    embedding=embeddings
)

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            temperature=0,
            google_api_key=google_key
        )

        system_prompt = (
            "You are a construction AI. Answer based ONLY on the context provided. "
            "If the answer is not in the context, say 'I cannot find that information'. "
            "Context: {context}"
        )
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        chain = create_retrieval_chain(retriever, create_stuff_documents_chain(llm, prompt))
        print(f"🤔 Thinking about: {request.query}")
        response = chain.invoke({"input": request.query})

        sources = []
        if "context" in response:
            for doc in response["context"]:
                sources.append({
                    "file": doc.metadata.get("source", "Unknown").split("/")[-1],
                    "page": doc.metadata.get("page", 0) + 1
                })

        return {"answer": response["answer"], "sources": sources}
    
    except Exception as e:
        print(f"❌ CRASH IN CHAT ENDPOINT: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract")
async def extract_schedule():
    try:
        print("🔍 Searching for door schedule in documents...")
        retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
        docs = retriever.invoke("door schedule list hardware openings")
        
        context_text = "\n\n".join([d.page_content for d in docs])
        print(f"📄 Found context length: {len(context_text)} characters")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            temperature=0,
            google_api_key=google_key
        )
        structured_llm = llm.with_structured_output(DoorSchedule)

        prompt = f"""
        Analyze the text below and extract the Door Schedule table.
        
        CRITICAL INSTRUCTION: The text might be messy (e.g. '2100 1 HR' might be on the same line). 
        You must infer the columns based on the headers 'Mark', 'Location', 'Width', 'Height', 'Fire Rating', 'Material'.
        
        Extract every single door row starting with 'D-'.
        
        TEXT CONTENT:
        {context_text}
        """
        
        print("🤖 Asking AI to extract...")
        result = structured_llm.invoke(prompt)
        
        print(f"✅ Extracted {len(result.doors)} doors!")
        for d in result.doors:
            print(f" - Found: {d.mark} ({d.location})")

        return result
    except Exception as e:
        print(f"❌ CRASH IN EXTRACT ENDPOINT: {e}")
        raise HTTPException(status_code=500, detail=str(e))
