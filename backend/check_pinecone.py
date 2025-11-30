import os
import time
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")
index_name = os.getenv("PINECONE_INDEX_NAME")

print(f"Checking Pinecone with Key: {api_key[:5]}...")
pc = Pinecone(api_key=api_key)

# 1. List Indexes
indexes = pc.list_indexes()
print(f"Existing Indexes: {[i.name for i in indexes]}")

# 2. Create if missing
existing_names = [i.name for i in indexes]

if index_name not in existing_names:
    print(f"Creating index '{index_name}'...")
    try:
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        print("Index creation command sent.")
    except Exception as e:
        print(f"Error creating index: {e}")
else:
    print(f"Index '{index_name}' already exists.")

# 3. Wait for it to be ready
print("Waiting for index to be ready...")
while True:
    try:
        idx = pc.describe_index(index_name)
        if idx.status['ready']:
            print("Index is READY!")
            break
        print("Still initializing...")
        time.sleep(2)
    except Exception as e:
        print(f"Index not found yet: {e}")
        time.sleep(2)