import hashlib
import hmac
import random
import time


def sign_request(
    access_key: str, secret_key: str, params: dict | None = None
) -> dict[str, str]:
    """Build signed headers for EcoFlow API requests.

    Every REST call requires HMAC-SHA256 signed headers:
    - accessKey
    - nonce (random int 10000-999999)
    - timestamp (milliseconds)
    - sign (HMAC-SHA256 of sorted query params + accessKey + nonce + timestamp)
    """
    nonce = str(random.randint(10000, 999999))
    timestamp = str(int(time.time() * 1000))

    # Build the sign string: sorted query params joined with &, then &accessKey&nonce&timestamp
    sign_parts = []
    if params:
        for key in sorted(params.keys()):
            sign_parts.append(f"{key}={params[key]}")

    sign_str = "&".join(sign_parts)
    if sign_str:
        sign_str += "&"
    sign_str += f"accessKey={access_key}&nonce={nonce}&timestamp={timestamp}"

    sign = hmac.new(
        secret_key.encode("utf-8"),
        sign_str.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return {
        "accessKey": access_key,
        "nonce": nonce,
        "timestamp": timestamp,
        "sign": sign,
    }
