from openai import AsyncOpenAI
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
client = AsyncOpenAI(api_key=api_key)


class LLMService:
    def __init__(self):
        self.model = "gpt-4o-mini"  # or "gpt-4o" for better quality
        self.max_tokens = 1000
        self.temperature = 0.3
    
    async def generate_answer(self, query: str, context: str) -> str:
        """
        Generate answer using GPT-4 with retrieved context
        """
        try:
            # Construct prompt
            system_prompt = """You are an expert information retrieval assistant. 
Your task is to answer questions based ONLY on the provided context from web pages.

Guidelines:
- Provide accurate, concise answers
- Use information from the context provided
- If the context doesn't contain relevant information, say so
- Include specific details and examples when available
- Cite key points from the context
- Be objective and factual"""

            user_prompt = f"""Context from web page:
{context}

Question: {query}

Please provide a comprehensive answer based on the context above."""

            # Call OpenAI API
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            answer = response.choices[0].message.content
            logger.info(f"Generated answer with {response.usage.total_tokens} tokens")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    async def summarize_content(self, content: str, max_length: int = 500) -> str:
        """
        Summarize long content
        """
        try:
            prompt = f"""Provide a concise summary of the following content in approximately {max_length} words:

{content}

Summary:"""

            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a expert summarizer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_length * 2,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content
            return summary
            
        except Exception as e:
            logger.error(f"Error summarizing content: {str(e)}")
            raise