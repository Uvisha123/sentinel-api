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
