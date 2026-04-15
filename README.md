# Turing Test Simulator

An experimental Turing test simulator built with FastAPI, Streamlit, and LangChain. The project provides a judge room, a hidden human room, and a live guest view, all backed by a shared FastAPI service that stores chat state in memory.

## What it does

- Lets a judge ask questions in a live Turing test session.
- Lets a hidden human answer as the other participant.
- Shows guests a read-only live transcript of the conversation.
- Generates the AI participant's replies using Google Gemini through LangChain.
- Tracks a shared five-minute round timer and moves the judge to a final verdict screen when time expires.

## Project Structure

- `src/main.py`: FastAPI app with chat, round state, and AI reply endpoints.
- `src/features/chat/service.py`: AI response generation and prompt formatting.
- `src/frontend/app.py`: Streamlit landing page and role entry points.
- `src/frontend/pages/judge_chat.py`: Judge chat room.
- `src/frontend/pages/hidden_human.py`: Hidden human reply room.
- `src/frontend/pages/guest_view.py`: Live public transcript view.
- `src/frontend/pages/judge_verdict.py`: Final guess screen after the round ends.
- `src/helper/config.py`: Environment-based settings loader.

## Requirements

- Python 3.11 or newer
- A Google Gemini API key if you won't use a local LLM
- Network access to the configured model provider

## Setup

Create and activate a virtual environment, then install the project in editable mode:

```bash
python -m venv venv
venv\Scripts\activate
pip install -e .
```

Create a `.env` file in the project root with the required values (or take `.env.example` file and remove `.example`):

```env
GOOGLE_API_KEY=your_google_api_key
GOOGLE_MODEL_NAME=gemini-3.0-flash
OLLAMA_MODEL_NAME=gemma2:2b
```

The current implementation uses `GOOGLE_API_KEY` and `GOOGLE_MODEL_NAME`. `OLLAMA_MODEL_NAME` is present in the configuration but the Ollama path is commented out in the chat service.

## Running the App

Open two terminals and start both services:

```bash
uvicorn src.main:app --reload
```

```bash
streamlit run src/frontend/app.py
```

The Streamlit pages call the FastAPI service at `http://127.0.0.1:8000/api/chat`.

## Demo Access Codes

The current UI uses hardcoded demo codes in `src/frontend/app.py`:

- Judge: `shoman2026`
- Hidden human: `human2026`

## API Endpoints

- `POST /api/chat/round/start`: Start the shared round timer.
- `GET /api/chat/round/state`: Read the round timer state.
- `GET /api/chat/history`: Read the full chat transcript.
- `POST /api/chat/judge_ask`: Submit a judge message and trigger an AI reply.
- `POST /api/chat/human_reply`: Submit the hidden human reply.
- `DELETE /api/chat/reset`: Clear chat history and reset the round timer.

## Notes

- Chat history and round timing are stored in process memory, so restarting FastAPI clears the session.
- The judge UI asks for gender so the AI can adjust pronouns in Arabic responses.
- The project currently targets a local development workflow rather than production deployment.
- This project is made for illustration purposes for a non-tech people so that they can deeply understand what Turing-Test is.