"""
Article Extraction API - Python Flask Implementation

Based on Capy Reader's article extraction logic.
Fetches, extracts, and cleans article content from URLs.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from readability import Document
import re
from urllib.parse import urlparse
from datetime import datetime

app = Flask(__name__)
CORS(app)

# User-Agent to use when fetching articles
USER_AGENT = (
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/137.0.0.0 Safari/537.36'
)

class ArticleExtractor:
    """Main class for article extraction and cleaning"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': USER_AGENT})
    
    def fetch_html(self, url, timeout=10):
        """
        Fetch HTML content from URL
        
        Args:
            url: Article URL to fetch
            timeout: Request timeout in seconds
            
        Returns:
            HTML string
            
        Raises:
            requests.RequestException: If fetch fails
            ValueError: If response is not HTML
        """
        response = self.session.get(url, timeout=timeout)
        response.raise_for_status()
        
        content_type = response.headers.get('Content-Type', '')
        if 'text/html' not in content_type:
            raise ValueError(f'Invalid content type: {content_type}')
        
        return response.text
    
    def clean_html(self, html, hide_images=False):
        """
        Clean and process HTML content
        Based on Capy Reader's HtmlPostProcessor
        
        Steps:
        1. Remove inline styles
        2. Optionally remove images
        3. Process image loading attributes
        4. Extract images from anchor tags
        5. Wrap tables for responsive display
        
        Args:
            html: HTML string to clean
            hide_images: Whether to remove all images
            
        Returns:
            Cleaned HTML string
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # 1. Remove inline styles
        for tag in soup.find_all(style=True):
            del tag['style']
        
        # 2. Remove images if requested
        if hide_images:
            for img in soup.find_all('img'):
                img.decompose()
        else:
            # 3. Process image loading
            images = soup.find_all('img')
            for i, img in enumerate(images):
                # First image gets high priority
                if i == 0:
                    img['fetchpriority'] = 'high'
                else:
                    img['loading'] = 'lazy'
                
                # Handle data-src (lazy loaded images)
                if img.get('data-src'):
                    img['src'] = img['data-src']
            
            # 4. Extract images from anchor tags
            for img in soup.find_all('img'):
                parent = img.find_parent('a')
                if parent:
                    # Move image out of anchor
                    grandparent = parent.find_parent()
                    if grandparent:
                        grandparent.append(img)
                        parent.decompose()
        
        # 5. Wrap tables for responsive display
        for table in soup.find_all('table'):
            if not table.parent or table.parent.name != 'div' or \
               'table__wrapper' not in table.parent.get('class', []):
                wrapper = soup.new_tag('div', **{'class': 'table__wrapper'})
                table.wrap(wrapper)
        
        return str(soup)
    
    def extract_article(self, url, hide_images=False):
        """
        Extract and clean article content from URL
        
        Args:
            url: Article URL
            hide_images: Whether to remove images
            
        Returns:
            Dictionary with article data
        """
        # 1. Fetch HTML
        html = self.fetch_html(url)
        
        # 2. Extract main content using readability
        doc = Document(html)
        
        # 3. Clean the extracted content
        cleaned_content = self.clean_html(doc.summary(), hide_images)
        
        # 4. Parse metadata
        soup = BeautifulSoup(html, 'html.parser')
        author = self._extract_author(soup)
        published_date = self._extract_date(soup)
        lead_image = self._extract_lead_image(soup, url)
        
        return {
            'title': doc.title(),
            'author': author,
            'content': cleaned_content,
            'excerpt': self._extract_excerpt(doc.summary()),
            'leadImage': lead_image,
            'publishedDate': published_date,
            'url': url,
            'domain': urlparse(url).netloc,
        }
    
    def _extract_author(self, soup):
        """Extract author from meta tags or article content"""
        # Try meta tags first
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_ = meta.get('property', '').lower()
            
            if name in ['author', 'article:author'] or \
               property_ in ['author', 'article:author']:
                return meta.get('content')
        
        return None
    
    def _extract_date(self, soup):
        """Extract published date from meta tags"""
        for meta in soup.find_all('meta'):
            property_ = meta.get('property', '').lower()
            name = meta.get('name', '').lower()
            
            if property_ in ['article:published_time', 'article:published'] or \
               name in ['published_time', 'publishdate', 'date']:
                content = meta.get('content')
                if content:
                    return content
        
        return None
    
    def _extract_lead_image(self, soup, base_url):
        """Extract lead/hero image from meta tags"""
        for meta in soup.find_all('meta'):
            property_ = meta.get('property', '').lower()
            name = meta.get('name', '').lower()
            
            if property_ in ['og:image', 'twitter:image'] or \
               name in ['og:image', 'twitter:image']:
                return meta.get('content')
        
        return None
    
    def _extract_excerpt(self, html, max_length=200):
        """Extract text excerpt from HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)
        
        if len(text) <= max_length:
            return text
        
        return text[:max_length].rsplit(' ', 1)[0] + '...'


# Initialize extractor
extractor = ArticleExtractor()


@app.route('/api/extract', methods=['POST'])
def extract_article():
    """
    Extract and clean article content from a URL
    
    Request JSON:
        {
            "url": "https://example.com/article",
            "hideImages": false
        }
    
    Response JSON:
        {
            "success": true,
            "article": {
                "title": "Article Title",
                "author": "Author Name",
                "content": "<html>...</html>",
                "excerpt": "Article excerpt...",
                "leadImage": "https://...",
                "publishedDate": "2024-01-01",
                "url": "https://...",
                "domain": "example.com"
            }
        }
    """
    data = request.get_json()
    
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    url = data['url']
    hide_images = data.get('hideImages', False)
    
    try:
        print(f'Extracting article from: {url}')
        
        article = extractor.extract_article(url, hide_images)
        
        return jsonify({
            'success': True,
            'article': article
        })
        
    except requests.Timeout:
        return jsonify({'error': 'Request timeout'}), 408
    
    except requests.RequestException as e:
        return jsonify({
            'error': 'Failed to fetch article',
            'message': str(e)
        }), 500
    
    except ValueError as e:
        return jsonify({
            'error': 'Invalid content',
            'message': str(e)
        }), 400
    
    except Exception as e:
        print(f'Error extracting article: {e}')
        return jsonify({
            'error': 'Failed to extract article',
            'message': str(e)
        }), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat()
    })


if __name__ == '__main__':
    port = 3000
    print(f'Article extraction API running on port {port}')
    print(f'Try: POST http://localhost:{port}/api/extract')
    print(f'Body: {{"url": "https://example.com/article"}}')
    app.run(debug=True, port=port)
