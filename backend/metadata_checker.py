"""
Metadata change detection module
Tracks content changes using hash, headers, etc.
"""
import hashlib
import requests
from typing import Optional, Dict, Tuple
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetadataChecker:
    """Checks for changes in program pages"""
    
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def check_metadata(self, url: str, existing_hash: Optional[str] = None,
                      existing_etag: Optional[str] = None,
                      existing_last_modified: Optional[str] = None) -> Dict:
        """
        Check metadata and detect changes
        Returns dict with:
        - content_hash: SHA256 hash
        - etag: ETag header
        - last_modified_header: Last-Modified header
        - has_changed: bool
        - last_checked: datetime
        """
        try:
            response = self.session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                return {
                    'content_hash': existing_hash,
                    'etag': existing_etag,
                    'last_modified_header': existing_last_modified,
                    'has_changed': False,
                    'last_checked': datetime.utcnow(),
                    'error': f'HTTP {response.status_code}'
                }
            
            # Extract headers
            etag = response.headers.get('ETag', '').strip('"')
            last_modified = response.headers.get('Last-Modified', '')
            
            # Calculate content hash
            content = self._clean_content(response.text)
            content_hash = self._calculate_hash(content)
            
            # Check for changes
            has_changed = False
            if existing_hash:
                if content_hash != existing_hash:
                    has_changed = True
                elif etag and existing_etag and etag != existing_etag:
                    has_changed = True
                elif last_modified and existing_last_modified and last_modified != existing_last_modified:
                    has_changed = True
            else:
                # First time checking
                has_changed = True
            
            return {
                'content_hash': content_hash,
                'etag': etag,
                'last_modified_header': last_modified,
                'has_changed': has_changed,
                'last_checked': datetime.utcnow()
            }
        
        except Exception as e:
            logger.error(f"Metadata check error for {url}: {e}")
            return {
                'content_hash': existing_hash,
                'etag': existing_etag,
                'last_modified_header': existing_last_modified,
                'has_changed': False,
                'last_checked': datetime.utcnow(),
                'error': str(e)
            }
    
    def _clean_content(self, html_content: str) -> str:
        """Clean HTML content for hashing (remove dynamic elements)"""
        from bs4 import BeautifulSoup
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style tags
            for tag in soup.find_all(['script', 'style', 'noscript']):
                tag.decompose()
            
            # Remove comments
            from bs4 import Comment
            comments = soup.find_all(string=lambda text: isinstance(text, Comment))
            for comment in comments:
                comment.extract()
            
            # Get text content
            text = soup.get_text()
            
            # Normalize whitespace
            text = ' '.join(text.split())
            
            return text
        except Exception as e:
            logger.warning(f"Content cleaning error: {e}")
            return html_content
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

