"""QR verificable (RF07, RNF02): código = uuid + "." + HMAC_SHA256(secreto, uuid|trip|asiento)."""
import base64
import hashlib
import hmac
import io

import qrcode

from .config import QR_SECRET


def sign(ticket_uuid: str, trip_id: int, seat_number: int) -> str:
    msg = f"{ticket_uuid}|{trip_id}|{seat_number}".encode()
    return hmac.new(QR_SECRET.encode(), msg, hashlib.sha256).hexdigest()[:32]


def build_code(ticket_uuid: str, signature: str) -> str:
    return f"{ticket_uuid}.{signature}"


def qr_data_url(data: str) -> str:
    buf = io.BytesIO()
    qrcode.make(data, box_size=8, border=2).save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
