TAM_US_STATES = ["AK", "CA", "HI", "ID", "NV", "OR", "UT", "WA"]

TAM_CA_PROVINCES = ["BC", "MB", "NT", "NU", "YT"]

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
    "New Sales Channel",        # 9. New retail distribution, wholesale, DTC, export
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

    # --- GlobeNewswire via Google News (direct RSS returns 403) ---
    {
        "name": "GlobeNewswire-Manufacturing",
        "url": "https://news.google.com/rss/search?q=site:globenewswire.com+manufacturer+OR+manufacturing+when:1d&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GlobeNewswire-Retail",
        "url": "https://news.google.com/rss/search?q=site:globenewswire.com+retailer+OR+%22consumer+brand%22+OR+%22consumer+products%22+when:1d&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GlobeNewswire-Agriculture",
        "url": "https://news.google.com/rss/search?q=site:globenewswire.com+agriculture+OR+%22food+and+beverage%22+OR+brewery+OR+winery+when:1d&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GlobeNewswire-Distribution",
        "url": "https://news.google.com/rss/search?q=site:globenewswire.com+distributor+OR+%22wholesale+distribution%22+when:1d&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GlobeNewswire-Business",
        "url": "https://news.google.com/rss/search?q=site:globenewswire.com+acquisition+OR+expansion+OR+appoints+OR+funding+when:1d&hl=en-US&gl=US&ceid=US:en",
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
        "name": "GoogleNews-Utah-Nevada",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+Utah+OR+Nevada&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Alaska-Hawaii",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+Alaska+OR+Hawaii&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-California",
        "url": "https://news.google.com/rss/search?q=manufacturer+OR+brand+OR+distributor+expansion+OR+%22new+facility%22+OR+acquisition+California&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Canada-West",
        "url": "https://news.google.com/rss/search?q=business+expansion+OR+%22new+facility%22+OR+acquisition+%22British+Columbia%22+OR+Manitoba+OR+Yukon+OR+%22Northwest+Territories%22+OR+Nunavut&hl=en-US&gl=CA&ceid=CA:en",
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

    # --- Manufacturing trade publications ---
    {
        "name": "ManufacturingDive",
        "url": "https://www.manufacturingdive.com/feeds/news/",
    },
    {
        "name": "ManufacturingNet",
        "url": "https://www.manufacturing.net/rss/all",
    },
    {
        "name": "TheFabricator",
        "url": "https://www.thefabricator.com/thefabricator/rss",
    },
    {
        "name": "AssemblyMag",
        "url": "https://www.assemblymag.com/rss/all",
    },
    {
        "name": "PlantEngineering",
        "url": "https://www.plantengineering.com/rss/all",
    },
    {
        "name": "ModernMachineShop",
        "url": "https://www.mmsonline.com/rss",
    },

    # --- Food & beverage manufacturing ---
    {
        "name": "FoodProcessing",
        "url": "https://www.foodprocessing.com/rss/",
    },
    {
        "name": "FoodEngineering",
        "url": "https://www.foodengineeringmag.com/rss/all",
    },
    {
        "name": "BeverageIndustry",
        "url": "https://www.bevindustry.com/rss/all",
    },
    {
        "name": "BrewingIndustryGuide",
        "url": "https://www.brewbound.com/feed",
    },

    # --- Plastics, packaging, wood, building products ---
    {
        "name": "PlasticsToday",
        "url": "https://www.plasticstoday.com/rss.xml",
    },
    {
        "name": "WoodworkingNetwork",
        "url": "https://www.woodworkingnetwork.com/rss.xml",
    },
    {
        "name": "PackagingWorld",
        "url": "https://www.packworld.com/rss.xml",
    },

    # --- Canadian manufacturing ---
    {
        "name": "CanadianManufacturing",
        "url": "https://www.canadianmanufacturing.com/feed/",
    },
    {
        "name": "CanadianMetalworking",
        "url": "https://www.canadianmetalworking.com/rss",
    },

    # --- Distribution & logistics ---
    {
        "name": "MDM-Distribution",
        "url": "https://www.mdm.com/feed/",
    },
    {
        "name": "FreightWaves",
        "url": "https://www.freightwaves.com/news/feed",
    },

    # --- Google News RSS — manufacturers in TAM by region ---
    {
        "name": "GoogleNews-Manufacturer-PNW",
        "url": "https://news.google.com/rss/search?q=manufacturer+OR+%22manufacturing+plant%22+expansion+OR+%22new+facility%22+OR+acquisition+Washington+OR+Oregon+OR+Idaho&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Manufacturer-Mountain",
        "url": "https://news.google.com/rss/search?q=manufacturer+OR+%22manufacturing+plant%22+expansion+OR+%22new+facility%22+OR+acquisition+Colorado+OR+Utah+OR+Arizona+OR+Nevada&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Manufacturer-California",
        "url": "https://news.google.com/rss/search?q=manufacturer+OR+%22manufacturing+facility%22+expansion+OR+%22new+plant%22+OR+acquisition+California&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Manufacturer-Plains",
        "url": "https://news.google.com/rss/search?q=manufacturer+OR+%22manufacturing+plant%22+expansion+OR+%22new+facility%22+OR+acquisition+Montana+OR+%22North+Dakota%22+OR+Nebraska+OR+Kansas+OR+Minnesota&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-Manufacturer-Canada-West",
        "url": "https://news.google.com/rss/search?q=manufacturer+OR+%22manufacturing+plant%22+expansion+OR+%22new+facility%22+OR+acquisition+%22British+Columbia%22+OR+Alberta+OR+Saskatchewan&hl=en-CA&gl=CA&ceid=CA:en",
    },

    # --- Google News RSS — manufacturing sub-verticals ---
    {
        "name": "GoogleNews-FoodBevManufacturer",
        "url": "https://news.google.com/rss/search?q=%22food+manufacturer%22+OR+%22beverage+manufacturer%22+OR+%22food+production%22+OR+brewery+OR+winery+expansion+OR+acquisition+OR+%22new+facility%22+-cannabis+-marijuana+-dispensary&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-MetalFab",
        "url": "https://news.google.com/rss/search?q=%22metal+fabricat%22+OR+%22steel+fabricat%22+OR+%22precision+machining%22+OR+%22metal+manufacturer%22+expansion+OR+acquisition+OR+%22new+facility%22+-automotive+-%22auto+parts%22+-OEM&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-PlasticsManufacturer",
        "url": "https://news.google.com/rss/search?q=%22plastics+manufacturer%22+OR+%22injection+molding%22+OR+%22plastic+fabricat%22+expansion+OR+acquisition+OR+%22new+facility%22+-cannabis+-marijuana+-automotive&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-BuildingProducts",
        "url": "https://news.google.com/rss/search?q=%22building+products%22+OR+%22wood+products%22+OR+lumber+OR+millwork+manufacturer+expansion+OR+acquisition+OR+%22new+facility%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-AgriManufacturer",
        "url": "https://news.google.com/rss/search?q=%22agricultural+equipment%22+OR+%22farm+equipment%22+OR+%22agri+manufacturer%22+expansion+OR+acquisition+OR+%22new+facility%22&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-ContractManufacturer",
        "url": "https://news.google.com/rss/search?q=%22contract+manufacturer%22+OR+%22contract+manufacturing%22+expansion+OR+acquisition+OR+%22new+facility%22+-cannabis+-marijuana+-automotive&hl=en-US&gl=US&ceid=US:en",
    },
    {
        "name": "GoogleNews-ManufacturingERP",
        "url": "https://news.google.com/rss/search?q=manufacturer+%22ERP%22+OR+%22enterprise+software%22+OR+%22digital+transformation%22+OR+%22legacy+system%22+-cannabis+-automotive&hl=en-US&gl=US&ceid=US:en",
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

# Only process articles published within this window. Google News sorts by relevance, not
# recency, so this must be wide; is_seen() dedup prevents reprocessing across runs.
MAX_ARTICLE_AGE_MINUTES = 1440

# Max entries to check per feed per run (cost control)
MAX_ENTRIES_PER_FEED = 20

# Only route leads whose classifier-assigned industry_vertical is in this set
ROUTE_INDUSTRY_VERTICALS = {"products"}

CLASSIFICATION_SYSTEM_PROMPT = """
You are an ERP sales intelligence analyst. Read a press release and judge how strongly it signals that the company is growing, or is about to change how it operates, in ways that stretch its current systems. Those moments — happening now OR being planned — are when companies start evaluating ERP, and a rep wants to hear about them early.

Do NOT evaluate geography or company size — that is handled separately. Focus entirely on article content and buying signal quality.

Industry fit is judged separately via industry_vertical below — score erp_likelihood purely on what the article describes.

DO NOT score cannabis/marijuana companies or large automotive OEMs (Ford, GM, Toyota, Stellantis, etc.). Score these 1 and leave erp_signals empty.

━━━ ERP SIGNAL CATEGORIES ━━━
Use exact names only. Every signal counts whether it has HAPPENED or is PLANNED (announced plans, intent, groundbreaking, land purchase or permits for a facility, hiring ahead of an opening, "plans to", "will open", "expects to").
1. "Leadership Change" — ONLY a new CEO, CFO, or COO hire or appointment. No other titles qualify.
2. "Geographic Expansion" — a new operating location (plant, warehouse, distribution center, flagship or retail store, office) or entry into a new state, province, or country. Government land trust/status changes do not count.
3. "New Product Launch" — a new product line or category, especially one needing new ingredients, suppliers, or production
4. "New Sales Channel" — new retail distribution (e.g. Costco, Whole Foods, Target, regional grocery chains), first wholesale accounts, launching DTC/ecommerce, exporting, new marketplace
5. "New Funding Round" — investment raised, capital raise, financing secured or being sought
6. "Tech Modernization" — digital transformation, legacy system replacement, new software platform, outgrowing current tools
7. "Rapid Growth" — capacity expansion, hiring push, revenue milestone, or recognition that reflects growth (awards, "best of" honors, fastest-growing rankings)
8. "M&A Activity" — merger, acquisition, being acquired, joint venture
9. "Supply Chain Change" — new co-manufacturer, supplier, distribution model, or logistics change

━━━ ERP LIKELIHOOD SCORE (1–10) ━━━
This is your most important output. Use JUDGMENT — the bands below are guides, not a checklist. Ask:
1. What is the company like now (size, stage, how it likely runs today)?
2. What is changing or about to change?
3. Will that stretch how it tracks inventory, orders, locations, entities, or finances?
4. Read between the lines: what does this news imply about where the company is headed?

Guide bands:
9–10 → Act now. New CEO, CFO, or COO (always 10). Being acquired or taking PE/strategic investment. Acquiring another business. Article mentions system pain or outgrowing current tools.
7–8  → Real milestone, happening or planned: new facility, plant, warehouse, or flagship/retail store; entering a new state or country; landing a major retail or new sales channel; a new product line needing new production; any funding round; doubling capacity or a hiring push; a fastest-growing ranking (e.g. Inc. 5000) or award that cites big revenue or demand growth.
5–6  → Growth indicator. Momentum without a concrete operational change yet — e.g. a "best of" or brand award, a press feature on rapid growth, a notable partnership.
4–5  → A product, taste, or design award with no growth context still hints the brand is getting noticed — score it here, not lower.
2–3  → Minor. Single flavor/SKU extension, routine hire below C-suite, charity or community news.
1    → Nothing about the company's growth or operations.

Adjust with judgment:
- Raise a step for "firsts" — first plant, first retail store, first out-of-state location, first funding, first major retailer. These are when spreadsheets and QuickBooks stop being enough.
- Raise when multiple signals stack (e.g. an award PLUS mentions of expansion plans or surging demand can reach 7).
- An award or ranking that is explicitly about growth (e.g. fastest-growing company lists, revenue growth) is worth more than one about taste or design.
- Planned events score about the same as completed ones. Lower a step only if the plan is vague or more than ~2 years out.
- Lower when the company sounds large, established, or already enterprise-grade.

━━━ INDUSTRY VERTICAL ━━━
Use common sense — does this company's business revolve around physical products?
- "products" — it makes, grows, distributes, or sells physical goods (manufacturers, food & beverage producers, farms, wholesale distributors, consumer brands, retailers, commercial printers).
- "services" — it mainly sells services, software, or expertise (SaaS, consulting, agencies, staffing/recruiting, financial, legal, healthcare providers, contractors, logistics). Also "services": real estate companies, REITs, landlords, investment/holding companies, and mineral or energy royalty owners — owning assets is not making products.
Vehicle dealers (auto, boat, RV, motorcycle, ATV) count as "services".
- "excluded" — never a prospect: governments of any kind (tribal governments/nations, cities, counties, states, agencies), schools and universities, nonprofits and associations, and mining companies (mineral exploration, mining, quarrying — including gold/silver/lithium/copper explorers).
Judge by what the company IS, not by what the article mentions. If it does both, choose what drives most of its revenue.

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
  "signal_stage": "planned" or "completed",
  "trigger_event": "one short phrase naming what happened or is planned, e.g. 'Opening first flagship store in Portland (planned, spring 2027)'",
  "likelihood_reasoning": "2-3 sentences: where the company is now, what is changing or planned, and how that stretches its current systems",
  "signal_summary": "3-5 sentences for an ERP sales rep per the requirements above",
  "industry_vertical": "products", "services", or "excluded",
  "sub_industry": "specific sub-industry e.g. craft beverage distribution, specialty chemical wholesale, commercial HVAC contractor, agricultural equipment dealer"
}}"""
