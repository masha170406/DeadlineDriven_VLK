# AI-Powered Medical Form Assistant

![Python Version](https://img.shields.io/badge/python-3.14-green)
![Package Manager](https://img.shields.io/badge/pkg--manager-uv-purple)
![AI Framework](https://img.shields.io/badge/framework-LiteLLM-orange)
![Database](https://img.shields.io/badge/vector--db-ChromaDB-blueviolet)
![License](https://img.shields.io/badge/license-MIT-yellow)

This AI assistant is a high-performance RAG (Retrieval-Augmented Generation) application designed to automate the filling of the Lithuanian **Forma Nr. 025/a-LK**. It uses vector search to map unstructured doctor's notes to official **TLK-10-AM** diagnosis codes and **ACHI** intervention codes.

## Contents

- [AI-Powered Medical Form Assistant](#ai-powered-medical-form-assistant)
  - [Contents](#contents)
  - [Key Features](#key-features)
  - [Project Structure](#project-structure)
  - [Setup and Installation](#setup-and-installation)
    - [Prerequisites](#prerequisites)
    - [Local Environment Setup](#local-environment-setup)
      - [1. Repository](#1-repository)
      - [2. .env File](#2-env-file)
      - [3. (Optional) uv](#3-optional-uv)
  - [Docker Deployment (Recommended)](#docker-deployment-recommended)
    - [1. Build](#1-build)
    - [2. App](#2-app)
  - [How the RAG System Works](#how-the-rag-system-works)
  - [Security \& Compliance](#security--compliance)

## Key Features

- **LLM-Agnostic Architecture**: Powered by `LiteLLM`, allowing seamless switching between Mistral, GPT-4o, and Claude 3.5.
- **Semantic RAG Search**: Uses `ChromaDB` with Cosine Similarity to find official medical codes even when the doctor uses slang or symptoms.
- **Identity Intelligence**: Automatically parses birth dates and gender from the Lithuanian Personal ID (*Asmens kodas*).
- **Deterministic Reliability**: Configured with `temperature=0` for consistent, audit-ready medical outputs.
- **Dockerized Deployment**: Production-ready containerization using `uv` for ultra-fast dependency management.

## Project Structure

```text
.
├── src/
│   ├── app.py             # Streamlit UI (The Dashboard)
│   ├── rag_backend.py     # Vector search & LLM Logic
│   ├── build_database.py  # Idempotent DB Ingestor
│   └── prompts.py         # Isolated Lithuanian System Prompts
├── data/
│   ├── tlk_10_am.csv      # Enriched Diagnosis Database
│   └── achi.csv           # Enriched Intervention Database
├── compose.yaml           # Docker Orchestration
└── Dockerfile             # Multi-stage UV-based Build
```

## Setup and Installation

### Prerequisites

- [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/).
- API Keys for Mistral (stored in `.env`).

### Local Environment Setup

#### 1. Repository

Clone the repository.

#### 2. .env File

Create a `.env` file in the root directory:

```env
MISTRAL_API_KEY=your_key_here
PORT=8501
```

#### 3. (Optional) uv

If running without Docker, use `uv`:

```bash
uv sync
uv run src/build_database.py
uv run streamlit run src/app.py
```

## Docker Deployment (Recommended)

The application is dockerized using a multi-stage build to minimize image size and maximize security (running as a non-root user).

### 1. Build

Build and Start the Container:

```bash
docker compose up --build
```

### 2. App

To access the Application, open [http://localhost:8501](http://localhost:8501) (or whatever other port you chose) in your browser.

**Note on Persistence:** The `vlk_chroma_db` is stored in a Docker named volume (`chroma_data`). This ensures your processed medical vectors survive container restarts.

## How the RAG System Works

1. **Ingestion**: `build_database.py` processes enriched CSVs, combining official descriptions with common Lithuanian symptoms into a vector.
2. **Retrieval**: When a doctor enters a note, the system searches the Top-10 most semantically similar codes using Cosine Similarity.
3. **Override Logic**: If a doctor explicitly types a code (e.g., "H52.1"), the LLM is instructed to prioritize that exact string over the vector search results.
4. **Extraction**: The LLM processes the retrieved context and extracts a structured JSON, including a reasoning string and a confidence score.

## Security & Compliance

- **Non-Root Execution**: The Docker container runs under a dedicated `appuser`.
- **Data Privacy**: The architecture is designed to support local LLM deployment (e.g., via Ollama) to keep patient data within the hospital intranet.
