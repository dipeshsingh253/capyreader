# Standalone JavaScript Article Extractor

A complete, single-page HTML application for extracting and displaying article content. Based on Capy Reader's extraction logic, this demo runs entirely in the browser.

## Features

- Pure client-side implementation (no backend required for demo)
- Uses Mercury Parser for content extraction
- Implements Capy Reader's HTML cleaning logic
- Responsive design
- Clean, readable article display

## Usage

### Local Development

Simply open `index.html` in a web browser:

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx http-server

# Or just open the file directly
open index.html
```

Then navigate to `http://localhost:8000`.

### Try It Out

1. Enter an article URL in the input field
2. Optionally check "Hide Images" to remove all images
3. Click "Extract" to fetch and display the article

### Example URLs

Try these URLs to test the extractor:

- https://www.theverge.com/2024/1/1/example-article
- https://arstechnica.com/gadgets/2024/01/example/
- https://medium.com/@author/article-title

## How It Works

### 1. Fetch Article HTML

The demo uses a CORS proxy (`allorigins.win`) to fetch article HTML:

```javascript
const proxyUrl = `https://api.allorigins.win/get?url=${encodeURIComponent(url)}`;
const response = await fetch(proxyUrl);
const data = await response.json();
```

**Note:** For production, use a backend API instead of a CORS proxy.

### 2. Parse with Mercury

Mercury Parser extracts the main content:

```javascript
const parsed = await Mercury.parse(url, {
  html: data.contents
});
```

### 3. Clean HTML

Apply Capy Reader's cleaning logic:

```javascript
function cleanHtml(htmlString, hideImages = false) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, 'text/html');
  
  // Remove inline styles
  doc.querySelectorAll('[style]').forEach(el => {
    el.removeAttribute('style');
  });
  
  // Process images
  if (hideImages) {
    doc.querySelectorAll('img').forEach(img => img.remove());
  } else {
    doc.querySelectorAll('img').forEach((img, index) => {
      if (index === 0) {
        img.setAttribute('fetchpriority', 'high');
      } else {
        img.setAttribute('loading', 'lazy');
      }
    });
  }
  
  // Wrap tables
  doc.querySelectorAll('table').forEach(table => {
    if (!table.parentElement.classList.contains('table__wrapper')) {
      const wrapper = document.createElement('div');
      wrapper.className = 'table__wrapper';
      table.parentNode.insertBefore(wrapper, table);
      wrapper.appendChild(table);
    }
  });
  
  return doc.body.innerHTML;
}
```

### 4. Display Article

Render the cleaned content:

```javascript
function displayArticle(articleData) {
  article.innerHTML = `
    <div class="article-header">
      <h1 class="article-title">${articleData.title}</h1>
      <div class="article-meta">By ${articleData.author}</div>
    </div>
    <div class="article-content">
      ${articleData.content}
    </div>
  `;
}
```

## Production Implementation

For a production application, replace the CORS proxy with a backend API:

```javascript
async function extractArticle() {
  const response = await fetch('/api/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: articleUrl })
  });
  
  const data = await response.json();
  displayArticle(data.article);
}
```

## Customization

### Change Theme

Edit the CSS in the `<style>` section:

```css
body {
  background: #1e1e1e;  /* Dark background */
  color: #ffffff;       /* Light text */
}

.article {
  background: #2d2d2d;  /* Dark article background */
}
```

### Adjust Article Width

```css
.container {
  max-width: 1000px;  /* Wider container */
}

.article {
  padding: 4rem;  /* More padding */
}
```

### Custom Font

```css
body {
  font-family: 'Georgia', serif;
}

.article-content {
  font-size: 1.25rem;  /* Larger text */
  line-height: 1.8;    /* More spacing */
}
```

## Browser Compatibility

- Chrome/Edge: ✅ Full support
- Firefox: ✅ Full support
- Safari: ✅ Full support
- Mobile browsers: ✅ Full support

Requires:
- ES6 (async/await)
- Fetch API
- DOMParser

## Limitations

1. **CORS Proxy**: The demo uses a public CORS proxy which may be slow or unreliable
2. **Rate Limits**: Public proxies have rate limits
3. **Paywall Content**: Cannot extract content behind paywalls
4. **JavaScript-Heavy Sites**: Some sites require JavaScript execution

## Deployment

### GitHub Pages

1. Push to a GitHub repository
2. Enable GitHub Pages in repository settings
3. Select the branch containing `index.html`
4. Access at `https://username.github.io/repository/`

### Netlify

1. Drag and drop the folder to Netlify
2. Or connect your Git repository
3. Deploy automatically

### Vercel

```bash
npm install -g vercel
vercel
```

## License

MIT

## Credits

Based on the article extraction logic from [Capy Reader](https://github.com/jocmp/capyreader).
