import requests
import json
from typing import Dict
import time


class APITester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def test_health(self):
        """Test health endpoint"""
        print("\n=== Testing Health Endpoint ===")
        response = requests.get(f"{self.base_url}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    
    def test_retrieve(self, url: str, query: str, top_k: int = 3):
        """Test retrieve endpoint"""
        print(f"\n=== Testing Retrieve Endpoint ===")
        print(f"URL: {url}")
        print(f"Query: {query}")
        
        payload = {
            "url": url,
            "query": query,
            "top_k": top_k,
            "use_llm": True
        }
        
        start_time = time.time()
        response = requests.post(
            f"{self.base_url}/retrieve",
            json=payload
        )
        elapsed_time = time.time() - start_time
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Time Taken: {elapsed_time:.2f} seconds")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Success!")
            print(f"\nMetadata:")
            print(f"  - Title: {result['metadata'].get('title', 'N/A')}")
            print(f"  - Total Chunks: {result['metadata']['total_chunks']}")
            print(f"  - Scraped At: {result['metadata'].get('scraped_at', 'N/A')}")
            
            print(f"\n📄 Relevant Chunks Found: {len(result['relevant_chunks'])}")
            for i, chunk in enumerate(result['relevant_chunks'][:2], 1):
                print(f"\nChunk {i}:")
                print(f"  Relevance Score: {chunk['relevance_score']:.3f}")
                print(f"  Content Preview: {chunk['content'][:200]}...")
            
            if result.get('answer'):
                print(f"\n🤖 LLM Answer:")
                print(f"{result['answer']}")
        else:
            print(f"\n❌ Error: {response.text}")
        
        return response.status_code == 200
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("Starting API Tests")
        print("=" * 60)
        
        # Test 1: Health check
        health_ok = self.test_health()
        
        if not health_ok:
            print("\n❌ Health check failed. Make sure the API is running.")
            return
        
        # Test 2: Simple Wikipedia article
        test_cases = [
            {
                "url": "https://en.wikipedia.org/wiki/Machine_learning",
                "query": "What is machine learning?",
                "top_k": 3
            },
            {
                "url": "https://en.wikipedia.org/wiki/Python_(programming_language)",
                "query": "What are the main features of Python?",
                "top_k": 5
            }
        ]
        
        results = []
        for i, test in enumerate(test_cases, 1):
            print(f"\n{'=' * 60}")
            print(f"Test Case {i}/{len(test_cases)}")
            print(f"{'=' * 60}")
            
            success = self.test_retrieve(
                url=test["url"],
                query=test["query"],
                top_k=test["top_k"]
            )
            results.append(success)
            
            # Wait between tests
            if i < len(test_cases):
                time.sleep(2)
        
        # Summary
        print(f"\n{'=' * 60}")
        print("Test Summary")
        print(f"{'=' * 60}")
        print(f"Total Tests: {len(results) + 1}")
        print(f"Passed: {sum(results) + (1 if health_ok else 0)}")
        print(f"Failed: {len(results) + 1 - sum(results) - (1 if health_ok else 0)}")


if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()