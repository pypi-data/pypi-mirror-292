# sensitive_module.pyx

from hashlib import sha256
import base64
import json


def check_hash(
    x_unique_id: str,
    x_signature: str,
    campaign_id: str = "",
    body: dict = None,
    sep: str = "",
) -> bool:
    if body:
        body = dict(sorted(body.items()))
    data = (
        base64.b64encode(json.dumps(body, separators=(",", ":")).encode())
        if body
        else b""
    )
    data_string = sep.join([x_unique_id, campaign_id, data.decode()])
    e_hash = sha256(data_string.encode()).hexdigest()
    return x_signature == e_hash
