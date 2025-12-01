import requests
import time

# URL of your deployed backend (or localhost if testing locally)
API_URL = "https://project-brain-yzjp.onrender.com"  # REPLACE with your actual Render URL

# 5 "Hard" questions to test your system
TEST_QUESTIONS = [
    "What is the fire rating for door D-101?",
    "List the hardware set for the Lobby door.",
    "What is the height of door 105?",
    "Who is the manufacturer of the wood doors?",
    "Does the roof have a warranty?" # Edge case: might not be in docs
]

def run_evaluation():
    print(f"🚀 Starting Evaluation on {API_URL}...\n")
    
    results = []

    for q in TEST_QUESTIONS:
        print(f"❓ Asking: {q}")
        start_time = time.time()
        
        try:
            response = requests.post(f"{API_URL}/chat", json={"query": q})
            data = response.json()
            elapsed = time.time() - start_time
            
            print(f"✅ Answer ({elapsed:.2f}s): {data.get('answer')}")
            print(f"📄 Sources: {len(data.get('sources', []))}")
            print("-" * 50)
            
            results.append({
                "question": q,
                "answer": data.get("answer"),
                "sources": data.get("sources"),
                "time": elapsed
            })
            
            # Wait a bit to avoid Google 429 Rate Limits!
            time.sleep(10) 

        except Exception as e:
            print(f"❌ Error: {e}")

    # Generate a mini report
    print("\n📊 EVALUATION SUMMARY")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['question']} -> {len(str(res['answer']))} chars")

if __name__ == "__main__":
    run_evaluation()