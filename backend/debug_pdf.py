from langchain_community.document_loaders import PyMuPDFLoader
import os

print("--- CHECKING PDF CONTENT ---")
pdf_path = "./documents/specs.pdf"

if not os.path.exists(pdf_path):
    print(f"❌ Error: File not found at {pdf_path}")
else:
    try:
        loader = PyMuPDFLoader(pdf_path)
        docs = loader.load()
        print(f"✅ Found {len(docs)} pages.")
        for i, doc in enumerate(docs):
            print(f"\n--- PAGE {i+1} CONTENT ---")
            content = doc.page_content.strip()
            if not content:
                print("⚠️ [WARNING] THIS PAGE IS EMPTY!")
            else:
                print(content[:500]) # Print first 500 characters
                print("...\n(End of preview)")
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")