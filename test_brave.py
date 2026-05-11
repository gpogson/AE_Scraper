"""Quick test — shows what Brave returns from ZoomInfo then runs full enrichment."""

import sys, os, re, requests
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from enricher import enrich_company

company = "Knife River Corporation"
strip_tags = re.compile(r"<[^>]+>")

print(f"Testing ZoomInfo enrichment for: {company}")
print("="*60)

api_key = os.environ.get("BRAVE_API_KEY", "")
resp = requests.get(
    "https://api.search.brave.com/res/v1/web/search",
    params={"q": f'"{company}" site:zoominfo.com', "count": 3},
    headers={"Accept": "application/json", "Accept-Encoding": "gzip", "X-Subscription-Token": api_key},
    timeout=10,
)
data = resp.json()

print(f"\nHTTP {resp.status_code}")

print("\n--- Web result description ---")
for r in data.get("web", {}).get("results", []):
    if "zoominfo.com" in r.get("url", ""):
        print(f"  {r.get('description')}")
        break

keep = {"revenue", "employee", "headquarter", "address", "location", "industry", "founded", "size", "website"}
skip = {"email", "phone", "work in", "work for", "contact", "role in", "latest job",
        "direct phone", "colleague", "based", "education", "stock symbol", "naics",
        "sic code", "competition", "social media", "acquired", "technology"}

print("\n--- FAQ cards (filtered — what gets sent to GPT) ---")
for faq in data.get("faq", {}).get("results", []):
    q = faq.get("question", "")
    ql = q.lower()
    if any(s in ql for s in skip):
        continue
    if any(k in ql for k in keep):
        a = strip_tags.sub("", faq.get("answer", "")).strip()
        print(f"  Q: {q}")
        print(f"  A: {a}")
        print()

print("\n" + "="*60)
print("Final enrichment result:")
result = enrich_company(company)
if result:
    print(f"  HQ:        {result.get('hq_city')}, {result.get('hq_state_or_province')}, {result.get('hq_country')}")
    print(f"  Employees: {result.get('employee_count')}")
    print(f"  Revenue:   {result.get('estimated_revenue')}")
    print(f"  Industry:  {result.get('industry')}")
else:
    print("  enrich_company() returned None")
