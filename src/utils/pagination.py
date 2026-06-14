import base64
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status


def encode_cursor(dt: datetime, record_id: uuid.UUID) -> str:
    raw_string = f"{dt.timestamp()}|{record_id}"
    return base64.urlsafe_b64encode(raw_string.encode()).decode()


def decode_cursor(cursor: str) -> tuple[datetime, uuid.UUID]:
    try:
        raw_string = base64.urlsafe_b64decode(cursor.encode()).decode()
        ts_str, id_str = raw_string.split("|")

        dt = datetime.fromtimestamp(float(ts_str), tz=timezone.utc)
        record_id = uuid.UUID(id_str)
        return dt, record_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid pagination cursor."
        )
