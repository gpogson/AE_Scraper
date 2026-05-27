"""Quick test — shows what Serper.dev returns from ZoomInfo then runs full enrichment."""

import sys, os, re, requests
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv
load_dotenv()

from enricher import enrich_company

company = "Knife River Corporation"
strip_tags = re.compile(r"<[^>]+>")

print(f"Testing ZoomInfo enrichment for: {company}")
print("="*60)

api_key = os.environ.get("SERPER_API_KEY", "")
resp = requests.post(
    "https://google.serper.dev/search",
    json={"q": f'"{company}" site:zoominfo.com/c/', "num": 5},
    headers={"X-API-KEY": api_key, "Content-Type": "application/json"},
    timeout=10,
)
data = resp.json()

print(f"\nHTTP {resp.status_code}")

print("\n--- Organic result snippet ---")
for r in data.get("organic", []):
    if "zoominfo.com" in r.get("link", ""):
        print(f"  {r.get('snippet')}")
        break

keep = {"revenue", "employee", "headquarter", "address", "location", "industry", "founded", "size", "website"}
skip = {"email", "phone", "work in", "work for", "contact", "role in", "latest job",
        "direct phone", "colleague", "based", "education", "stock symbol", "naics",
        "sic code", "competition", "social media", "acquired", "technology"}

print("\n--- People Also Ask (filtered — what gets sent to GPT) ---")
for faq in data.get("peopleAlsoAsk", []):
    q = faq.get("question", "")
    ql = q.lower()
    if any(s in ql for s in skip):
        continue
    if any(k in ql for k in keep):
        a = strip_tags.sub("", faq.get("snippet", "")).strip()
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
