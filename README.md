# Moodrae

> **What does your chat really say about you?**

Moodrae is a privacy-first, local-only NLP engine that analyzes WhatsApp chat exports. It uses advanced NLP models to detect who's the driver, who's the dry texter, who's got main character energy, and who is lowkey manipulative, along with a full sentiment and tension timeline.

## How it Works

1. **Parser**: Cleans and normalizes WhatsApp `.txt` exports.
2. **Analysis**: Uses transformer models (via Hugging Face & ONNX) for Sentiment, Toxicity, and Topic Modeling.
3. **Scoring**: A robust heuristics engine that calculates participant dynamics, red flags, and tension points.
4. **Privacy**: All processing happens entirely in-memory. **No database. No external API calls.** Content is garbage collected immediately after processing.

## 🛠️ Local Setup

### Backend (Python / FastAPI)
```bash
cd backend
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m spacy download en_core_web_sm
uvicorn main:app --port 8000 --reload
```

### Frontend (Next.js)
```bash
cd frontend
pnpm install
pnpm dev
```

## Environment Variables

Create a `.env` file in the `backend/` directory:

| Variable | Default | Description |
|---|---|---|
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins (comma-separated) |
| `PORT` | `8000` | Port for the backend API |
| `SPACY_MODEL` | `en_core_web_sm` | Spacy model for entity/tonality extraction |
| `SENTIMENT_MODEL` | `SamLowe/roberta-base-go_emotions` | Model for sentiment analysis |
| `TOXICITY_MODEL` | `unitary/unbiased-toxic-roberta` | Model for toxicity analysis |
| `TOPIC_MODEL` | `all-MiniLM-L6-v2` | Model for topic embeddings |
| `MAX_UPLOAD_BYTES` | `10485760` | Maximum file upload size in bytes |
| `THREAD_WORKERS` | `2` | Number of background CPU workers |

## Privacy Model

- **No Disk Storage**: All uploaded content is processed in memory via byte-streams.
- **Ephemeral Lifecycle**: Objects are explicitly garbage collected after response delivery.
- **Local-First**: 100% of NLP processing occurs within the local CPU/memory space using spaCy and Transformers (via ONNX runtime).
- **No External LLMs**: The backend does not contact OpenAI, Anthropic, or any other cloud provider.
