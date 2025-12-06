# utils.py
import base64
import uuid
from datetime import datetime
from whisper import load_model
import asyncio
import os
import tempfile

# Load Whisper model
asr_model = load_model("small")

DEMO_DIR = os.path.join(os.getcwd(), "demo")

# ---- MOCK FUNCTIONS for beginner testing ----

# ---- TRANSCRIPTION FUNCTION ----
async def transcribe_audio(audio_bytes: bytes) -> str:
    """
    Convert raw audio bytes into text using Whisper model.
    """
    import tempfile

    # Save bytes temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    # Run Whisper model
    result = asr_model.transcribe(tmp_path)

    # Remove temp file
    os.remove(tmp_path)

    return result["text"]

async def generate_llm_response(prompt: str) -> str:
    # Simulate an LLM response
    await asyncio.sleep(0.5)  # simulate latency
    return f"Mock LLM reply to: {prompt[:50]}..."

async def synthesize_tts(text: str, language: str="en") -> bytes:
    # Simulate TTS audio as base64 bytes
    await asyncio.sleep(0.2)
    # We'll just return the text encoded as bytes (not real audio)
    return text.encode("utf-8")

# ---- AUDIO HANDLER ----
# utils.py
import os
import uuid
import base64
import asyncio
import tempfile
from pydub import AudioSegment
from whisper import load_model

DEMO_DIR = os.path.join(os.getcwd(), "demo")

# Load Whisper ASR model
asr_model = load_model("small")


# ---------------------- TRANSCRIBE (mp3 → wav → text) -----------------------
async def transcribe_audio_from_file(audio_file: str) -> str:
    """
    Read MP3 from /demo, convert to WAV, pass to Whisper ASR.
    """
    audio_path = os.path.join(DEMO_DIR, audio_file)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    # 1. Convert mp3 → wav using pydub
    sound = AudioSegment.from_file(audio_path)
    wav_path = os.path.join(DEMO_DIR, f"temp_{uuid.uuid4().hex}.wav")
    sound.export(wav_path, format="wav")

    # 2. Transcribe WAV using Whisper
    result = asr_model.transcribe(wav_path)
    text = result.get("text", "").strip()

    # Cleanup
    os.remove(wav_path)

    return text


# ---------------------- MOCK LLM (Replace later) ----------------------------
async def generate_llm_response(prompt: str) -> str:
    await asyncio.sleep(0.3)
    return f"LLM reply to: {prompt}"


# ---------------------- MOCK TTS (Replace later) ----------------------------
async def synthesize_tts(text: str) -> str:
    await asyncio.sleep(0.3)
    return base64.b64encode(text.encode()).decode()


# ---------------------- FULL AUDIO HANDLER ----------------------------------
async def handle_audio_message(audio_file: str):
    """
    Entire flow:
    1. Read mp3 from demo folder
    2. Convert → wav → text
    3. LLM → reply
    4. TTS → base64 audio
    """
    # 1. Transcribe
    text_from_audio = await transcribe_audio_from_file(audio_file)

    # 2. LLM reply
    llm_reply = await generate_llm_response(text_from_audio)

    # 3. TTS audio_base64
    reply_audio_base64 = await synthesize_tts(llm_reply)

    return {
        "user_text": text_from_audio,
        "agent_text": llm_reply,
        "agent_audio_base64": reply_audio_base64,
        "mime": "audio/mp3"
    }

def save_audio_file(audio_bytes, folder="demo", filename_prefix="reply"):
    # Ensure folder exists
    os.makedirs(folder, exist_ok=True)
    
    # Generate unique filename
    filename = f"{filename_prefix}_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(folder, filename)
    
    # Decode and save
    audio_bytes = base64.b64decode(audio_bytes)
    with open(filepath, "wb") as f:
        f.write(audio_bytes)
    
    return filepath

async def process_uploaded_audio(mp3_path: str):
    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"Audio file not found: {mp3_path}")

    # Convert MP3 → WAV
    wav_path = mp3_path.replace(".mp3", ".wav")
    AudioSegment.from_mp3(mp3_path).export(wav_path, format="wav")

    # ---- TRANSCRIBE ----
    # replace with your model
    transcribed_text = fake_transcribe(wav_path)

    # ---- TTS RESPONSE ----
    reply_audio_path = generate_tts_audio(transcribed_text)

    return {
        "incoming_audio": os.path.basename(mp3_path),
        "transcribed_text": transcribed_text,
        "reply_text": f"Echo: {transcribed_text}",
        "reply_audio_file": reply_audio_path
    }


def fake_transcribe(wav_path):
    return "This is a test transcription."


def generate_tts_audio(text: str):
    out = "demo/reply_audio.wav"
    with open(out, "wb") as f:
        f.write(b"WAVDATA")
    return out