from fastapi import FastAPI, Depends, HTTPException, status, Header, APIRouter
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import uuid, datetime, os
from fastapi import UploadFile, File
import base64

from utils import (
    generate_llm_response,
    synthesize_tts,
    handle_audio_message,
    process_uploaded_audio,
    save_audio_file
)

app = FastAPI(title="VoxLoom Backend Challenge")


@app.get("/")
async def root():
    return {"message": "VoxLoom Backend Running"}


security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.scheme != "Bearer" or credentials.credentials != "demo123":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return True


class SessionCreate(BaseModel):
    customer_id: str
    language: str
    channel: str
    persona: str | None = None


class MessageIn(BaseModel):
    type: str
    text: str = None
    audio_file: str = None
    mime: str = None


sessions_db = {}
messages_db = {}

# Simulated tables
SESSIONS = {}
MESSAGES = {}
MODEL_CALLS = {}
CRM_RECORDS = {}
TOOL_CALLS = {}



@app.post("/api/v1/sessions")
def create_session(payload: SessionCreate, auth: bool = Depends(verify_token)):
    session_id = str(uuid.uuid4())
    sessions_db[session_id] = payload.dict()
    sessions_db[session_id]["created_at"] = datetime.datetime.utcnow().isoformat()
    return {"session_id": session_id, "created_at": sessions_db[session_id]["created_at"]}


@app.post("/audio-message")
async def audio_message(file: UploadFile = File(...)):
    try:
        os.makedirs("demo", exist_ok=True)

        file_path = f"demo/{file.filename}"
        with open(file_path, "wb") as f:
            f.write(await file.read())

        result = await process_uploaded_audio(file_path)

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/sessions/{session_id}/messages")
async def post_message(session_id: str, message: MessageIn):

    # create session container if not exists
    if session_id not in SESSIONS:
        SESSIONS[session_id] = {"session_id": session_id, "messages": []}

    # -------- TEXT MESSAGE --------
    if message.type == "text":
        reply_text = await generate_llm_response(message.text)
        # reply_audio_base64 = await synthesize_tts(reply_text)
        reply_audio = await synthesize_tts(reply_text)

        reply_audio_base64 = base64.b64encode(reply_audio).decode("utf-8")
        saved_audio_path = save_audio_file(reply_audio_base64)

        # ----- Log LLM model call -----
        model_call_id = str(uuid.uuid4())
        MODEL_CALLS[model_call_id] = {
            "id": model_call_id,
            "session_id": session_id,
            "model": "mock-llm",
            "input": message.text,
            "output": reply_text,
            "timestamp": datetime.datetime.utcnow().isoformat()
}


        msg_obj = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "incoming_text": message.text,
            "reply_text": reply_text,
            "reply_audio_base64": reply_audio_base64,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        # ⭐ Save message
        messages_db[msg_obj["id"]] = msg_obj
        SESSIONS[session_id]["messages"].append(msg_obj)

        # return msg_obj


    # -------- AUDIO MESSAGE --------
    elif message.type == "audio":
        if not message.audio_file:
            raise HTTPException(status_code=400, detail="audio_file required")

        # utils.handle_audio_message expects ONLY the filename
        result = await handle_audio_message(message.audio_file)

        # ----- Log Whisper ASR model call -----
        MODEL_CALLS[uuid.uuid4().hex] = {
            "session_id": session_id,
            "model": "whisper-small",
            "input": message.audio_file,
            "output": result["user_text"],
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        # reply_text = result["response_text"]
        # reply_audio_base64 = result["response_audio"]
        # saved_audio_path = save_audio_file(reply_audio_base64)

        msg_obj = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "incoming_audio": message.audio_file,
            "user_text": result["user_text"],
            "agent_text": result["agent_text"],
            "agent_audio_base64": result["agent_audio_base64"],
            "timestamp": datetime.datetime.utcnow().isoformat()
        }

        # ⭐ Save message
        messages_db[msg_obj["id"]] = msg_obj
        SESSIONS[session_id]["messages"].append(msg_obj)

        # return msg_obj
    else:
        raise HTTPException(status_code=400, detail="Unknown message type")


    # ----- Save message to message DB -----
    msg_id = str(uuid.uuid4())
    msg_obj = {
        "id": msg_id,
        "session_id": session_id,
        "incoming_text": message.text if message.type == "text" else result["user_text"],
        "reply_text": result["agent_text"] if message.type == "audio" else reply_text,
        "reply_audio": result.get("agent_audio_base64") if message.type == "audio" else reply_audio_base64,
        "created_at": datetime.datetime.utcnow().isoformat(),
        "type": message.type
    }

    messages_db[msg_id] = msg_obj
    SESSIONS[session_id]["messages"].append(msg_obj)

    # Auto call MCP
    mcp_payload = {
        "session_id": session_id,
        "customer_id": "unknown",
        "llm_reply": reply_text,
        "scenario": "conversation_turn"
    }
    mcp_tool(mcp_payload, auth=True)



@app.get("/api/v1/sessions/{session_id}/conversation")
def get_conversation(session_id: str, auth: bool = Depends(verify_token)):
    session_msgs = [
        msg for msg in messages_db.values() if msg["session_id"] == session_id
    ]
    return {"session_id": session_id, "messages": session_msgs}


@app.post("/api/v1/tools/mcp")
def mcp_tool(payload: dict, auth: bool = Depends(verify_token)):
    
    tool_id = str(uuid.uuid4())
    
    TOOL_CALLS[tool_id] = {
        "id": tool_id,
        "status": "success",
        "payload": payload,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    # also store CRM record
    crm_id = str(uuid.uuid4())
    CRM_RECORDS[crm_id] = {
        "id": crm_id,
        "session_id": payload.get("session_id"),
        "customer_id": payload.get("customer_id"),
        "scenario": payload.get("scenario", "default"),
        "record": payload,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    return {
        "tool_call_id": tool_id,
        "crm_record_id": crm_id,
        "status": "success"
    }
