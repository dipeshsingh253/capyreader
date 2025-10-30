# Node.js Express Article Extraction API

This is a complete example of an article extraction API built with Node.js and Express, based on Capy Reader's article extraction logic.

## Features

- Fetch and extract article content from any URL
- Clean HTML (remove styles, process images, wrap tables)
- Use Mercury Parser for content extraction
- RESTful API design
- Error handling and validation

## Installation

```bash
npm install
```

## Usage

### Start the server

```bash
npm start
```

Or with auto-reload during development:

```bash
npm run dev
```

The server will start on `http://localhost:3000`.

### API Endpoints

#### Extract Article

**POST** `/api/extract`

Request body:
```json
{
  "url": "https://example.com/article",
  "hideImages": false,
  "parser": "mercury"
}
```

Response:
```json
{
  "success": true,
  "article": {
    "title": "Article Title",
    "author": "Author Name",
    "content": "<html>cleaned article content</html>",
    "excerpt": "Article excerpt...",
    "leadImage": "https://example.com/image.jpg",
    "publishedDate": "2024-01-01T00:00:00.000Z",
    "url": "https://example.com/article",
    "domain": "example.com",
    "wordCount": 1234
  }
}
```

#### Health Check

**GET** `/api/health`

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000Z"
}
```

## Testing

### Using curl

```bash
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.theverge.com/2024/1/1/example-article"}'
```

### Using JavaScript fetch

```javascript
const response = await fetch('http://localhost:3000/api/extract', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'https://example.com/article',
    hideImages: false
  })
});

const data = await response.json();
console.log(data.article.title);
```

## HTML Cleaning Process

The API applies the following cleaning steps (from Capy Reader):

1. **Remove inline styles** - All `style` attributes are removed
2. **Process images** - First image gets high priority, others lazy load
3. **Extract images from links** - Images wrapped in `<a>` tags are unwrapped
4. **Wrap tables** - Tables are wrapped in `.table__wrapper` for responsive display
5. **Optionally remove images** - If `hideImages: true` is passed

## Environment Variables

- `PORT` - Server port (default: 3000)

## Dependencies

- **express** - Web framework
- **axios** - HTTP client for fetching articles
- **cheerio** - HTML parsing and manipulation
- **@postlight/mercury-parser** - Article content extraction
- **cors** - CORS middleware

## Error Handling

The API handles these error cases:

- **400 Bad Request** - Missing URL or invalid content type
- **404 Not Found** - URL is unreachable
- **408 Timeout** - Request takes too long
- **500 Internal Server Error** - Other errors

## Integration Example

### Save articles to database

```javascript
const express = require('express');
const app = require('./server');
const db = require('./database'); // Your database module

app.post('/api/save-article', async (req, res) => {
  const { url } = req.body;
  
  try {
    // Extract article
    const extractResponse = await fetch('http://localhost:3000/api/extract', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    
    const { article } = await extractResponse.json();
    
    // Save to database
    const saved = await db.articles.insert({
      url: article.url,
      title: article.title,
      author: article.author,
      content: article.content,
      excerpt: article.excerpt,
      leadImage: article.leadImage,
      publishedDate: article.publishedDate,
      savedAt: new Date()
    });
    
    res.json({ success: true, id: saved.id });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});
```

## License

MIT

## Credits

Based on the article extraction logic from [Capy Reader](https://github.com/jocmp/capyreader).
