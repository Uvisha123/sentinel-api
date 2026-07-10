# 📚 Semantic Book Recommender – AI-Powered Book Discovery Engine



![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Gradio](https://img.shields.io/badge/Gradio-Frontend-orange)
![ML](https://img.shields.io/badge/Machine%20Learning-Enabled-purple)
![ChromaDB](https://img.shields.io/badge/ChromaDB-Vector%20Store-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-yellow)



---

## 🧠 Overview

**Semantic Book Recommender** is an intelligent, interactive recommendation engine that goes beyond simple keyword matching. Instead of searching titles or tags, it understands the **meaning** behind your query and the **emotional tone** you're looking for — then finds books that actually fit.

> 👉 Goal: Combine semantic vector search, zero-shot classification, and sentiment analysis into a single, easy-to-use recommendation dashboard.

---

## 🌍 Problem Statement

Traditional book search relies on:

- Exact keyword or title matches
- Manually tagged genres and categories
- No sense of tone, mood, or emotional fit

### 💥 Real-World Impact

- Readers struggle to describe *what they want* in searchable terms
- Great matches get missed because the wording doesn't line up
- No way to filter by how a book *feels* (suspenseful, heartwarming, dark, etc.)

---

## 🎯 Objectives

- Search books by the **meaning** of a free-text description, not just keywords
- Classify books into clean, simplified categories
- Score each book's emotional tone across 7 dimensions
- Let users filter and browse recommendations by category and mood
- Present everything through a clean, interactive web dashboard

---

## 🏗️ System Architecture

```text
         ┌──────────────────────────────────┐
         │             USER QUERY           │
         │   "A story about forgiveness"    │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │        EMBEDDING LAYER           │
         │   HuggingFace all-MiniLM-L6-v2   │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │        VECTOR SEARCH LAYER       │
         │   ChromaDB similarity search     │
         │   (via LangChain)                │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │      CLASSIFICATION LAYER        │
         │  Category grouping (zero-shot)   │
         │  Emotion scoring (DistilRoBERTa) │
         └────────────────┬─────────────────┘
                          │
         ┌────────────────▼─────────────────┐
         │         GRADIO DASHBOARD         │
         │   Search, filter, browse results │
         └──────────────────────────────────┘
```

---

## ✨ Core Features

### 🔍 Semantic Vector Search
- Powered by HuggingFace embeddings (`all-MiniLM-L6-v2`) and ChromaDB
- Describe what you want to read in plain language — matches are found by **plot meaning**, not exact words

### 🎭 Emotional Tone Filtering
- Uses `j-hartmann/emotion-english-distilroberta-base` to score every book description across 7 emotions
- Filter recommendations by tone: *Happy, Sad, Surprising, Angry, Suspenseful,* and more

### 🗂️ Category Classification
- Groups books into simplified, distinct categories for easy browsing
- Removes noisy, overlapping genre tags from the raw dataset

### 🖥️ Interactive Dashboard
- Sleek, glass-themed web interface built entirely in Python with Gradio
- No frontend code required — search, filter, and explore results in one view

---

## ⚙️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend Interface** | Gradio |
| **Vector Database** | ChromaDB |
| **Embeddings & Orchestration** | LangChain, sentence-transformers |
| **NLP & Sentiment Analysis** | HuggingFace `transformers` pipeline |
| **Data Processing** | Pandas, Jupyter Notebooks |

---

## 📂 Project Structure

```text
semantic-book-recommender/
│
├── gradio-dashboard.py          ← Main application — launches the web interface
│
├── data-exploration.ipynb       ← Kaggle dataset download, missing-values analysis
├── vector-search.ipynb          ← LangChain + ChromaDB setup using HuggingFace embeddings
├── text-classification.ipynb    ← Dataset cleaning and category classification
├── sentiment-analysis.ipynb     ← Emotional tone scoring for every book description
│
├── requirements.txt
└── .env                         ← API keys / config (gitignored)
```

---

## ▶️ How to Run Locally

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/semantic-book-recommender.git
cd semantic-book-recommender
```

### 2. Install Dependencies
Ensure you have PyTorch, LangChain, Transformers, Gradio, and Pandas installed.
```bash
pip install langchain langchain-chroma langchain-openai sentence-transformers transformers gradio pandas python-dotenv
```

### 3. Run the Dashboard
```bash
python gradio-dashboard.py
```

### 4. Open in Browser
Click the local URL (usually `http://127.0.0.1:7860`) shown in your terminal to start exploring.

---

## 🔥 What Makes This Project Stand Out

This is **not** just a keyword search tool. It's a full semantic recommendation pipeline:

- ✅ Real vector embeddings for meaning-based search — not string matching
- ✅ Multi-model NLP pipeline (embeddings + classification + emotion scoring)
- ✅ Clean separation between data prep (notebooks) and the live app (dashboard)
- ✅ Emotion-aware filtering — a rare feature in typical recommender projects
- ✅ End-to-end pipeline: data exploration → classification → sentiment scoring → live search

---

## 🤝 Contribution

1. Fork the repository
2. Create a new branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Submit a pull request

---

## 📜 License

MIT License

---

## 🧠 Final Thought

> *"Search isn't just about words — it's about what a reader is actually looking for."*

---

⭐ If you find this project useful, give it a star and support the journey 🚀
