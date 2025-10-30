# 📰 Article Extraction Documentation

> **Complete documentation and implementation guide for Capy Reader's article extraction system**

This documentation package extracts and explains the article extraction logic from Capy Reader, a smallish RSS reader for Android. It's designed to help you understand and integrate this powerful article extraction system into your own "read it later" web application or any project that needs clean, readable article content.

## 📚 What's Included

### 1. **Comprehensive Architecture Guide** 
[`ARTICLE_EXTRACTION_GUIDE.md`](./ARTICLE_EXTRACTION_GUIDE.md)

A complete technical deep-dive into the article extraction architecture:
- 📐 Architecture diagrams and flow charts
- 🔍 Detailed component explanations
- 💻 Source code walkthroughs
- 🛠️ Integration patterns for different platforms
- 🎯 Best practices and design decisions

**Read this if you want to:**
- Understand the complete architecture
- Learn how each component works
- Implement a custom solution
- Extend or modify the extraction logic

### 2. **Quick Start Guide**
[`QUICK_START_GUIDE.md`](./QUICK_START_GUIDE.md)

A simplified guide to get you up and running quickly:
- ⚡ Minimal code examples
- 🚀 Copy-paste implementations
- 🎯 Common use cases
- 🔧 Troubleshooting tips

**Read this if you want to:**
- Get started immediately
- Integrate quickly into an existing project
- See working code examples
- Learn the essential concepts only

### 3. **Working Examples**
[`examples/`](./examples/)

Three complete, production-ready implementations:

| Example | Language | Framework | Use Case |
|---------|----------|-----------|----------|
| [**Node.js + Express**](./examples/node-express/) | JavaScript | Express | Backend API for web/mobile apps |
| [**Python + Flask**](./examples/python-flask/) | Python | Flask | Backend API for Python projects |
| [**Standalone JavaScript**](./examples/standalone-js/) | JavaScript | Vanilla JS | Browser-based demo/prototype |

Each example includes:
- ✅ Complete, runnable code
- 📖 Detailed README
- 🧪 Testing instructions
- 🚀 Deployment guidance

## 🎯 What Does It Do?

The article extraction system performs these key functions:

```
URL → Fetch HTML → Extract Content → Clean HTML → Render → Beautiful Article
```

### Key Features

1. **Intelligent Content Extraction**
   - Removes ads, navigation, and clutter
   - Preserves article content, images, and formatting
   - Uses Mercury Parser or Defuddle

2. **HTML Cleaning & Processing**
   - Removes inline styles for consistent theming
   - Optimizes image loading (lazy load, priority hints)
   - Makes tables responsive
   - Extracts images from links

3. **Template-Based Rendering**
   - Dynamic variable substitution
   - Customizable fonts, colors, and layout
   - Consistent cross-platform appearance

4. **Robust Error Handling**
   - Network timeouts
   - Invalid content types
   - Missing or malformed HTML
   - Graceful degradation

## 🚀 Quick Start

Choose your path:

### Path 1: Read First, Code Later

1. Start with [`QUICK_START_GUIDE.md`](./QUICK_START_GUIDE.md) for concepts
2. Pick an example from [`examples/`](./examples/) that matches your stack
3. Follow the example's README to get it running
4. Refer to [`ARTICLE_EXTRACTION_GUIDE.md`](./ARTICLE_EXTRACTION_GUIDE.md) for deep dives

### Path 2: Code First, Learn Later

1. Go to [`examples/`](./examples/)
2. Pick the example matching your tech stack
3. Follow the quick start in its README
4. Experiment and modify
5. Read the guides when you need more context

### Path 3: Copy-Paste Solution

1. Open [`QUICK_START_GUIDE.md`](./QUICK_START_GUIDE.md)
2. Find the "Quick Implementation" section
3. Copy the code for your platform
4. Paste into your project
5. Customize as needed

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Article Data Model                        │
│         (title, author, content, url, metadata)              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  ArticleContent                              │
│              Fetches HTML from URL                           │
│  • Custom User-Agent • Timeout handling • Error handling    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               Content Parsers                                │
│         Extract main article content                         │
│  • Mercury Parser (Readability-based)                        │
│  • Defuddle (Alternative algorithm)                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              HtmlPostProcessor                               │
│       Clean and optimize HTML content                        │
│  • Remove styles • Process images • Wrap tables              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              ArticleRenderer                                 │
│       Render with template and styling                       │
│  • Template substitution • Font/color customization          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
                 📱 Beautiful Article
```

## 💡 Use Cases

This extraction system is perfect for:

- 📖 **Read-It-Later Apps** - Save and read articles offline
- 🔖 **RSS Readers** - Display full content from truncated feeds
- 📚 **Content Aggregators** - Collect and display articles
- 🌐 **Browser Extensions** - "Reader mode" functionality
- 📱 **Mobile Apps** - Clean article viewing
- 🤖 **Content Analysis** - Extract text for NLP/ML
- 📰 **News Dashboards** - Curate and display news

## 🛠️ Technology Stack

The original implementation uses:

### Backend (Kotlin/Android)
- **Jsoup** - HTML parsing and manipulation
- **OkHttp** - HTTP client
- **Kotlin Coroutines** - Async operations

### Frontend (JavaScript/WebView)
- **Mercury Parser** - Content extraction (~459KB)
- **Defuddle** - Alternative parser (~100KB)
- **Native JavaScript** - HTML processing

### Easily Ported To
- **Node.js** - Use Cheerio + Mercury Parser
- **Python** - Use BeautifulSoup + Readability
- **Ruby** - Use Nokogiri + Readability
- **PHP** - Use DOMDocument + Readability
- **Go** - Use goquery + go-readability

## 📖 Documentation Structure

```
.
├── README.md (this file)           # Overview and navigation
├── ARTICLE_EXTRACTION_GUIDE.md     # Complete technical guide
├── QUICK_START_GUIDE.md            # Quick implementation guide
└── examples/                       # Working code examples
    ├── README.md                   # Examples overview
    ├── node-express/               # Node.js REST API
    │   ├── server.js
    │   ├── package.json
    │   └── README.md
    ├── python-flask/               # Python REST API
    │   ├── app.py
    │   ├── requirements.txt
    │   └── README.md
    └── standalone-js/              # Browser-based demo
        ├── index.html
        └── README.md
```

## 🔗 API Reference

All examples implement a consistent REST API:

### Extract Article

**Endpoint:** `POST /api/extract`

**Request:**
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
    "content": "<html>cleaned content</html>",
    "excerpt": "Short summary...",
    "leadImage": "https://example.com/image.jpg",
    "publishedDate": "2024-01-01T00:00:00Z",
    "url": "https://example.com/article",
    "domain": "example.com",
    "wordCount": 1234
  }
}
```

## 🧪 Testing

Test the extraction with these diverse article sources:

```bash
# Tech news
https://www.theverge.com/2024/7/11/24195947/sonos-lasso-soundbar

# Technical article
https://arstechnica.com/gadgets/2024/07/three-betas-in-ios-18

# Long-form
https://www.theatlantic.com/magazine/archive/2024/01/article

# Blog post
https://medium.com/@author/article-title
```

## 🤝 Contributing

Found an issue or want to improve the documentation?

1. Check the original [Capy Reader repository](https://github.com/jocmp/capyreader)
2. Open an issue describing the problem
3. Submit a pull request with improvements

## 📄 License

This documentation is derived from [Capy Reader](https://github.com/jocmp/capyreader), which is open source. Please refer to the project's LICENSE file for usage terms.

## 🙏 Credits

This documentation and extraction logic is based on the excellent work in [Capy Reader](https://github.com/jocmp/capyreader) by [jocmp](https://github.com/jocmp).

### Key Components Documented

- **ArticleContent.kt** - HTTP fetching with OkHttp
- **ArticleRenderer.kt** - Template-based rendering
- **HtmlPostProcessor.kt** - HTML cleaning orchestration
- **CleanLinks.kt** - Image processing and extraction
- **CleanStyles.kt** - Style removal
- **WrapTables.kt** - Table responsiveness
- **RemoveImages.kt** - Optional image removal
- **MacroProcessor.kt** - Template variable substitution
- **full-content.js** - JavaScript content parsing
- **media.js** - Video and embed handling
- **mercury-parser.js** - Mercury Parser integration
- **defuddle.js** - Alternative parser

## 🚦 Next Steps

1. **Choose your path** from the Quick Start section above
2. **Run an example** to see it in action
3. **Read the guides** to understand the architecture
4. **Integrate** into your own project
5. **Customize** to match your needs

## 💬 Questions?

- 📖 Check [`ARTICLE_EXTRACTION_GUIDE.md`](./ARTICLE_EXTRACTION_GUIDE.md) for deep dives
- ⚡ Check [`QUICK_START_GUIDE.md`](./QUICK_START_GUIDE.md) for quick answers
- 💻 Check [`examples/`](./examples/) for working code
- 🐛 Open an issue if something's unclear

---

**Ready to extract some articles?** Start with the [Quick Start Guide](./QUICK_START_GUIDE.md) or jump straight to the [examples](./examples/)!
