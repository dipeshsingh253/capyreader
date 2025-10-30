# Quick Start: Article Extraction for Read-It-Later Apps

This guide provides a quick overview of how to integrate Capy Reader's article extraction logic into your own read-it-later web application.

## What Does It Do?

The article extraction system:
1. **Fetches** article HTML from URLs
2. **Extracts** the main content (removing ads, sidebars, etc.)
3. **Cleans** HTML (removes styles, processes images)
4. **Renders** in a beautiful, readable format

## Core Flow

```
URL → Fetch HTML → Parse Content → Clean HTML → Render in Template → Display
```

## Quick Implementation

### Option 1: Client-Side (Browser)

```html
<!DOCTYPE html>
<html>
<head>
  <title>My Read-It-Later App</title>
  <!-- Include Mercury Parser -->
  <script src="https://unpkg.com/@postlight/mercury-parser@2.2.0/dist/mercury.web.js"></script>
  <style>
    body {
      max-width: 40rem;
      margin: 0 auto;
      padding: 2rem;
      font-family: sans-serif;
      line-height: 1.6;
    }
    img {
      max-width: 100%;
      height: auto;
    }
    .table__wrapper {
      overflow-x: auto;
    }
  </style>
</head>
<body>
  <input type="url" id="articleUrl" placeholder="Enter article URL">
  <button onclick="extractArticle()">Extract</button>
  
  <div id="articleContent"></div>

  <script>
    async function extractArticle() {
      const url = document.getElementById('articleUrl').value;
      
      try {
        // Fetch the article HTML (requires CORS proxy for web)
        const response = await fetch(`https://api.allorigins.win/get?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        
        // Parse with Mercury
        const article = await Mercury.parse(url, {
          html: data.contents
        });
        
        // Clean and display
        const cleaned = cleanHtml(article.content);
        
        document.getElementById('articleContent').innerHTML = `
          <h1>${article.title}</h1>
          <p><em>By ${article.author || 'Unknown'}</em></p>
          ${cleaned}
        `;
      } catch (error) {
        console.error('Error:', error);
        alert('Failed to extract article');
      }
    }
    
    function cleanHtml(html) {
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      
      // Remove inline styles
      doc.querySelectorAll('[style]').forEach(el => {
        el.removeAttribute('style');
      });
      
      // Set lazy loading on images
      doc.querySelectorAll('img').forEach((img, i) => {
        if (i === 0) {
          img.setAttribute('fetchpriority', 'high');
        } else {
          img.setAttribute('loading', 'lazy');
        }
      });
      
      // Wrap tables for responsive display
      doc.querySelectorAll('table').forEach(table => {
        const wrapper = doc.createElement('div');
        wrapper.className = 'table__wrapper';
        table.parentNode.insertBefore(wrapper, table);
        wrapper.appendChild(table);
      });
      
      return doc.body.innerHTML;
    }
  </script>
</body>
</html>
```

### Option 2: Server-Side (Node.js + Express)

```javascript
// server.js
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const Mercury = require('@postlight/mercury-parser');

const app = express();
app.use(express.json());

// Article extraction endpoint
app.post('/api/extract', async (req, res) => {
  const { url } = req.body;
  
  try {
    // 1. Fetch HTML
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
      }
    });
    
    // 2. Parse with Mercury
    const article = await Mercury.parse(url, {
      html: response.data
    });
    
    // 3. Clean HTML
    const $ = cheerio.load(article.content);
    
    // Remove styles
    $('[style]').removeAttr('style');
    
    // Process images
    $('img').each((i, img) => {
      $(img).attr('loading', i === 0 ? 'eager' : 'lazy');
    });
    
    // Wrap tables
    $('table').wrap('<div class="table__wrapper"></div>');
    
    // 4. Return cleaned article
    res.json({
      title: article.title,
      author: article.author,
      content: $.html(),
      excerpt: article.excerpt,
      leadImage: article.lead_image_url,
      publishedDate: article.date_published
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000, () => {
  console.log('Server running on http://localhost:3000');
});
```

```javascript
// client.js
async function saveArticle(url) {
  const response = await fetch('/api/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url })
  });
  
  const article = await response.json();
  
  // Save to your database
  await db.articles.insert({
    url: url,
    title: article.title,
    author: article.author,
    content: article.content,
    excerpt: article.excerpt,
    leadImage: article.leadImage,
    savedAt: new Date()
  });
  
  return article;
}
```

### Option 3: Python (Flask/Django)

```python
# app.py
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from readability import Document

app = Flask(__name__)

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'

@app.route('/api/extract', methods=['POST'])
def extract_article():
    url = request.json.get('url')
    
    try:
        # 1. Fetch HTML
        response = requests.get(url, headers={'User-Agent': USER_AGENT})
        response.raise_for_status()
        
        # 2. Extract content
        doc = Document(response.text)
        
        # 3. Clean HTML
        soup = BeautifulSoup(doc.summary(), 'html.parser')
        
        # Remove styles
        for tag in soup.find_all(style=True):
            del tag['style']
        
        # Process images
        for i, img in enumerate(soup.find_all('img')):
            img['loading'] = 'eager' if i == 0 else 'lazy'
        
        # Wrap tables
        for table in soup.find_all('table'):
            wrapper = soup.new_tag('div', **{'class': 'table__wrapper'})
            table.wrap(wrapper)
        
        # 4. Return article
        return jsonify({
            'title': doc.title(),
            'content': str(soup),
            'url': url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Essential CSS

Add this to your stylesheets for proper article display:

```css
/* Article Container */
#article-content {
  max-width: 40rem;
  margin: 0 auto;
  padding: 2rem 1rem;
  font-size: 16px;
  line-height: 1.6;
}

/* Images */
img {
  max-width: 100%;
  height: auto;
  margin: 1rem 0;
  display: block;
}

/* Tables */
.table__wrapper {
  width: 100%;
  overflow-x: auto;
  margin: 1rem 0;
}

.table__wrapper table {
  width: 100%;
  border-collapse: collapse;
}

.table__wrapper td,
.table__wrapper th {
  border: 1px solid #999;
  padding: 0.5rem;
  text-align: left;
}

/* Code blocks */
pre {
  background: #f5f5f5;
  padding: 1rem;
  overflow-x: auto;
  border-radius: 4px;
}

code {
  background: #f5f5f5;
  padding: 0.2em 0.4em;
  border-radius: 3px;
  font-family: monospace;
}

/* Videos */
iframe {
  max-width: 100%;
  border: 0;
}

/* Responsive YouTube embeds */
.video-wrapper {
  position: relative;
  padding-bottom: 56.25%; /* 16:9 */
  height: 0;
}

.video-wrapper iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
```

## Key Features Explained

### 1. Fetch Article HTML

**Why?** RSS feeds often contain truncated content. Fetching the full page ensures you get the complete article.

```javascript
const response = await fetch(url, {
  headers: {
    'User-Agent': 'Mozilla/5.0 ...'  // Pretend to be a browser
  }
});
const html = await response.text();
```

### 2. Parse with Mercury

**Why?** Mercury Parser uses readability algorithms to extract just the article content, removing ads, navigation, etc.

```javascript
const article = await Mercury.parse(url, { html: html });
// Returns: { title, author, content, excerpt, lead_image_url, ... }
```

### 3. Clean HTML

**Why?** Articles from various sources have inconsistent styling. Cleaning ensures a uniform appearance.

```javascript
// Remove inline styles (so your CSS takes over)
element.removeAttribute('style');

// Lazy load images (faster page loads)
img.setAttribute('loading', 'lazy');

// Make tables scrollable (mobile-friendly)
table.wrap('<div class="table__wrapper"></div>');
```

### 4. Template Rendering

**Why?** Provides consistent layout and theming across all articles.

```javascript
const template = `
  <article>
    <h1>${article.title}</h1>
    <p class="byline">${article.author} • ${article.date}</p>
    <div class="content">${article.content}</div>
  </article>
`;
```

## Common Issues & Solutions

### Issue 1: CORS Errors (Browser-Side)

**Problem:** Browsers block cross-origin requests.

**Solution:** Use a CORS proxy or implement server-side fetching.

```javascript
// Use a CORS proxy
const proxyUrl = 'https://api.allorigins.win/get?url=';
const response = await fetch(proxyUrl + encodeURIComponent(articleUrl));
```

### Issue 2: Paywalled Content

**Problem:** Some sites block or paywall content.

**Solution:** Can't bypass legally. Use RSS feed content instead.

### Issue 3: JavaScript-Heavy Sites

**Problem:** Some sites render content with JavaScript.

**Solution:** Use a headless browser (Puppeteer/Playwright) to render the page first.

```javascript
const puppeteer = require('puppeteer');

async function fetchWithBrowser(url) {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: 'networkidle0' });
  const html = await page.content();
  await browser.close();
  return html;
}
```

### Issue 4: Large Images

**Problem:** High-resolution images slow down loading.

**Solution:** Use lazy loading and consider image proxies/CDNs.

```html
<img 
  src="image.jpg" 
  loading="lazy"
  decoding="async"
>
```

## Testing

Test your extraction with these diverse article sources:

1. **News Sites**: CNN, BBC, The Verge
2. **Blogs**: Medium, WordPress blogs
3. **Technical**: Ars Technica, Stack Overflow blogs
4. **Long-form**: The Atlantic, Longreads

Example test:

```javascript
const testUrls = [
  'https://www.theverge.com/2024/1/1/test-article',
  'https://medium.com/@user/test-article',
  'https://wordpress.com/blog/test-article'
];

for (const url of testUrls) {
  try {
    const article = await extractArticle(url);
    console.log(`✓ ${url}: ${article.title}`);
  } catch (error) {
    console.error(`✗ ${url}: ${error.message}`);
  }
}
```

## Next Steps

1. **Add Database Storage**: Save extracted articles to PostgreSQL/MongoDB
2. **Implement Caching**: Cache extracted content to avoid re-fetching
3. **Add Tags/Labels**: Let users organize articles
4. **Enable Search**: Full-text search across saved articles
5. **Offline Support**: Use Service Workers for offline reading
6. **Mobile Apps**: Wrap in React Native/Flutter for mobile

## Resources

- **Mercury Parser**: https://github.com/postlight/mercury-parser
- **Readability**: https://github.com/mozilla/readability
- **Jsoup (Java/Kotlin)**: https://jsoup.org/
- **BeautifulSoup (Python)**: https://www.crummy.com/software/BeautifulSoup/
- **Cheerio (Node.js)**: https://cheerio.js.org/

## Full Stack Example

See `examples/` directory for complete implementations:
- `examples/react-app/` - React SPA with client-side extraction
- `examples/node-express/` - Node.js API server
- `examples/python-flask/` - Python Flask backend
- `examples/chrome-extension/` - Browser extension

---

**Need Help?** Check the full `ARTICLE_EXTRACTION_GUIDE.md` for detailed explanations and advanced topics.
