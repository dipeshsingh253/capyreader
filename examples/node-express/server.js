const express = require('express');
const axios = require('axios');
const cheerio = require('cheerio');
const Mercury = require('@postlight/mercury-parser');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());
app.use(cors());

// User-Agent to use when fetching articles
const USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36';

/**
 * Clean and process HTML content
 * Based on Capy Reader's HtmlPostProcessor
 */
function cleanHtml(htmlContent, options = {}) {
  const { hideImages = false } = options;
  const $ = cheerio.load(htmlContent);
  
  // 1. Remove inline styles
  $('[style]').removeAttr('style');
  
  // 2. Remove images if requested
  if (hideImages) {
    $('img').remove();
  } else {
    // 3. Process images for optimal loading
    $('img').each((index, img) => {
      const $img = $(img);
      
      // Set loading priority
      if (index === 0) {
        $img.attr('fetchpriority', 'high');
      } else {
        $img.attr('loading', 'lazy');
      }
      
      // Handle data-src (lazy loaded images)
      const dataSrc = $img.attr('data-src');
      if (dataSrc) {
        $img.attr('src', dataSrc);
      }
    });
    
    // 4. Extract images from anchor tags
    $('a img').each((_, img) => {
      const $img = $(img);
      const $anchor = $img.parent('a');
      
      if ($anchor.length) {
        // Move image out of anchor
        $anchor.parent().append($img);
        $anchor.remove();
      }
    });
  }
  
  // 5. Wrap tables for responsive display
  $('table').each((_, table) => {
    const $table = $(table);
    if (!$table.parent().hasClass('table__wrapper')) {
      $table.wrap('<div class="table__wrapper"></div>');
    }
  });
  
  return $.html();
}

/**
 * POST /api/extract
 * Extract and clean article content from a URL
 */
app.post('/api/extract', async (req, res) => {
  const { url, hideImages = false, parser = 'mercury' } = req.body;
  
  if (!url) {
    return res.status(400).json({ error: 'URL is required' });
  }
  
  try {
    console.log(`Extracting article from: ${url}`);
    
    // 1. Fetch HTML content
    const response = await axios.get(url, {
      headers: { 'User-Agent': USER_AGENT },
      timeout: 10000, // 10 second timeout
    });
    
    // Validate content type
    const contentType = response.headers['content-type'] || '';
    if (!contentType.includes('text/html')) {
      return res.status(400).json({
        error: 'Invalid content type',
        contentType: contentType
      });
    }
    
    // 2. Parse with Mercury
    const article = await Mercury.parse(url, {
      html: response.data,
    });
    
    if (!article) {
      return res.status(500).json({
        error: 'Failed to parse article'
      });
    }
    
    // 3. Clean the HTML content
    const cleanedContent = cleanHtml(article.content, { hideImages });
    
    // 4. Return the extracted and cleaned article
    res.json({
      success: true,
      article: {
        title: article.title,
        author: article.author,
        content: cleanedContent,
        excerpt: article.excerpt,
        leadImage: article.lead_image_url,
        publishedDate: article.date_published,
        url: article.url,
        domain: article.domain,
        wordCount: article.word_count,
      }
    });
    
  } catch (error) {
    console.error('Error extracting article:', error.message);
    
    if (error.code === 'ENOTFOUND') {
      return res.status(404).json({
        error: 'URL not found or unreachable'
      });
    }
    
    if (error.code === 'ETIMEDOUT') {
      return res.status(408).json({
        error: 'Request timeout'
      });
    }
    
    res.status(500).json({
      error: 'Failed to extract article',
      message: error.message
    });
  }
});

/**
 * GET /api/health
 * Health check endpoint
 */
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString()
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Article extraction API running on port ${PORT}`);
  console.log(`Try: POST http://localhost:${PORT}/api/extract`);
  console.log(`Body: { "url": "https://example.com/article" }`);
});

module.exports = app;
