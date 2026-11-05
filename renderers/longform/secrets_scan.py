"""Search the OCR scan (probe/ocr_*.jsonl) for anything that looks like a secret or private detail."""
import json, re, glob
pat = re.compile(r"(sk[-_][a-z0-9]|pk_(live|test)|rk_|whsec|ghp_|github_pat|xai-|AKIA|api[_ -]?key|secret|passw|bearer|\.env\b|"
                 r"token\s*[:=]|[A-Za-z0-9_\-]{32,}|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}|\b\d{3}[-. ]\d{3}[-. ]\d{4}\b)", re.I)
seen = {}
for f in sorted(glob.glob("probe/ocr_*.jsonl")):
    for l in open(f, encoding="utf-8"):
        r = json.loads(l)
        m = pat.search(r["txt"])
        if m:
            k = r["txt"][:50]
            seen.setdefault(k, []).append(r["t"])
for k, ts in sorted(seen.items(), key=lambda kv: kv[1][0]):
    print(f"{ts[0]:7.1f}-{ts[-1]:7.1f} x{len(ts):<3} {k}")
