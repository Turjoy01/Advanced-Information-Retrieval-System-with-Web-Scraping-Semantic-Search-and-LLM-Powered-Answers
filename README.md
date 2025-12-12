Advanced Information Retrieval API

An advanced FastAPI-based information retrieval system that provides web scraping, semantic search, and LLM-powered answers for extracting relevant data from websites and generating context-aware responses.

🌟 Features
✨ Advanced Web Scraping

Intelligent content extraction using BeautifulSoup

Metadata extraction (e.g., title, author, description)

Ad/navigation content filtering

🔍 Semantic Search

Vector representation using OpenAI embeddings

ChromaDB for storing and retrieving vectors

Context-aware chunking with overlap for better search results

🤖 LLM-Powered Answers

GPT-4 for natural language answers

Context-based response generation

Relevance scoring for more accurate results

🔧 Project Structure
info-retrieval-api/
│
├── main.py                   # FastAPI application
├── config.py                 # Configuration for the API
├── requirements.txt          # Dependencies list
├── .env                      # Environment variables (API keys)
│
└── services/
    ├── __init__.py
    ├── scraper.py            # Web scraping logic
    ├── retriever.py          # Vector DB & search logic
    └── llm_service.py        # LLM-based answer generation

📦 Installation
1. Create Virtual Environment

Create a virtual environment to isolate dependencies.

python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

2. Install Dependencies

Install all required dependencies using pip.

pip install -r requirements.txt

3. Setup Environment Variables

Create a .env file to store your OpenAI API key and other configuration settings.

OPENAI_API_KEY=your_api_key_here

🚀 Running the API

After the installation and environment setup, run the API using Uvicorn.

python main.py


Your API will be available at http://localhost:8000.

📚 API Documentation
1. Retrieve Information

Endpoint: POST /retrieve

This endpoint retrieves relevant chunks of information from the specified URL based on a query and returns a context-aware answer generated using an LLM.

Request Body:

{
  "url": "https://example.com/article",
  "query": "What are the main benefits?",
  "top_k": 5,
  "use_llm": true
}


Response:

{
  "query": "What are the main benefits?",
  "url": "https://example.com/article",
  "relevant_chunks": [
    {
      "content": "Chunk text...",
      "metadata": {
        "doc_id": "abc123",
        "chunk_index": 0,
        "url": "https://example.com/article"
      },
      "relevance_score": 0.89
    }
  ],
  "answer": "Based on the article, the main benefits are...",
  "metadata": {
    "total_chunks": 5,
    "title": "Article Title",
    "scraped_at": "2024-01-15T10:30:00"
  }
}

2. Health Check

Endpoint: GET /health

This is a simple health check endpoint to verify if the API is running.

💡 Usage Examples
cURL Example

To retrieve information about a topic from a URL, use the following curl command:

curl -X POST "http://localhost:8000/retrieve" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://en.wikipedia.org/wiki/Machine_learning",
    "query": "What is machine learning?",
    "top_k": 3
  }'

Python Example

Use the Python requests library to interact with the API:

import requests

response = requests.post(
    "http://localhost:8000/retrieve",
    json={
        "url": "https://example.com",
        "query": "What is the main topic?",
        "top_k": 5,
        "use_llm": True
    }
)

result = response.json()
print(result['answer'])

🧑‍💻 How It Works

Web Scraping: The system scrapes the content from the provided URL.

Text Chunking: The content is split into smaller, semantic chunks for better processing.

Embedding: OpenAI’s API is used to generate embeddings for these chunks.

Vector Storage: The embeddings are stored in ChromaDB for quick retrieval.

Semantic Search: The query is matched to relevant chunks from the database.

LLM Answer: GPT-4 generates a context-aware response based on the selected chunks.

🔧 Advanced Configuration

You can configure the following in the config.py file:

Chunk size and overlap

Embedding model selection

LLM model and parameters

Top-K results

Temperature settings for OpenAI models

📈 Requirements

Python 3.9+

OpenAI API key

2GB+ RAM (ChromaDB)

⚡ Performance Tips

Chunk Size: For larger documents, increase the chunk size.

Top-K: Reduce the top_k for more precise results.

Model Selection:

Fast: gpt-4o-mini

High Quality: gpt-4o

🛑 Error Handling

The API handles the following errors:

Invalid URLs

Scraping failures

OpenAI API errors

Vector DB issues

🚧 Limitations

JavaScript-heavy websites may require additional tools like Playwright.

Processing time may increase for very large documents.

OpenAI API rate limits apply.

🔮 Future Enhancements

 Playwright integration for JavaScript rendering

 Caching mechanism for faster responses

 Multi-document comparison for cross-referencing

 Advanced filtering options for chunk results

 Streaming responses for large document processing

📜 License

MIT License

<img width="1300" height="674" alt="image" src="https://github.com/user-attachments/assets/cba00462-3a3c-4958-a761-ede85c9d9f55" />
<img width="705" height="816" alt="image" src="https://github.com/user-attachments/assets/13e54642-90a2-42b6-8ce0-c96d66d5ac40" />

