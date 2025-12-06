📝 VoxLoom Backend — Technical Notes & Trade-offs
⚙️ Architecture Overview

The project implements a conversational backend supporting:

Text → LLM → TTS responses

Audio → ASR (Whisper-small) → LLM → TTS

Session-level message threading

Model-call logging

CRM logging via MCP simulation

Persistent file storage in /demo/

In-memory DB for fast development & testing

API built fully with FastAPI, using:

Whisper-small (ASR)

Mock LLM

Mock TTS

Python’s base64 + pydub for audio processing

In-memory dictionaries simulating database tables

🧩 Key Design Choices & Why
1️⃣ In-Memory DB instead of PostgreSQL

✔ Faster to develop
✔ Zero schema migrations
✔ Perfect for 48-hour challenge
❗ PostgreSQL pool exists (database.py) for future integration
❗ In production, SESSIONS, MESSAGES, MODEL_CALLS, etc. must move to actual DB.

2️⃣ Mock LLM & TTS

The challenge did not require real LLM or TTS models; therefore:

LLM → returns "LLM reply to: <text>"

TTS → base64-encodes the text

Advantages:

Lightweight

Easy to test

No GPU required

Deterministic outputs

3️⃣ Whisper-small as ASR

Whisper was required, and small model chosen because:

✔ Faster on CPU
✔ Small enough for local execution
✔ Good accuracy for challenge

4️⃣ Audio Upload Pipeline

To support voice-based interactions:

User uploads MP3

File saved in /demo/

MP3 → WAV (pydub)

WAV → Whisper → text

LLM reply generated

TTS output generated & returned

This mimics real conversational voice agents.

5️⃣ MCP & CRM Storage

Every conversation turn automatically triggers MCP logic:

tool_call stored

CRM record saved

timestamp stored

These simulate enterprise backend workflows.

🔍 Limitations (If More Time Was Given)
⏳ 1. No persistent DB

Should integrate:

PostgreSQL models

Async queries

Foreign key relations

🎤 2. TTS is not real

Could integrate:

gTTS

Coqui TTS

Azure Speech

🤖 3. LLM is mocked

Replace with:

OpenAI GPT

HuggingFace Inference API

OpenRouter models

🧪 4. No automated tests

Planned:

Unit tests for utils

Integration tests for audio pipeline

Load-testing with Locust

🧵 5. Session context is shallow

Currently does not maintain full conversation memory.

A future version would include:

sliding window memory

persona conditioning

conversation embeddings

🌟 Possible Enhancements

If more development time was available, would add:

✔ Real DB storage
✔ JWT authentication
✔ Rate limiting
✔ S3 storage for audio
✔ Retry queues for MCP
✔ Monitoring dashboards
✔ Production Docker images
🎯 Final Summary

This backend is a clean, modular implementation that demonstrates:

API design

Audio processing

ASR + LLM + TTS pipeline

IoT-style file uploads

Internal system logs

Data modeling

Good backend engineering practices

It is ready to run, easy to extend, and organized for real production upgrades.
