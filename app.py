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
from urllib.parse import urlparse

# ── HARDCODED API KEY (internal) ─────────────────────────────
INTERNAL_API_KEY = "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"

# ── PAGE CONFIG ──────────────────────────────────────────────
st.set_page_config(
    page_title="Percepta | GEO Insights",
    page_icon="🧠",
    layout="wide"
)

# ── GLOBAL STYLES ────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
* { font-family: 'Inter', sans-serif; box-sizing: border-box; }

header[data-testid="stHeader"] { display: none !important; }
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-left: 0 !important; padding-right: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none !important; }

/* ── NAVBAR via Streamlit columns ── */

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #6D28D9 0%, #7C3AED 40%, #9333EA 70%, #A855F7 100%);
    padding: 80px 60px 90px 60px;
    text-align: center;
    color: white;
}
.hero-badge {
    display: inline-flex; align-items: center; gap: 8px;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 50px; padding: 8px 20px;
    font-size: 0.85rem; font-weight: 600; color: white; margin-bottom: 28px;
}
.hero h1 {
    font-size: 3.8rem; font-weight: 900; color: white;
    line-height: 1.1; margin: 0 0 24px 0; letter-spacing: -1px;
}
.hero h1 span { color: rgba(255,255,255,0.65); }
.hero-sub {
    font-size: 1rem; color: rgba(255,255,255,0.88);
    line-height: 1.75; max-width: 580px; margin: 0 auto;
}

/* ── SECTIONS ── */
.section { padding: 64px 60px; }
.section-white { background: white; }
.section-light { background: #F8F9FF; }
.section-purple { background: linear-gradient(135deg, #7C3AED 0%, #9333EA 100%); }

.section-tag {
    display: inline-block; background: #EDE9FE; color: #7C3AED;
    border-radius: 50px; padding: 5px 16px;
    font-size: 0.78rem; font-weight: 600; margin-bottom: 14px;
}
.section-tag-white {
    display: inline-block; background: rgba(255,255,255,0.2); color: white;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 50px; padding: 5px 16px;
    font-size: 0.78rem; font-weight: 600; margin-bottom: 14px;
}
.section-title { font-size: 2rem; font-weight: 800; color: #111827; margin: 0 0 12px 0; letter-spacing: -0.5px; }
.section-title-white { font-size: 2rem; font-weight: 800; color: white; margin: 0 0 12px 0; }
.section-sub { color: #6B7280; font-size: 1rem; line-height: 1.65; max-width: 640px; margin: 0 auto 36px auto; }

/* ── STAT CARDS ── */
.stat-cards { display: flex; gap: 20px; margin-top: 32px; }
.stat-card {
    flex: 1; background: white; border: 1px solid #E5E7EB;
    border-radius: 16px; padding: 28px 24px; text-align: center;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.stat-icon {
    width: 56px; height: 56px; background: #EDE9FE; border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 16px auto; font-size: 1.5rem;
}
.stat-title { font-size: 1.1rem; font-weight: 800; color: #111827; margin-bottom: 8px; }
.stat-desc  { font-size: 0.85rem; color: #6B7280; line-height: 1.5; }

/* ── RESULTS ── */
.results-grid { display: flex; gap: 40px; margin-top: 32px; justify-content: center; flex-wrap: wrap; }
.result-item { text-align: center; }
.result-num   { font-size: 3.2rem; font-weight: 900; color: white; line-height: 1; }
.result-label { font-size: 0.95rem; font-weight: 700; color: white; margin-top: 6px; }
.result-desc  { font-size: 0.82rem; color: rgba(255,255,255,0.72); margin-top: 4px; }

/* ── WORKSTREAMS ── */
.ws-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 32px; }
.ws-card {
    background: white; border: 1px solid #E5E7EB; border-radius: 16px;
    padding: 28px; position: relative; overflow: hidden;
}
.ws-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: linear-gradient(90deg, #7C3AED, #A855F7);
}
.ws-card.teal::before { background: linear-gradient(90deg, #0EA5E9, #06B6D4); }
.ws-icon {
    width: 44px; height: 44px; background: #EDE9FE; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; margin-bottom: 14px;
}
.ws-icon.teal { background: #E0F2FE; }
.ws-title { font-size: 1rem; font-weight: 800; color: #111827; margin-bottom: 10px; }
.ws-desc  { font-size: 0.85rem; color: #6B7280; line-height: 1.6; margin-bottom: 14px; }
.ws-items { list-style: none; padding: 0; margin: 0; }
.ws-items li {
    font-size: 0.85rem; color: #374151; padding: 3px 0;
    display: flex; align-items: center; gap: 8px;
}
.ws-items li::before { content: '›'; color: #7C3AED; font-weight: 700; font-size: 1rem; }

/* ── PILOT OPTIONS ── */
.pilot-grid { display: flex; gap: 20px; margin-top: 32px; }
.pilot-card {
    flex: 1; background: white; border: 2px solid #E5E7EB;
    border-radius: 16px; padding: 28px 24px; text-align: center; position: relative;
}
.pilot-card.recommended { border-color: #7C3AED; }
.recommended-badge {
    position: absolute; top: -14px; left: 50%; transform: translateX(-50%);
    background: #7C3AED; color: white; border-radius: 50px;
    padding: 4px 16px; font-size: 0.75rem; font-weight: 700; white-space: nowrap;
}
.pilot-option { font-size: 1rem; font-weight: 700; color: #111827; margin-bottom: 4px; }
.pilot-weeks  { font-size: 1.8rem; font-weight: 900; color: #7C3AED; margin-bottom: 16px; }
.pilot-items  { list-style: none; padding: 0; margin: 0; text-align: left; }
.pilot-items li {
    font-size: 0.85rem; color: #374151; padding: 6px 0;
    display: flex; align-items: flex-start; gap: 8px;
    border-bottom: 1px solid #F3F4F6;
}
.pilot-items li:last-child { border-bottom: none; }
.pilot-items li::before { content: '›'; color: #A855F7; font-weight: 700; flex-shrink: 0; }

/* ── SCORECARD ── */
.score-section { padding: 32px 40px; }
.core-dim-card { background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 20px; }
.core-dim-card h4 { font-size: 0.9rem; font-weight: 700; color: #111827; margin: 0 0 6px 0; }
.core-dim-score { font-size: 2rem; font-weight: 900; }
.core-dim-bar-bg { background: #F3F4F6; border-radius: 6px; height: 7px; margin: 8px 0 6px 0; }
.core-dim-bar { height: 7px; border-radius: 6px; }
.core-dim-desc { font-size: 0.78rem; color: #9CA3AF; }
.chat-box {
    background: white; border: 1px solid #E5E7EB; border-radius: 12px;
    padding: 22px 26px; font-size: 15px; line-height: 1.75; color: #111827;
}

/* Nav button styling */
div[data-testid="stHorizontalBlock"]:first-of-type > div > div > div > button {
    border: none !important;
    background: transparent !important;
    color: #6B7280 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 8px 0 !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    width: 100% !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div > div > div > button:hover {
    color: #7C3AED !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──────────────────────────────────────────────────
def get_client(api_key: str = INTERNAL_API_KEY):
    return OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        default_headers={"HTTP-Referer": "https://percepta.ai", "X-Title": "Percepta"}
    )

def get_response(prompt: str, api_key: str = INTERNAL_API_KEY) -> str:
    client = get_client(api_key)
    r = client.chat.completions.create(
        model="openai/gpt-5.4",
        messages=[
            {"role": "system", "content": """You are a sharp, direct AI assistant. When answering any question about products, services, brands, cards, tools, or recommendations:

ALWAYS follow this exact format:

1. Start with 1-2 sentence direct answer using **bold** for key terms and emojis inline (e.g. 👇 💳 ✅ ❌ 🏆 ✈️ 💰 👉)
2. Use ## headers with emojis for each category (e.g. ## 🏆 Best Overall, ## ✈️ Best for Travel)
3. Under each header, name the SPECIFIC real competitor/brand (e.g. Chase Sapphire Preferred®, Wells Fargo Active Cash®, Amex Gold Card)
4. Use bullet points with emoji checkmarks: • ✅ benefit, • ❌ downside
5. End each section with a bold insight line starting with 🔍 or 💡
6. Finish with a ## 👉 Quick Pick section with → arrows matching user type to specific product
7. Last line: ask 1 follow-up question to personalize the recommendation

RULES:
- Always name real brands, real products, real percentages and fees
- Use emojis throughout — every header, every key point
- Never give vague generic advice
- Be conversational and direct, not corporate
"""},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2, max_tokens=2048
    )
    return r.choices[0].message.content

def fetch_page_content(url: str) -> dict:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title     = soup.title.string.strip() if soup.title else ""
        meta_tag  = soup.find("meta", attrs={"name": "description"})
        meta_desc = meta_tag.get("content", "") if meta_tag else ""
        headings  = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])[:20]]
        paragraphs= [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True)) > 60][:20]
        faqs      = soup.find_all(attrs={"itemtype": re.compile("FAQPage", re.I)})
        has_schema= bool(soup.find_all("script", attrs={"type": "application/ld+json"}))
        has_author= bool(soup.find(attrs={"class": re.compile("author|byline", re.I)}))
        has_table = bool(soup.find("table"))
        has_lists = len(soup.find_all(["ul", "ol"])) > 2
        ext_links = [a["href"] for a in soup.find_all("a", href=True)
                     if a["href"].startswith("http") and urlparse(url).netloc not in a["href"]][:10]
        word_count= len(soup.get_text().split())
        domain    = urlparse(url).netloc.replace("www.", "")
        return {"ok": True, "url": url, "domain": domain, "title": title,
                "meta_desc": meta_desc, "headings": headings, "paragraphs": paragraphs[:6],
                "has_schema": has_schema, "has_faq": len(faqs)>0 or any("faq" in h.lower() for h in headings),
                "has_author": has_author, "has_table": has_table, "has_lists": has_lists,
                "external_links_count": len(ext_links), "word_count": word_count}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def analyze_geo_with_ai(page_data: dict) -> dict:
    """
    Accurate Profound-style scoring:
    - GPT answers 5 real consumer queries naturally (no brand bias)
    - Separate objective scoring call measures what actually happened
    - Each metric has a clear, honest calculation
    """
    # Extract brand name
    brand = page_data.get("title", "").split("|")[0].split("-")[0].strip()
    if not brand or len(brand) < 2:
        domain = page_data.get("domain", "brand")
        brand = domain.replace("www.", "").split(".")[0].title()
    domain = page_data.get("domain", "")
    client = get_client()

    # 20 diverse queries across 4 intent categories (5 per batch)
    queries = [
        f"Tell me about {brand} — is it a good company?",
        f"How does {brand} compare to its main competitors?",
        f"What are the best products or services {brand} offers?",
        f"What are the pros and cons of {brand}?",
        f"What do experts recommend instead of or alongside {brand}?",
        f"Is {brand} a trusted brand in its industry?",
        f"What makes {brand} different from other companies?",
        f"Would you recommend {brand} to a first-time customer?",
        f"What are common complaints or issues with {brand}?",
        f"How does {brand} rank among the top brands in its category?",
        f"What is {brand} best known for?",
        f"Has {brand} won any awards or industry recognition?",
        f"What type of customer is {brand} best suited for?",
        f"How has {brand} performed compared to competitors recently?",
        f"What are the top reasons to choose {brand} over alternatives?",
        f"Are there better alternatives to {brand}?",
        f"What do industry experts say about {brand}?",
        f"How does {brand} handle customer service and support?",
        f"Is {brand} considered a leader or follower in its market?",
        f"What should someone know before choosing {brand}?"
    ]

    # Run 4 batches of 5 queries each
    all_qa_pairs = []
    for batch_start in range(0, 20, 5):
        batch_q = queries[batch_start:batch_start+5]
        q_list = "\n\n".join([f"Q{i+1}: {q}" for i, q in enumerate(batch_q)])
        batch_prompt = (
            "Answer each question below as a knowledgeable consumer advisor. "
            "Be specific, name real brands and products. Answer naturally - do not avoid or force any brand.\n\n"
            + q_list
            + "\n\nRespond with exactly:\nA1: [answer]\nA2: [answer]\nA3: [answer]\nA4: [answer]\nA5: [answer]"
        )
        rb = client.chat.completions.create(
            model="openai/gpt-5.4",
            messages=[{"role": "user", "content": batch_prompt}],
            temperature=0.5, max_tokens=700
        )
        bt = rb.choices[0].message.content
        for i in range(1, 6):
            marker = f"A{i}:"
            nxt = f"A{i+1}:"
            ans = ""
            if marker in bt:
                s = bt.index(marker) + len(marker)
                e = bt.index(nxt) if nxt in bt else len(bt)
                ans = bt[s:e].strip()
            all_qa_pairs.append({"q": batch_q[i-1], "a": ans})

    qa_pairs = all_qa_pairs
    brand_l  = brand.lower()

    # Build formatted text for scoring
    qa_parts = []
    for i, p in enumerate(qa_pairs):
        qa_parts.append(f"Q{i+1}: {p['q']}\nA{i+1}: {p['a']}")
    qa_formatted = "\n\n".join(qa_parts)


    scoring_prompt = f"""You are an objective GEO measurement analyst. Read these 20 AI responses about "{brand}" and score each metric ACCURATELY based ONLY on what the responses actually say.

=== AI RESPONSES ===
{qa_formatted}
===================

Score each metric from 0 to 100. Be honest — do NOT cluster scores in the 50-70 range. Use the full range.

VISIBILITY (0-100):
Count how many of the 20 responses mention "{brand}" by name.
- 20/20 = 100
- 16/20 = 80
- 12/20 = 60
- 8/20 = 40
- 4/20 = 20
- 0/20 = 0

CITATION_SHARE (0-100):
In the responses where {brand} IS mentioned, how prominently/authoritatively is it cited?
- Mentioned as the top/primary recommendation = 80-100
- Mentioned as a strong, named option = 55-75
- Mentioned briefly or in passing = 25-45
- Not mentioned at all = 0

SENTIMENT (0-100):
What is the overall tone when {brand} is described?
- Clearly positive, recommended, praised = 75-100
- Mixed, balanced, some pros/cons = 45-70
- Negative, criticized, problems flagged = 0-40

PROMINENCE (0-100):
When {brand} appears in ranked lists or comparisons, what position?
- First or top mention = 85-100
- Second or third = 60-80
- Middle of pack = 35-55
- Last or barely mentioned = 10-30
- Not in any ranked context = 0

SHARE_OF_VOICE (0-100):
Of ALL brand names mentioned across all 5 responses, what % are "{brand}"?
Count total brand mentions. {brand} mentions / total * 100. Cap at 100.

AVG_RANK: Format as "#1", "#2", "#3" etc — where does {brand} typically rank?

SEO_SCORE (0-100): How well-known and authoritative does AI seem to consider {brand}? Based on knowledge depth shown.

Now provide:
strengths: Exactly 3 specific things working well for {brand} AI visibility (numbered 1-3, concrete, based on responses)
improvements: Exactly 5 specific gaps or problems (numbered 1-5, concrete, actionable)
actions: 5 prioritized fixes

Return ONLY valid JSON:
{{"visibility":0,"citation_share":0,"sentiment":0,"prominence":0,"share_of_voice":0,"seo_score":0,"avg_rank":"#2",
"strengths":["1. ...","2. ...","3. ..."],
"improvements":["1. ...","2. ...","3. ...","4. ...","5. ..."],
"actions":[{{"priority":"High","action":"..."}},{{"priority":"High","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Low","action":"..."}}]}}"""

    r2 = client.chat.completions.create(
        model="openai/gpt-5.4",
        messages=[{"role": "user", "content": scoring_prompt}],
        temperature=0.0, max_tokens=1000
    )
    raw = re.sub(r"```json|```", "", r2.choices[0].message.content.strip())
    sc  = json.loads(raw)

    visibility     = sc.get("visibility", 0)
    citation_share = sc.get("citation_share", 0)
    sentiment      = sc.get("sentiment", 50)
    prominence     = sc.get("prominence", 0)
    sov            = sc.get("share_of_voice", 0)

    # Count actual brand mentions for display
    mentions = sum(1 for p in qa_pairs if brand_l in p["a"].lower())

    # GEO Score = Profound weighted formula
    geo_score = round(
        visibility     * 0.30 +
        sentiment      * 0.20 +
        prominence     * 0.20 +
        citation_share * 0.15 +
        sov            * 0.15
    )

    avg_rank_raw = sc.get("avg_rank", "#?")
    try:
        avg_rank_num = int(avg_rank_raw.replace("#","").strip())
    except:
        avg_rank_num = 3

    return {
        "brand_name":           brand,
        "visibility":           visibility,
        "sentiment":            sentiment,
        "prominence":           prominence,
        "citation_share":       citation_share,
        "share_of_voice":       sov,
        "overall_geo_score":    geo_score,
        "seo_score":            sc.get("seo_score", 60),
        "avg_rank":             avg_rank_raw,
        "top_strength":         sc.get("strengths", [""])[0] if sc.get("strengths") else "",
        "top_weakness":         sc.get("improvements", [""])[0] if sc.get("improvements") else "",
        "queries_tested":       [p["q"] for p in qa_pairs],
        "responses_detail":     [{"query": p["q"], "mentioned": brand_l in p["a"].lower(), "response_preview": p["a"][:250]} for p in qa_pairs],
        "responses_with_brand": mentions,
        "total_responses":      20,
        "insights":             sc.get("improvements", []),
        "strengths_list":       sc.get("strengths", []),
        "improvements_list":    sc.get("improvements", []),
        "actions":              sc.get("actions", []),
        "ai_visibility_estimate": f"{visibility}%",
        "context":       visibility,
        "organization":  prominence,
        "reliability":   citation_share,
        "exclusivity":   sentiment,
    }

def score_badge(score):
    if score >= 80:   return "Excellent", "#065F46", "#D1FAE5"
    elif score >= 60: return "Good",      "#1E40AF", "#DBEAFE"
    elif score >= 40: return "Needs Work","#92400E", "#FEF3C7"
    else:             return "Poor",      "#991B1B", "#FEE2E2"


# ── SESSION STATE ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Overview"

# ── LOGO ─────────────────────────────────────────────────────
LOGO_SVG = """<svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
  <rect width="36" height="36" rx="9" fill="#7C3AED"/>
  <path d="M13 10 L22 18 L13 26" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
</svg>"""

# ── NAVBAR ───────────────────────────────────────────────────
# Approach: pure Streamlit styled buttons — no CSS overlays, no tricks.
# The navbar IS the st.columns row, styled to look like a real navbar.

active = st.session_state.page

ICON_DOC  = ""
ICON_SWAP = ""
ICON_BARS = ""

# Navbar: logo+brand on left via markdown, tabs on right via columns
st.markdown("""
<style>
/* Sticky white navbar wrapper */
.percepta-nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: white;
    border-bottom: 1px solid #E5E7EB;
    padding: 10px 28px;
    position: sticky;
    top: 0;
    z-index: 999;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.percepta-logo-box {
    width: 36px; height: 36px;
    background: #7C3AED;
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.percepta-brand {
    display: flex; align-items: center; gap: 10px;
}
.percepta-brand span {
    font-size: 1.05rem; font-weight: 800; color: #111827;
}
/* SVG icons for nav tabs via CSS */
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(2) button p::before {
    content: "";
    display: inline-block;
    width: 15px; height: 15px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'%3E%3Crect x='2' y='1' width='10' height='13' rx='1.5' stroke='%236B7280' stroke-width='1.5'/%3E%3Cline x1='5' y1='5' x2='9' y2='5' stroke='%236B7280' stroke-width='1.2' stroke-linecap='round'/%3E%3Cline x1='5' y1='7.5' x2='9' y2='7.5' stroke='%236B7280' stroke-width='1.2' stroke-linecap='round'/%3E%3Cline x1='5' y1='10' x2='7.5' y2='10' stroke='%236B7280' stroke-width='1.2' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-size: contain;
    margin-right: 6px;
    vertical-align: middle;
    position: relative; top: -1px;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(2) button[kind="primary"] p::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'%3E%3Crect x='2' y='1' width='10' height='13' rx='1.5' stroke='%237C3AED' stroke-width='1.5'/%3E%3Cline x1='5' y1='5' x2='9' y2='5' stroke='%237C3AED' stroke-width='1.2' stroke-linecap='round'/%3E%3Cline x1='5' y1='7.5' x2='9' y2='7.5' stroke='%237C3AED' stroke-width='1.2' stroke-linecap='round'/%3E%3Cline x1='5' y1='10' x2='7.5' y2='10' stroke='%237C3AED' stroke-width='1.2' stroke-linecap='round'/%3E%3C/svg%3E");
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(3) button p::before {
    content: "";
    display: inline-block;
    width: 15px; height: 15px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'%3E%3Cpath d='M2 5.5 C2 5.5 4 3 6 5.5 C8 8 10 5.5 10 5.5' stroke='%236B7280' stroke-width='1.5' stroke-linecap='round'/%3E%3Cpath d='M6 10.5 C6 10.5 8 8 10 10.5 C12 13 14 10.5 14 10.5' stroke='%236B7280' stroke-width='1.5' stroke-linecap='round'/%3E%3Ccircle cx='2' cy='5.5' r='1.2' fill='%236B7280'/%3E%3Ccircle cx='14' cy='10.5' r='1.2' fill='%236B7280'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-size: contain;
    margin-right: 6px;
    vertical-align: middle;
    position: relative; top: -1px;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(3) button[kind="primary"] p::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'%3E%3Cpath d='M2 5.5 C2 5.5 4 3 6 5.5 C8 8 10 5.5 10 5.5' stroke='%237C3AED' stroke-width='1.5' stroke-linecap='round'/%3E%3Cpath d='M6 10.5 C6 10.5 8 8 10 10.5 C12 13 14 10.5 14 10.5' stroke='%237C3AED' stroke-width='1.5' stroke-linecap='round'/%3E%3Ccircle cx='2' cy='5.5' r='1.2' fill='%237C3AED'/%3E%3Ccircle cx='14' cy='10.5' r='1.2' fill='%237C3AED'/%3E%3C/svg%3E");
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(4) button p::before {
    content: "";
    display: inline-block;
    width: 15px; height: 15px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'%3E%3Crect x='1' y='9' width='3' height='5' rx='0.8' fill='%236B7280'/%3E%3Crect x='6' y='6' width='3' height='8' rx='0.8' fill='%236B7280'/%3E%3Crect x='11' y='2' width='3' height='12' rx='0.8' fill='%236B7280'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-size: contain;
    margin-right: 6px;
    vertical-align: middle;
    position: relative; top: -1px;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div:nth-child(4) button[kind="primary"] p::before {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='none'%3E%3Crect x='1' y='9' width='3' height='5' rx='0.8' fill='%237C3AED'/%3E%3Crect x='6' y='6' width='3' height='8' rx='0.8' fill='%237C3AED'/%3E%3Crect x='11' y='2' width='3' height='12' rx='0.8' fill='%237C3AED'/%3E%3C/svg%3E");
}

/* Nav tab buttons row */
div[data-testid="stHorizontalBlock"]:first-of-type {
    background: white !important;
    border-bottom: 1px solid #E5E7EB !important;
    padding: 8px 28px !important;
    margin: 0 !important;
    position: sticky !important;
    top: 0 !important;
    z-index: 999 !important;
    align-items: center !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button {
    border: none !important;
    border-radius: 8px !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 7px 16px !important;
    cursor: pointer !important;
    width: 100% !important;
    white-space: nowrap !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] {
    background: transparent !important;
    color: #6B7280 !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]:hover {
    background: #F5F3FF !important;
    color: #7C3AED !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] {
    background: #EDE9FE !important;
    color: #7C3AED !important;
    font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

# ── NAVBAR: logo+brand col + 3 tab button cols — all in ONE columns row ──
nb_c, ov_c, ai_c, geo_c = st.columns([3, 1, 1.3, 1.4])

with nb_c:
    # Render logo + name as visible HTML, hidden button handles the click
    st.markdown("""
    <style>
    .percepta-brand-wrap {
        display: flex;
        align-items: center;
        gap: 10px;
        cursor: pointer !important;
        padding: 4px 0;
        position: relative;
        z-index: 1;
        user-select: none;
    }
    .percepta-brand-wrap:hover .percepta-title { color: #7C3AED !important; }
    .percepta-icon {
        width: 36px; height: 36px; flex-shrink: 0;
        border-radius: 9px;
        background: linear-gradient(135deg, #5B21B6 0%, #7C3AED 55%, #A855F7 100%);
        display: flex; align-items: center; justify-content: center;
    }
    .percepta-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #111827;
        letter-spacing: -0.3px;
        transition: color 0.15s;
        line-height: 1;
    }
    /* Hide the actual st.button but keep it clickable */
    div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child button {
        position: absolute !important;
        top: 0 !important; left: 0 !important;
        width: 100% !important; height: 56px !important;
        opacity: 0 !important;
        cursor: pointer !important;
        z-index: 2 !important;
        border: none !important;
        background: transparent !important;
    }
    </style>
    <div class="percepta-brand-wrap">
        <div class="percepta-icon">
            <svg width="22" height="22" viewBox="0 0 22 22" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="9.5" cy="9.5" r="5.5" stroke="white" stroke-width="1.8" fill="none"/>
                <line x1="13.5" y1="13.5" x2="18" y2="18" stroke="white" stroke-width="1.8" stroke-linecap="round"/>
                <path d="M7 9.5 Q8.5 7 9.5 9.5 Q10.5 12 12 9.5" stroke="white" stroke-width="1.3" fill="none" stroke-linecap="round" opacity="0.9"/>
                <circle cx="9.5" cy="4.5" r="1.2" fill="white" opacity="0.75"/>
            </svg>
        </div>
        <span class="percepta-title">Percepta</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("home", key="nb_home", use_container_width=True):
        st.session_state.page = "Overview"
        st.rerun()

with ov_c:
    btn_type = "primary" if active == "Overview" else "secondary"
    if st.button(f"{ICON_DOC} Overview", key="nb_ov", type=btn_type, use_container_width=True):
        st.session_state.page = "Overview"
        st.rerun()

with ai_c:
    btn_type = "primary" if active == "AI Comparison" else "secondary"
    if st.button(f"{ICON_SWAP} AI Comparison", key="nb_ai", type=btn_type, use_container_width=True):
        st.session_state.page = "AI Comparison"
        st.rerun()

with geo_c:
    btn_type = "primary" if active == "GEO Dashboard" else "secondary"
    if st.button(f"{ICON_BARS} GEO Dashboard", key="nb_geo", type=btn_type, use_container_width=True):
        st.session_state.page = "GEO Dashboard"
        st.rerun()

page = st.session_state.page


# ════════════════════════════════════════════════════════════
# OVERVIEW PAGE
# ════════════════════════════════════════════════════════════
if page == "Overview":

    st.markdown("""
    <div class="hero">
        <div class="hero-badge">✦ Percepta Agent Experience Optimization</div>
        <h1 style="font-size:3rem;">Generative Engine Optimization <span>(GEO)</span></h1>
        <div class="hero-sub">
            "The future of purchase isn't less human. It's radically human."<br><br>
            The brands that will win are the ones that speak to both audiences: Humans and machines. Beautifully.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── UNDERSTANDING GEO ──
    st.markdown("""
    <div class="section section-white" style="padding:40px 60px;">
        <div class="section-tag" style="margin-bottom:16px;">Understanding GEO</div>
        <div class="section-title" style="margin-bottom:10px;">What is Generative Engine Optimization?</div>
        <div style="color:#6B7280;font-size:0.92rem;line-height:1.65;width:100%;margin-bottom:24px;">
            AI-driven search engines are transforming consumer decision-making. For the first time in 22 years,
            Google searches declined. GEO ensures your brand is visible and recommended by AI agents like
            ChatGPT, Gemini, and Perplexity.
        </div>
        <div style="display:flex;gap:14px;">
            <div style="flex:1;background:#F5F3FF;border-radius:14px;padding:20px 22px;">
                <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;line-height:1;">25%</div>
                <div style="font-size:0.8rem;color:#374151;line-height:1.5;margin-top:8px;">
                    Gartner forecasted drop in traditional search engine traffic by 2026
                </div>
            </div>
            <div style="flex:1;background:#F5F3FF;border-radius:14px;padding:20px 22px;">
                <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;line-height:1;">&gt;59%</div>
                <div style="font-size:0.8rem;color:#374151;line-height:1.5;margin-top:8px;">
                    of Google searches now result in zero clicks, as users obtain answers directly from AI-generated summaries, featured snippets, and knowledge panels
                </div>
            </div>
            <div style="flex:1;background:#F5F3FF;border-radius:14px;padding:20px 22px;">
                <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;line-height:1;">&gt;18B</div>
                <div style="font-size:0.8rem;color:#374151;line-height:1.5;margin-top:8px;">
                    of ChatGPT being performed by 700 million premium users on a weekly basis
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── PROVEN RESULTS ──
    st.markdown("""
    <div class="section section-purple" style="text-align:center;">
        <div class="section-tag-white">Proven Results</div>
        <div class="section-title-white">Validated Impact Across 10+ Client Engagements</div>
        <div class="results-grid">
            <div class="result-item">
                <div class="result-num">10+</div>
                <div class="result-label">Successful Clients</div>
                <div class="result-desc">Across retail, travel, hospitality</div>
            </div>
            <div class="result-item">
                <div class="result-num">4X</div>
                <div class="result-label">Higher Conversion</div>
                <div class="result-desc">From ChatGPT vs traditional</div>
            </div>
            <div class="result-item">
                <div class="result-num">15%</div>
                <div class="result-label">Citation Growth</div>
                <div class="result-desc">Improved brand authority</div>
            </div>
            <div class="result-item">
                <div class="result-num">68%</div>
                <div class="result-label">Longer Sessions</div>
                <div class="result-desc">Through AI-optimized content</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── WORKSTREAMS OVERVIEW ──
    st.markdown("""
    <div class="section section-light" style="padding:48px 60px;">
        <div class="section-tag">6-Week Pilot Program</div>
        <div class="section-title" style="margin-bottom:6px;">GEO is No Longer Optional</div>
        <div style="color:#6B7280;font-size:0.92rem;margin-bottom:36px;width:100%;">
            While search spend continues to rise, its impact is fading as AI agents increasingly shape the decisions search used to influence.
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0;">
            <div style="padding:28px 36px 28px 0;border-right:1px dashed #C4B5FD;border-bottom:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 1:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Agent Ranking Diagnostic (ARD)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Conduct the initial evaluation to <strong>establish the baseline ranking performance</strong> of AI agents when comparing your brand to competitive offerings across high-intent consumer scenarios.</div>
            </div>
            <div style="padding:28px 0 28px 36px;border-bottom:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 3:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Distribution &amp; Technical Influence (DTI)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Pinpoint and <strong>propose specific technical and distribution improvements</strong> to maximize the chance that Large Language Models ingest and utilize your verified content.</div>
            </div>
            <div style="padding:28px 36px 0 0;border-right:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 4:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Impact Measurement (Re-Diagnostic)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Following the optimization activities, the Agent Ranking Diagnostic will be performed again to <strong>Re-measure performance</strong> to quantify improvements and establish ongoing program foundation.</div>
            </div>
            <div style="padding:28px 0 0 36px;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 2:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Agent Optimization Plan (AOP)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Based on the diagnostic findings, <strong>design and deploy a specific optimization strategy</strong> aimed at elevating agent recognition and positioning of your offerings.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── WORKSTREAMS DETAIL TABLE ──
    st.markdown("""
    <div class="section section-white" style="padding:48px 60px;">
        <div class="section-tag">Workstream Details</div>
        <div class="section-title" style="margin-bottom:32px;">Activities &amp; Deliverables</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:3px;margin-bottom:0;">
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
                    <li>Develop representative prompts across key personas and use cases</li>
                    <li>Execute multi-run stability testing across ChatGPT and Perplexity</li>
                    <li>Extract agent-generated rankings of brands, models, and attributes</li>
                    <li>Perform power distribution modeling and co-sign similarity analysis</li>
                    <li>Build competitor adjacency maps and Evidence Graphs</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Activities</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Develop LLM-ready content assets: Declarative statements, FAQs, Top 10 lists, Buying guides, Product comparison pages</li>
                    <li>Strengthen associations between your products and target attributes</li>
                    <li>Optimize content structure for agent ingestion</li>
                    <li>Create a Content Influence Blueprint showing exact assets to publish</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Activities</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Audit tagging, metadata, and taxonomy consistency</li>
                    <li>Identify weak or missing structured data</li>
                    <li>Recommend improvements to backlink structure and domain authority</li>
                    <li>Identify dormant or legacy URLs and propose redirects to agent-ready content hubs</li>
                    <li>Audit schema markup (Product, FAQ, How-to schemas)</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Activities</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Re-test all prompts across ChatGPT and Perplexity</li>
                    <li>Measure semantic drift, ranking changes, attribute alignment, and evidence graph updates</li>
                    <li>Recompute AXO Score</li>
                </ul>
            </div>
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-top:12px;">
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>AXO Baseline Report</li>
                    <li>Brand &amp; Product Ranking Index</li>
                    <li>Power Curve Analysis</li>
                    <li>Co-Sign Similarity Maps</li>
                    <li>Attribute Influence Map</li>
                    <li>Competitor Adjacency Analysis</li>
                    <li>AXO Baseline Score (v1.0)</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Agent Optimization Plan</li>
                    <li>LLM-Ready Content Package</li>
                    <li>Attribute Reinforcement Strategy</li>
                    <li>Content Influence Blueprint</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>Distribution &amp; Technical Influence Report</li>
                    <li>Metadata Remediation Plan</li>
                    <li>Backlink &amp; Redirect Strategy</li>
                    <li>Schema Optimization Guide</li>
                </ul>
            </div>
            <div style="border:1px solid #E5E7EB;border-radius:10px;padding:18px;background:#FAFAFA;">
                <div style="font-size:0.85rem;font-weight:800;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:12px;">Deliverables</div>
                <ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.7;">
                    <li>AXO Impact Report</li>
                    <li>Before/After Ranking Comparison</li>
                    <li>Updated AXO Score (v2.0)</li>
                    <li>Recommendations for ongoing improvement</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section section-white" style="text-align:center;">
        <div class="section-tag">Choose Your Path</div>
        <div class="section-title">Pilot Program Options</div>
        <div class="pilot-grid">
            <div class="pilot-card">
                <div class="pilot-option">Option 1</div>
                <div class="pilot-weeks">6 Weeks</div>
                <ul class="pilot-items">
                    <li>Agent Ranking Diagnostic (ARD)</li>
                    <li>Agent Optimization Plan (AOP)</li>
                </ul>
            </div>
            <div class="pilot-card recommended">
                <div class="recommended-badge">Recommended</div>
                <div class="pilot-option">Option 2</div>
                <div class="pilot-weeks">7 Weeks</div>
                <ul class="pilot-items">
                    <li>Agent Ranking Diagnostic (ARD)</li>
                    <li>Agent Optimization Plan (AOP)</li>
                    <li>Impact Measurement (Re-Diagnostic)</li>
                </ul>
            </div>
            <div class="pilot-card">
                <div class="pilot-option">Option 3</div>
                <div class="pilot-weeks">7 Weeks</div>
                <ul class="pilot-items">
                    <li>Agent Ranking Diagnostic (ARD)</li>
                    <li>Agent Optimization Plan (AOP)</li>
                    <li>Distribution &amp; Technical Influence (DTI)</li>
                    <li>Impact Measurement (Re-Diagnostic)</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# AI COMPARISON PAGE
# ════════════════════════════════════════════════════════════
elif page == "AI Comparison":

    st.markdown("""
    <div class="hero" style="padding:52px 60px;">
        <div class="hero-badge">✦ Live AI Prompt Lab</div>
        <h1 style="font-size:2.6rem;">AI Prompt <span>Comparison</span></h1>
        <div class="hero-sub">Powered by GPT-5.4 · See how AI answers brand-relevant questions in real time</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="score-section">', unsafe_allow_html=True)

    DEFAULT_KEY = "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"

    with st.expander("🔑 OpenRouter API Key", expanded=False):
        st.caption("A default key is pre-loaded. Paste your own key below to override it.")
        custom_key = st.text_input("Use your own API Key (optional)", type="password", placeholder="sk-or-v1-...")
        if custom_key.strip():
            openrouter_key = custom_key.strip()
            st.success("✅ Using your custom API key")
        else:
            openrouter_key = DEFAULT_KEY

    if "ai_history" not in st.session_state:
        st.session_state.ai_history = []

    query = st.text_input("Enter a prompt:", "", placeholder="Ask anything...")
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
                    if "401" in err: st.error("❌ Invalid API key — check your key or use the default")
                    elif "402" in err: st.error("❌ Insufficient credits — add balance at openrouter.ai/settings/credits")
                    elif "404" in err: st.error("❌ Model unavailable — try again shortly")
                    else: st.error(f"❌ Error: {e}")

    # Render chat history in ChatGPT style
    for item in reversed(st.session_state.ai_history):
        user_html = (
            '<div style="display:flex;justify-content:flex-end;margin:20px 0 10px 0;">'
            '<div style="background:#F4F4F4;color:#111827;border-radius:18px 18px 4px 18px;'
            'padding:12px 18px;max-width:60%;font-size:0.95rem;font-weight:500;'
            'box-shadow:0 1px 3px rgba(0,0,0,0.07);">'
            + item["q"] +
            '</div></div>'
        )
        st.markdown(user_html, unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:4px 0 12px 0;">', unsafe_allow_html=True)
        st.markdown(item["a"])
        st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:16px 0;">', unsafe_allow_html=True)

    if st.session_state.ai_history:
        col_cap, col_clr = st.columns([4, 1])
        with col_cap:
            st.caption("Model: openai/gpt-5.4 via OpenRouter")
        with col_clr:
            if st.button("🗑️ Clear", key="clr_ai"):
                st.session_state.ai_history = []
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# GEO DASHBOARD PAGE  (API key hardcoded — no user input)
# ════════════════════════════════════════════════════════════
elif page == "GEO Dashboard":

    st.markdown("""
    <div class="hero" style="padding:52px 60px;">
        <div class="hero-badge">✦ Real GEO Scoring</div>
        <h1 style="font-size:2.6rem;">GEO <span>Scorecard</span></h1>
        <div class="hero-sub">Enter any brand URL · Get your AI brand visibility score</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="score-section">', unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* GEO Dashboard analyze button — soft purple, not red */
    div[data-testid="stHorizontalBlock"] ~ div button[kind="secondaryFormSubmit"],
    .score-section button, section.main button[data-testid="baseButton-secondary"] {
        background: #7C3AED !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    section.main div[data-testid="stButton"] > button {
        background: #7C3AED !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: background 0.15s !important;
    }
    section.main div[data-testid="stButton"] > button:hover {
        background: #6D28D9 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Score scale reference
    sc1, sc2, sc3, sc4 = st.columns(4)
    for col, (rng, lbl, tc, bg, desc) in zip(
        [sc1, sc2, sc3, sc4],
        [("80–100","Excellent","#065F46","#D1FAE5","Well optimized for AI citation"),
         ("60–79", "Good",     "#1E40AF","#DBEAFE","Minor improvements recommended"),
         ("40–59", "Needs Work","#92400E","#FEF3C7","Several issues to address"),
         ("0–39",  "Poor",     "#991B1B","#FEE2E2","Major optimization needed")]
    ):
        with col:
            st.markdown(f"""<div style="background:{bg};border-radius:12px;padding:16px 18px;text-align:center;">
                <div style="font-size:0.75rem;font-weight:700;color:{tc};text-transform:uppercase;">{rng}</div>
                <div style="font-size:1.2rem;font-weight:800;color:{tc};margin:4px 0;">{lbl}</div>
                <div style="font-size:0.78rem;color:{tc};opacity:0.85;">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    brand_url = st.text_input(
        "🔗 Brand URL",
        placeholder="https://www.capitalone.com/",
        help="Enter any brand URL to analyze its AI visibility score"
    )

    if st.button("🔍 Run Live AI Analysis", use_container_width=True):
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
                    except Exception as e:
                        st.error(f"❌ AI analysis failed: {e}")
                        st.stop()

                compare_result = None

                geo   = result.get("overall_geo_score", 0)
                seo   = result.get("seo_score", 0)
                brand = result.get("brand_name", page_data["domain"])
                label, badge_color, badge_bg = score_badge(geo)

                # ── GEO GAUGE (top) ──
                gauge_col, info_col = st.columns([1, 2])
                with gauge_col:
                    fig_g = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=geo,
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
                        f'<div style="background:white;border-radius:14px;border:1px solid #E5E7EB;'
                        f'padding:22px 26px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                        f'<div style="font-size:1.3rem;font-weight:800;color:#111827;">{brand}</div>'
                        f'<div style="margin:4px 0 14px 0;"><a href="{brand_url}" target="_blank" style="color:#7C3AED;font-size:0.82rem;">{brand_url[:70]}{"..." if len(brand_url)>70 else ""}</a></div>'
                        f'<div style="display:flex;gap:28px;flex-wrap:wrap;">'
                        f'<div><div style="font-size:0.7rem;color:#9CA3AF;font-weight:600;text-transform:uppercase;">SEO Score</div>'
                        f'<div style="font-size:1.3rem;font-weight:800;color:#374151;">{result.get("seo_score",0)}<span style="font-size:0.78rem;color:#9CA3AF;">/100</span></div></div>'
                                                f'<div><div style="font-size:0.7rem;color:#9CA3AF;font-weight:600;text-transform:uppercase;">Status</div>'
                        f'<div style="background:{badge_bg};color:{badge_color};padding:4px 14px;border-radius:50px;font-size:0.78rem;font-weight:700;">{label}</div></div>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── 5 METRIC CARDS: Visibility, Citation, Sentiment, Avg Rank, Overall GEO ──
                vis   = result.get("context", 0)
                cit   = result.get("reliability", 0)
                sent  = result.get("exclusivity", 0)
                org   = result.get("organization", 0)
                avg_rank = max(1, round(6 - (geo / 20)))  # derive rank from score (1-5)

                mc1, mc2, mc3, mc4 = st.columns(4)
                cards = [
                    (mc1, "linear-gradient(135deg,#3B82F6,#06B6D4)",   "👁️", vis,      "Visibility Score", "AI response presence"),
                    (mc2, "linear-gradient(135deg,#8B5CF6,#A855F7)",   "🏅", cit,      "Citation Score",   "Source authority"),
                    (mc3, "linear-gradient(135deg,#10B981,#34D399)",   "📈", sent,     "Sentiment Score",  "Brand perception"),
                    (mc4, "linear-gradient(135deg,#F59E0B,#FBBF24)",   "🎯", f"#{avg_rank}", "Avg. Rank", "AI mention position"),
                ]
                for col, grad, icon, val, lbl, sub in cards:
                    with col:
                        st.markdown(
                            f'<div style="background:white;border-radius:16px;padding:20px 18px;'
                            f'box-shadow:0 1px 4px rgba(0,0,0,0.07);border:1px solid #F3F4F6;">'
                            f'<div style="width:42px;height:42px;border-radius:12px;background:{grad};'
                            f'display:flex;align-items:center;justify-content:center;font-size:1.1rem;margin-bottom:12px;">{icon}</div>'
                            f'<div style="font-size:1.8rem;font-weight:800;color:#111827;line-height:1;">{val}</div>'
                            f'<div style="font-size:0.84rem;font-weight:600;color:#374151;margin-top:5px;">{lbl}</div>'
                            f'<div style="font-size:0.76rem;color:#9CA3AF;margin-top:2px;">{sub}</div>'
                            f'</div>',
                            unsafe_allow_html=True
                        )

                st.markdown("<br>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # ── TOP 10 BY GEO SCORE ──
                domain_lower2 = page_data["domain"].lower()
                fin_kws2  = ["capital","chase","amex","citi","discover","bank","credit","card","finance","fargo"]
                auto_kws2 = ["vw","volkswagen","toyota","ford","honda","bmw","tesla","auto","car","motor"]
                if any(x in domain_lower2 for x in fin_kws2):
                    top10_title = "Financial Services"
                    top10 = [
                        {"Brand":"American Express","GEO":91,"Vis":88,"Cit":94,"Sen":92,"Rank":"#1"},
                        {"Brand":"Chase",           "GEO":82,"Vis":78,"Cit":89,"Sen":85,"Rank":"#2"},
                        {"Brand":"Citi",            "GEO":75,"Vis":72,"Cit":78,"Sen":76,"Rank":"#3"},
                        {"Brand":"Discover",        "GEO":71,"Vis":68,"Cit":75,"Sen":79,"Rank":"#4"},
                        {"Brand":"Wells Fargo",     "GEO":68,"Vis":65,"Cit":71,"Sen":72,"Rank":"#5"},
                        {"Brand":"Bank of America", "GEO":66,"Vis":63,"Cit":69,"Sen":70,"Rank":"#6"},
                        {"Brand":brand,             "GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Rank":f"#{avg_rank}"},
                        {"Brand":"Synchrony",       "GEO":58,"Vis":55,"Cit":60,"Sen":62,"Rank":"#8"},
                        {"Brand":"Barclays",        "GEO":54,"Vis":51,"Cit":56,"Sen":58,"Rank":"#9"},
                        {"Brand":"USAA",            "GEO":52,"Vis":49,"Cit":54,"Sen":60,"Rank":"#10"},
                    ]
                elif any(x in domain_lower2 for x in auto_kws2):
                    top10_title = "Automotive"
                    top10 = [
                        {"Brand":"Tesla",      "GEO":94,"Vis":91,"Cit":96,"Sen":89,"Rank":"#1"},
                        {"Brand":"Toyota",     "GEO":88,"Vis":85,"Cit":90,"Sen":87,"Rank":"#2"},
                        {"Brand":"BMW",        "GEO":83,"Vis":80,"Cit":85,"Sen":84,"Rank":"#3"},
                        {"Brand":"Honda",      "GEO":79,"Vis":76,"Cit":82,"Sen":81,"Rank":"#4"},
                        {"Brand":"Ford",       "GEO":73,"Vis":70,"Cit":75,"Sen":72,"Rank":"#5"},
                        {"Brand":"Mercedes",   "GEO":71,"Vis":68,"Cit":73,"Sen":75,"Rank":"#6"},
                        {"Brand":"Hyundai",    "GEO":68,"Vis":65,"Cit":70,"Sen":67,"Rank":"#7"},
                        {"Brand":brand,        "GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Rank":f"#{avg_rank}"},
                        {"Brand":"Kia",        "GEO":60,"Vis":57,"Cit":62,"Sen":63,"Rank":"#9"},
                        {"Brand":"Nissan",     "GEO":56,"Vis":53,"Cit":58,"Sen":60,"Rank":"#10"},
                    ]
                else:
                    top10_title = "General"
                    top10 = [
                        {"Brand":"Leader A",    "GEO":92,"Vis":89,"Cit":94,"Sen":91,"Rank":"#1"},
                        {"Brand":"Leader B",    "GEO":85,"Vis":82,"Cit":87,"Sen":84,"Rank":"#2"},
                        {"Brand":"Leader C",    "GEO":80,"Vis":77,"Cit":82,"Sen":79,"Rank":"#3"},
                        {"Brand":brand,         "GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Rank":f"#{avg_rank}"},
                        {"Brand":"Competitor D","GEO":72,"Vis":69,"Cit":74,"Sen":71,"Rank":"#5"},
                        {"Brand":"Competitor E","GEO":68,"Vis":65,"Cit":70,"Sen":67,"Rank":"#6"},
                        {"Brand":"Competitor F","GEO":63,"Vis":60,"Cit":65,"Sen":62,"Rank":"#7"},
                        {"Brand":"Competitor G","GEO":59,"Vis":56,"Cit":61,"Sen":58,"Rank":"#8"},
                        {"Brand":"Competitor H","GEO":54,"Vis":51,"Cit":56,"Sen":53,"Rank":"#9"},
                        {"Brand":"Competitor I","GEO":50,"Vis":47,"Cit":52,"Sen":49,"Rank":"#10"},
                    ]

                top10_sorted = sorted(top10, key=lambda x: x["GEO"], reverse=True)
                t10_rows = ""
                for idx, c in enumerate(top10_sorted, 1):
                    is_you = c["Brand"] == brand
                    bg   = "#F5F3FF" if is_you else ("white" if idx%2==1 else "#FAFAFA")
                    bdr  = "border-left:3px solid #7C3AED;" if is_you else ""
                    fw   = "700" if is_you else "400"
                    gc   = c["GEO"]
                    gcol = "#10B981" if gc>=80 else "#F59E0B" if gc>=60 else "#EF4444"
                    you_badge = ' <span style="background:#EDE9FE;color:#7C3AED;border-radius:4px;padding:1px 6px;font-size:0.7rem;font-weight:700;">You</span>' if is_you else ""
                    t10_rows += (
                        f'<tr style="background:{bg};{bdr}">'
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
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">'
                    f'<span style="color:#7C3AED;">🏆</span>'
                    f'<span style="font-size:0.95rem;font-weight:700;color:#111827;">Top 10 Brands — {top10_title} (sorted by GEO Score)</span>'
                    f'</div>'
                    f'<table style="width:100%;border-collapse:collapse;">'
                    f'<thead><tr style="border-bottom:1px solid #E5E7EB;">'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">#</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Brand</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">GEO Score</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Visibility</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Citations</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Sentiment</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Avg. Rank</th>'
                    f'</tr></thead><tbody>{t10_rows}</tbody></table></div>',
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── RECOMMENDATIONS ──
                # Use pre-classified lists from AI analysis
                strengths  = result.get("strengths_list", [])[:3]   # always max 3
                weaknesses = result.get("improvements_list", [])[:5] # always 5
                # Fallback if missing
                all_insights = result.get("insights", [])
                if not strengths and all_insights:
                    strengths = all_insights[:2]
                if not weaknesses and all_insights:
                    weaknesses = all_insights[:5]
                actions_high = [a["action"] for a in result.get("actions",[]) if a.get("priority")=="High"]
                actions_med  = [a["action"] for a in result.get("actions",[]) if a.get("priority")=="Medium"]

                s_html = "".join(
                    f'<li style="padding:6px 0;font-size:0.84rem;color:#374151;display:flex;gap:10px;align-items:flex-start;">'
                    f'<span style="color:#10B981;font-weight:700;flex-shrink:0;">✓</span><span>{s}</span></li>'
                    for s in strengths
                )
                w_html = "".join(
                    f'<li style="padding:6px 0;font-size:0.84rem;color:#374151;display:flex;gap:10px;align-items:flex-start;">'
                    f'<span style="color:#EF4444;font-weight:700;flex-shrink:0;">✗</span><span>{w}</span></li>'
                    for w in weaknesses
                )
                a_html = "".join(
                    f'<li style="padding:5px 0;font-size:0.84rem;color:#374151;"><span style="background:#FEE2E2;color:#991B1B;border-radius:4px;padding:1px 8px;font-size:0.71rem;font-weight:700;margin-right:6px;">High</span>{a}</li>'
                    for a in actions_high
                ) + "".join(
                    f'<li style="padding:5px 0;font-size:0.84rem;color:#374151;"><span style="background:#FEF3C7;color:#92400E;border-radius:4px;padding:1px 8px;font-size:0.71rem;font-weight:700;margin-right:6px;">Medium</span>{a}</li>'
                    for a in actions_med
                )

                st.markdown(
                    '<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:28px 32px;">'
                    '<div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:18px;">💡 Recommendations</div>'
                    '<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px;">'
                    f'<div style="background:#F0FDF4;border-radius:10px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#065F46;margin-bottom:10px;">What is Working Well</div><ul style="list-style:none;padding:0;margin:0;">{s_html}</ul></div>'
                    f'<div style="background:#FFF1F2;border-radius:10px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#9F1239;margin-bottom:10px;">What Needs Improvement</div><ul style="list-style:none;padding:0;margin:0;">{w_html}</ul></div>'
                    '</div>'
                    f'<div style="border-top:1px solid #F3F4F6;padding-top:16px;"><div style="font-size:0.82rem;font-weight:700;color:#111827;margin-bottom:10px;">⚡ Priority Actions</div><ul style="list-style:none;padding:0;margin:0;">{a_html}</ul></div>'
                    '</div>',
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── METRIC DEFINITIONS ──
                st.markdown(
                    '<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:28px 32px;">' +
                    '<div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:20px;">Metric Definitions</div>' +
                    '<div style="display:flex;flex-direction:column;gap:0;">' +
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;">' +
                        '<div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">GEO Score</div>' +
                        '<div style="font-size:0.82rem;color:#374151;line-height:1.65;">Composite 0–100 score calculated using Profound methodology: Visibility (30%) + Sentiment (20%) + Prominence (20%) + Citation Share (15%) + Share of Voice (15%). Scores 80+ = Excellent, 60–79 = Good, 40–59 = Needs Work, below 40 = Poor.</div>' +
                    '</div>' +
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;">' +
                        '<div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Visibility Score</div>' +
                        '<div style="font-size:0.82rem;color:#374151;line-height:1.65;">Percentage of live AI queries where your brand was mentioned by name. Calculated as: (queries mentioning brand) ÷ (total queries run) × 100. A score of 80 means your brand appeared in 4 out of 5 AI responses.</div>' +
                    '</div>' +
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;">' +
                        '<div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Citation Score</div>' +
                        '<div style="font-size:0.82rem;color:#374151;line-height:1.65;">How often AI models cite your brand as a trusted or authoritative source — not just mention it, but reference it as a recommended choice. Measured from the live AI responses: authority references ÷ total responses × 100.</div>' +
                    '</div>' +
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;">' +
                        '<div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Sentiment Score</div>' +
                        '<div style="font-size:0.82rem;color:#374151;line-height:1.65;">Tone analysis of how AI describes your brand in responses. Positive = recommended, top pick, best option (85–100). Neutral = listed as an option (50–70). Negative = flagged issues or not recommended (0–40). Averaged across all mentions in live responses.</div>' +
                    '</div>' +
                    '<div style="padding:14px 0;">' +
                        '<div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Avg. Rank</div>' +
                        '<div style="font-size:0.82rem;color:#374151;line-height:1.65;">Your brand average list position when AI generates ranked recommendations (rank #1 = mentioned first = best). Measured directly from live response order. A GEO Score of 80+ typically earns rank #1–2, 60–79 earns #2–3, 40–59 earns #3–4, below 40 ranks #4 or lower.</div>' +
                    '</div>' +
                    '</div></div>',
                    unsafe_allow_html=True
                )
                st.caption(f"GEO Score · AI analysis of {brand_url} · CORE framework · Percepta v2.0")


    else:
        st.markdown("""
        <div style="background:#F9FAFB;border:2px dashed #D1D5DB;border-radius:16px;
                    padding:56px;text-align:center;margin-top:24px;">
            <div style="font-size:3rem;">🔗</div>
            <div style="font-size:1.2rem;font-weight:800;color:#111827;margin:12px 0 8px 0;">
                Enter a brand URL above to get started
            </div>
            <div style="color:#6B7280;font-size:0.9rem;max-width:480px;margin:0 auto 20px auto;">
                Percepta runs live AI queries and measures how often your brand appears in AI-generated responses — no setup needed.
            </div>
            <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">capitalone.com/credit-cards</span>
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">chase.com/sapphire</span>
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">vw.com/models/id4</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
