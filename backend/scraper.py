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
        """Fetch universities from Wikipedia - IMPROVED with better error handling"""
        universities = set()
        try:
            # Wikipedia list format: "List of universities in [Country]"
            # Try multiple variations
            country_clean = country.replace(' ', '_').replace(',', '').strip()
            search_terms = [
                f"List_of_universities_in_{country_clean}",
                f"List_of_universities_and_colleges_in_{country_clean}",
                f"Universities_in_{country_clean}",
                f"List_of_higher_education_institutions_in_{country_clean}",
                f"List_of_universities_in_{country_clean.replace('_', ' ')}",  # Try with spaces
            ]
            
            logger.info(f"Searching Wikipedia for universities in {country}")
            
            for term in search_terms:
                url = f"https://en.wikipedia.org/wiki/{term}"
                logger.info(f"Trying URL: {url}")
                try:
                    response = self._make_request(url)
                    if response and response.status_code == 200:
                        logger.info(f"Successfully fetched: {url}")
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Method 1: Find ALL tables (not just wikitable class)
                        all_tables = soup.find_all('table')
                        for table in all_tables:
                            rows = table.find_all('tr')
                            for row in rows[1:]:  # Skip header
                                cells = row.find_all(['td', 'th'])
                                for cell in cells[:3]:  # Check first 3 cells
                                    # Look for links
                                    links = cell.find_all('a')
                                    for link in links:
                                        name = link.get_text(strip=True)
                                        href = link.get('href', '')
                                        # Filter for university-related links
                                        if name and len(name) > 3:
                                            name_lower = name.lower()
                                            if any(keyword in name_lower for keyword in ['university', 'college', 'institute', 'academy', 'school']):
                                                universities.add(name)
                                            # Also check if href suggests it's a university page
                                            elif '/wiki/' in href and any(keyword in href.lower() for keyword in ['university', 'college', 'institute']):
                                                universities.add(name)
                        
                        # Method 2: Check ALL lists more thoroughly
                        all_lists = soup.find_all(['ul', 'ol'])
                        for ul in all_lists:
                            items = ul.find_all('li')
                            for item in items:
                                # Get all links in the item
                                links = item.find_all('a')
                                for link in links:
                                    name = link.get_text(strip=True)
                                    href = link.get('href', '')
                                    if name and len(name) > 3:
                                        name_lower = name.lower()
                                        # More lenient matching
                                        if any(keyword in name_lower for keyword in ['university', 'college', 'institute', 'academy', 'school', 'universität', 'université', 'universidad']):
                                            universities.add(name)
                                        elif '/wiki/' in href:
                                            # Check if it's likely a university page
                                            href_lower = href.lower()
                                            if any(keyword in href_lower for keyword in ['university', 'college', 'institute', 'academy']):
                                                universities.add(name)
                        
                        # Method 3: Look for divs with university lists
                        content_divs = soup.find_all('div', class_=['mw-parser-output', 'mw-content-ltr'])
                        for div in content_divs:
                            # Find all links that might be universities
                            links = div.find_all('a', href=True)
                            for link in links:
                                name = link.get_text(strip=True)
                                href = link.get('href', '')
                                if name and len(name) > 5 and '/wiki/' in href:
                                    name_lower = name.lower()
                                    href_lower = href.lower()
                                    # Check if it's a university-related page
                                    if any(keyword in name_lower or keyword in href_lower for keyword in ['university', 'college', 'institute', 'academy']):
                                        universities.add(name)
                        
                        if universities:
                            logger.info(f"Found {len(universities)} universities from {term}")
                            break  # Found universities, no need to try other terms
                    else:
                        logger.warning(f"Failed to fetch {url}: Status {response.status_code if response else 'No response'}")
                except Exception as e:
                    logger.warning(f"Error fetching from Wikipedia for {term}: {e}")
                    continue
            
            # If no results, try alternative method: search Wikipedia directly
            if not universities:
                logger.info("No results from list pages, trying alternative search method...")
                universities = self._search_wikipedia_alternative(country)
            
            logger.info(f"Total universities found: {len(universities)}")
        except Exception as e:
            logger.error(f"Error in Wikipedia fetch: {e}")
        
        return list(universities)
    
    def _search_wikipedia_alternative(self, country: str) -> set:
        """Alternative method: search Wikipedia for university pages"""
        universities = set()
        try:
            # Try searching for individual university pages
            search_url = f"https://en.wikipedia.org/wiki/Special:Search/{country}_university"
            response = self._make_request(search_url)
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Find search results
                results = soup.find_all('div', class_='mw-search-result')
                for result in results:
                    title = result.find('a')
                    if title:
                        name = title.get_text(strip=True)
                        if 'university' in name.lower() or 'college' in name.lower():
                            universities.add(name)
        except Exception as e:
            logger.warning(f"Alternative search failed: {e}")
        
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
        """Try to guess university website URL - IMPROVED with more patterns"""
        # Common patterns
        name_lower = university_name.lower()
        name_clean = re.sub(r'[^a-z0-9\s]', '', name_lower)
        name_parts = [p for p in name_clean.split() if len(p) > 2]  # Filter short words
        
        if not name_parts:
            return None
        
        # Try common domain patterns - EXPANDED
        patterns = []
        
        # US/International patterns
        if len(name_parts) >= 1:
            patterns.extend([
                f"https://www.{name_parts[0]}.edu",
                f"https://{name_parts[0]}.edu",
                f"https://www.{name_parts[0]}.ac.uk",
                f"https://{name_parts[0]}.ac.uk",
            ])
        
        if len(name_parts) >= 2:
            patterns.extend([
                f"https://www.{'-'.join(name_parts[:2])}.edu",
                f"https://{'-'.join(name_parts[:2])}.edu",
                f"https://www.{name_parts[0]}{name_parts[1]}.edu",
                f"https://{name_parts[0]}{name_parts[1]}.edu",
            ])
        
        # European patterns
        if len(name_parts) >= 1:
            patterns.extend([
                f"https://www.{name_parts[0]}.ac.at",  # Austria
                f"https://www.{name_parts[0]}.ac.de",  # Germany
                f"https://www.{name_parts[0]}.ac.fr",  # France
                f"https://www.{name_parts[0]}.university",
                f"https://{name_parts[0]}.university",
            ])
        
        # Try Wikipedia to get official URL
        try:
            wiki_url = f"https://en.wikipedia.org/wiki/{university_name.replace(' ', '_')}"
            response = self._make_request(wiki_url)
            if response and response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Look for official website link
                infobox = soup.find('table', class_='infobox')
                if infobox:
                    links = infobox.find_all('a', href=True)
                    for link in links:
                        href = link.get('href', '')
                        text = link.get_text(strip=True).lower()
                        if 'website' in text or 'official' in text:
                            if href.startswith('http'):
                                return href
                        # Also check for .edu, .ac.uk, etc.
                        if any(domain in href for domain in ['.edu', '.ac.uk', '.ac.', '.university']):
                            if href.startswith('http'):
                                return href
                            elif href.startswith('//'):
                                return 'https:' + href
        except:
            pass
        
        # Try patterns
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
        """Search via website search functionality - IMPROVED"""
        from urllib.parse import quote
        
        keyword_encoded = quote(keyword)
        search_urls = [
            urljoin(base_url, f'/search?q={keyword_encoded}'),
            urljoin(base_url, f'/search/?query={keyword_encoded}'),
            urljoin(base_url, f'/search?query={keyword_encoded}'),
            urljoin(base_url, f'/programs/search?q={keyword_encoded}'),
            urljoin(base_url, f'/courses/search?q={keyword_encoded}'),
            urljoin(base_url, f'/study/search?q={keyword_encoded}'),
            urljoin(base_url, f'/academics/search?q={keyword_encoded}'),
        ]
        
        links = []
        for search_url in search_urls:
            try:
                response = self._make_request(search_url)
                if response and response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    # Find links in search results - more thorough
                    result_links = soup.find_all('a', href=True)
                    for link in result_links:
                        href = link.get('href')
                        text = link.get_text(strip=True)
                        if href:
                            keyword_lower = keyword.lower()
                            href_lower = href.lower()
                            text_lower = text.lower()
                            
                            # More lenient matching
                            if (keyword_lower in href_lower or 
                                keyword_lower in text_lower or
                                any(word in href_lower for word in keyword_lower.split()) or
                                any(word in text_lower for word in keyword_lower.split())):
                                full_url = urljoin(base_url, href)
                                # Avoid duplicates and non-program pages
                                if full_url not in [l['url'] for l in links]:
                                    if any(term in href_lower for term in ['program', 'course', 'degree', 'study', 'academic']):
                                        links.append({'url': full_url, 'title': text or href})
            except Exception as e:
                logger.debug(f"Search page failed: {e}")
        
        return links
    
    def _crawl_common_paths(self, base_url: str, keyword: str) -> List[Dict[str, str]]:
        """Crawl common program/course paths - IMPROVED"""
        common_paths = [
            '/programs', '/programmes', '/program',
            '/courses', '/course',
            '/study', '/studies', '/studying',
            '/academics', '/academic',
            '/departments', '/department',
            '/faculties', '/faculty',
            '/degrees', '/degree',
            '/undergraduate', '/graduate',
            '/bachelor', '/master',
        ]
        
        links = []
        keyword_lower = keyword.lower()
        keyword_words = keyword_lower.split()
        
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
                        
                        # More lenient matching
                        matches = (
                            keyword_lower in (href_lower + text_lower) or
                            any(word in href_lower for word in keyword_words) or
                            any(word in text_lower for word in keyword_words)
                        )
                        
                        if matches:
                            full_url = urljoin(url, href)
                            # Avoid duplicates
                            if full_url not in [l['url'] for l in links]:
                                # Prefer program-related links
                                if any(term in href_lower for term in ['program', 'course', 'degree', 'study', 'bachelor', 'master']):
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

