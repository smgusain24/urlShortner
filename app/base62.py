import os
from url_normalize import url_normalize
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from dotenv import load_dotenv

load_dotenv()

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
BASE = len(ALPHABET)
MIN_LEN = 6
SECRET_MASK = os.getenv("SECRET_MASK")

def base62_pad(n: int, min_len: int = MIN_LEN) -> str:
    s = encode(n)
    if len(s) < min_len:
        s = ALPHABET[0] * (min_len - len(s)) + s
    return s


def make_code_from_id(row_id: int) -> str:
    obfuscated = row_id ^ int(SECRET_MASK, 16)
    return base62_pad(obfuscated, MIN_LEN)

def normalize_url(raw: str) -> str:
    norm = url_normalize(raw.strip())
    p = urlparse(norm)
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not k.lower().startswith("utm_")]
    query = urlencode(q)
    return urlunparse((p.scheme, p.netloc, p.path or "/", "", query, ""))


def encode(n: int) -> str:
    if n == 0:
        return ALPHABET[0]
    output = []
    while n>0:
        n, r = divmod(n, BASE)
        output.append(ALPHABET[r])
    return "".join(output[::-1])

