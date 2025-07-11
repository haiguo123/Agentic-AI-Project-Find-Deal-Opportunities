# 🤖 Autonomous Agentic AI: Deal Discovery & Pricing System

This project implements a full-stack autonomous AI agent that discovers product deals, estimates their prices, and delivers real-time alerts using a hybrid of retrieval-augmented generation, LLM planning, and automation.

---

## 📌 Key Features

1. **Large-Scale Product Data Curation**  
   - Curated a dataset of 400,000 product entries from Amazon, accessed via Hugging Face datasets.

2. **Hybrid Price Prediction Engine**  
   - Used a combination of RAG (SentenceTransformer + custom FrontierAgent) and QLoRA (fine-tuned open-source LLM) to build a price estimation model.
   - Deployed on Modal cloud platform to dynamically infer prices from product descriptions.
   - Integrated a Linear Regression baseline for comparison, achieving **70% accuracy** within an acceptable tolerance.

3. **Web Crawling Automation**  
   - Built Python pipelines to scrape multiple RSS feeds (e.g., DealNews), covering electronics, home, and automotive categories.
   - Used `requests` + `BeautifulSoup` to extract structured deal descriptions from HTML pages.

4. **Agent Framework with Real-Time Alerting**  
   - Developed an LLM-powered agent framework that performs product analysis and sends real-time deal notifications via Pushover.
   - Retrieves the most realistic estimated price based on embedding similarity and product metadata.

5. **Interactive UI with Gradio**  
   - Built a web-based user interface using Gradio for easy interaction with the pricing agent.

---

## 🧰 Tech Stack

- Python, OpenAI API, DeepSeek, SentenceTransformers, QLoRA
- ChromaDB (vector database), Pushover API, Gradio
- BeautifulSoup, requests, RSS parsing
- Modal (cloud hosting), Linear Regression (scikit-learn)

---

## 📊 Project Goals

- Automate end-to-end price estimation and deal discovery.
- Combine agent planning + vector search for robust product understanding.
- Enable fast, scalable alerting for valuable deals across categories.

---
