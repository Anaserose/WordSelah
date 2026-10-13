"""bible_api.py - fetches King James Version verses and remembers them.

The KJV is public domain. Verses come from the free bible-api.com service, which
needs no key. Every verse that is fetched is saved to a small cache file in the
user's home folder, so it is only downloaded once and still works offline later.

If verses will not load, run this file directly (python bible_api.py, or
right-click > Run in PyCharm). It tests one verse and explains what went wrong.
"""
import json
import socket
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_URL = "https://bible-api.com/{ref}?translation=kjv"
CACHE_FILE = Path.home() / ".wordselah" / "kjv_cache.json"
TIMEOUT_SECONDS = 8

_cache = None
_context = None


class BibleAPIError(Exception):
    """The verse could not be fetched. .hint is a short reason that is safe to show."""

    def __init__(self, hint, detail=""):
        super().__init__(f"{hint} [{detail}]" if detail else hint)
        self.hint = hint


def _load_cache():
    global _cache
    if _cache is None:
        try:
            _cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _cache = {}
    return _cache


def _save_cache():
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        temp = CACHE_FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(_load_cache(), ensure_ascii=False, indent=1), encoding="utf-8")
        temp.replace(CACHE_FILE)
    except OSError:
        pass  # the app still works without a cache, it just downloads again next time


def is_cached(reference):
    return reference in _load_cache()


def _ssl_context():
    """Use the certifi certificate list when it is installed (it fixes many Python
    installs that cannot verify websites); otherwise use Python's own."""
    global _context
    if _context is None:
        try:
            import certifi
            _context = ssl.create_default_context(cafile=certifi.where())
        except Exception:
            _context = ssl.create_default_context()
    return _context


def _explain(error):
    """Turn a network exception into a short, plain-English reason."""
    if isinstance(error, urllib.error.HTTPError):
        if error.code == 429:
            return "the Bible service says too many requests, wait a minute"
        return f"the Bible service answered with an error (HTTP {error.code})"
    reason = getattr(error, "reason", error)
    text = str(reason)
    if isinstance(reason, ssl.SSLCertVerificationError) or "CERTIFICATE_VERIFY_FAILED" in text:
        return "Python cannot verify the website's security certificate"
    if isinstance(reason, (socket.timeout, TimeoutError)):
        return "the connection timed out"
    if isinstance(reason, socket.gaierror):
        return "the website's address could not be found (no internet or a DNS problem)"
    if isinstance(reason, ConnectionRefusedError):
        return "the connection was refused (a firewall or proxy may be blocking it)"
    return f"{type(reason).__name__}: {text}"[:120]


def _fetch(reference):
    # spaces must be %20 (a '+' breaks names like "Song of Solomon")
    url = API_URL.format(ref=urllib.parse.quote(reference, safe=":-,"))
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; WordSelah/1.0)", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS, context=_ssl_context()) as reply:
            data = json.load(reply)
    except ValueError as error:
        raise BibleAPIError("the Bible service sent a reply the app could not read", repr(error)) from error
    except (urllib.error.URLError, OSError) as error:
        raise BibleAPIError(_explain(error), repr(error)) from error

    text = data.get("text") or " ".join(v.get("text", "") for v in data.get("verses", []))
    text = " ".join(text.split())  # verses come back separated by newlines
    if not text:
        raise BibleAPIError("the Bible service sent no verse text", str(data)[:120])
    return text


def get_verse(reference):
    """Return the KJV text for a reference such as 'Psalm 51:5-6'."""
    cache = _load_cache()
    if reference in cache:
        return cache[reference]
    text = _fetch(reference)
    cache[reference] = text
    _save_cache()
    return text


if __name__ == "__main__":
    import platform

    print("Python", platform.python_version(), "on", platform.platform())
    print("OpenSSL:", ssl.OPENSSL_VERSION)
    try:
        import certifi
        print("certifi: installed")
    except ImportError:
        print("certifi: not installed")
    print("Cache file:", CACHE_FILE, "(exists)" if CACHE_FILE.exists() else "(not created yet)")
    print("\nFetching John 3:16 from", API_URL.format(ref="John%203:16"), "...")
    try:
        print("OK ->", _fetch("John 3:16"))
    except BibleAPIError as error:
        print("FAILED:", error.hint)
        print("Details:", error)
        if "certificate" in error.hint:
            print("\nFix: on macOS open /Applications/Python 3.x/ and run 'Install Certificates.command', "
                  "or run: pip install certifi")
        elif "timed out" in error.hint or "address" in error.hint:
            print("\nFix: check the internet connection, VPN or proxy, then run this again.")
        print("\nPlease send me the three lines starting 'FAILED', 'Details' and 'Python'.")
