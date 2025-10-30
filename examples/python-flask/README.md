# Python Flask Article Extraction API

This is a complete example of an article extraction API built with Python and Flask, based on Capy Reader's article extraction logic.

## Features

- Fetch and extract article content from any URL
- Clean HTML (remove styles, process images, wrap tables)
- Use readability-lxml for content extraction
- RESTful API design
- Error handling and validation

## Installation

### Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Start the server

```bash
python app.py
```

The server will start on `http://localhost:3000`.

### API Endpoints

#### Extract Article

**POST** `/api/extract`

Request body:
```json
{
  "url": "https://example.com/article",
  "hideImages": false
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
    "publishedDate": "2024-01-01",
    "url": "https://example.com/article",
    "domain": "example.com"
  }
}
```

#### Health Check

**GET** `/api/health`

Response:
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T00:00:00.000000"
}
```

## Testing

### Using curl

```bash
curl -X POST http://localhost:3000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.theverge.com/2024/1/1/example-article"}'
```

### Using Python requests

```python
import requests

response = requests.post('http://localhost:3000/api/extract', json={
    'url': 'https://example.com/article',
    'hideImages': False
})

data = response.json()
print(data['article']['title'])
```

## HTML Cleaning Process

The API applies the following cleaning steps (from Capy Reader):

1. **Remove inline styles** - All `style` attributes are removed
2. **Process images** - First image gets high priority, others lazy load
3. **Extract images from links** - Images wrapped in `<a>` tags are unwrapped
4. **Wrap tables** - Tables are wrapped in `.table__wrapper` for responsive display
5. **Optionally remove images** - If `hideImages: true` is passed

## Dependencies

- **Flask** - Web framework
- **flask-cors** - CORS support
- **requests** - HTTP client for fetching articles
- **beautifulsoup4** - HTML parsing and manipulation
- **readability-lxml** - Article content extraction
- **lxml** - XML/HTML parser

## Error Handling

The API handles these error cases:

- **400 Bad Request** - Missing URL or invalid content type
- **408 Timeout** - Request takes too long
- **500 Internal Server Error** - Other errors

## Integration Example

### Save articles to database (SQLAlchemy)

```python
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy(app)

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), unique=True, nullable=False)
    title = db.Column(db.String(500))
    author = db.Column(db.String(200))
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    lead_image = db.Column(db.String(500))
    published_date = db.Column(db.String(100))
    saved_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route('/api/save-article', methods=['POST'])
def save_article():
    data = request.get_json()
    url = data.get('url')
    
    try:
        # Extract article
        article_data = extractor.extract_article(url)
        
        # Save to database
        article = Article(
            url=article_data['url'],
            title=article_data['title'],
            author=article_data['author'],
            content=article_data['content'],
            excerpt=article_data['excerpt'],
            lead_image=article_data['leadImage'],
            published_date=article_data['publishedDate']
        )
        
        db.session.add(article)
        db.session.commit()
        
        return jsonify({'success': True, 'id': article.id})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## Production Deployment

### Using Gunicorn

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:3000 app:app
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 3000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:3000", "app:app"]
```

Build and run:

```bash
docker build -t article-extraction-api .
docker run -p 3000:3000 article-extraction-api
```

## License

MIT

## Credits

Based on the article extraction logic from [Capy Reader](https://github.com/jocmp/capyreader).
