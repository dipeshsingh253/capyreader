# Article Extraction Architecture Diagrams

This document contains visual diagrams explaining the article extraction architecture using Mermaid syntax. These diagrams are rendered automatically on GitHub and many Markdown viewers.

## 1. High-Level System Flow

```mermaid
flowchart TD
    A[Article URL] --> B[ArticleContent]
    B -->|Fetch HTML| C[HTTP Client]
    C -->|Raw HTML| D{Full Content?}
    D -->|Yes| E[Mercury/Defuddle Parser]
    D -->|No| F[Use RSS Content]
    E -->|Extracted Content| G[HtmlPostProcessor]
    F -->|RSS Content| G
    G -->|Cleaned HTML| H[ArticleRenderer]
    H -->|Apply Template| I[MacroProcessor]
    I -->|Final HTML| J[Display Article]
    
    style A fill:#e1f5ff
    style J fill:#c8e6c9
    style E fill:#fff9c4
    style G fill:#fff9c4
    style H fill:#fff9c4
```

## 2. ArticleContent Flow

```mermaid
sequenceDiagram
    participant Client
    participant ArticleContent
    participant OkHttp
    participant WebServer
    
    Client->>ArticleContent: fetch(url)
    ArticleContent->>OkHttp: GET request
    Note over OkHttp: User-Agent: Mozilla/5.0...
    OkHttp->>WebServer: HTTP GET
    WebServer-->>OkHttp: HTML Response
    OkHttp-->>ArticleContent: Response
    
    alt Success & HTML
        ArticleContent-->>Client: Result.success(html)
    else Timeout
        ArticleContent-->>Client: Result.failure(Timeout)
    else Non-HTML
        ArticleContent-->>Client: Result.failure(InvalidType)
    else Error
        ArticleContent-->>Client: Result.failure(Exception)
    end
```

## 3. HTML Processing Pipeline

```mermaid
flowchart LR
    A[Raw HTML] --> B[Parse with Jsoup]
    B --> C[HtmlPostProcessor]
    C --> D[CleanStyles]
    D --> E{Hide Images?}
    E -->|Yes| F[RemoveImages]
    E -->|No| G[CleanLinks]
    F --> H[WrapTables]
    G --> H
    H --> I[Cleaned HTML]
    
    style A fill:#ffebee
    style I fill:#e8f5e9
    style C fill:#fff3e0
```

## 4. Image Processing Detail

```mermaid
flowchart TD
    A[Find All Images] --> B{First Image?}
    B -->|Yes| C[Set fetchpriority='high']
    B -->|No| D[Set loading='lazy']
    C --> E[Handle data-src]
    D --> E
    E --> F{Has data-src?}
    F -->|Yes| G[Copy data-src to src]
    F -->|No| H[Keep existing src]
    G --> I[Convert to absolute URL]
    H --> I
    I --> J{Wrapped in anchor?}
    J -->|Yes| K[Extract from anchor]
    J -->|No| L[Done]
    K --> L
    
    style A fill:#e3f2fd
    style L fill:#c8e6c9
```

## 5. Mercury Parser Integration

```mermaid
flowchart TD
    A[Article HTML] --> B{Parser Type?}
    B -->|MERCURY_PARSER| C[Mercury.parse]
    B -->|DEFUDDLE| D[Defuddle.parse]
    C --> E[Extracted Result]
    D --> E
    E --> F{Has Lead Image?}
    F -->|Yes| G{Content has images?}
    F -->|No| H[Skip image]
    G -->|No| I[Prepend lead image]
    G -->|Yes| H
    I --> J[Final Content]
    H --> J
    J --> K[Replace in DOM]
    
    style A fill:#fff3e0
    style K fill:#c8e6c9
    style C fill:#e1f5ff
    style D fill:#e1f5ff
```

## 6. Template Rendering Process

```mermaid
flowchart LR
    A[Article Data] --> B[Prepare Substitutions]
    B --> C[MacroProcessor]
    D[HTML Template] --> C
    C --> E[Parse with Jsoup]
    E --> F{Full Content Mode?}
    F -->|Yes| G[Inject JS Parser]
    F -->|No| H[Inject RSS Content]
    G --> I[Add Enclosures]
    H --> I
    I --> J[Clean HTML]
    J --> K[Return Final HTML]
    
    style A fill:#e1f5ff
    style D fill:#fff9c4
    style K fill:#c8e6c9
```

## 7. MacroProcessor Algorithm

```mermaid
flowchart TD
    A[Start] --> B[Read Template Character]
    B --> C{Is Open Tag Start?}
    C -->|Yes| D[Add to Queue]
    C -->|No| E{Queue Empty?}
    E -->|Yes| F[Add to Result]
    E -->|No| G{Complete Tag Pair?}
    D --> H[Continue Reading]
    G -->|Yes| I[Extract Key]
    G -->|No| H
    I --> J{Key in Substitutions?}
    J -->|Yes| K[Add Value to Result]
    J -->|No| L[Add Original Tag]
    K --> M{More Characters?}
    L --> M
    F --> M
    H --> M
    M -->|Yes| B
    M -->|No| N[Return Result]
    
    style A fill:#e1f5ff
    style N fill:#c8e6c9
```

## 8. Component Dependencies

```mermaid
graph TD
    A[Article] --> B[ArticleRenderer]
    B --> C[MacroProcessor]
    B --> D[HtmlPostProcessor]
    B --> E[ArticleContent]
    D --> F[CleanStyles]
    D --> G[RemoveImages]
    D --> H[CleanLinks]
    D --> I[WrapTables]
    B --> J[ParseHTML]
    J --> K[Mercury Parser JS]
    J --> L[Defuddle JS]
    E --> M[OkHttp]
    B --> N[Template HTML]
    B --> O[Preferences]
    
    style A fill:#e1f5ff
    style B fill:#fff3e0
    style D fill:#fff9c4
    style K fill:#ffebee
    style L fill:#ffebee
```

## 9. Error Handling Flow

```mermaid
flowchart TD
    A[Extract Article] --> B{URL Valid?}
    B -->|No| C[Return 400 Bad Request]
    B -->|Yes| D[Fetch HTML]
    D --> E{Network Success?}
    E -->|Timeout| F[Return 408 Timeout]
    E -->|Connection Error| G[Return 404 Not Found]
    E -->|Success| H{Content-Type HTML?}
    H -->|No| I[Return 400 Invalid Type]
    H -->|Yes| J[Parse with Mercury]
    J --> K{Parse Success?}
    K -->|No| L[Return 500 Parse Error]
    K -->|Yes| M[Clean HTML]
    M --> N{Clean Success?}
    N -->|No| L
    N -->|Yes| O[Return 200 Success]
    
    style O fill:#c8e6c9
    style C fill:#ffcdd2
    style F fill:#ffcdd2
    style G fill:#ffcdd2
    style I fill:#ffcdd2
    style L fill:#ffcdd2
```

## 10. Data Model Relationships

```mermaid
classDiagram
    class Article {
        +String id
        +String feedID
        +String title
        +String author
        +String contentHTML
        +URL url
        +String summary
        +String imageURL
        +ZonedDateTime publishedAt
        +Boolean read
        +Boolean starred
        +FullContentState fullContent
        +List~Enclosure~ enclosures
    }
    
    class Enclosure {
        +URL url
        +String type
        +Long length
    }
    
    class FullContentState {
        <<enumeration>>
        NONE
        LOADING
        LOADED
        ERROR
    }
    
    class ArticleRenderer {
        +render(article, byline, colors, hideImages) String
    }
    
    class ArticleContent {
        +fetch(url) Result~String~
    }
    
    class HtmlPostProcessor {
        +clean(document, hideImages) void
    }
    
    Article --> Enclosure : contains
    Article --> FullContentState : has state
    ArticleRenderer --> Article : renders
    ArticleContent --> Article : fetches for
    HtmlPostProcessor --> ArticleRenderer : used by
```

## 11. Complete System Architecture

```mermaid
graph TB
    subgraph "Data Layer"
        A1[Article Model]
        A2[Enclosure Model]
        A3[Feed Model]
    end
    
    subgraph "Fetching Layer"
        B1[ArticleContent]
        B2[OkHttp Client]
        B3[UserAgentInterceptor]
    end
    
    subgraph "Parsing Layer"
        C1[Mercury Parser]
        C2[Defuddle Parser]
        C3[ParseHTML]
    end
    
    subgraph "Processing Layer"
        D1[HtmlPostProcessor]
        D2[CleanStyles]
        D3[CleanLinks]
        D4[RemoveImages]
        D5[WrapTables]
    end
    
    subgraph "Rendering Layer"
        E1[ArticleRenderer]
        E2[MacroProcessor]
        E3[Template HTML]
        E4[Preferences]
    end
    
    subgraph "Presentation Layer"
        F1[WebView]
        F2[JavaScript]
        F3[CSS Stylesheet]
    end
    
    A1 --> B1
    B1 --> B2
    B2 --> B3
    B2 --> C1
    B2 --> C2
    C1 --> C3
    C2 --> C3
    C3 --> D1
    D1 --> D2
    D1 --> D3
    D1 --> D4
    D1 --> D5
    D2 --> E1
    D3 --> E1
    D4 --> E1
    D5 --> E1
    E1 --> E2
    E1 --> E3
    E1 --> E4
    E2 --> F1
    E3 --> F1
    F1 --> F2
    F1 --> F3
    
    style A1 fill:#e1f5ff
    style B1 fill:#fff3e0
    style C1 fill:#fff9c4
    style D1 fill:#f3e5f5
    style E1 fill:#fce4ec
    style F1 fill:#c8e6c9
```

## Diagram Usage

These diagrams can be:
1. **Viewed on GitHub** - Automatically rendered in the README
2. **Copied to documentation** - Use in your own docs
3. **Modified** - Edit the Mermaid syntax to customize
4. **Exported** - Use Mermaid live editor to export as PNG/SVG

## Mermaid Resources

- [Mermaid Official Docs](https://mermaid.js.org/)
- [Mermaid Live Editor](https://mermaid.live/)
- [GitHub Mermaid Support](https://github.blog/2022-02-14-include-diagrams-markdown-files-mermaid/)

---

**Tip:** Copy these diagrams into your own documentation or use them as reference when implementing the extraction logic!
