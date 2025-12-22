# OpsPilot Layer 0 - SLM Tuning & Optimization

This folder contains experiments and tests for Small Language Model (SLM) tuning and optimization, part of the Layer 2 roadmap initiative for model routing and inference optimization.

## Overview

The goal of this module is to evaluate and optimize inference performance using smaller, locally-hosted language models as part of a model cascade strategy:
- **Simple queries** → cheaper/faster SLM (e.g., DeepSeek-R1:8B via Ollama)
- **Complex queries** → larger hosted model

## Prerequisites

- Python 3.13+
- [Ollama](https://ollama.ai/) installed and running locally
- DeepSeek-R1:8B model pulled: `ollama pull deepseek-r1:8b`

## Setup

```bash
cd opspilot-layer0

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install openai tqdm
```

## Running Tests

Ensure Ollama is running on `localhost:11434`, then:

```bash
python main/llmtest.py
```

## What's Being Tested

- **Local inference latency**: Using Ollama's OpenAI-compatible API
- **Model response quality**: DeepSeek-R1:8B for operational queries
- **API compatibility**: OpenAI client library with local Ollama backend

## Roadmap Alignment

This work supports **Layer 2** objectives:
- Model routing (SLM + LLM cascade)
- Self-hosted inference evaluation
- Baseline latency measurements for local models

## Next Steps

1. Add latency benchmarking scripts
2. Implement query complexity classifier
3. Compare SLM vs hosted model response quality
4. Integrate with OpsPilot RAG pipeline for A/B testing

