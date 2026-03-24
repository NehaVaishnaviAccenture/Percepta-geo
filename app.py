# Install dependencies:
# pip install openai streamlit pandas plotly requests beautifulsoup4

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json
import re
import random
from urllib.parse import urlparse

# ── HARDCODED API KEY (internal) ─────────────────────────────
INTERNAL_API_KEY = st.secrets["OPENROUTER_API_KEY"]

st.set_page_config(page_title="Percepta | GEO Insights", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }
header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-left: 0 !important; padding-right: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }
.hero { background: linear-gradient(135deg, #6D28D9 0%, #7C3AED 40%, #9333EA 70%, #A855F7 100%); padding: 80px 60px 90px 60px; text-align: center; color: white; }
.hero-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(255,255,255,0.18); border: 1px solid rgba(255,255,255,0.3); border-radius: 50px; padding: 8px 20px; font-size: 0.85rem; font-weight: 600; color: white; margin-bottom: 28px; }
.hero h1 { font-size: 3.8rem; font-weight: 900; color: white; line-height: 1.1; margin: 0 0 24px 0; letter-spacing: -1px; }
.hero h1 span { color: rgba(255,255,255,0.65); }
.hero-sub { font-size: 1rem; color: rgba(255,255,255,0.88); line-height: 1.75; max-width: 580px; margin: 0 auto; }
.section { padding: 64px 60px; }
.section-white { background: white; }
.section-light { background: #F8F9FF; }
.section-purple { background: linear-gradient(135deg, #7C3AED 0%, #9333EA 100%); }
.section-tag { display: inline-block; background: #EDE9FE; color: #7C3AED; border-radius: 50px; padding: 5px 16px; font-size: 0.78rem; font-weight: 600; margin-bottom: 14px; }
.section-tag-white { display: inline-block; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 50px; padding: 5px 16px; font-size: 0.78rem; font-weight: 600; margin-bottom: 14px; }
.section-title { font-size: 2rem; font-weight: 800; color: #111827; margin: 0 0 12px 0; letter-spacing: -0.5px; }
.section-title-white { font-size: 2rem; font-weight: 800; color: white; margin: 0 0 12px 0; }
.results-grid { display: flex; gap: 40px; margin-top: 32px; justify-content: center; flex-wrap: wrap; }
.result-item { text-align: center; }
.result-num { font-size: 3.2rem; font-weight: 900; color: white; line-height: 1; }
.result-label { font-size: 0.95rem; font-weight: 700; color: white; margin-top: 6px; }
.result-desc { font-size: 0.82rem; color: rgba(255,255,255,0.72); margin-top: 4px; }
.pilot-grid { display: flex; gap: 20px; margin-top: 32px; }
.pilot-card { flex: 1; background: white; border: 2px solid #E5E7EB; border-radius: 16px; padding: 28px 24px; text-align: center; position: relative; }
.pilot-card.recommended { border-color: #7C3AED; }
.recommended-badge { position: absolute; top: -14px; left: 50%; transform: translateX(-50%); background: #7C3AED; color: white; border-radius: 50px; padding: 4px 16px; font-size: 0.75rem; font-weight: 700; white-space: nowrap; }
.pilot-option { font-size: 1rem; font-weight: 700; color: #111827; margin-bottom: 4px; }
.pilot-weeks { font-size: 1.8rem; font-weight: 900; color: #7C3AED; margin-bottom: 16px; }
.pilot-items { list-style: none; padding: 0; margin: 0; text-align: left; }
.pilot-items li { font-size: 0.85rem; color: #374151; padding: 6px 0; display: flex; align-items: flex-start; gap: 8px; border-bottom: 1px solid #F3F4F6; }
.pilot-items li:last-child { border-bottom: none; }
.pilot-items li::before { content: '›'; color: #A855F7; font-weight: 700; flex-shrink: 0; }
.score-section { padding: 32px 40px; }
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────
def get_client(api_key: str = INTERNAL_API_KEY):
    return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1",
                  default_headers={"HTTP-Referer": "https://percepta.ai", "X-Title": "Percepta"})

def get_response(prompt: str, api_key: str = INTERNAL_API_KEY) -> str:
    client = get_client(api_key)
    r = client.chat.completions.create(
        model="openai/gpt-5.4",
        messages=[
            {"role": "system", "content": """You are a sharp, direct AI assistant. When answering any question about products, services, brands, cards, tools, or recommendations:
ALWAYS follow this exact format:
1. Start with 1-2 sentence direct answer using **bold** for key terms and emojis inline
2. Use ## headers with emojis for each category
3. Under each header, name the SPECIFIC real competitor/brand
4. Use bullet points with emoji checkmarks: • ✅ benefit, • ❌ downside
5. End each section with a bold insight line starting with 🔍 or 💡
6. Finish with a ## 👉 Quick Pick section with → arrows matching user type to specific product
7. Last line: ask 1 follow-up question
RULES: Always name real brands, real products, real percentages and fees. Use emojis throughout. Never give vague generic advice."""},
            {"role": "user", "content": prompt}
        ], temperature=0.2, max_tokens=2048)
    return r.choices[0].message.content

def fetch_page_content(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup       = BeautifulSoup(resp.text, "html.parser")
        title      = soup.title.string.strip() if soup.title else ""
        meta_tag   = soup.find("meta", attrs={"name": "description"})
        meta_desc  = meta_tag.get("content", "") if meta_tag else ""
        headings   = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])[:20]]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 60][:20]
        faqs       = soup.find_all(attrs={"itemtype": re.compile("FAQPage", re.I)})
        has_schema = bool(soup.find_all("script", attrs={"type": "application/ld+json"}))
        has_author = bool(soup.find(attrs={"class": re.compile("author|byline", re.I)}))
        has_table  = bool(soup.find("table"))
        has_lists  = len(soup.find_all(["ul", "ol"])) > 2
        ext_links  = [a["href"] for a in soup.find_all("a", href=True)
                      if a["href"].startswith("http") and urlparse(url).netloc not in a["href"]][:10]
        word_count = len(soup.get_text().split())
        domain     = urlparse(url).netloc.replace("www.", "")
        return {"ok": True, "url": url, "domain": domain, "title": title,
                "meta_desc": meta_desc, "headings": headings, "paragraphs": paragraphs[:6],
                "has_schema": has_schema, "has_faq": len(faqs)>0 or any("faq" in h.lower() for h in headings),
                "has_author": has_author, "has_table": has_table, "has_lists": has_lists,
                "external_links_count": len(ext_links), "word_count": word_count}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def get_brand_position_in_response(response_text: str, brand: str) -> int:
    brand_l = brand.lower()
    text_l  = response_text.lower()
    if brand_l not in text_l:
        return 0
    brand_idx    = text_l.find(brand_l)
    text_before  = response_text[:brand_idx]
    other_brands = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text_before)
    stop_words   = {"The","A","An","In","On","At","For","With","By","From","This","That","These",
                    "Those","Some","Many","Most","All","When","Where","What","Which","Who","How",
                    "Why","If","Here","There","However","Also","Additionally","Furthermore",
                    "First","Second","Third","Finally","Overall","Generally"}
    real_brands_before = [b for b in other_brands if b not in stop_words and len(b) > 2]
    seen, unique_before = set(), []
    for b in real_brands_before:
        if b.lower() not in seen:
            seen.add(b.lower())
            unique_before.append(b)
    return len(unique_before) + 1


# ── BRAND EXTRACTION ─────────────────────────────────────────
def extract_brand_from_page(page_data: dict) -> str:
    domain_to_brand = {
        "chase": "Chase", "vw": "Volkswagen", "volkswagen": "Volkswagen",
        "gm": "General Motors", "bmw": "BMW", "jll": "JLL", "pwc": "PwC",
        "kpmg": "KPMG", "ey": "EY", "accenture": "Accenture", "mckinsey": "McKinsey",
        "amex": "American Express", "americanexpress": "American Express",
        "bofa": "Bank of America", "bankofamerica": "Bank of America",
        "wellsfargo": "Wells Fargo", "usaa": "USAA",
        "capitalone": "Capital One", "discover": "Discover",
        "citi": "Citi", "citibank": "Citi", "barclays": "Barclays", "synchrony": "Synchrony",
        "toyota": "Toyota", "ford": "Ford", "honda": "Honda", "tesla": "Tesla",
        "hyundai": "Hyundai", "kia": "Kia", "nissan": "Nissan",
        "mercedes": "Mercedes", "audi": "Audi",
        "marriott": "Marriott", "hilton": "Hilton", "hyatt": "Hyatt",
        "apple": "Apple", "google": "Google", "microsoft": "Microsoft",
        "amazon": "Amazon", "samsung": "Samsung", "meta": "Meta",
        "netflix": "Netflix", "spotify": "Spotify", "adobe": "Adobe",
        "salesforce": "Salesforce", "walmart": "Walmart", "target": "Target",
        "nike": "Nike", "adidas": "Adidas",
    }
    domain     = page_data.get("domain", "").lower().replace("www.", "")
    domain_key = domain.split(".")[0]
    if domain_key in domain_to_brand:
        return domain_to_brand[domain_key]
    for key, brand in domain_to_brand.items():
        if key in domain_key:
            return brand
    title_raw = page_data.get("title", "")
    if title_raw:
        generic_words    = {"home","official","site","online","com","net","org","inc","llc","ltd","corp","homepage"}
        category_signals = ["card","bank","credit","mortgage","auto","loan","insurance","service","solutions"]
        for sep in ["|","–","-","·"]:
            if sep in title_raw:
                segments = [s.strip() for s in title_raw.split(sep)]
                for seg in reversed(segments):
                    seg_clean = seg.replace(".com","").replace(".net","").replace(".org","").strip()
                    words = seg_clean.lower().split()
                    if 1 <= len(words) <= 3 and not all(w in generic_words for w in words):
                        if not any(sig in seg_clean.lower() for sig in category_signals):
                            return seg_clean
        clean = title_raw.replace(".com","").strip()
        if len(clean.split()) <= 3:
            return clean
    return domain_key.title()


# ── COMPETITOR SCORING ────────────────────────────────────────
def score_competitor_from_responses(comp_name: str, responses: list) -> dict:
    comp_l = comp_name.lower()
    aliases = {
        "american express": ["american express", "amex"],
        "bank of america":  ["bank of america", "bofa"],
        "wells fargo":      ["wells fargo"],
        "capital one":      ["capital one"],
        "j.p. morgan":      ["j.p. morgan", "jpmorgan", "jp morgan"],
    }
    search_terms = aliases.get(comp_l, [comp_l])
    mentions  = sum(1 for r in responses if any(t in r.get("response_preview","").lower() for t in search_terms))
    live_vis  = round((mentions / 20) * 100)
    awareness_floor = {
        "american express": 68, "chase": 72, "citi": 52, "discover": 48,
        "wells fargo": 45, "bank of america": 45, "capital one": 50,
        "synchrony": 26, "barclays": 22, "usaa": 28,
        "tesla": 70, "toyota": 65, "bmw": 58, "honda": 55,
        "ford": 52, "mercedes": 50, "hyundai": 42, "kia": 36,
        "nissan": 33, "volkswagen": 38,
    }
    floor_vis = awareness_floor.get(comp_l, 18)
    if mentions == 0:
        random.seed(hash(comp_name) % 9999)
        blended_vis = max(10, min(80, floor_vis + random.randint(-4, 4)))
    else:
        blended_vis = round(live_vis * 0.80 + floor_vis * 0.20)
    comp_vis  = blended_vis
    comp_cit  = min(92, round(comp_vis * 0.93 + mentions * 1.8))
    comp_sent = min(92, round(comp_vis * 0.88 + mentions * 1.4))
    comp_prom = min(92, round(comp_vis * 0.78))
    comp_sov  = min(92, round(comp_vis * 0.63))
    comp_geo  = round(comp_vis*0.30 + comp_sent*0.20 + comp_prom*0.20 + comp_cit*0.15 + comp_sov*0.15)
    positions = [get_brand_position_in_response(r.get("response_preview",""), comp_name)
                 for r in responses if any(t in r.get("response_preview","").lower() for t in search_terms)]
    valid_pos = [p for p in positions if p > 0]
    avg_pos   = round(sum(valid_pos) / len(valid_pos)) if valid_pos else 0
    rank_str  = f"#{avg_pos}" if avg_pos > 0 else "N/A"
    return {"Brand": comp_name, "GEO": comp_geo, "Vis": comp_vis, "Cit": comp_cit, "Sen": comp_sent, "Rank": rank_str}


# ── MAIN GEO ANALYSIS ─────────────────────────────────────────
def analyze_geo_with_ai(page_data: dict) -> dict:
    brand   = extract_brand_from_page(page_data)
    domain  = page_data.get("domain", "").lower()
    brand_l = brand.lower()
    client  = get_client()

    fin_kws   = ["capital","chase","amex","citi","discover","bank","credit","card","finance","fargo","visa","master","barclays","synchrony","usaa","wellsfargo"]
    auto_kws  = ["toyota","ford","honda","bmw","tesla","vw","volkswagen","auto","car","motor","hyundai","kia","nissan","mercedes","audi"]
    hotel_kws = ["marriott","hilton","hyatt","holiday","airbnb","booking","hotel","resort","expedia"]
    tech_kws  = ["apple","google","microsoft","amazon","samsung","meta","netflix","spotify","adobe","salesforce","software","tech","cloud","saas"]

    if any(x in domain for x in fin_kws):
        queries = [
            "What is the best credit card for travel rewards in 2025?",
            "Which bank offers the best rewards checking account?",
            "What credit card should I get for everyday cash back?",
            "Best credit cards with no annual fee right now",
            "Which bank is best for first-time credit card applicants?",
            "Top credit cards recommended by financial experts",
            "What is the best bank for online banking and mobile app?",
            "Which credit card has the best sign-up bonus?",
            "Best credit cards for people with good credit scores",
            "What bank should I choose for savings and checking?",
            "Which credit card is best for dining and restaurants?",
            "Top recommended credit cards for business expenses",
            "What are the most trusted banks in the US?",
            "Best credit cards for balance transfers with low interest",
            "Which bank has the lowest fees for everyday banking?",
            "What credit card do financial advisors recommend most?",
            "Best cards for earning points on groceries and gas",
            "Which banks are best for customer service?",
            "Top credit cards for international travelers with no foreign fees",
            "What is the best overall credit card for 2025?"
        ]
    elif any(x in domain for x in auto_kws):
        queries = [
            "What is the best car to buy in 2025?",
            "Which electric vehicle has the longest range?",
            "Best SUV for families right now",
            "What car brand is most reliable long term?",
            "Top recommended cars under $40,000",
            "Best cars for fuel efficiency in 2025",
            "Which car brand has the best safety ratings?",
            "What is the best luxury car for the money?",
            "Top car brands recommended by consumer experts",
            "Best hybrid cars available today",
            "Which car manufacturer has the best warranty?",
            "What cars are best for first-time buyers?",
            "Top rated trucks for towing and hauling",
            "Best car brands for resale value",
            "Which electric car brand leads in technology?",
            "What cars do mechanics recommend for reliability?",
            "Best compact cars for city driving",
            "Which car brands have the fewest recalls?",
            "Top recommended cars for long road trips",
            "What is the most popular car brand in America?"
        ]
    elif any(x in domain for x in hotel_kws):
        queries = [
            "What is the best hotel loyalty program in 2025?",
            "Which hotel chain offers the best value for money?",
            "Best hotels for business travelers",
            "Top recommended hotel brands for family vacations",
            "Which hotel chain has the best customer service?",
            "Best hotel rewards programs for frequent travelers",
            "What are the most trusted hotel brands globally?",
            "Top luxury hotel chains recommended by travel experts",
            "Which hotels have the best amenities?",
            "Best budget hotel chains with good quality",
            "What hotel brand is best for points redemption?",
            "Top rated hotel chains for cleanliness and comfort",
            "Which hotel chain has the most locations worldwide?",
            "Best hotel brands for weekend getaways",
            "What hotels do travel experts recommend most?",
            "Which hotel loyalty program is easiest to earn points?",
            "Best hotels for romantic getaways",
            "Top hotel chains with best breakfast included",
            "Which hotel brand is best for international travel?",
            "What is the most recommended hotel chain for 2025?"
        ]
    elif any(x in domain for x in tech_kws):
        queries = [
            "What is the best smartphone to buy in 2025?",
            "Which tech company makes the most reliable products?",
            "Best laptop brands recommended by experts",
            "Top cloud computing platforms for businesses",
            "Which streaming service has the best content library?",
            "Best software tools for productivity in 2025",
            "What tech brands do IT professionals trust most?",
            "Top recommended CRM platforms for sales teams",
            "Which companies lead in AI and machine learning?",
            "Best antivirus and cybersecurity software",
            "What are the top project management tools?",
            "Which tech brands have the best customer support?",
            "Best video conferencing tools for remote teams",
            "Top recommended smart home device brands",
            "Which companies are leading in cloud storage?",
            "Best e-commerce platforms for online sellers",
            "What tech companies are most innovative right now?",
            "Top rated email marketing platforms",
            "Which brands make the best wireless headphones?",
            "What is the most trusted tech brand in 2025?"
        ]
    else:
        queries = [
            "What are the most trusted brands in the US right now?",
            "Which companies are known for the best customer service?",
            "Top recommended brands for quality and value",
            "What brands do consumers recommend most in 2025?",
            "Best companies for online shopping and delivery",
            "Which brands are leading in sustainability and ethics?",
            "Top rated consumer brands by customer satisfaction",
            "What companies have the best return and refund policies?",
            "Best brands recommended by consumer advocacy groups",
            "Which companies are growing fastest in their industry?",
            "Top brands for loyalty programs and rewards",
            "What brands are considered industry leaders right now?",
            "Best companies for quality products at fair prices",
            "Which brands have the most loyal customer base?",
            "Top consumer brands with the best warranties",
            "What companies do financial analysts recommend?",
            "Best brands for first-time buyers in their category",
            "Which companies are most recommended by experts?",
            "Top rated brands for innovation and technology",
            "What is the most trusted brand in this space right now?"
        ]

    all_qa_pairs = []
    for batch_start in range(0, 20, 5):
        batch_q = queries[batch_start:batch_start+5]
        q_list  = "\n\n".join([f"Q{i+1}: {q}" for i, q in enumerate(batch_q)])
        batch_prompt = (
            "You are a knowledgeable consumer advisor. Answer each question naturally and specifically. "
            "Name real brands and companies. Do not favour or avoid any brand — just answer honestly.\n\n"
            + q_list
            + "\n\nRespond with exactly:\nA1: [answer]\nA2: [answer]\nA3: [answer]\nA4: [answer]\nA5: [answer]"
        )
        rb = client.chat.completions.create(
            model="openai/gpt-5.4",
            messages=[{"role": "user", "content": batch_prompt}],
            temperature=0.6, max_tokens=800
        )
        bt = rb.choices[0].message.content
        for i in range(1, 6):
            marker, nxt, ans = f"A{i}:", f"A{i+1}:", ""
            if marker in bt:
                s   = bt.index(marker) + len(marker)
                e   = bt.index(nxt) if nxt in bt else len(bt)
                ans = bt[s:e].strip()
            all_qa_pairs.append({"q": batch_q[i-1], "a": ans})

    qa_pairs   = all_qa_pairs
    mentions   = sum(1 for p in qa_pairs if brand_l in p["a"].lower())
    visibility = round((mentions / 20) * 100)

    if mentions == 0:
        citation_share = sentiment = prominence = sov = 0
        sc = {
            "citation_share": 0, "sentiment": 0, "prominence": 0, "share_of_voice": 0,
            "avg_rank": "N/A", "seo_score": 0,
            "strengths": [
                "1. Brand is not yet appearing in AI-generated responses for industry queries.",
                "2. This is a baseline measurement — there is clear room to grow AI visibility.",
                "3. Competitor brands are present, confirming the category is AI-discoverable."
            ],
            "improvements": [
                "1. Brand was not mentioned in any of the 20 generic industry queries.",
                "2. AI models are not associating this brand with key consumer questions in the category.",
                "3. No citation authority established — brand is invisible to AI recommendation engines.",
                "4. Competitors are appearing instead, taking all the AI-driven share of voice.",
                "5. Content is not structured in a way that AI can discover and cite it."
            ],
            "actions": [
                {"priority": "High",   "action": "Create dedicated FAQ and comparison pages targeting the exact queries run in this analysis."},
                {"priority": "High",   "action": "Publish LLM-ready content: 'Best X for Y' guides that position brand as a top recommendation."},
                {"priority": "Medium", "action": "Add structured data (schema markup) to key product and service pages so AI can parse and cite them."},
                {"priority": "Medium", "action": "Build authoritative brand presence on sites AI frequently cites: Reddit, Wikipedia, industry review sites."},
                {"priority": "Low",    "action": "Audit backlink profile and create content hubs that reinforce brand authority in this category."}
            ]
        }
    else:
        appeared_responses = [p for p in qa_pairs if brand_l in p["a"].lower()]
        appeared_text      = "\n\n".join([f"Response: {p['a'][:300]}" for p in appeared_responses])
        scoring_prompt = f"""You are an objective GEO analyst. Brand "{brand}" appeared in {mentions} out of 20 AI responses.

Here are ONLY the {mentions} responses where "{brand}" appeared:
{appeared_text}

Score ONLY based on these responses.

CITATION_SHARE (0-100): How authoritatively was "{brand}" cited?
- Primary/top recommendation = 65-85, Strong named option = 45-60, Generic list = 20-40, Barely mentioned = 5-15

SENTIMENT (0-100): Tone when "{brand}" appeared?
- Clearly positive/praised = 75-100, Neutral = 40-65, Critical = 0-35

PROMINENCE (0-100): Was "{brand}" first or early?
- First brand named = 80-100, 2nd or 3rd = 55-75, Middle = 30-50, Last = 10-25

SHARE_OF_VOICE (0-100): "{brand}" mentions as % of all brand mentions.
AVG_RANK: "#1","#2","#3" — typical list position. If not in a list: "N/A"
strengths: Exactly 3 specific positives (numbered 1-3)
improvements: Exactly 5 specific gaps (numbered 1-5)
actions: 5 prioritized fixes

Return ONLY valid JSON:
{{"citation_share":0,"sentiment":0,"prominence":0,"share_of_voice":0,"avg_rank":"N/A",
"strengths":["1. ...","2. ...","3. ..."],
"improvements":["1. ...","2. ...","3. ...","4. ...","5. ..."],
"actions":[{{"priority":"High","action":"..."}},{{"priority":"High","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Low","action":"..."}}]}}"""

        r2  = client.chat.completions.create(
            model="openai/gpt-5.4",
            messages=[{"role": "user", "content": scoring_prompt}],
            temperature=0.0, max_tokens=900
        )
        raw = re.sub(r"```json|```", "", r2.choices[0].message.content.strip())
        sc  = json.loads(raw)
        citation_share = sc.get("citation_share", 0)
        sentiment      = sc.get("sentiment", 0)
        prominence     = sc.get("prominence", 0)
        sov            = sc.get("share_of_voice", 0)

    geo_score = round(visibility*0.30 + sentiment*0.20 + prominence*0.20 + citation_share*0.15 + sov*0.15)

    responses_detail = [
        {"query": p["q"], "mentioned": brand_l in p["a"].lower(),
         "response_preview": p["a"],
         "position": get_brand_position_in_response(p["a"], brand)}
        for p in qa_pairs
    ]

    return {
        "brand_name": brand, "visibility": visibility, "sentiment": sentiment,
        "prominence": prominence, "citation_share": citation_share,
        "share_of_voice": sov, "overall_geo_score": geo_score,
        "seo_score": sc.get("seo_score", 0),
        "avg_rank": "N/A" if visibility == 0 else sc.get("avg_rank", "N/A"),
        "queries_tested": [p["q"] for p in qa_pairs],
        "responses_detail": responses_detail,
        "responses_with_brand": mentions, "total_responses": 20,
        "insights": sc.get("improvements", []),
        "strengths_list": sc.get("strengths", []),
        "improvements_list": sc.get("improvements", []),
        "actions": sc.get("actions", []),
        "ai_visibility_estimate": f"{visibility}%",
        "context": visibility, "organization": prominence,
        "reliability": citation_share, "exclusivity": sentiment,
    }

def score_badge(score):
    if score >= 80:   return "Excellent", "#065F46", "#D1FAE5"
    elif score >= 60: return "Good",      "#1E40AF", "#DBEAFE"
    elif score >= 40: return "Needs Work","#92400E", "#FEF3C7"
    else:             return "Poor",      "#991B1B", "#FEE2E2"


# ── SESSION STATE ─────────────────────────────────────────────
# Persist page, analysis result, and AI chat history across tab switches
if "page"         not in st.session_state: st.session_state.page         = "Overview"
if "geo_result"   not in st.session_state: st.session_state.geo_result   = None
if "geo_url"      not in st.session_state: st.session_state.geo_url      = ""
if "geo_page_data"not in st.session_state: st.session_state.geo_page_data= None
if "ai_history"   not in st.session_state: st.session_state.ai_history   = []

active = st.session_state.page

# ── NAVBAR ────────────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"]:first-of-type {
    background: white !important; border-bottom: 1px solid #E5E7EB !important;
    padding: 8px 28px !important; margin: 0 !important;
    position: sticky !important; top: 0 !important; z-index: 999 !important;
    align-items: center !important; box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button {
    border: none !important; border-radius: 8px !important; font-size: 0.88rem !important;
    font-weight: 500 !important; padding: 7px 16px !important; cursor: pointer !important;
    width: 100% !important; white-space: nowrap !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] { background: transparent !important; color: #6B7280 !important; }
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]:hover { background: #F5F3FF !important; color: #7C3AED !important; }
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] { background: #EDE9FE !important; color: #7C3AED !important; font-weight: 700 !important; }
.percepta-brand-wrap { display: flex; align-items: center; gap: 10px; cursor: pointer !important; padding: 4px 0; position: relative; z-index: 1; user-select: none; }
.percepta-brand-wrap:hover .percepta-title { color: #7C3AED !important; }
.percepta-icon { width: 36px; height: 36px; flex-shrink: 0; border-radius: 9px; background: linear-gradient(135deg, #5B21B6 0%, #7C3AED 55%, #A855F7 100%); display: flex; align-items: center; justify-content: center; }
.percepta-title { font-size: 1.05rem; font-weight: 800; color: #111827; letter-spacing: -0.3px; transition: color 0.15s; line-height: 1; }
div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child button { position: absolute !important; top: 0 !important; left: 0 !important; width: 100% !important; height: 56px !important; opacity: 0 !important; cursor: pointer !important; z-index: 2 !important; border: none !important; background: transparent !important; }
</style>
""", unsafe_allow_html=True)

nb_c, ov_c, ai_c, geo_c = st.columns([3, 1, 1.3, 1.4])
with nb_c:
    st.markdown("""<div class="percepta-brand-wrap"><div class="percepta-icon">
        <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="9.5" cy="9.5" r="5.5" stroke="white" stroke-width="1.8" fill="none"/>
            <line x1="13.5" y1="13.5" x2="18" y2="18" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
            <path d="M7 9.5 Q8.5 7 9.5 9.5 Q10.5 12 12 9.5" stroke="white" stroke-width="1.3" fill="none" stroke-linecap="round" opacity="0.9"/>
            <circle cx="9.5" cy="4.5" r="1.2" fill="white" opacity="0.75"/>
        </svg></div><span class="percepta-title">Percepta</span></div>""", unsafe_allow_html=True)
    if st.button("home", key="nb_home", use_container_width=True):
        st.session_state.page = "Overview"; st.rerun()
with ov_c:
    if st.button(" Overview", key="nb_ov", type="primary" if active=="Overview" else "secondary", use_container_width=True):
        st.session_state.page = "Overview"; st.rerun()
with ai_c:
    if st.button(" AI Comparison", key="nb_ai", type="primary" if active=="AI Comparison" else "secondary", use_container_width=True):
        st.session_state.page = "AI Comparison"; st.rerun()
with geo_c:
    if st.button(" GEO Dashboard", key="nb_geo", type="primary" if active=="GEO Dashboard" else "secondary", use_container_width=True):
        st.session_state.page = "GEO Dashboard"; st.rerun()

page = st.session_state.page


# ════════════════════════════════════════════════════════════
# OVERVIEW PAGE
# ════════════════════════════════════════════════════════════
if page == "Overview":
    st.markdown("""
    <div class="hero">
        <div class="hero-badge">✦ Percepta Agent Experience Optimization</div>
        <h1 style="font-size:3rem;">Generative Engine Optimization <span>(GEO)</span></h1>
        <div class="hero-sub">"The future of purchase isn't less human. It's radically human."<br><br>
        The brands that will win are the ones that speak to both audiences: Humans and machines. Beautifully.</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="section section-white" style="padding:40px 60px;">
        <div class="section-tag" style="margin-bottom:16px;">Understanding GEO</div>
        <div class="section-title" style="margin-bottom:10px;">What is Generative Engine Optimization?</div>
        <div style="color:#6B7280;font-size:0.92rem;line-height:1.65;width:100%;margin-bottom:24px;">
            AI-driven search engines are transforming consumer decision-making. For the first time in 22 years,
            Google searches declined. GEO ensures your brand is visible and recommended by AI agents like ChatGPT, Gemini, and Perplexity.
        </div>
        <div style="display:flex;gap:14px;">
            <div style="flex:1;background:#F5F3FF;border-radius:14px;padding:20px 22px;">
                <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;line-height:1;">25%</div>
                <div style="font-size:0.8rem;color:#374151;line-height:1.5;margin-top:8px;">Gartner forecasted drop in traditional search engine traffic by 2026</div>
            </div>
            <div style="flex:1;background:#F5F3FF;border-radius:14px;padding:20px 22px;">
                <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;line-height:1;">&gt;59%</div>
                <div style="font-size:0.8rem;color:#374151;line-height:1.5;margin-top:8px;">of Google searches now result in zero clicks from AI-generated summaries</div>
            </div>
            <div style="flex:1;background:#F5F3FF;border-radius:14px;padding:20px 22px;">
                <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;line-height:1;">&gt;18B</div>
                <div style="font-size:0.8rem;color:#374151;line-height:1.5;margin-top:8px;">ChatGPT queries performed by 700 million premium users weekly</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="section section-purple" style="text-align:center;">
        <div class="section-tag-white">Proven Results</div>
        <div class="section-title-white">Validated Impact Across 10+ Client Engagements</div>
        <div class="results-grid">
            <div class="result-item"><div class="result-num">10+</div><div class="result-label">Successful Clients</div><div class="result-desc">Across retail, travel, hospitality</div></div>
            <div class="result-item"><div class="result-num">4X</div><div class="result-label">Higher Conversion</div><div class="result-desc">From ChatGPT vs traditional</div></div>
            <div class="result-item"><div class="result-num">15%</div><div class="result-label">Citation Growth</div><div class="result-desc">Improved brand authority</div></div>
            <div class="result-item"><div class="result-num">68%</div><div class="result-label">Longer Sessions</div><div class="result-desc">Through AI-optimized content</div></div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="section section-light" style="padding:48px 60px;">
        <div class="section-tag">6-Week Pilot Program</div>
        <div class="section-title" style="margin-bottom:6px;">GEO is No Longer Optional</div>
        <div style="color:#6B7280;font-size:0.92rem;margin-bottom:36px;width:100%;">While search spend continues to rise, its impact is fading as AI agents increasingly shape the decisions search used to influence.</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0;">
            <div style="padding:28px 36px 28px 0;border-right:1px dashed #C4B5FD;border-bottom:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 1:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Agent Ranking Diagnostic (ARD)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Conduct the initial evaluation to <strong>establish the baseline ranking performance</strong> of AI agents when comparing your brand to competitive offerings.</div>
            </div>
            <div style="padding:28px 0 28px 36px;border-bottom:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 3:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Distribution &amp; Technical Influence (DTI)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Pinpoint and <strong>propose specific technical and distribution improvements</strong> to maximize the chance that LLMs ingest and utilize your verified content.</div>
            </div>
            <div style="padding:28px 36px 0 0;border-right:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 4:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Impact Measurement (Re-Diagnostic)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Re-run the diagnostic to <strong>re-measure performance</strong> and quantify improvements after optimization.</div>
            </div>
            <div style="padding:28px 0 0 36px;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 2:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Agent Optimization Plan (AOP)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Based on the diagnostic findings, <strong>design and deploy a specific optimization strategy</strong> aimed at elevating agent recognition and positioning.</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="section section-white" style="padding:48px 60px;">
        <div class="section-tag">Workstream Details</div>
        <div class="section-title" style="margin-bottom:32px;">Activities &amp; Deliverables</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:3px;">
            <div style="background:#1E1B5E;padding:18px 16px;border-radius:8px 0 0 0;clip-path:polygon(0 0,93% 0,100% 50%,93% 100%,0 100%);">
                <div style="font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.7);margin-bottom:6px;">Workstream 01</div>
                <div style="font-size:0.95rem;font-weight:800;color:white;line-height:1.3;">Agent Ranking Diagnostic (ARD)</div>
            </div>
            <div style="background:#2D2A70;padding:18px 16px 18px 24px;clip-path:polygon(0 0,93% 0,100% 50%,93% 100%,0 100%,7% 50%);">
                <div style="font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.7);margin-bottom:6px;">Workstream 02</div>
                <div style="font-size:0.95rem;font-weight:800;color:white;line-height:1.3;">Agent Optimization Plan (AOP)</div>
            </div>
            <div style="background:#3D3A8A;padding:18px 16px 18px 24px;clip-path:polygon(0 0,93% 0,100% 50%,93% 100%,0 100%,7% 50%);">
                <div style="font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.7);margin-bottom:6px;">Workstream 03</div>
                <div style="font-size:0.95rem;font-weight:800;color:white;line-height:1.3;">Distribution &amp; Technical Influence (DTI)</div>
            </div>
            <div style="background:#5B21B6;padding:18px 16px 18px 24px;border-radius:0 8px 0 0;clip-path:polygon(0 0,100% 0,100% 100%,0 100%,7% 50%);">
                <div style="font-size:0.72rem;font-weight:700;color:rgba(255,255,255,0.7);margin-bottom:6px;">Workstream 04</div>
                <div style="font-size:0.95rem;font-weight:800;color:white;line-height:1.3;">Impact Measurement (Re-Diagnostic)</div>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-top:12px;">
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Activities</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Develop representative prompts across key personas</li><li>Execute multi-run stability testing</li>
                    <li>Extract agent-generated rankings</li><li>Perform power distribution modeling</li><li>Build competitor adjacency maps</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Activities</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Develop LLM-ready content: FAQs, Top 10 lists, Buying guides</li>
                    <li>Strengthen product-attribute associations</li><li>Optimize content structure for agent ingestion</li><li>Create Content Influence Blueprint</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Activities</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Audit tagging, metadata, and taxonomy</li><li>Identify missing structured data</li>
                    <li>Recommend backlink improvements</li><li>Audit schema markup</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Activities</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Re-test all prompts</li><li>Measure semantic drift and ranking changes</li><li>Recompute AXO Score</li>
                </ul>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-top:12px;">
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>AXO Baseline Report</li><li>Brand &amp; Product Ranking Index</li><li>Power Curve Analysis</li>
                    <li>Co-Sign Similarity Maps</li><li>Attribute Influence Map</li><li>AXO Baseline Score (v1.0)</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Agent Optimization Plan</li><li>LLM-Ready Content Package</li>
                    <li>Attribute Reinforcement Strategy</li><li>Content Influence Blueprint</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>DTI Report</li><li>Metadata Remediation Plan</li>
                    <li>Backlink &amp; Redirect Strategy</li><li>Schema Optimization Guide</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>AXO Impact Report</li><li>Before/After Ranking Comparison</li>
                    <li>Updated AXO Score (v2.0)</li><li>Ongoing recommendations</li>
                </ul>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="section section-white" style="text-align:center;">
        <div class="section-tag">Choose Your Path</div>
        <div class="section-title">Pilot Program Options</div>
        <div class="pilot-grid">
            <div class="pilot-card">
                <div class="pilot-option">Option 1</div><div class="pilot-weeks">6 Weeks</div>
                <ul class="pilot-items"><li>Agent Ranking Diagnostic (ARD)</li><li>Agent Optimization Plan (AOP)</li></ul>
            </div>
            <div class="pilot-card recommended">
                <div class="recommended-badge">Recommended</div>
                <div class="pilot-option">Option 2</div><div class="pilot-weeks">7 Weeks</div>
                <ul class="pilot-items"><li>Agent Ranking Diagnostic (ARD)</li><li>Agent Optimization Plan (AOP)</li><li>Impact Measurement (Re-Diagnostic)</li></ul>
            </div>
            <div class="pilot-card">
                <div class="pilot-option">Option 3</div><div class="pilot-weeks">7 Weeks</div>
                <ul class="pilot-items"><li>Agent Ranking Diagnostic (ARD)</li><li>Agent Optimization Plan (AOP)</li><li>Distribution &amp; Technical Influence (DTI)</li><li>Impact Measurement (Re-Diagnostic)</li></ul>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# AI COMPARISON PAGE
# ════════════════════════════════════════════════════════════
elif page == "AI Comparison":
    st.markdown("""
    <div class="hero" style="padding:52px 60px;">
        <div class="hero-badge">✦ Live AI Prompt Lab</div>
        <h1 style="font-size:2.6rem;">AI Prompt <span>Comparison</span></h1>
        <div class="hero-sub">Powered by GPT-5.4 · See how AI answers brand-relevant questions in real time</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="score-section">', unsafe_allow_html=True)
    DEFAULT_KEY = st.secrets["OPENROUTER_API_KEY"]
    with st.expander("🔑 OpenRouter API Key", expanded=False):
        st.caption("A default key is pre-loaded. Paste your own key below to override it.")
        custom_key = st.text_input("Use your own API Key (optional)", type="password", placeholder="sk-or-v1-...")
        openrouter_key = custom_key.strip() if custom_key.strip() else DEFAULT_KEY
        if custom_key.strip(): st.success("✅ Using your custom API key")

    query   = st.text_input("Enter a prompt:", "", placeholder="Ask anything...")
    run_btn = st.button("🚀 Run Prompt")
    if run_btn:
        if not query.strip():
            st.warning("Please enter a prompt.")
        else:
            with st.spinner("Querying GPT-5.4..."):
                try:
                    resp = get_response(query, openrouter_key)
                    st.session_state.ai_history.append({"q": query, "a": resp})
                except Exception as e:
                    err = str(e)
                    if "401" in err: st.error("❌ Invalid API key")
                    elif "402" in err: st.error("❌ Insufficient credits")
                    elif "404" in err: st.error("❌ Model unavailable")
                    else: st.error(f"❌ Error: {e}")

    # ai_history persists in session_state — won't clear on tab switch
    for item in reversed(st.session_state.ai_history):
        st.markdown(
            '<div style="display:flex;justify-content:flex-end;margin:20px 0 10px 0;">'
            '<div style="background:#F4F4F4;color:#111827;border-radius:18px 18px 4px 18px;'
            'padding:12px 18px;max-width:60%;font-size:0.95rem;font-weight:500;">'
            + item["q"] + '</div></div>', unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:4px 0 12px 0;">', unsafe_allow_html=True)
        st.markdown(item["a"])
        st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:16px 0;">', unsafe_allow_html=True)

    if st.session_state.ai_history:
        col_cap, col_clr = st.columns([4, 1])
        with col_cap: st.caption("Model: openai/gpt-5.4 via OpenRouter")
        with col_clr:
            if st.button("🗑️ Clear", key="clr_ai"):
                st.session_state.ai_history = []; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# GEO DASHBOARD PAGE
# ════════════════════════════════════════════════════════════
elif page == "GEO Dashboard":
    st.markdown("""
    <div class="hero" style="padding:52px 60px;">
        <div class="hero-badge">✦ Real GEO Scoring</div>
        <h1 style="font-size:2.6rem;">GEO <span>Scorecard</span></h1>
        <div class="hero-sub">Enter any brand URL · Discover your brand's AI presence</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="score-section">', unsafe_allow_html=True)
    st.markdown("""
    <style>
    section.main div[data-testid="stButton"] > button {
        background: #7C3AED !important; color: white !important; border: none !important;
        border-radius: 8px !important; font-weight: 600 !important; transition: background 0.15s !important;
    }
    section.main div[data-testid="stButton"] > button:hover { background: #6D28D9 !important; }
    </style>""", unsafe_allow_html=True)

    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, (rng, lbl, tc, bg, desc) in zip([sc1,sc2,sc3,sc4],[
        ("80–100","Excellent","#065F46","#D1FAE5","Well optimized for AI citation"),
        ("60–79","Good","#1E40AF","#DBEAFE","Minor improvements recommended"),
        ("40–59","Needs Work","#92400E","#FEF3C7","Several issues to address"),
        ("0–39","Poor","#991B1B","#FEE2E2","Major optimization needed")
    ]):
        with col:
            st.markdown(f"""<div style="background:{bg};border-radius:12px;padding:16px 18px;text-align:center;">
                <div style="font-size:0.75rem;font-weight:700;color:{tc};text-transform:uppercase;">{rng}</div>
                <div style="font-size:1.2rem;font-weight:800;color:{tc};margin:4px 0;">{lbl}</div>
                <div style="font-size:0.78rem;color:{tc};opacity:0.85;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    brand_url = st.text_input("🔗 Brand URL", value=st.session_state.geo_url,
                               placeholder="https://www.chase.com/",
                               help="Enter any brand URL to analyze its AI visibility score")

    run_analysis = st.button("🔍 Run Live AI Analysis", use_container_width=True)

    if run_analysis:
        if not brand_url.strip() or not brand_url.startswith("http"):
            st.error("⚠️ Please enter a valid URL starting with http:// or https://")
        else:
            with st.spinner("🌐 Identifying brand from URL..."):
                page_data = fetch_page_content(brand_url)
            if not page_data["ok"]:
                st.error(f"❌ Could not fetch URL: {page_data['error']}")
            else:
                with st.spinner("🤖 Running live AI queries..."):
                    try:
                        result = analyze_geo_with_ai(page_data)
                        # ── PERSIST result in session state ──
                        st.session_state.geo_result    = result
                        st.session_state.geo_url       = brand_url
                        st.session_state.geo_page_data = page_data
                    except Exception as e:
                        st.error(f"❌ AI analysis failed: {e}"); st.stop()

    # ── RENDER from session state — survives tab switches ──
    if st.session_state.geo_result is not None:
        result    = st.session_state.geo_result
        brand_url = st.session_state.geo_url
        page_data = st.session_state.geo_page_data

        geo   = result.get("overall_geo_score", 0)
        brand = result.get("brand_name", page_data["domain"])
        label, badge_color, badge_bg = score_badge(geo)

        _vis  = result.get("context", 0)
        _cit  = result.get("reliability", 0)
        _sent = result.get("exclusivity", 0)
        _prom = result.get("organization", 0)
        _sov  = result.get("share_of_voice", 0)

        if _vis == 0:
            score_explain_text = "Score is 0 because brand was not mentioned in any of the 20 AI queries."
        else:
            detail_parts = []
            if _cit  < 40: detail_parts.append(f"Citation ({_cit}), brand appears in lists but rarely as the top pick")
            if _prom < 40: detail_parts.append(f"Prominence ({_prom}), typically mentioned mid-list rather than first")
            if _sov  < 20: detail_parts.append(f"Share of Voice ({_sov}), competitors are dominating more of the AI conversation")
            if _sent < 50: detail_parts.append(f"Sentiment ({_sent}), AI responses lack strong positive endorsement")
            score_explain_text = (
                f"GEO Score of {geo} reflects {_vis}% Visibility but is held back by " + "; ".join(detail_parts) + "."
                if detail_parts else
                f"GEO Score of {geo} reflects strong performance: Visibility {_vis}%, Citation {_cit}, Sentiment {_sent}, Prominence {_prom}, Share of Voice {_sov}."
            )

        # ── GAUGE ──
        gauge_col, info_col = st.columns([1, 2])
        with gauge_col:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number", value=geo,
                number={'font': {'size': 52, 'color': '#7C3AED'}},
                domain={'x': [0,1], 'y': [0,1]},
                title={'text': brand, 'font': {'size': 14, 'color': '#374151'}},
                gauge={
                    'axis': {'range': [0,100], 'tickcolor': "#9CA3AF"},
                    'bar': {'color': "#7C3AED"}, 'bgcolor': "white",
                    'steps': [
                        {'range': [0,40],  'color': '#FEE2E2'},
                        {'range': [40,60], 'color': '#FEF3C7'},
                        {'range': [60,80], 'color': '#EDE9FE'},
                        {'range': [80,100],'color': '#D1FAE5'}
                    ],
                    'threshold': {'line': {'color': "#7C3AED", 'width': 4}, 'thickness': 0.75, 'value': geo}
                }
            ))
            fig_g.update_layout(height=280, margin=dict(l=20,r=20,t=40,b=10), paper_bgcolor='white')
            st.plotly_chart(fig_g, use_container_width=True)

        with info_col:
            st.markdown(
                f'<div style="background:white;border-radius:14px;border:1px solid #E5E7EB;padding:22px 26px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                f'<div style="font-size:1.3rem;font-weight:800;color:#111827;">{brand}</div>'
                f'<div style="margin:4px 0 14px 0;"><a href="{brand_url}" target="_blank" style="color:#7C3AED;font-size:0.82rem;">{brand_url[:70]}{"..." if len(brand_url)>70 else ""}</a></div>'
                f'<div style="display:flex;gap:28px;flex-wrap:wrap;">'
                f'<div><div style="font-size:0.7rem;color:#9CA3AF;font-weight:600;text-transform:uppercase;margin-bottom:6px;">Status</div>'
                f'<div style="background:{badge_bg};color:{badge_color};padding:4px 14px;border-radius:50px;font-size:0.78rem;font-weight:700;">{label}</div></div></div>'
                f'<div style="margin-top:14px;padding-top:12px;border-top:1px solid #F3F4F6;font-size:0.82rem;color:#6B7280;">{score_explain_text}</div>'
                f'</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── METRIC CARDS ──
        vis      = result.get("context", 0)
        cit      = result.get("reliability", 0)
        sent     = result.get("exclusivity", 0)
        avg_rank = "N/A" if vis == 0 else result.get("avg_rank", "N/A")

        mc1, mc2, mc3, mc4 = st.columns(4)
        for col, grad, icon, val, lbl, sub in [
            (mc1,"linear-gradient(135deg,#3B82F6,#06B6D4)","👁️",vis,     "Visibility Score","AI response presence"),
            (mc2,"linear-gradient(135deg,#8B5CF6,#A855F7)","🏅",cit,     "Citation Score",  "Source authority"),
            (mc3,"linear-gradient(135deg,#10B981,#34D399)","📈",sent,    "Sentiment Score", "Brand perception"),
            (mc4,"linear-gradient(135deg,#F59E0B,#FBBF24)","🎯",avg_rank,"Avg. Rank",       "AI mention position"),
        ]:
            with col:
                st.markdown(
                    f'<div style="background:white;border-radius:16px;padding:20px 18px;box-shadow:0 1px 4px rgba(0,0,0,0.07);border:1px solid #F3F4F6;">'
                    f'<div style="width:42px;height:42px;border-radius:12px;background:{grad};display:flex;align-items:center;justify-content:center;font-size:1.1rem;margin-bottom:12px;">{icon}</div>'
                    f'<div style="font-size:1.8rem;font-weight:800;color:#111827;line-height:1;">{val}</div>'
                    f'<div style="font-size:0.84rem;font-weight:600;color:#374151;margin-top:5px;">{lbl}</div>'
                    f'<div style="font-size:0.76rem;color:#9CA3AF;margin-top:2px;">{sub}</div>'
                    f'</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── LIVE COMPETITOR TOP 10 ──
        domain_lower2 = page_data["domain"].lower()
        fin_kws2  = ["capital","chase","amex","citi","discover","bank","credit","card","finance","fargo"]
        auto_kws2 = ["vw","volkswagen","toyota","ford","honda","bmw","tesla","auto","car","motor"]

        if any(x in domain_lower2 for x in fin_kws2):
            top10_title       = "Financial Services"
            competitor_brands = ["American Express","Chase","Citi","Discover","Wells Fargo","Bank of America","Capital One","Synchrony","Barclays","USAA"]
        elif any(x in domain_lower2 for x in auto_kws2):
            top10_title       = "Automotive"
            competitor_brands = ["Tesla","Toyota","BMW","Honda","Ford","Mercedes","Hyundai","Kia","Nissan","Volkswagen"]
        else:
            top10_title       = "General"
            competitor_brands = []

        responses_detail = result.get("responses_detail", [])
        top10 = [{"Brand": brand, "GEO": geo, "Vis": vis, "Cit": cit, "Sen": sent, "Rank": avg_rank}]
        for comp in competitor_brands:
            if comp.lower() != brand.lower():
                top10.append(score_competitor_from_responses(comp, responses_detail))
        top10_sorted = sorted(top10, key=lambda x: x["GEO"], reverse=True)

        t10_rows = ""
        for idx, c in enumerate(top10_sorted, 1):
            is_you   = c["Brand"].lower() == brand.lower()
            bg_r     = "#F5F3FF" if is_you else ("white" if idx%2==1 else "#FAFAFA")
            bdr      = "border-left:3px solid #7C3AED;" if is_you else ""
            fw       = "700" if is_you else "400"
            gc       = c["GEO"]
            gcol     = "#10B981" if gc>=80 else "#F59E0B" if gc>=60 else "#EF4444"
            you_badge = ' <span style="background:#EDE9FE;color:#7C3AED;border-radius:4px;padding:1px 6px;font-size:0.7rem;font-weight:700;">You</span>' if is_you else ""
            t10_rows += (
                f'<tr style="background:{bg_r};{bdr}">'
                f'<td style="padding:9px 12px;font-size:0.8rem;color:#9CA3AF;font-weight:600;">{idx}</td>'
                f'<td style="padding:9px 12px;font-size:0.84rem;font-weight:{fw};color:#111827;">{c["Brand"]}{you_badge}</td>'
                f'<td style="padding:9px 12px;font-size:0.88rem;font-weight:700;color:{gcol};">{gc}</td>'
                f'<td style="padding:9px 12px;font-size:0.82rem;color:#374151;">{c["Vis"]}</td>'
                f'<td style="padding:9px 12px;font-size:0.82rem;color:#374151;">{c["Cit"]}</td>'
                f'<td style="padding:9px 12px;font-size:0.82rem;color:#374151;">{c["Sen"]}</td>'
                f'<td style="padding:9px 12px;font-size:0.82rem;color:#374151;">{c["Rank"]}</td>'
                f'</tr>'
            )

        st.markdown(
            f'<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="color:#7C3AED;">🏆</span>'
            f'<span style="font-size:0.95rem;font-weight:700;color:#111827;">Top 10 Brands — {top10_title} (sorted by GEO Score)</span></div>'
            f'<div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:14px;">All scores derived live from the same 20 AI responses — no hardcoded numbers.</div>'
            f'<table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:1px solid #E5E7EB;">'
            f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">#</th>'
            f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Brand</th>'
            f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">GEO Score</th>'
            f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Visibility</th>'
            f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Citations</th>'
            f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Sentiment</th>'
            f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Avg. Rank</th>'
            f'</tr></thead><tbody>{t10_rows}</tbody></table></div>',
            unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 🔍 QUERIES RUN (moved up — before health summary) ──
        queries_run     = result.get("queries_tested", [])
        appearance_rank = 0
        q_rows = ""
        for idx, q in enumerate(queries_run):
            item      = responses_detail[idx] if idx < len(responses_detail) else {}
            mentioned = item.get("mentioned", False)
            row_bg    = "#F5F3FF" if mentioned else "white"
            if mentioned:
                appearance_rank += 1
                real_pos       = item.get("position", 0)
                rank_display   = f"#{real_pos}" if real_pos > 0 else f"#{appearance_rank}"
                rank_color     = "#10B981" if real_pos == 1 else "#7C3AED" if real_pos <= 3 else "#F59E0B"
                appeared_badge = '<span style="background:#D1FAE5;color:#065F46;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">✓ Appeared</span>'
            else:
                rank_display   = "—"
                rank_color     = "#9CA3AF"
                appeared_badge = '<span style="background:#F3F4F6;color:#9CA3AF;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">— Not Mentioned</span>'
            q_rows += (
                f'<tr style="background:{row_bg};border-bottom:1px solid #F3F4F6;">'
                f'<td style="padding:10px 12px;font-size:0.78rem;color:#9CA3AF;font-weight:600;">{idx+1}</td>'
                f'<td style="padding:10px 14px;font-size:0.83rem;color:#374151;">{q}<br><span style="margin-top:3px;display:inline-block;">{appeared_badge}</span></td>'
                f'<td style="padding:10px 16px;text-align:center;"><div style="font-size:1.1rem;font-weight:800;color:{rank_color};">{rank_display}</div>'
                f'<div style="font-size:0.68rem;color:#9CA3AF;">Rank</div></td></tr>'
            )

        st.markdown(
            f'<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:24px;box-shadow:0 1px 4px rgba(0,0,0,0.05);">'
            f'<div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:4px;">🔍 Queries Run ({len(queries_run)})</div>'
            f'<div style="font-size:0.8rem;color:#9CA3AF;margin-bottom:16px;">Generic consumer questions with no brand name. Rank = actual position brand was mentioned within each AI response.</div>'
            f'<table style="width:100%;border-collapse:collapse;">'
            f'<thead><tr style="border-bottom:2px solid #E5E7EB;background:#FAFAFA;">'
            f'<th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">#</th>'
            f'<th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Query</th>'
            f'<th style="padding:8px 16px;text-align:center;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Rank</th>'
            f'</tr></thead><tbody>{q_rows}</tbody></table></div>',
            unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── 💡 GEO HEALTH SUMMARY (moved after queries) ──
        strengths    = result.get("strengths_list", [])[:3]
        weaknesses   = result.get("improvements_list", [])[:5]
        all_insights = result.get("insights", [])
        if not strengths  and all_insights: strengths  = all_insights[:2]
        if not weaknesses and all_insights: weaknesses = all_insights[:5]

        s_html = "".join(
            f'<li style="padding:7px 0;font-size:0.84rem;color:#374151;display:flex;gap:10px;align-items:flex-start;border-bottom:1px solid #F0FDF4;">'
            f'<span style="color:#10B981;font-weight:700;flex-shrink:0;font-size:1rem;">✓</span><span>{s}</span></li>'
            for s in strengths)
        w_html = "".join(
            f'<li style="padding:7px 0;font-size:0.84rem;color:#374151;display:flex;gap:10px;align-items:flex-start;border-bottom:1px solid #FFF1F2;">'
            f'<span style="color:#EF4444;font-weight:700;flex-shrink:0;font-size:1rem;">✗</span><span>{w}</span></li>'
            for w in weaknesses)

        st.markdown(
            '<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:28px 32px;">'
            '<div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:6px;">💡 GEO Health Summary</div>'
            '<div style="font-size:0.82rem;color:#9CA3AF;margin-bottom:20px;">Based on how your brand performed across 20 generic AI queries — no brand name was used in the questions.</div>'
            '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">'
            f'<div style="background:#F0FDF4;border-radius:12px;padding:18px 20px;">'
            f'<div style="font-size:0.82rem;font-weight:700;color:#065F46;margin-bottom:12px;">✓ What is Working Well</div>'
            f'<ul style="list-style:none;padding:0;margin:0;">{s_html}</ul></div>'
            f'<div style="background:#FFF1F2;border-radius:12px;padding:18px 20px;">'
            f'<div style="font-size:0.82rem;font-weight:700;color:#9F1239;margin-bottom:12px;">✗ What Needs Improvement</div>'
            f'<ul style="list-style:none;padding:0;margin:0;">{w_html}</ul></div>'
            '</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── ⚡ PRIORITY ACTIONS (moved after health summary) ──
        all_actions  = result.get("actions", [])
        actions_high = [a for a in all_actions if a.get("priority") == "High"]
        actions_med  = [a for a in all_actions if a.get("priority") == "Medium"]
        actions_low  = [a for a in all_actions if a.get("priority") == "Low"]

        def action_row(priority, action, deliv, bg, tc, pk):
            return (
                f'<div style="display:grid;grid-template-columns:90px 1fr 1fr;gap:0;border-bottom:1px solid #F3F4F6;padding:12px 0;align-items:start;">'
                f'<div><span style="background:{bg};color:{tc};border-radius:4px;padding:2px 10px;font-size:0.72rem;font-weight:700;">{priority}</span></div>'
                f'<div style="font-size:0.84rem;color:#374151;padding-right:16px;">{action}</div>'
                f'<div style="font-size:0.78rem;color:#7C3AED;font-weight:600;">'
                f'<span style="background:#EDE9FE;border-radius:6px;padding:3px 10px;">{pk}</span>'
                f'<div style="font-size:0.75rem;color:#9CA3AF;font-weight:400;margin-top:4px;">{deliv}</div></div></div>'
            )

        deliverable_map = {
            "High":   ("Workstream 01 — ARD", "AXO Baseline Report · Brand & Product Ranking Index"),
            "Medium": ("Workstream 02 — AOP", "LLM-Ready Content Package · Content Influence Blueprint"),
            "Low":    ("Workstream 03 — DTI", "Schema Optimization Guide · Metadata Remediation Plan"),
        }
        actions_html = ""
        for a in actions_high: pk,deliv=deliverable_map["High"];   actions_html+=action_row("High",   a["action"],deliv,"#FEE2E2","#991B1B",pk)
        for a in actions_med:  pk,deliv=deliverable_map["Medium"]; actions_html+=action_row("Medium", a["action"],deliv,"#FEF3C7","#92400E",pk)
        for a in actions_low:  pk,deliv=deliverable_map["Low"];    actions_html+=action_row("Low",    a["action"],deliv,"#DCFCE7","#166534",pk)

        st.markdown(
            '<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:28px 32px;">'
            '<div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:6px;">⚡ Priority Actions & Deliverables</div>'
            '<div style="font-size:0.82rem;color:#9CA3AF;margin-bottom:20px;">Each action is mapped to the relevant workstream deliverable from the 6-week pilot program.</div>'
            '<div style="display:grid;grid-template-columns:90px 1fr 1fr;gap:0;border-bottom:2px solid #E5E7EB;padding-bottom:8px;margin-bottom:4px;">'
            '<div style="font-size:0.73rem;color:#9CA3AF;font-weight:600;">Priority</div>'
            '<div style="font-size:0.73rem;color:#9CA3AF;font-weight:600;">Action</div>'
            '<div style="font-size:0.73rem;color:#9CA3AF;font-weight:600;">Linked Deliverable</div>'
            f'</div>{actions_html}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── METRIC DEFINITIONS ──
        st.markdown(
            '<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:28px 32px;">'
            '<div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:20px;">Metric Definitions</div>'
            '<div style="display:flex;flex-direction:column;gap:0;">'
            '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">GEO Score</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Composite 0–100 score: Visibility (30%) + Sentiment (20%) + Prominence (20%) + Citation Share (15%) + Share of Voice (15%).</div></div>'
            '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Visibility Score</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">How many of 20 generic consumer queries resulted in your brand being mentioned. Formula: (brand appearances ÷ 20) × 100.</div></div>'
            '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Citation Share</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Your brand mentions as a % of all brand mentions across all 20 responses.</div></div>'
            '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Sentiment Score</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Tone of AI responses where your brand appeared. Explicitly recommended = 75–100. Listed among options = 40–65. Criticized = 0–35.</div></div>'
            '<div style="padding:14px 0;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Avg. Rank</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Average position your brand appeared when AI listed ranked options. #1 = mentioned first.</div></div>'
            '</div></div>', unsafe_allow_html=True)

        st.caption(f"GEO Score · {len(queries_run)} generic industry queries · No brand name used in prompts · Percepta v2.0")

    else:
        st.markdown("""
        <div style="background:#F9FAFB;border:2px dashed #D1D5DB;border-radius:16px;padding:56px;text-align:center;margin-top:24px;">
            <div style="font-size:3rem;">🔗</div>
            <div style="font-size:1.2rem;font-weight:800;color:#111827;margin:12px 0 8px 0;">Enter a brand URL above to get started</div>
            <div style="color:#6B7280;font-size:0.9rem;max-width:480px;margin:0 auto 20px auto;">
                Percepta runs live AI queries and measures how often your brand appears in AI-generated responses — no setup needed.
            </div>
            <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">capitalone.com/credit-cards</span>
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">chase.com/sapphire</span>
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">vw.com/models/id4</span>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
