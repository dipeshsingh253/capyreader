# Article Extraction Architecture Guide

This guide provides a comprehensive overview of the article extraction and rendering system used in Capy Reader. This documentation is designed to help you understand and integrate this logic into your own "read it later" web application.

## Table of Contents

1. [Overview](#overview)
2. [Architecture Components](#architecture-components)
3. [Article Extraction Flow](#article-extraction-flow)
4. [Core Components](#core-components)
5. [HTML Processing Pipeline](#html-processing-pipeline)
6. [JavaScript Integration](#javascript-integration)
7. [Usage Examples](#usage-examples)
8. [Integration Guide](#integration-guide)

---

## Overview

The article extraction system in Capy Reader is designed to fetch, parse, and render web articles in a clean, readable format. The system consists of several key components:

1. **ArticleContent** - Fetches raw HTML from article URLs
2. **ArticleRenderer** - Renders articles using a template system
3. **HtmlPostProcessor** - Cleans and processes HTML content
4. **JavaScript Parsers** - Mercury Parser and Defuddle for content extraction
5. **Template System** - MacroProcessor for dynamic content substitution

## Architecture Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Article Data Model                        │
│  (id, title, author, contentHTML, url, summary, etc.)       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   ArticleContent                             │
│         Fetches HTML content from URL                        │
│    • HTTP client with custom User-Agent                      │
│    • Error handling for network issues                       │
│    • Validates response (HTML content type)                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  ArticleRenderer                             │
│       Combines template + article data                       │
│    • Loads HTML template                                     │
│    • Substitutes variables using MacroProcessor              │
│    • Applies font/size/color preferences                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│               HtmlPostProcessor                              │
│          Cleans and processes HTML                           │
│    • CleanStyles - Removes inline styles                     │
│    • RemoveImages - Optionally removes images                │
│    • CleanLinks - Processes image lazy loading               │
│    • WrapTables - Wraps tables for responsiveness            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│             JavaScript Parsers                               │
│   Extract main content from full HTML                        │
│    • Mercury Parser - Readability-based extraction           │
│    • Defuddle - Alternative parser                           │
│    • Full-content.js - Orchestrates parsing                  │
└─────────────────────────────────────────────────────────────┘
```

## Article Extraction Flow

### 1. Data Model

The `Article` data class represents an article with all its metadata:

```kotlin
data class Article(
    val id: String,
    val feedID: String,
    val title: String,
    val author: String?,
    val contentHTML: String,        // Raw HTML from RSS feed
    val url: URL?,                  // Article URL
    val summary: String,            // Text summary
    val imageURL: String?,          // Lead image
    val updatedAt: ZonedDateTime,
    val publishedAt: ZonedDateTime,
    val read: Boolean,
    val starred: Boolean,
    val feedName: String = "",
    val faviconURL: String? = null,
    val feedURL: String? = null,
    val siteURL: String? = null,
    val enableStickyFullContent: Boolean = false,
    val openInBrowser: Boolean = false,
    val fullContent: FullContentState = FullContentState.NONE,
    val content: String = contentHTML.ifBlank { summary },
    val enclosures: List<Enclosure> = emptyList(),
)
```

**Key Properties:**
- `contentHTML`: The HTML content from the RSS feed (may be truncated)
- `content`: Either contentHTML or summary - the content to display
- `fullContent`: State indicating if full content should be fetched
- `url`: URL to fetch full article content if needed
- `enclosures`: Media attachments (images, videos, etc.)

### 2. Fetching Article Content

The `ArticleContent` class fetches the full HTML page from an article URL:

```kotlin
class ArticleContent(client: OkHttpClient) {
    private val httpClient = client.newBuilder()
        .addInterceptor(UserAgentInterceptor(USER_AGENT))
        .build()

    suspend fun fetch(url: URL?): Result<String> {
        url ?: return Result.failure(MissingURLError())
        
        val request = Request.Builder()
            .url(url)
            .get()
            .build()
        
        return try {
            val response = httpClient.newCall(request).await()
            val body = getBodyOrNull(response)
            
            if (body == null) {
                Result.failure(MissingBodyError(response.code.toString()))
            } else {
                Result.success(body)
            }
        } catch (e: IOException) {
            Result.failure(e)
        }
    }

    companion object {
        const val USER_AGENT = 
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) " +
            "Chrome/137.0.0.0 Safari/537.36"
    }
}
```

**Key Features:**
- Uses a browser-like User-Agent to avoid blocks
- Validates response is HTML content type
- Returns `Result<String>` for error handling
- Asynchronous using Kotlin coroutines

### 3. Rendering Articles

The `ArticleRenderer` class orchestrates the rendering process:

```kotlin
class ArticleRenderer(
    private val context: Context,
    private val textSize: Preference<Int>,
    private val fontOption: Preference<FontOption>,
    private val hideTopMargin: Preference<Boolean>,
    private val enableHorizontalScroll: Preference<Boolean>,
    private val parser: Preference<FullContentParserType>,
) {
    private val template by lazy {
        context.resources.openRawResource(R.raw.template)
            .bufferedReader()
            .readText()
    }

    fun render(
        article: Article,
        byline: String,
        colors: Map<String, String>,
        hideImages: Boolean,
    ): String {
        // 1. Prepare substitution variables
        val substitutions = colors + mapOf(
            "external_link" to article.externalLink(),
            "title" to title,
            "byline" to byline,
            "feed_name" to feedName,
            "font_size" to "${textSize.get()}px",
            "font_family" to fontFamily.slug,
            "font_preload" to fontPreload(fontFamily),
            "top_margin" to topMargin(),
            "pre_white_space" to preWhiteSpace(),
        )

        // 2. Apply template substitution
        val html = MacroProcessor(
            template = template,
            substitutions = substitutions
        ).renderedText

        // 3. Parse as Jsoup Document
        val document = Jsoup.parse(html)

        // 4. Handle full content parsing or regular content
        if (article.parseFullContent) {
            // Full content mode - use JavaScript parser
            val contentHTML = Jsoup.parse(article.content)
            document.setBaseUri(baseUri)
            HtmlPostProcessor.clean(contentHTML, hideImages)
            document.content?.append(
                parseHtml(article, contentHTML, hideImages, parser.get())
            )
        } else {
            // Regular mode - use RSS content directly
            article.imageEnclosures()?.let {
                document.content?.appendChild(it)
            }
            document.content?.append(article.content)
            HtmlPostProcessor.clean(document, hideImages)
        }

        return document.html()
    }
}
```

## Core Components

### MacroProcessor

The `MacroProcessor` performs template variable substitution:

```kotlin
data class MacroProcessor(
    val template: String,
    val substitutions: Map<String, String>,
    val openTag: String = "{{",
    val closeTag: String = "}}",
) {
    val renderedText: String by lazy { process() }
}
```

**How it works:**
1. Scans template for `{{variable_name}}` patterns
2. Replaces with values from `substitutions` map
3. Handles nested and malformed tags gracefully

**Example:**
```kotlin
val template = """
    <h1>{{title}}</h1>
    <div style="font-size: {{font_size}}">{{content}}</div>
"""

val processor = MacroProcessor(
    template = template,
    substitutions = mapOf(
        "title" to "My Article",
        "font_size" to "16px",
        "content" to "<p>Article content here</p>"
    )
)

val result = processor.renderedText
// Output:
// <h1>My Article</h1>
// <div style="font-size: 16px"><p>Article content here</p></div>
```

### Article Data Extensions

**Image Enclosures:**
```kotlin
fun Article.imageEnclosures(): Element? {
    val images = enclosures.filter { it.type.startsWith("image/") }
    
    if (images.isEmpty()) return null
    
    return Element("div").apply {
        enclosures.forEach { enclosure ->
            val image = Element("img").apply {
                attr("src", enclosure.url.toString())
            }
            appendChild(image)
        }
    }
}
```

## HTML Processing Pipeline

### HtmlPostProcessor

The main orchestrator for HTML cleaning:

```kotlin
object HtmlPostProcessor {
    fun clean(document: Document, hideImages: Boolean) {
        cleanStyles(document)
        if (hideImages) {
            removeImages(document)
        }
        cleanLinks(document)
        wrapTables(document)
    }
}
```

### 1. CleanStyles

Removes inline styles to ensure consistent appearance:

```kotlin
fun cleanStyles(document: Document) {
    document.select("#article-body-content *").forEach {
        it.removeAttr("style")
    }
}
```

**Why?** RSS feeds often include inline styles that conflict with your app's theme.

### 2. RemoveImages

Optionally removes all images (for data saving or privacy):

```kotlin
fun removeImages(document: Document) {
    document.select("img").forEach {
        it.remove()
    }
}
```

### 3. CleanLinks

Processes images for optimal loading:

```kotlin
fun cleanLinks(element: Element) {
    // Set loading priority
    element.getElementsByTag("img").forEachIndexed { index, child ->
        if (index == 0) {
            child.attr("fetchpriority", "high")  // First image loads immediately
        } else {
            child.attr("loading", "lazy")        // Others lazy load
        }
        
        // Convert relative URLs to absolute
        child.attr("src", child.attr("abs:src"))
    }
    
    // Handle lazy-loaded images
    element.select("img[data-src]").forEach { child ->
        child.attr("src", child.attr("data-src"))
    }
    
    // Extract images from anchor tags
    extractChildImages(element)
}

private fun extractChildImages(document: Element) {
    try {
        document.select("a img").forEach {
            attachImageToAnchorParent(it, it.parent())
        }
    } catch (e: StackOverflowError) {
        return
    }
}

private fun attachImageToAnchorParent(img: Element, parent: Element?) {
    if (parent == null || parent.tagName() == "body") {
        return
    } else if (parent.tagName() == "a") {
        // Move image out of anchor tag
        parent.parent()?.apply { appendChild(img) }
        parent.remove()
    } else {
        attachImageToAnchorParent(img, parent.parent())
    }
}
```

**Why extract images from anchors?** Many RSS feeds wrap images in links, which prevents click-to-zoom functionality.

### 4. WrapTables

Makes tables responsive by wrapping them:

```kotlin
fun wrapTables(document: Document) {
    document.select("table").forEach { table ->
        val wrapper = document.createElement("div")
        wrapper.addClass("table__wrapper")
        table.wrap(wrapper.outerHtml())
    }
}
```

**CSS for wrapper:**
```css
.table__wrapper {
    width: 100%;
    overflow-x: auto;
}

.table__wrapper table {
    table-layout: fixed;
    width: 100%;
    border-spacing: 0;
}
```

## JavaScript Integration

### Full Content Parsing

The system uses JavaScript parsers to extract the main content from full HTML pages:

#### 1. ParseHTML Function

Generates JavaScript to parse content client-side:

```kotlin
fun parseHtml(
    article: Article,
    document: Document,
    hideImages: Boolean,
    fullContentParser: FullContentParserType
): String {
    val html = document.html()
    
    return """
      <script>
        (async () => {
          const input = ${JSONObject(mapOf(
              "url" to article.url?.toString(),
              "html" to html,
              "hideImages" to hideImages,
              "parserType" to fullContentParser.toString(),
          ))};

          displayFullContent(input);
        })();
      </script>
    """.trimIndent()
}
```

#### 2. Full-Content.js

The JavaScript that runs in the WebView:

```javascript
/**
 * @param {Object} article
 * @param {string} article.html - Full HTML page
 * @param {string | null} article.url - Article URL
 * @param {boolean} article.hideImages - Whether to hide images
 * @param {string} article.parserType - Parser to use (MERCURY_PARSER or DEFUDDLE)
 */
async function displayFullContent(article) {
  const { hideImages } = article;

  try {
    // Parse using selected parser
    const result = await parseWithParser(article);
    
    // Create container for extracted content
    const extracted = document.createElement("div");
    extracted.id = "article-body-content";
    extracted.innerHTML = result.content;

    // Clean embedded content
    cleanEmbeds(extracted);

    // Add lead image if not already present
    const shouldAddImage =
      result.image &&
      !hideImages &&
      !extracted.querySelectorAll("img:not(iframe img):not(.iframe-embed img)")
        .length;

    if (shouldAddImage) {
      const leadImage = document.createElement("img");
      leadImage.src = result.image;
      extracted.prepend(leadImage);
    }

    // Replace placeholder with extracted content
    const content = document.getElementById("article-body-content");
    content.replaceWith(extracted);
  } catch (e) {
    console.error(e);
  }
}

/**
 * Parse content using specified parser
 */
async function parseWithParser(article) {
  if (article.parserType === "DEFUDDLE") {
    const parser = new DOMParser();
    const doc = parser.parseFromString(article.html, 'text/html');

    const defuddle = new Defuddle(doc, {
      url: article.url,
      debug: true,
      markdown: false,
    });

    return defuddle.parse();
  }

  // Default to Mercury Parser
  const result = await Mercury.parse(article.url, { html: article.html });

  return {
    image: result.lead_image_url,
    content: result.content,
  };
}
```

#### 3. Parser Options

**Mercury Parser:**
- Industry-standard readability-based extraction
- Works with most article layouts
- Minified size: ~459KB

**Defuddle:**
- Alternative parser
- Different heuristics for content extraction
- Size: ~100KB

### Media Handling

The `media.js` file handles video and embed processing:

```javascript
// Configure video tags for proper playback
function configureVideoTags() {
  [...document.getElementsByTagName("video")].forEach((v) => {
    v.setAttribute("preload", "auto");
    v.setAttribute("playsinline", "true");
    v.setAttribute("controls", "true");
    v.setAttribute("controlslist", "nofullscreen nodownload noremoteplayback");

    if (v.classList.contains("article__video-autoplay--looped")) {
      v.setAttribute("loop", "true");
      v.play();
    }
  });
}

// Replace YouTube iframes with placeholder images
function cleanEmbeds(element = document) {
  const embeds = element.querySelectorAll("iframe");

  for (const embed of embeds) {
    const src = embed.getAttribute("src");
    if (!src) continue;

    const youtubeID = findYouTubeMatch(src);

    if (youtubeID !== null) {
      swapPlaceholder(embed, src, youtubeID);
    }
  }
}

// Replace iframe with clickable placeholder
function swapPlaceholder(embed, src, youtubeID) {
  const placeholderImage = document.createElement("img");
  placeholderImage.classList.add("iframe-embed__image");
  placeholderImage.setAttribute("src", imageURL(youtubeID));

  const playButton = document.createElement("div");
  playButton.classList.add("iframe-embed__play-button");

  const placeholder = document.createElement("div");
  placeholder.classList.add("iframe-embed");
  placeholder.setAttribute("data-iframe-src", autoplaySrc(src));
  placeholder.appendChild(placeholderImage);
  placeholder.appendChild(playButton);

  embed.replaceWith(placeholder);
}
```

**Why?** Replacing iframes with placeholders:
- Improves page load performance
- Reduces data usage
- User explicitly opts-in to loading videos

## HTML Template

The base template (`template.html`):

```html
<!DOCTYPE html>
<html dir="auto">
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta http-equiv="Content-Security-Policy" 
          content="upgrade-insecure-requests" />
    
    <style>
      :root {
        --color-primary: {{color_primary}};
        --color-surface: {{color_surface}};
        --color-on-surface: {{color_on_surface}};
        --article-top-margin: {{top_margin}};
        --article-font-size: {{font_size}};
        --pre-white-space: {{pre_white_space}};
      }
    </style>
    
    {{font_preload}}
    
    <link rel="stylesheet" 
          href="https://appassets.androidplatform.net/assets/stylesheet.css">
    <script src="https://appassets.androidplatform.net/assets/media.js"></script>
    <script src="https://appassets.androidplatform.net/assets/mercury-parser.js"></script>
    <script src="https://appassets.androidplatform.net/assets/defuddle.js"></script>
    <script src="https://appassets.androidplatform.net/assets/full-content.js"></script>
  </head>
  
  <body>
    <article role="main">
      <header>
        <a class="article__header" href="{{external_link}}">
          <h1 class="article__title">{{title}}</h1>
          <div>{{byline}}</div>
          <div>{{feed_name}}</div>
        </a>
      </header>
      
      <div class="article__body article__body--font-{{font_family}}">
        <div id="article-body-content"></div>
      </div>
    </article>
  </body>
</html>
```

## Usage Examples

### Example 1: Basic Article Rendering

```kotlin
// Setup
val client = OkHttpClient()
val articleContent = ArticleContent(client)
val renderer = ArticleRenderer(
    context = context,
    textSize = Preference(16),
    fontOption = Preference(FontOption.SYSTEM_DEFAULT),
    hideTopMargin = Preference(false),
    enableHorizontalScroll = Preference(true),
    parser = Preference(FullContentParserType.MERCURY_PARSER)
)

// Render article
val article = Article(
    id = "123",
    feedID = "456",
    title = "My Article",
    author = "John Doe",
    contentHTML = "<p>Article content...</p>",
    url = URL("https://example.com/article"),
    summary = "Summary text",
    imageURL = null,
    updatedAt = ZonedDateTime.now(),
    publishedAt = ZonedDateTime.now(),
    read = false,
    starred = false
)

val colors = mapOf(
    "color_primary" to "#6200EE",
    "color_surface" to "#FFFFFF",
    "color_on_surface" to "#000000"
)

val html = renderer.render(
    article = article,
    byline = "By John Doe • 2 hours ago",
    colors = colors,
    hideImages = false
)

// Display in WebView
webView.loadDataWithBaseURL(
    "https://appassets.androidplatform.net",
    html,
    "text/html",
    "UTF-8",
    null
)
```

### Example 2: Fetching Full Content

```kotlin
suspend fun fetchAndRenderFullContent(article: Article): String {
    // Fetch full HTML
    val htmlResult = articleContent.fetch(article.url)
    
    if (htmlResult.isFailure) {
        // Handle error - use RSS content instead
        return renderer.render(
            article = article,
            byline = formatByline(article),
            colors = getThemeColors(),
            hideImages = false
        )
    }
    
    // Update article with full content
    val updatedArticle = article.copy(
        content = htmlResult.getOrThrow(),
        fullContent = Article.FullContentState.LOADED
    )
    
    // Render with full content parsing
    return renderer.render(
        article = updatedArticle,
        byline = formatByline(updatedArticle),
        colors = getThemeColors(),
        hideImages = false
    )
}
```

### Example 3: HTML Post-Processing Only

```kotlin
// If you already have HTML and just want to clean it
val htmlString = "<div>...</div>"
val document = Jsoup.parse(htmlString)

HtmlPostProcessor.clean(
    document = document,
    hideImages = false
)

val cleanedHtml = document.html()
```

## Integration Guide

### For Web Applications

To integrate this logic into a web application:

#### 1. HTTP Fetching

Use `fetch()` or `axios` to get article HTML:

```javascript
async function fetchArticleContent(url) {
  const response = await fetch(url, {
    headers: {
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' +
                    'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                    'Chrome/137.0.0.0 Safari/537.36'
    }
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const contentType = response.headers.get('content-type');
  if (!contentType || !contentType.includes('text/html')) {
    throw new Error('Response is not HTML');
  }
  
  return await response.text();
}
```

#### 2. Template Substitution

Simple JavaScript implementation of MacroProcessor:

```javascript
function processTemplate(template, substitutions) {
  let result = template;
  
  for (const [key, value] of Object.entries(substitutions)) {
    const pattern = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
    result = result.replace(pattern, value);
  }
  
  return result;
}

// Usage
const template = `
  <h1>{{title}}</h1>
  <div style="font-size: {{font_size}}">{{content}}</div>
`;

const html = processTemplate(template, {
  title: 'My Article',
  font_size: '16px',
  content: '<p>Article content</p>'
});
```

#### 3. HTML Cleaning

Use a library like `cheerio` (Node.js) or `DOMParser` (browser):

```javascript
// Browser-based
function cleanHtml(htmlString, hideImages = false) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(htmlString, 'text/html');
  
  // Remove styles
  doc.querySelectorAll('[style]').forEach(el => {
    el.removeAttribute('style');
  });
  
  // Remove images if requested
  if (hideImages) {
    doc.querySelectorAll('img').forEach(img => img.remove());
  }
  
  // Process image loading
  doc.querySelectorAll('img').forEach((img, index) => {
    if (index === 0) {
      img.setAttribute('fetchpriority', 'high');
    } else {
      img.setAttribute('loading', 'lazy');
    }
    
    // Convert to absolute URLs
    if (img.src) {
      img.setAttribute('src', img.src); // Already absolute from .src property
    }
  });
  
  // Wrap tables
  doc.querySelectorAll('table').forEach(table => {
    const wrapper = doc.createElement('div');
    wrapper.className = 'table__wrapper';
    table.parentNode.insertBefore(wrapper, table);
    wrapper.appendChild(table);
  });
  
  return doc.body.innerHTML;
}
```

#### 4. Content Extraction

Include Mercury Parser or Defuddle:

```html
<script src="https://unpkg.com/@postlight/mercury-parser@2.2.0/dist/mercury.web.js"></script>

<script>
async function extractArticleContent(url, html) {
  try {
    const result = await Mercury.parse(url, { html: html });
    
    return {
      title: result.title,
      author: result.author,
      content: result.content,
      excerpt: result.excerpt,
      leadImage: result.lead_image_url,
      publishedDate: result.date_published
    };
  } catch (error) {
    console.error('Failed to parse article:', error);
    return null;
  }
}
</script>
```

### Backend Implementation (Node.js)

```javascript
const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const Mercury = require('@postlight/mercury-parser');

const app = express();

app.post('/api/extract-article', async (req, res) => {
  const { url } = req.body;
  
  try {
    // 1. Fetch HTML
    const response = await axios.get(url, {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ' +
                      'AppleWebKit/537.36 (KHTML, like Gecko) ' +
                      'Chrome/137.0.0.0 Safari/537.36'
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
    
    // Set image loading
    $('img').each((i, img) => {
      if (i === 0) {
        $(img).attr('fetchpriority', 'high');
      } else {
        $(img).attr('loading', 'lazy');
      }
    });
    
    // Wrap tables
    $('table').each((i, table) => {
      $(table).wrap('<div class="table__wrapper"></div>');
    });
    
    // 4. Return processed article
    res.json({
      title: article.title,
      author: article.author,
      content: $.html(),
      excerpt: article.excerpt,
      leadImage: article.lead_image_url,
      publishedDate: article.date_published,
      url: url
    });
    
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.listen(3000);
```

### Python Implementation

```python
import requests
from bs4 import BeautifulSoup
from mercury_parser import ParserAPI
import json

class ArticleExtractor:
    USER_AGENT = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
    
    def fetch_html(self, url):
        """Fetch HTML content from URL"""
        response = requests.get(
            url,
            headers={'User-Agent': self.USER_AGENT}
        )
        response.raise_for_status()
        
        if 'text/html' not in response.headers.get('Content-Type', ''):
            raise ValueError('Response is not HTML')
        
        return response.text
    
    def clean_html(self, html, hide_images=False):
        """Clean and process HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove styles
        for tag in soup.find_all(style=True):
            del tag['style']
        
        # Remove images if requested
        if hide_images:
            for img in soup.find_all('img'):
                img.decompose()
        else:
            # Process image loading
            for i, img in enumerate(soup.find_all('img')):
                if i == 0:
                    img['fetchpriority'] = 'high'
                else:
                    img['loading'] = 'lazy'
        
        # Wrap tables
        for table in soup.find_all('table'):
            wrapper = soup.new_tag('div', **{'class': 'table__wrapper'})
            table.wrap(wrapper)
        
        return str(soup)
    
    def extract_article(self, url):
        """Extract article content"""
        # Fetch HTML
        html = self.fetch_html(url)
        
        # Parse with Mercury (requires Mercury Parser API or local parser)
        # For Python, you might use readability-lxml or newspaper3k
        from readability import Document
        
        doc = Document(html)
        
        return {
            'title': doc.title(),
            'content': self.clean_html(doc.summary()),
            'url': url
        }

# Usage
extractor = ArticleExtractor()
article = extractor.extract_article('https://example.com/article')
print(article['title'])
```

## Key Takeaways

1. **Separation of Concerns**: The architecture separates fetching, parsing, cleaning, and rendering
2. **Error Handling**: Use Result types or try/catch for robust error handling
3. **User-Agent**: Always use a browser-like User-Agent to avoid blocks
4. **Progressive Enhancement**: Start with RSS content, fetch full content only when needed
5. **Performance**: Lazy load images, replace embeds with placeholders
6. **Accessibility**: Maintain semantic HTML structure
7. **Theming**: Use CSS variables for consistent theming
8. **Security**: Use Content Security Policy, sanitize HTML

## Dependencies

### Android/Kotlin (Original Implementation)
- **Jsoup**: HTML parsing and manipulation
- **OkHttp**: HTTP client
- **Kotlin Coroutines**: Async/await
- **Mercury Parser**: Content extraction (JavaScript)
- **Defuddle**: Alternative parser (JavaScript)

### Web/JavaScript Alternative
- **Mercury Parser** or **Readability**: Content extraction
- **DOMParser** or **Cheerio**: HTML manipulation
- **Fetch API** or **Axios**: HTTP requests

### Python Alternative
- **BeautifulSoup4**: HTML manipulation
- **Requests**: HTTP client
- **readability-lxml** or **newspaper3k**: Content extraction

---

## License

This extraction logic is part of Capy Reader, which is open source. Please refer to the project's LICENSE file for usage terms.

## Contributing

If you improve this extraction logic or add support for more websites, consider contributing back to the Capy Reader project!

---

**Last Updated**: 2025-10-30
**Capy Reader Version**: Based on commit ca8906b
