import chromadb
from chromadb.config import Settings
from openai import AsyncOpenAI
import os
from typing import List, Dict
import hashlib
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = AsyncOpenAI(api_key=api_key)


class InformationRetriever:
    def __init__(self):
        # Initialize ChromaDB
        self.chroma_client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="web_documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embedding_model = "text-embedding-3-small"
        self.chunk_size = 1000
        self.chunk_overlap = 200
    
    async def process_document(self, content: str, url: str, metadata: Dict) -> str:
        """
        Process document: chunk, embed, and store in vector DB
        """
        try:
            # Generate document ID
            doc_id = hashlib.md5(url.encode()).hexdigest()
            
            # Chunk the content
            chunks = self._chunk_text(content)
            logger.info(f"Created {len(chunks)} chunks from document")
            
            if not chunks:
                raise ValueError("No chunks created from content")
            
            # Generate embeddings
            embeddings = await self._generate_embeddings(chunks)
            
            # Prepare metadata for each chunk
            chunk_metadatas = []
            chunk_ids = []
            for i, chunk in enumerate(chunks):
                chunk_id = f"{doc_id}_chunk_{i}"
                chunk_ids.append(chunk_id)
                
                chunk_metadata = {
                    'doc_id': doc_id,
                    'chunk_index': i,
                    'url': url,
                    'title': metadata.get('title', ''),
                    'scraped_at': metadata.get('scraped_at', datetime.now().isoformat()),
                    'chunk_size': len(chunk)
                }
                chunk_metadatas.append(chunk_metadata)
            
            # Add to ChromaDB
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadatas,
                ids=chunk_ids
            )
            
            logger.info(f"Successfully stored {len(chunks)} chunks in vector DB")
            return doc_id
            
        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            raise
    
    async def search(self, query: str, doc_id: str = None, top_k: int = 5) -> List[Dict]:
        """
        Semantic search using query embedding
        """
        try:
            # Generate query embedding
            query_embedding = await self._generate_embeddings([query])
            
            # Build where filter
            where_filter = None
            if doc_id:
                where_filter = {"doc_id": doc_id}
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                where=where_filter
            )
            
            # Format results
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    result = {
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None,
                        'relevance_score': 1 - results['distances'][0][i] if 'distances' in results else None
                    }
                    search_results.append(result)
            
            logger.info(f"Found {len(search_results)} relevant chunks")
            return search_results
            
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
            raise
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        Chunk text with overlap for better context preservation
        """
        if not text or len(text.strip()) == 0:
            return []
        
        # Split by paragraphs first
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    # Keep overlap from end of previous chunk
                    words = current_chunk.split()
                    overlap_words = words[-self.chunk_overlap//5:] if len(words) > self.chunk_overlap//5 else []
                    current_chunk = ' '.join(overlap_words) + '\n\n' + para
                else:
                    # Single paragraph is too long, split by sentences
                    sentences = para.split('. ')
                    for sent in sentences:
                        if len(current_chunk) + len(sent) > self.chunk_size:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = sent + '. '
                        else:
                            current_chunk += sent + '. '
            else:
                current_chunk += para + '\n\n'
        
        # Add last chunk
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    async def _generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using OpenAI API
        """
        try:
            response = await client.embeddings.create(
                model=self.embedding_model,
                input=texts
            )
            
            embeddings = [item.embedding for item in response.data]
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise