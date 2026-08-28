import urllib.request
import re

url = "https://m.cqg.com/cqg/desktop/main-Z5E3RK6Q.js"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    content = resp.read().decode("utf-8", errors="ignore")

for match in re.finditer(r"cwas\s*:\s*\{[^\}]+\}", content):
    print("cwas object:", match.group(0))

for match in re.finditer(r"authServer\s*:\s*\{[^\}]+\}", content):
    print("authServer object:", match.group(0))
