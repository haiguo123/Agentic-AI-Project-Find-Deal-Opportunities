# 🤖 Autonomous Agentic AI: Deal Discovery & Underpricing Detection

This project builds an autonomous agent-based system that scrapes product deals, estimates expected prices using LLMs and regression models, and automatically identifies **underpriced products**—those whose actual deal prices fall below the model’s predictions—for potential profit opportunities.

# 🎯 Project Goal

> **Automatically detect and return products priced significantly below model-estimated fair value**, enabling users to spot deals with strong profit potential.

---

## 1. Data Curation

This repository contains a lightweight data-curation pipeline that
converts Amazon product metadata into high-quality, fixed-length
training examples for training a model to predict product prices from
text.

The pipeline consists of two main components:

-   Item: Cleans and compacts a single product datapoint into a
    prompt--answer pair.
-   Loader: Loads a HuggingFace dataset split, filters datapoints by
    price, and processes them in parallel to produce curated Item
    objects.

### Overview

For each product datapoint, the pipeline performs the following steps:

1.  Assemble product text from multiple fields:
    -   title
    -   description (list of strings)
    -   features (list of strings)
    -   details (string, additionally cleaned with rule-based removals)
2.  Scrub noise from the text:
    -   Remove punctuation and formatting artifacts
    -   Normalize whitespace and stray commas
    -   Drop product-number-like tokens (long tokens containing digits)
3.  Length control:
    -   Enforce a minimum amount of text (MIN_CHARS)
    -   Cap raw characters (CEILING_CHARS)
    -   Tokenize using the base tokenizer (e.g., Llama 3.1 8B)
    -   Require enough tokens to be useful (MIN_TOKENS)
    -   Truncate to a consistent maximum (MAX_TOKENS)
4.  Prompt construction:
    -   Prepend a natural-language question
    -   Append the rounded price as the training target

### Prompt Format

Each curated sample uses the following template:

``` text
How much does this cost to the nearest dollar?

<TITLE>
<CLEANED PRODUCT TEXT>

Price is $<rounded_price>.00
```

The target price is rounded to the nearest dollar to reduce label noise
and stabilize training.

### Key Parameters

-   MIN_PRICE, MAX_PRICE: Filter unrealistic or out-of-range prices
    (default: 0.5 to 999.49)
-   MIN_CHARS: Minimum raw text length before tokenization (default:
    300)
-   MIN_TOKENS: Minimum tokens required after tokenization (default:
    150)
-   MAX_TOKENS: Maximum tokens retained for the product text (default:
    160)
-   CEILING_CHARS: Pre-tokenization character cap (MAX_TOKENS \* 7)

### Parallel Processing

ItemLoader processes dataset chunks in parallel using
ProcessPoolExecutor:

-   Iterates over the dataset in fixed-size chunks (CHUNK_SIZE)
-   Converts each valid datapoint into an Item
-   Keeps only samples with include = True
-   Assigns the loader name as category for downstream analysis
-   Displays progress using tqdm

This significantly speeds up preprocessing on large datasets.

---

## 2. **Hybrid Price Prediction Engine** 

### Overview
   - Combined RAG (SentenceTransformer + custom FrontierAgent) and fine-tuned QLoRA models to estimate product prices from natural language descriptions.
   - Used Linear Regression as a baseline estimator.
   - Achieved ~70% accuracy within a tolerance range by comparing methods.

### RAG

The RAG pipeline consists of four main stages:

1. **Document Ingestion & Indexing**
   - Sources:
     - Historical product listings and prices  
     - Product specifications and descriptions  
     - Category-level statistics (e.g., average prices, distributions)  
     - User-curated deal datasets (optional)  
   - Processing:
     - Chunk long documents into fixed-size passages  
     - Clean and normalize text (similar rules as data curation)  
     - Embed each chunk using a sentence embedding model  
   - Storage:
     - Persist embeddings in a vector database (e.g., FAISS / Chroma / Milvus)

2. **Query Construction**
   - For each candidate deal, construct a structured query from:
     - Product title  
     - Cleaned description + features  
     - Optional category or brand hints  
   - The query is embedded using the same encoder as the index.

3. **Retrieval**
   - Perform top-*k* nearest-neighbor search over the vector store  
   - Retrieve semantically similar products, historical comparables, and pricing references  
   - Optionally apply:
     - Category filters  
     - Recency weighting  
     - Price-range constraints  

4. **Augmented Generation**
   - The retrieved context is injected into the LLM prompt alongside the product text  
   - The LLM produces:
     - An estimated fair price  
     - A confidence score or uncertainty band (optional)  
     - A brief natural-language rationale referencing retrieved evidence
       
### 🧾 Prompt Template (RAG-Augmented)

```text
You are a pricing expert. Given the product below and reference examples of similar products with known prices, estimate the fair market price.

[Product]
<TITLE>
<CLEANED PRODUCT TEXT>

[Retrieved Comparables]
<CHUNK 1>
<CHUNK 2>
...
<CHUNK K>

Return:
- Estimated fair price (USD, rounded to nearest dollar)
- Brief justification citing the comparables

```

---

## 3. **Web Crawling & Deal Collection**  

This module implements an automated **web scraping and RSS-based deal collection pipeline** that continuously gathers real-time product deals from public deal aggregation websites (e.g., DealNews). The collected deals serve as the upstream data source for downstream price estimation, underpricing detection, and agent-based decision making.

### 📡 Data Sources

The system currently monitors multiple DealNews RSS feeds across categories:

- Electronics  
- Computers  
- Automotive  
- Smart Home  
- Home & Garden  

Each RSS feed provides structured metadata (title, summary, URL), which is enriched by crawling the full product detail page.

### 🧩 Scraping Pipeline Overview

For each RSS feed entry, the pipeline performs the following steps:

1. **RSS Parsing**
   - Uses `feedparser` to fetch and parse RSS feeds.
   - Iterates over the latest deal entries (top N per category).

2. **HTML Content Extraction**
   - Fetches the full deal page using `requests`.
   - Parses HTML with `BeautifulSoup`.
   - Extracts:
     - Product title  
     - Cleaned summary  
     - Detailed description  
     - Feature list (if available)  

3. **Text Cleaning & Normalization**
   - Removes HTML tags and formatting artifacts.
   - Normalizes whitespace and line breaks.
   - Splits product content into:
     - `details`  
     - `features` (if present)  

4. **Rate Limiting & Politeness**
   - Adds a fixed delay between requests to avoid overloading source websites.
   - Limits scraping to a small number of recent entries per feed.

### 🏗️ Core Data Structures

Represents a deal crawled from RSS + HTML:

- `title`: Product title  
- `summary`: Cleaned RSS summary  
- `url`: Deal URL  
- `details`: Full textual product description  
- `features`: Parsed feature list (if available)  

Each `ScrapedDeal` instance exposes a unified natural language representation via:

```text
Title: <title>
Details: <details>
Features: <features>
URL: <url>
```

---

## 4. **Agentic Price Gap Detection**  
   - Compares real-time deal prices to model estimates and flags deals where the market price is significantly lower than predicted.

---

## 5. **Real-Time Notifications & Alerts**  
   - Integrated Pushover to push price alerts for underpriced deals.
   - Only alerts for products where the price gap exceeds a predefined margin (e.g., >20% below model price).

---

## 6. **Gradio UI for Live Interaction**  
   - Built a Gradio-based interface for users to look up real-time profitable deals with deal description, actual price, estimate price and discount.

---
