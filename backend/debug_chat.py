import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI

# 1. Load Secrets
load_dotenv()
google_key = os.getenv("GOOGLE_API_KEY")
pinecone_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

print("--- DIAGNOSTIC START ---")

# 2. Check Keys
if not google_key:
    print("❌ MISSING: GOOGLE_API_KEY")
else:
    print(f"✅ Google Key found: {google_key[:5]}...")

if not pinecone_key:
    print("❌ MISSING: PINECONE_API_KEY")
else:
    print(f"✅ Pinecone Key found: {pinecone_key[:5]}...")

# 3. Test Embeddings (Local)
print("\n1. Testing Local Embeddings...")
try:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    print("✅ Embeddings Loaded!")
except Exception as e:
    print(f"❌ Embeddings Crashed: {e}")

# 4. Test Pinecone Connection
print("\n2. Testing Pinecone Connection...")
try:
    vectorstore = PineconeVectorStore(index_name=index_name, embedding=embeddings)
    # Try a dummy search
    vectorstore.similarity_search("test", k=1)
    print("✅ Pinecone Connected & Searchable!")
except Exception as e:
    print(f"❌ Pinecone Crashed: {e}")

# 5. Test Google Gemini Chat
print("\n3. Testing Google Gemini Chat...")
try:
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=google_key
    )
    res = llm.invoke("Hello, are you working?")
    print(f"✅ Gemini Responded: {res.content}")
except Exception as e:
    print(f"❌ Gemini Crashed: {e}")

print("\n--- DIAGNOSTIC END ---")