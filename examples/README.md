# Article Extraction Examples

This directory contains complete, working examples of article extraction implementations based on Capy Reader's logic. These examples demonstrate how to integrate the article extraction system into different tech stacks.

## 📁 Available Examples

### 1. Node.js + Express API (`node-express/`)

A production-ready REST API built with Node.js and Express.

**Tech Stack:**
- Node.js
- Express
- Cheerio (HTML manipulation)
- Mercury Parser (content extraction)

**Use Case:** Backend API for web/mobile applications

**Quick Start:**
```bash
cd node-express
npm install
npm start
```

[→ Full Documentation](./node-express/README.md)

---

### 2. Python + Flask API (`python-flask/`)

A REST API implementation using Python and Flask.

**Tech Stack:**
- Python 3.11+
- Flask
- BeautifulSoup4 (HTML manipulation)
- Readability-lxml (content extraction)

**Use Case:** Backend API for Python-based projects

**Quick Start:**
```bash
cd python-flask
pip install -r requirements.txt
python app.py
```

[→ Full Documentation](./python-flask/README.md)

---

### 3. Standalone JavaScript (`standalone-js/`)

A single-page HTML application that runs entirely in the browser.

**Tech Stack:**
- Pure JavaScript (ES6+)
- Mercury Parser
- No build tools required

**Use Case:** Quick demo, browser extension, or client-side prototype

**Quick Start:**
```bash
cd standalone-js
open index.html  # or use a local server
```

[→ Full Documentation](./standalone-js/README.md)

---

## 🚀 Getting Started

Choose the example that best fits your project:

| Example | Best For | Complexity | Setup Time |
|---------|----------|------------|------------|
| Node.js + Express | Production web apps | Medium | ~5 min |
| Python + Flask | Python projects | Medium | ~5 min |
| Standalone JS | Quick demos, prototypes | Low | ~1 min |

## 🔧 Common Features

All examples implement the same core functionality from Capy Reader:

### 1. Article Fetching
- HTTP requests with browser-like User-Agent
- Timeout handling
- Error handling for network issues

### 2. Content Extraction
- Mercury Parser or Readability for main content extraction
- Removes ads, navigation, and other non-content elements
- Preserves semantic HTML structure

### 3. HTML Cleaning
Based on Capy Reader's `HtmlPostProcessor`:

- **Remove Styles** - Strip all inline styles
- **Process Images** - Set lazy loading, optimize first image
- **Extract Images** - Remove images from anchor tags
- **Wrap Tables** - Make tables responsive
- **Optional Image Removal** - Support for hiding images

### 4. REST API Design

All examples expose consistent endpoints:

**POST** `/api/extract`
```json
{
  "url": "https://example.com/article",
  "hideImages": false
}
```

**Response:**
```json
{
  "success": true,
  "article": {
    "title": "Article Title",
    "author": "Author Name",
    "content": "<html>...</html>",
    "excerpt": "Summary...",
    "leadImage": "https://...",
    "publishedDate": "2024-01-01",
    "url": "https://...",
    "domain": "example.com"
  }
}
```

## 📖 Documentation

For detailed information about the article extraction architecture, see:

- [**Full Architecture Guide**](../ARTICLE_EXTRACTION_GUIDE.md) - Complete technical documentation
- [**Quick Start Guide**](../QUICK_START_GUIDE.md) - Simplified integration guide

## 🧪 Testing

### Test URLs

Use these URLs to test the examples:

```bash
# Tech news
https://www.theverge.com/2024/7/11/24195947/sonos-lasso-soundbar-photos-features-leak

# Long-form article
https://arstechnica.com/gadgets/2024/07/three-betas-in-ios-18-testers-still-cant-try-out-apple-intelligence-features/

# Blog post
https://medium.com/@user/example-article
```

### Test with curl

```bash
# Node.js or Python API
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.theverge.com/2024/1/1/example"}'
```

## 🔄 Integration Patterns

### Pattern 1: Save-for-Later Service

```javascript
// User saves an article
POST /api/save-article
{
  "url": "https://example.com/article"
}

// Backend:
1. Extract article with /api/extract
2. Save to database
3. Return article ID

// User reads article
GET /api/articles/:id
```

### Pattern 2: RSS Reader Enhancement

```javascript
// Fetch RSS feed
const feed = await fetchRSS(feedUrl);

// For each article with truncated content:
for (const item of feed.items) {
  if (item.contentSnippet.length < 500) {
    // Extract full content
    const full = await extractArticle(item.link);
    item.content = full.content;
  }
}
```

### Pattern 3: Browser Extension

```javascript
// Content script detects "Save" button click
chrome.runtime.sendMessage({
  action: 'saveArticle',
  url: window.location.href
});

// Background script
chrome.runtime.onMessage.addListener((request) => {
  if (request.action === 'saveArticle') {
    fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      body: JSON.stringify({ url: request.url })
    });
  }
});
```

## 🛠️ Extending the Examples

### Add Database Storage

**Node.js + PostgreSQL:**
```javascript
const { Pool } = require('pg');
const pool = new Pool({ connectionString: process.env.DATABASE_URL });

app.post('/api/save-article', async (req, res) => {
  const article = await extractArticle(req.body.url);
  
  const result = await pool.query(
    'INSERT INTO articles (url, title, content, saved_at) VALUES ($1, $2, $3, NOW()) RETURNING id',
    [article.url, article.title, article.content]
  );
  
  res.json({ id: result.rows[0].id });
});
```

**Python + SQLAlchemy:**
```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500))
    title = db.Column(db.String(500))
    content = db.Column(db.Text)
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/api/save-article', methods=['POST'])
def save():
    article_data = extractor.extract_article(request.json['url'])
    article = Article(**article_data)
    db.session.add(article)
    db.session.commit()
    return jsonify({'id': article.id})
```

### Add Authentication

**JWT Example:**
```javascript
const jwt = require('jsonwebtoken');

function authenticate(req, res, next) {
  const token = req.headers['authorization']?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'No token provided' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.userId = decoded.userId;
    next();
  } catch (err) {
    res.status(401).json({ error: 'Invalid token' });
  }
}

// Protect extraction endpoint
app.post('/api/extract', authenticate, async (req, res) => {
  // ... extraction logic
});
```

### Add Caching

**Redis Example:**
```javascript
const redis = require('redis');
const client = redis.createClient();

app.post('/api/extract', async (req, res) => {
  const { url } = req.body;
  
  // Check cache first
  const cached = await client.get(url);
  if (cached) {
    return res.json(JSON.parse(cached));
  }
  
  // Extract if not cached
  const article = await extractArticle(url);
  
  // Cache for 1 hour
  await client.setEx(url, 3600, JSON.stringify(article));
  
  res.json(article);
});
```

## 🐛 Common Issues

### Issue 1: CORS Errors

**Problem:** Browser blocks cross-origin requests

**Solution:** Use backend API, not client-side fetching

### Issue 2: Paywall Content

**Problem:** Some sites block or paywall content

**Solution:** Cannot bypass legally. Use RSS content instead.

### Issue 3: Large Responses

**Problem:** Some articles are very large

**Solution:** Add response size limits and streaming

```javascript
app.use(express.json({ limit: '10mb' }));
```

### Issue 4: Rate Limiting

**Problem:** Too many requests to source sites

**Solution:** Implement caching and rate limiting

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use('/api/', limiter);
```

## 📊 Performance Tips

1. **Cache Extracted Articles** - Use Redis or in-memory cache
2. **Implement Rate Limiting** - Protect your API from abuse
3. **Use Connection Pooling** - For database connections
4. **Add Timeouts** - Prevent hanging requests
5. **Monitor Memory** - Large HTML pages can use significant memory

## 📝 License

All examples are provided under the MIT License.

## 🙏 Credits

Based on the article extraction logic from [Capy Reader](https://github.com/jocmp/capyreader) by jocmp.

## 💬 Support

For questions or issues:

1. Check the [main documentation](../ARTICLE_EXTRACTION_GUIDE.md)
2. Review the [quick start guide](../QUICK_START_GUIDE.md)
3. Look at example-specific READMEs
4. Open an issue in the Capy Reader repository

---

**Ready to start?** Pick an example and follow its README to get started in minutes!
