# import os
# import sys
# from dotenv import load_dotenv
# from langchain_community.document_loaders import PyMuPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_pinecone import PineconeVectorStore
# from pinecone import Pinecone, ServerlessSpec

# load_dotenv()

# def setup_vector_db():
#     pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
#     index_name = os.getenv("PINECONE_INDEX_NAME")

#     existing_indexes = [i.name for i in pc.list_indexes()]
#     if index_name not in existing_indexes:
#         print(f"Creating index {index_name}...")
#         pc.create_index(
#             name=index_name,
#             dimension=384, # <--- Standard size for MiniLM (Local Model)
#             metric="cosine",
#             spec=ServerlessSpec(cloud="aws", region="us-east-1")
#         )
#     return index_name

# def ingest_docs():
#     index_name = setup_vector_db()
    
#     print("⏳ Loading Local Embedding Model (all-MiniLM-L6-v2)...")
#     # This runs LOCALLY on your Mac. No API Limit. 100% Free.
#     embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
#     docs = []
#     doc_folder = "./documents"
    
#     if not os.path.exists(doc_folder):
#         os.makedirs(doc_folder)
        
#     for file in os.listdir(doc_folder):
#         if file.endswith(".pdf"):
#             print(f"Loading {file}...")
#             loader = PyMuPDFLoader(os.path.join(doc_folder, file))
#             docs.extend(loader.load())

#     if not docs:
#         print("⚠️ No PDF files found in backend/documents/")
#         return

#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     splits = text_splitter.split_documents(docs)

#     if splits:
#         print(f"Upserting {len(splits)} chunks to Pinecone...")
#         PineconeVectorStore.from_documents(
#             documents=splits,
#             embedding=embeddings,
#             index_name=index_name
#         )
#         print("✅ Ingestion Complete!")
#     else:
#         print("No documents found to ingest.")

# if __name__ == "__main__":
#     ingest_docs()

import os
from dotenv import load_dotenv
# Use standard PDF loader
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# CHANGED: Use Google Embeddings (768 dims)
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore

load_dotenv()

def ingest_docs():
    # 1. Load PDFs
    # Make sure your PDFs are in a folder named "Documents" inside backend
    pdf_folder_path = "Documents"
    
    if not os.path.exists(pdf_folder_path):
        print(f"❌ Error: Folder '{pdf_folder_path}' not found. Please create it and add PDFs.")
        return

    print(f"📂 Loading PDFs from '{pdf_folder_path}'...")
    loader = PyPDFDirectoryLoader(pdf_folder_path)
    raw_docs = loader.load()
    
    if not raw_docs:
        print("⚠️ No documents found to ingest.")
        return
        
    print(f"   - Found {len(raw_docs)} pages.")

    # 2. Split Text
    print("✂️ Splitting text...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(raw_docs)
    print(f"   - Created {len(docs)} chunks.")

    # 3. Embed & Store
    print(f"💾 Uploading to Pinecone Index: {os.getenv('PINECONE_INDEX_NAME')}...")
    
    # Must match the model used in main.py
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    PineconeVectorStore.from_documents(
        docs, 
        embeddings, 
        index_name=index_name
    )
    print("✅ Success! Documents are indexed with Google Embeddings (768 dims).")

if __name__ == "__main__":
    ingest_docs()