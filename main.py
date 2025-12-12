from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional
import uvicorn
from services.scraper import WebScraper
from services.retriever import InformationRetriever
from services.llm_service import LLMService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Advanced Information Retrieval API",
    description="Web scraping + Semantic Search + LLM-powered answers",
    version="1.0.0"
)

# Initialize services
scraper = WebScraper()
retriever = InformationRetriever()
llm_service = LLMService()


class QueryRequest(BaseModel):
    url: HttpUrl
    query: str
    top_k: Optional[int] = 5
    use_llm: Optional[bool] = True


class QueryResponse(BaseModel):
    query: str
    url: str
    relevant_chunks: list
    answer: Optional[str] = None
    metadata: dict


@app.get("/")
async def root():
    return {
        "message": "Advanced Information Retrieval API",
        "endpoints": {
            "/retrieve": "POST - Retrieve information from URL",
            "/health": "GET - Health check"
        }
    }


@app.post("/retrieve", response_model=QueryResponse)
async def retrieve_information(request: QueryRequest):
    """
    Main endpoint for information retrieval
    
    1. Scrapes the URL
    2. Chunks and embeds content
    3. Performs semantic search
    4. Generates LLM answer (optional)
    """
    try:
        url_str = str(request.url)
        logger.info(f"Processing request for URL: {url_str}")
        
        # Step 1: Scrape the website
        logger.info("Step 1: Scraping website...")
        scraped_data = await scraper.scrape_url(url_str)
        
        if not scraped_data or not scraped_data.get('content'):
            raise HTTPException(status_code=400, detail="Failed to scrape content from URL")
        
        # Step 2: Process and store in vector DB
        logger.info("Step 2: Processing and embedding content...")
        doc_id = await retriever.process_document(
            content=scraped_data['content'],
            url=url_str,
            metadata=scraped_data.get('metadata', {})
        )
        
        # Step 3: Semantic search
        logger.info("Step 3: Performing semantic search...")
        search_results = await retriever.search(
            query=request.query,
            doc_id=doc_id,
            top_k=request.top_k
        )
        
        # Step 4: Generate LLM answer
        answer = None
        if request.use_llm and search_results:
            logger.info("Step 4: Generating LLM answer...")
            context = "\n\n".join([chunk['content'] for chunk in search_results])
            answer = await llm_service.generate_answer(
                query=request.query,
                context=context
            )
        
        return QueryResponse(
            query=request.query,
            url=url_str,
            relevant_chunks=search_results,
            answer=answer,
            metadata={
                "total_chunks": len(search_results),
                "scraped_at": scraped_data.get('metadata', {}).get('scraped_at'),
                "title": scraped_data.get('metadata', {}).get('title')
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "scraper": "operational",
            "retriever": "operational",
            "llm": "operational"
        }
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)