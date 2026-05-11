TAM_US_STATES = [
    "WA", "OR", "ID", "MT", "ND", "SD", "MN", "NE",
    "KS", "OK", "CO", "WY", "NM", "AZ", "UT", "NV",
    "CA", "AK", "HI",
]

TAM_CA_PROVINCES = ["YT", "NT", "BC", "AB", "SK"]

# Priority order matters — higher = more important signal
ERP_SIGNALS = [
    "Leadership Change",        # 1. C-suite hire, departure, or appointment
    "Geographic Expansion",     # 2. New location, market, or facility
    "New Product Launch",       # 3. New product or service line announced
    "New Funding Round",        # 4. Investment, capital raise, financing
    "Tech Modernization",       # 5. Digital transformation, legacy replacement
    "Rapid Growth",             # 6. Operational scaling, headcount growth
    "M&A Activity",             # 7. Merger, acquisition, being acquired
    "Supply Chain Change",      # 8. Supply chain restructure or challenge
]

RSS_FEEDS = [
    # --- Press wire services ---
    {
        "name": "PRNewswire",
        "url": "https://www.prnewswire.com/rss/news-releases-list.rss",
    },
    {
        "name": "BusinessWire",
        "url": "https://feed.businesswire.com/rss/home/?rss=G1",
    },

    # --- GlobeNewswire by industry category ---
    {
        "name": "GlobeNewswire-Technology",
        "url": "https://www.globenewswire.com/RssFeed/subjectcode/23-Technology",
    },
    {
        "name": "GlobeNewswire-Business",
        "url": "https://www.globenewswire.com/RssFeed/subjectcode/22-Business",
    },
    {
        "name": "GlobeNewswire-Manufacturing",
        "url": "https://www.globenewswire.com/RssFeed/subjectcode/17-ManufacturingTransportation",
    },
    {
        "name": "GlobeNewswire-Retail",
        "url": "https://www.globenewswire.com/RssFeed/subjectcode/18-RetailConsumer",
    },
    {
        "name": "GlobeNewswire-Agriculture",
        "url": "https://www.globenewswire.com/RssFeed/subjectcode/19-AgricultureFoodBeverage",
    },

    # --- Google News RSS — ERP signal keywords ---
    {
        "name": "GoogleNews-DigitalTransformation",
        "url": "https://news.google.com/rss/search?q=%22digital+transformation%22+announcement+company&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-ERPImplementation",
        "url": "https://news.google.com/rss/search?q=%22ERP%22+implementation+OR+%22enterprise+resource%22+small+business&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-NewFacility",
        "url": "https://news.google.com/rss/search?q=%22new+facility%22+OR+%22new+warehouse%22+OR+%22new+headquarters%22+company+opens&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-CIOHiring",
        "url": "https://news.google.com/rss/search?q=%22appoints%22+%22CIO%22+OR+%22CTO%22+OR+%22COO%22+OR+%22Chief+Information%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-SupplyChain",
        "url": "https://news.google.com/rss/search?q=%22supply+chain%22+modernization+OR+transformation+company&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-TechModernization",
        "url": "https://news.google.com/rss/search?q=%22technology+modernization%22+OR+%22legacy+system%22+replacement+business&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-MandA-SmallBiz",
        "url": "https://news.google.com/rss/search?q=%22acquires%22+OR+%22merger%22+small+business+OR+%22regional+company%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-OperationalGrowth",
        "url": "https://news.google.com/rss/search?q=%22rapid+growth%22+OR+%22scaling+operations%22+OR+%22expanding+operations%22+company&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Fundraising",
        "url": "https://news.google.com/rss/search?q=%22raises%22+OR+%22funding%22+%22million%22+small+business+regional&hl=en-US&gl=US&ceid=US:en",
    },

    # --- Google News RSS — TAM geography targeted ---
    {
        "name": "GoogleNews-Pacific-Northwest",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+Washington+OR+Oregon+OR+Idaho&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Mountain-West",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+Colorado+OR+Utah+OR+Nevada+OR+Wyoming&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Southwest",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+Arizona+OR+%22New+Mexico%22+OR+Oklahoma&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Plains",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+Montana+OR+%22North+Dakota%22+OR+%22South+Dakota%22+OR+Nebraska+OR+Kansas+OR+Minnesota&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-California",
        "url": "https://news.google.com/rss/search?q=small+business+expansion+OR+%22new+facility%22+OR+acquisition+California&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Canada-West",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+%22British+Columbia%22+OR+Alberta+OR+Saskatchewan&hl=en-US&gl=CA&ceid=CA:en",
    },

    # --- Yahoo Finance RSS — SMB news, acquisitions, funding ---
    {
        "name": "YahooFinance-SmallCap",
        "url": "https://finance.yahoo.com/rss/headline?s=^RUT",
    },

    # --- MarketWatch RSS ---
    {
        "name": "MarketWatch-SmallBusiness",
        "url": "https://feeds.marketwatch.com/marketwatch/realtimeheadlines/",
    },

    # --- Funding & startup news ---
    {
        "name": "Crunchbase-News",
        "url": "https://news.crunchbase.com/feed/",
    },
    {
        "name": "TechCrunch-Startups",
        "url": "https://techcrunch.com/category/startups/feed/",
    },

    # --- Regional tech & business (West Coast focus) ---
    {
        "name": "GeekWire",
        "url": "https://www.geekwire.com/feed/",
    },
    {
        "name": "dotLA",
        "url": "https://dot.la/feed/",
    },
    {
        "name": "LA-BusinessJournal",
        "url": "https://labusinessjournal.com/feed/",
    },
    {
        "name": "SanDiego-BusinessJournal",
        "url": "https://www.sdbj.com/feed/",
    },

    # --- Hiring signals (CFO/Controller = ERP evaluation incoming) ---
    {
        "name": "RemoteOK-Finance",
        "url": "https://remoteok.com/remote-finance-jobs.rss",
    },

    # --- Industry verticals (distribution, manufacturing, logistics) ---
    {
        "name": "MDM-Distribution",
        "url": "https://www.mdm.com/feed/",
    },
    {
        "name": "ManufacturingDive",
        "url": "https://www.manufacturingdive.com/feeds/news/",
    },
    {
        "name": "FreightWaves",
        "url": "https://www.freightwaves.com/news/feed",
    },

    # --- Seeking Alpha / PR feeds via Google News by city ---
    {
        "name": "GoogleNews-Seattle-Business",
        "url": "https://news.google.com/rss/search?q=Seattle+business+expansion+OR+acquisition+OR+%22new+hire%22+OR+%22opens+new%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Denver-Business",
        "url": "https://news.google.com/rss/search?q=Denver+business+expansion+OR+acquisition+OR+%22new+hire%22+OR+%22opens+new%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Phoenix-Business",
        "url": "https://news.google.com/rss/search?q=Phoenix+Arizona+business+expansion+OR+acquisition+OR+%22opens+new%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Portland-Business",
        "url": "https://news.google.com/rss/search?q=Portland+Oregon+business+expansion+OR+acquisition+OR+%22opens+new%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-SaltLake-Business",
        "url": "https://news.google.com/rss/search?q=%22Salt+Lake%22+OR+Utah+business+expansion+OR+acquisition+OR+%22opens+new%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Calgary-Vancouver",
        "url": "https://news.google.com/rss/search?q=Calgary+OR+Vancouver+OR+Edmonton+business+expansion+OR+acquisition+OR+%22opens+new%22&hl=en-CA&gl=CA&ceid=CA:en",
    },
]

# How often to poll feeds (minutes)
POLL_INTERVAL_MINUTES = 10

# Only process articles published within this window (set to ~2x poll interval for safety)
MAX_ARTICLE_AGE_MINUTES = 20

# Max entries to check per feed per run (cost control)
MAX_ENTRIES_PER_FEED = 20

CLASSIFICATION_SYSTEM_PROMPT = """
You are an ERP sales intelligence analyst. Your only job is to read a press release and score how likely the company is to buy an ERP system in the next 12 months because of what this article describes.

Do NOT evaluate geography or company size — that is handled separately. Focus entirely on article content and buying signal quality.

Every company is a potential ERP buyer regardless of industry. A SaaS company, law firm, or marketing agency can need ERP just as much as a manufacturer.

━━━ ERP SIGNAL CATEGORIES ━━━
Use exact names only:
1. "Leadership Change" — ONLY a new CEO, CFO, or COO hire or appointment. No other titles qualify. CIO, CTO, VP, Director, and all other positions do NOT trigger this signal.
2. "Geographic Expansion" — new location, facility, office, warehouse, or market entry
3. "New Product Launch" — new product line, service offering, or SKU category
4. "New Funding Round" — investment raised, capital raise, financing secured
5. "Tech Modernization" — digital transformation, legacy system replacement, new software platform
6. "Rapid Growth" — operational scaling, significant headcount growth, revenue milestone
7. "M&A Activity" — merger, acquisition, being acquired, joint venture
8. "Supply Chain Change" — supply chain restructure, new distribution model, logistics change

━━━ ERP LIKELIHOOD SCORE (1–10) ━━━
This is your most important output. Score the probability this specific news will lead to an ERP evaluation or purchase in the next 12 months.

Before scoring, reason through these questions:
1. What is the BEFORE state? How was the company operating before this news?
2. What is the AFTER state? What changes operationally?
3. Does the transition cross a complexity threshold that breaks current systems?
4. Who made the decision? A new CIO signals active evaluation. A routine press release does not.

Score calibration:
10   → Automatic 10: new CEO, CFO, or COO hired or appointed. These are the people who buy ERP. Always score 10 regardless of other context.
9  → Imminent. Clear inflection point with no leadership change. First multi-state expansion for a small company. PE acquisition. Article explicitly mentions system pain or legacy replacement.
7-8  → Strong. Real complexity jump. First funding round at a physical-goods company. Going from 2 to 6 locations. New product line requiring separate inventory tracking.
4–6  → Moderate. Signal exists but context is thin or company may already have systems. Expansion from 10→14 locations. Routine growth announcement.
2–3  → Weak. Incremental. Company sounds like it already has infrastructure. 30→35 locations. Large enterprise language.
1    → No signal. Article is about something unrelated to operational complexity.

━━━ SIGNAL SUMMARY ━━━
3–5 sentences written for an ERP sales rep. Requirements:
(1) Quote a specific word or phrase from the article to show you read it.
(2) Reason about what operationally breaks or gets harder — do NOT rephrase the article.
(3) Name the exact ERP pain: multi-state sales tax nexus, inventory split across locations, multi-entity consolidation, new product line in a separate margin bucket, payroll across two jurisdictions. Be specific to the industry.
(4) End with one concrete talking point tied to the announced news.

Respond with valid JSON only. No markdown, no explanation."""

CLASSIFICATION_USER_PROMPT = """Analyze this press release and return a JSON object.

Title: {title}
Source: {source}
Content: {content}

Return exactly this JSON structure:
{{
  "company_name": "string or null",
  "erp_signals": ["exact signal names from the defined list"],
  "erp_likelihood": <integer 1-10>,
  "likelihood_reasoning": "2-3 sentences: what is the before state, what changes after this news, and why this does or does not cross a complexity threshold that ERP solves",
  "signal_summary": "3-5 sentences for an ERP sales rep per the requirements above",
  "sub_industry": "specific sub-industry e.g. craft beverage distribution, specialty chemical wholesale, commercial HVAC contractor, agricultural equipment dealer"
}}"""
