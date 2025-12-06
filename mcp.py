from utils import sessions
import uuid
from datetime import datetime

tool_calls = []
crm_records = []

def call_mcp(payload: dict):
    record_id = str(uuid.uuid4())
    crm_records.append({
        "id": record_id,
        "session_id": payload["session_id"],
        "customer_id": payload["customer_id"],
        "record_json": payload["crm_record"],
        "status": "pending",
        "created_at": datetime.utcnow()
    })
    tool_calls.append({
        "id": str(uuid.uuid4()),
        "session_id": payload["session_id"],
        "payload_json": payload,
        "status": "done",
        "created_at": datetime.utcnow()
    })
    return {"status": "ok", "crm_id": record_id}
