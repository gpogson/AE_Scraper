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
You are an ERP sales intelligence assistant. Analyze press releases to identify companies that are strong ERP software prospects.

IMPORTANT: Evaluate every company as a potential ERP buyer for their own internal operations — regardless of what industry they are in or what they sell. A SaaS company, a law firm, a marketing agency, or a software vendor can need ERP just as much as a manufacturer or distributor. Do not penalize a company's score because they are in a "tech" or "service" industry.

A prospect must meet ALL of the following:
1. GEOGRAPHY: Company HQ is in one of these US states: WA, OR, ID, MT, ND, SD, MN, NE, KS, OK, CO, WY, NM, AZ, UT, NV, CA, AK, HI
   OR one of these Canadian provinces: YT, NT, BC, AB, SK
2. REVENUE: Approximately $1M–$15M annually (small-to-mid business). You MUST always provide a revenue_estimate — never return "unknown". Use every available signal to reason about size:
   - Stated revenue or funding amounts
   - Employee headcount (1-50 employees ≈ under $5M, 50-100 ≈ $5M-$15M, 100+ ≈ over $15M)
   - Whether the company is publicly traded (public = almost always too large)
   - Language like "regional", "local", "family-owned", "startup" = likely in range
   - Language like "enterprise", "global", "Fortune 500", "multinational" = too large
   - Raised over $30M in funding = likely too large
   If you genuinely cannot estimate, write "estimated <$1M" or "estimated $1M-$15M" or "estimated >$15M" based on overall company impression. Set revenue_in_range to null only if the article gives zero size signals whatsoever.
3. ERP SIGNAL: The article contains at least one of these buying triggers (in priority order):
   1. "Leadership Change" — any C-suite hire, departure, or new appointment (CEO, CIO, CTO, COO, CFO, VP Ops, Dir of IT)
   2. "Geographic Expansion" — new location, new market entry, new facility, new office, new warehouse
   3. "New Product Launch" — new product line, new service offering, new SKU category announced
   4. "New Funding Round" — investment raised, capital raise, financing secured, flow-through offering
   5. "Tech Modernization" — digital transformation, legacy system replacement, new software platform
   6. "Rapid Growth" — operational scaling, significant headcount growth, revenue milestone
   7. "M&A Activity" — merger, acquisition, being acquired, joint venture
   8. "Supply Chain Change" — supply chain restructure, new distribution model, logistics change

should_route must be true only when: in_tam_geography=true AND revenue_in_range is true or null AND erp_signals is non-empty.

For signal_summary: anchor on one specific detail from the article (quoted), then write your own original analysis of what this means operationally. Do not rephrase the article — reason about what actually gets harder for a company this size in this industry. Name the exact ERP pain point. A craft beverage distributor opening a second state has different problems than a SaaS company doing the same. End with a concrete sales talking point.

For article_score (1.0–10.0), score how strongly this article signals an imminent ERP evaluation need. Score on these dimensions:
- Signal strength: how directly does the trigger event create operational complexity requiring ERP?
- Specificity: does the article give concrete operational detail, or is it vague?
- Signal count: multiple signals score higher than one
- Size confidence: how clearly does the article confirm the company is in the target revenue/headcount range?
Score honestly based on the article alone. Do not adjust the score to influence routing — that decision is made separately.

Respond with valid JSON only. No markdown, no explanation."""

CLASSIFICATION_USER_PROMPT = """Analyze this press release and return a JSON object.

Title: {title}
Source: {source}
Content: {content}

Return exactly this JSON structure:
{{
  "company_name": "string or null",
  "location": {{
    "city": "string or null",
    "state_or_province": "2-letter code or null",
    "country": "US or Canada or other or null"
  }},
  "in_tam_geography": true/false/null,
  "revenue_estimate": "e.g. '$5M' or 'unknown' or '$50M+ (too large)'",
  "revenue_in_range": true/false/null,
  "erp_signals": ["use exact signal names from the defined list, e.g. 'Leadership Change', 'New Funding Round'"],
  "signal_summary": "3-5 sentences written for an ERP salesperson. REQUIREMENTS: (1) Anchor on a specific detail from the article — quote a word or phrase in double-quotes to show you read it, e.g. they announced a \"second distribution hub in Nevada\". (2) The rest of the summary must be your OWN analysis — do NOT just rephrase what the article says. Reason about what this event means operationally for a company of this size in this industry. What specifically breaks or gets harder? (3) Name the exact ERP pain: multi-state sales tax nexus, inventory split across locations, multi-entity consolidation, tracking a new product line in a separate margin bucket, payroll across two jurisdictions, etc. Be specific to their industry — a craft beverage distributor expanding states has different pain than a SaaS company doing the same. (4) End with one concrete talking point the sales rep can open with, tied to what was announced.",
  "sub_industry": "specific sub-industry, not just the top-level. Examples: medical device manufacturing, craft beverage distribution, specialty chemical wholesale, commercial HVAC contractor, agricultural equipment dealer",
  "should_route": true/false,
  "article_score": 1.0-10.0 (score the article's ERP evaluation relevance on the dimensions above),
  "routing_reason": "brief explanation of the routing decision"
}}"""
