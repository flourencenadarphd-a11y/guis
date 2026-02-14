"""
University and course scraper module
Fetches universities by country and searches for course programs
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time
import re
from urllib.parse import urljoin, urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UniversityScraper:
    """Scrapes universities from various sources"""
    
    def __init__(self, timeout: int = 10, retry_count: int = 3):
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def fetch_universities(self, country: str) -> List[str]:
        """
        Fetch universities for a given country
        Sources: Wikipedia, government portals
        """
        universities = set()
        
        # Try Wikipedia first
        wiki_universities = self._fetch_from_wikipedia(country)
        universities.update(wiki_universities)
        
        # Try country-specific sources
        country_universities = self._fetch_country_specific(country)
        universities.update(country_universities)
        
        # Clean and return
        cleaned = [self._clean_name(name) for name in universities if name]
        return list(set(cleaned))  # Remove duplicates
    
    def _fetch_from_wikipedia(self, country: str) -> List[str]:
        """Fetch universities from Wikipedia"""
        universities = []
        try:
            # Wikipedia list format: "List of universities in [Country]"
            search_terms = [
                f"List of universities in {country}",
                f"Universities in {country}",
                f"List of universities and colleges in {country}"
            ]
            
            for term in search_terms:
                url = f"https://en.wikipedia.org/wiki/{term.replace(' ', '_')}"
                try:
                    response = self._make_request(url)
                    if response and response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Find table rows or list items
                        tables = soup.find_all('table', class_='wikitable')
                        for table in tables:
                            rows = table.find_all('tr')
                            for row in rows[1:]:  # Skip header
                                cells = row.find_all(['td', 'th'])
                                if cells:
                                    # Usually first or second cell contains university name
                                    name_cell = cells[0] if len(cells) > 0 else None
                                    if name_cell:
                                        link = name_cell.find('a')
                                        if link:
                                            name = link.get_text(strip=True)
                                            if name and len(name) > 3:
                                                universities.append(name)
                        
                        # Also check unordered lists
                        lists = soup.find_all(['ul', 'ol'])
                        for ul in lists:
                            items = ul.find_all('li')
                            for item in items:
                                link = item.find('a')
                                if link:
                                    name = link.get_text(strip=True)
                                    if 'university' in name.lower() or 'college' in name.lower():
                                        universities.append(name)
                        
                        if universities:
                            break  # Found universities, no need to try other terms
                except Exception as e:
                    logger.warning(f"Error fetching from Wikipedia for {term}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error in Wikipedia fetch: {e}")
        
        return universities
    
    def _fetch_country_specific(self, country: str) -> List[str]:
        """Fetch from country-specific education portals"""
        universities = []
        # This can be extended with country-specific sources
        # For now, return empty list
        return universities
    
    def _clean_name(self, name: str) -> str:
        """Clean university name"""
        if not name:
            return ""
        # Remove extra whitespace
        name = ' '.join(name.split())
        # Remove common prefixes/suffixes that might cause issues
        name = re.sub(r'^The\s+', '', name, flags=re.IGNORECASE)
        return name.strip()
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.retry_count):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:  # Rate limited
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
        return None


class CourseScraper:
    """Scrapes course/program links from university websites"""
    
    def __init__(self, timeout: int = 10, retry_count: int = 3):
        self.timeout = timeout
        self.retry_count = retry_count
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_courses(self, university_name: str, course_keyword: str, base_url: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Search for courses matching keyword in university website
        Returns list of dicts with 'url' and 'title'
        """
        if not base_url:
            # Try to construct base URL from university name
            base_url = self._guess_university_url(university_name)
        
        if not base_url:
            logger.warning(f"Could not determine URL for {university_name}")
            return []
        
        program_links = []
        
        # Search strategies
        strategies = [
            self._search_via_sitemap,
            self._search_via_search_page,
            self._crawl_common_paths
        ]
        
        for strategy in strategies:
            try:
                links = strategy(base_url, course_keyword)
                if links:
                    program_links.extend(links)
                    break  # If one strategy works, use it
            except Exception as e:
                logger.warning(f"Strategy {strategy.__name__} failed: {e}")
                continue
        
        # Validate and filter links
        validated_links = []
        for link_info in program_links:
            if self._validate_program_page(link_info['url'], course_keyword):
                validated_links.append(link_info)
        
        return validated_links
    
    def _guess_university_url(self, university_name: str) -> Optional[str]:
        """Try to guess university website URL"""
        # Common patterns
        name_lower = university_name.lower()
        name_clean = re.sub(r'[^a-z0-9\s]', '', name_lower)
        name_parts = name_clean.split()
        
        # Try common domain patterns
        patterns = [
            f"https://www.{name_parts[0]}.edu",
            f"https://www.{name_parts[0]}.ac.{name_parts[-1] if len(name_parts) > 1 else 'uk'}",
            f"https://{name_parts[0]}.edu",
            f"https://www.{'-'.join(name_parts[:2])}.edu" if len(name_parts) >= 2 else None
        ]
        
        for pattern in patterns:
            if pattern:
                try:
                    response = self._make_request(pattern)
                    if response and response.status_code == 200:
                        return pattern
                except:
                    continue
        
        return None
    
    def _search_via_sitemap(self, base_url: str, keyword: str) -> List[Dict[str, str]]:
        """Search via sitemap.xml"""
        sitemap_urls = [
            urljoin(base_url, '/sitemap.xml'),
            urljoin(base_url, '/sitemap_index.xml')
        ]
        
        links = []
        for sitemap_url in sitemap_urls:
            try:
                response = self._make_request(sitemap_url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'xml')
                    urls = soup.find_all('url')
                    for url_tag in urls:
                        loc = url_tag.find('loc')
                        if loc:
                            url = loc.text
                            if keyword.lower() in url.lower():
                                links.append({'url': url, 'title': url})
            except Exception as e:
                logger.debug(f"Sitemap search failed: {e}")
        
        return links
    
    def _search_via_search_page(self, base_url: str, keyword: str) -> List[Dict[str, str]]:
        """Search via website search functionality"""
        search_urls = [
            urljoin(base_url, f'/search?q={keyword}'),
            urljoin(base_url, f'/search/?query={keyword}'),
            urljoin(base_url, f'/programs/search?q={keyword}')
        ]
        
        links = []
        for search_url in search_urls:
            try:
                response = self._make_request(search_url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Find links in search results
                    result_links = soup.find_all('a', href=True)
                    for link in result_links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        if href and keyword.lower() in (href.lower() + text.lower()):
                            full_url = urljoin(base_url, href)
                            links.append({'url': full_url, 'title': text or href})
            except Exception as e:
                logger.debug(f"Search page failed: {e}")
        
        return links
    
    def _crawl_common_paths(self, base_url: str, keyword: str) -> List[Dict[str, str]]:
        """Crawl common program/course paths"""
        common_paths = [
            '/programs',
            '/courses',
            '/study',
            '/academics',
            '/departments',
            '/faculties'
        ]
        
        links = []
        for path in common_paths:
            try:
                url = urljoin(base_url, path)
                response = self._make_request(url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    all_links = soup.find_all('a', href=True)
                    for link in all_links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        href_lower = href.lower() if href else ""
                        text_lower = text.lower() if text else ""
                        
                        if keyword.lower() in (href_lower + text_lower):
                            full_url = urljoin(url, href)
                            links.append({'url': full_url, 'title': text or href})
            except Exception as e:
                logger.debug(f"Crawl path {path} failed: {e}")
        
        return links
    
    def _validate_program_page(self, url: str, course_keyword: str) -> bool:
        """
        Validate that URL is a valid program page
        Checks: HTTP 200, contains keyword, contains academic structure
        """
        try:
            response = self._make_request(url)
            if not response or response.status_code != 200:
                return False
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text = soup.get_text().lower()
            
            # Must contain course keyword
            if course_keyword.lower() not in text:
                return False
            
            # Must contain academic structure keywords
            academic_keywords = [
                'program', 'curriculum', 'course', 'module', 'credit',
                'degree', 'bachelor', 'master', 'study', 'academic'
            ]
            
            has_academic_structure = any(keyword in text for keyword in academic_keywords)
            if not has_academic_structure:
                return False
            
            return True
        except Exception as e:
            logger.debug(f"Validation failed for {url}: {e}")
            return False
    
    def _make_request(self, url: str) -> Optional[requests.Response]:
        """Make HTTP request with retry logic"""
        for attempt in range(self.retry_count):
            try:
                response = self.session.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response
                elif response.status_code == 429:
                    time.sleep(2 ** attempt)
                else:
                    return None
            except requests.exceptions.RequestException as e:
                if attempt < self.retry_count - 1:
                    time.sleep(2 ** attempt)
        return None

