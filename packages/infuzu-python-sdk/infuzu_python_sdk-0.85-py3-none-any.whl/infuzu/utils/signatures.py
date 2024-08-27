import base64
import json


def get_signature_version(signature: str) -> str:

    try:
        signature_data: dict[str, any] = json.loads(base64.urlsafe_b64decode(signature))
        version: str = signature_data.get("v", "1.0")
        return version
    except (json.JSONDecodeError, KeyError):
        return "1.0"
