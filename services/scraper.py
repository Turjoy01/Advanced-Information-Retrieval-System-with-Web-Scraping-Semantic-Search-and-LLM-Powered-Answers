import asyncio
from bs4 import BeautifulSoup
import aiohttp
from typing import Dict, Optional
from datetime import datetime
import logging
from urllib.parse import urljoin, urlparse
import re

logger = logging.getLogger(__name__)


class WebScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.timeout = aiohttp.ClientTimeout(total=30)
    
    async def scrape_url(self, url: str) -> Dict:
        """
        Advanced web scraping with multiple strategies
        """
        try:
            # First try with aiohttp (faster for static pages)
            html_content = await self._fetch_with_aiohttp(url)
            
            if not html_content:
                logger.warning(f"Failed to fetch {url}")
                return {}
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Extract content
            content = self._extract_content(soup)
            metadata = self._extract_metadata(soup, url)
            
            return {
                'content': content,
                'metadata': metadata,
                'url': url
            }
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            raise
    
    async def _fetch_with_aiohttp(self, url: str) -> Optional[str]:
        """
        Fetch HTML content using aiohttp
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.warning(f"HTTP {response.status} for {url}")
                        return None
        except Exception as e:
            logger.error(f"aiohttp fetch error: {str(e)}")
            return None
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """
        Extract main content from HTML with advanced cleaning
        """
        # Remove script, style, nav, footer, ads
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 
                            'header', 'noscript', 'iframe']):
            element.decompose()
        
        # Remove elements with common ad/navigation classes
        ad_patterns = ['ad', 'advertisement', 'sidebar', 'menu', 'navigation', 
                      'cookie', 'popup', 'modal', 'banner']
        for pattern in ad_patterns:
            for elem in soup.find_all(class_=re.compile(pattern, re.I)):
                elem.decompose()
        
        # Priority extraction: article, main, body
        main_content = None
        for tag in ['article', 'main', '[role="main"]']:
            main_content = soup.select_one(tag)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body
        
        if not main_content:
            return ""
        
        # Extract text with paragraph preservation
        paragraphs = []
        for p in main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li']):
            text = p.get_text(strip=True)
            if len(text) > 20:  # Filter very short texts
                paragraphs.append(text)
        
        content = '\n\n'.join(paragraphs)
        
        # Clean up whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        
        return content.strip()
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract metadata from HTML
        """
        metadata = {
            'scraped_at': datetime.now().isoformat(),
            'url': url,
            'domain': urlparse(url).netloc
        }
        
        # Title
        title = soup.find('title')
        if title:
            metadata['title'] = title.get_text(strip=True)
        
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata['description'] = meta_desc['content']
        
        # Open Graph tags
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            metadata['og_title'] = og_title['content']
        
        # Author
        author = soup.find('meta', attrs={'name': 'author'})
        if author and author.get('content'):
            metadata['author'] = author['content']
        
        # Keywords
        keywords = soup.find('meta', attrs={'name': 'keywords'})
        if keywords and keywords.get('content'):
            metadata['keywords'] = keywords['content']
        
        # Published date
        published = soup.find('meta', property='article:published_time')
        if published and published.get('content'):
            metadata['published_date'] = published['content']
        
        return metadata