# 🤖 Autonomous Agentic AI: Deal Discovery & Underpricing Detection

This project builds an autonomous agent-based system that scrapes product deals, estimates expected prices using LLMs and regression models, and automatically identifies **underpriced products**—those whose actual deal prices fall below the model’s predictions—for potential profit opportunities.

---

## 🎯 Project Goal

> **Automatically detect and return products priced significantly below model-estimated fair value**, enabling users to spot deals with strong profit potential.

---

## 📌 Key Features

1. **Large-Scale Product Dataset Curation**  
   - Curated a dataset of 400,000 product records from Amazon, accessed via Hugging Face.

2. **Hybrid Price Prediction Engine**  
   - Combined RAG (SentenceTransformer + custom FrontierAgent) and fine-tuned QLoRA models to estimate product prices from natural language descriptions.
   - Used Linear Regression as a baseline estimator.
   - Achieved ~70% accuracy within a tolerance range by comparing methods.

3. **Web Crawling & Deal Collection**  
   - Automated pipelines collect real-time RSS deal data from sources like DealNews.
   - Parsed HTML product listings using `requests` and `BeautifulSoup`, covering electronics, home goods, automotive, and more.

4. **Agentic Price Gap Detection**  
   - Compares real-time deal prices to model estimates and flags deals where the market price is **significantly lower** than predicted.

5. **Real-Time Notifications & Alerts**  
   - Integrated Pushover to push price alerts for underpriced deals.
   - Only alerts for products where the price gap exceeds a predefined margin (e.g., >20% below model price).

6. **Gradio UI for Live Interaction**  
   - Built a Gradio-based interface for users to input descriptions and see estimated price vs. deal price difference.

---
