"""Upload dev/epubs/*.epub into the local dev instance (admin/admin123)."""

import http.cookiejar
import re
import sys
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8083"
jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def csrf(path):
    html = opener.open(BASE + path).read().decode()
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


token = csrf("/login")
opener.open(BASE + "/login", urllib.parse.urlencode(
    {"username": "admin", "password": "admin123", "csrf_token": token, "remember_me": "on", "submit": ""}).encode())

for epub in sorted((Path(__file__).parent / "epubs").glob("*.epub")):
    token = csrf("/")
    boundary = uuid.uuid4().hex
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"csrf_token\"\r\n\r\n{token}\r\n"
            f"--{boundary}\r\nContent-Disposition: form-data; name=\"btn-upload\"; filename=\"{epub.name}\"\r\n"
            f"Content-Type: application/epub+zip\r\n\r\n").encode() + epub.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(BASE + "/upload", body, {"Content-Type": f"multipart/form-data; boundary={boundary}",
                                                          "X-CSRFToken": token, "Referer": BASE + "/"})
    print(epub.name, opener.open(req).status)
