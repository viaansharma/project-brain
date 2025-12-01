import os
import json
import re
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings 
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

if not google_key or not pinecone_key:
    raise ValueError("❌ Missing API Keys. Please check your .env settings.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For production, replace * with your Vercel URL
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    query: str

# 3. Setup Models
# CHANGED: Switched to Google Embeddings (Lightweight, no download required)
# NOTE: Ensure your Pinecone Index is set to 768 Dimensions for this model.
print("⏳ Connecting to Google Embeddings...")
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

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
        retriever = vectorstore.as_retriever(search_kwargs={"k": 20})
        docs = retriever.invoke("door schedule list hardware openings frame material width height fire rating")
        
        context_text = "\n\n".join([d.page_content for d in docs])
        print(f"📄 Found context length: {len(context_text)} characters")

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", 
            temperature=0,
            google_api_key=google_key
        )
        
        prompt = f"""
        You are a smart data extraction AI. 
        Your goal is to extract the DOOR SCHEDULE table from the messy text below.
        Return ONLY a valid JSON object.
        
        The JSON structure must strictly follow this format:
        {{
            "doors": [
                {{
                    "mark": "Door Number (e.g. D-101)",
                    "location": "Room Name or Location",
                    "width_mm": "Width (e.g. 900)",
                    "height_mm": "Height (e.g. 2100)",
                    "fire_rating": "Rating (e.g. 1 HR, 45 min, or None)",
                    "material": "Material (e.g. HM, Wood, Alum)"
                }}
            ]
        }}
        
        MESSY TEXT CONTENT:
        {context_text}
        """
        
        print("🤖 Asking AI to extract JSON...")
        response = llm.invoke(prompt)
        
        clean_json = response.content.replace("```json", "").replace("```", "").strip()
        
        try:
            data = json.loads(clean_json)
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", clean_json, re.DOTALL)
            if match:
                data = json.loads(match.group())
            else:
                return {"doors": []}

        doors_list = data.get("doors", [])
        print(f"✅ Extracted {len(doors_list)} doors!")
        return {"doors": doors_list}

    except Exception as e:
        print(f"❌ CRASH IN EXTRACT ENDPOINT: {e}")
        return {"doors": []}