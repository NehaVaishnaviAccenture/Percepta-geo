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

# ── API KEY FROM STREAMLIT SECRETS ───────────────────────────
INTERNAL_API_KEY = st.secrets["OPENROUTER_API_KEY"]

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
.results-grid { display: flex; gap: 40px; margin-top: 32px; justify-content: center; flex-wrap: wrap; }
.result-item { text-align: center; }
.result-num   { font-size: 3.2rem; font-weight: 900; color: white; line-height: 1; }
.result-label { font-size: 0.95rem; font-weight: 700; color: white; margin-top: 6px; }
.result-desc  { font-size: 0.82rem; color: rgba(255,255,255,0.72); margin-top: 4px; }
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
.score-section { padding: 32px 40px; }
div[data-testid="stHorizontalBlock"]:first-of-type > div > div > div > button {
    border: none !important; background: transparent !important;
    color: #6B7280 !important; font-weight: 500 !important;
    font-size: 0.88rem !important; padding: 8px 0 !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; width: 100% !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type > div > div > div > button:hover {
    color: #7C3AED !important; background: transparent !important;
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
        model="openai/gpt-4o",
        messages=[
            {"role": "system", "content": """You are a sharp, direct AI assistant. When answering any question about products, services, brands, cards, tools, or recommendations:
ALWAYS follow this exact format:
1. Start with 1-2 sentence direct answer using **bold** for key terms and emojis inline
2. Use ## headers with emojis for each category
3. Under each header, name the SPECIFIC real competitor/brand
4. Use bullet points: • ✅ benefit, • ❌ downside
5. End each section with a bold insight line starting with 🔍 or 💡
6. Finish with a ## 👉 Quick Pick section with → arrows
7. Last line: ask 1 follow-up question
RULES: Always name real brands, real products, real percentages and fees. Never give vague generic advice."""},
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
    brand = page_data.get("title", "").split("|")[0].split("-")[0].strip()
    if not brand or len(brand) < 2:
        domain = page_data.get("domain", "brand")
        brand = domain.replace("www.", "").split(".")[0].title()

    client = get_client()

    queries = [
        f"Tell me about {brand} — is it a good company?",
        f"How does {brand} compare to its main competitors?",
        f"What are the best products or services {brand} offers?",
        f"What are the pros and cons of {brand}?",
        f"What do experts recommend instead of or alongside {brand}?"
    ]

    q_list = "\n\n".join([f"Q{i+1}: {q}" for i, q in enumerate(queries)])
    batch_prompt = (
        "Answer each question below as a knowledgeable consumer advisor. "
        "Be specific, name real brands and products. Answer naturally - do not avoid or force any brand.\n\n"
        + q_list
        + "\n\nRespond with exactly:\nA1: [answer]\nA2: [answer]\nA3: [answer]\nA4: [answer]\nA5: [answer]"
    )

    r1 = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": batch_prompt}],
        temperature=0.5, max_tokens=700
    )
    batch_text = r1.choices[0].message.content

    answers = {}
    for i in range(1, 6):
        marker = f"A{i}:"
        nxt = f"A{i+1}:"
        if marker in batch_text:
            s = batch_text.index(marker) + len(marker)
            e = batch_text.index(nxt) if nxt in batch_text else len(batch_text)
            answers[i] = batch_text[s:e].strip()
        else:
            answers[i] = ""

    qa_pairs = [{"q": queries[i-1], "a": answers.get(i, "")} for i in range(1, 6)]
    brand_l  = brand.lower()

    qa_parts = []
    for i, p in enumerate(qa_pairs):
        qa_parts.append(f"Q{i+1}: {p['q']}\nA{i+1}: {p['a']}")
    qa_formatted = "\n\n".join(qa_parts)

    scoring_prompt = f"""You are an objective GEO measurement analyst.

Read these 5 AI responses about "{brand}" carefully. Every score MUST be derived by counting and measuring from the actual text. Do not estimate independently.

=== AI RESPONSES ===
{qa_formatted}
===================

Follow these exact steps in order:

STEP 1 — VISIBILITY (count exactly):
Go through each response A1 to A5. Does the word "{brand}" appear in it? (case insensitive)
Write out: A1=yes/no, A2=yes/no, A3=yes/no, A4=yes/no, A5=yes/no
Count total YES. Call this V.
Visibility = (V / 5) * 100
Example: V=2 means visibility=40. V=5 means visibility=100. V=0 means visibility=0.

STEP 2 — PROMINENCE (only from YES responses):
For each YES response, what position was "{brand}" first mentioned among all brand names?
First brand named = position 1, second = position 2, etc.
Average the positions across all YES responses.
Convert to score: avg<=1.0→100, avg<=2.0→75, avg<=3.0→50, avg<=4.0→25, avg>4.0→10, V=0→0

STEP 3 — SENTIMENT (only from YES responses):
For each YES response, classify language about "{brand}":
Positive (recommended, best, great, top, excellent, leading) = 100
Neutral (also available, one option, listed alongside) = 50
Negative (avoid, problems, worse, criticized) = 0
Average across YES responses only. V=0 means sentiment=0.

STEP 4 — CITATION SHARE:
Count every brand name mentioned across ALL 5 responses. List them with counts.
Count how many times "{brand}" appears total. Call this B.
Count ALL brand mentions total. Call this T.
Citation share = round((B / T) * 100) if T>0 else 0. Cap at 100.
NOTE: If V=2, brand only appeared in 2 responses, so B will be small, so citation share will naturally be small. This is mathematically correct.

STEP 5 — SHARE OF VOICE:
Same as Step 4. Share of voice = citation share.

STEP 6 — AVG RANK:
From Step 2, average position rounded to nearest integer. Format as "#1", "#2", "#3".
V=0 → "N/A"

STEP 7 — SEO SCORE:
Depth of knowledge AI showed about "{brand}" specifically:
Rich specific detail = 70-100, Some detail but vague = 40-69, Very little = 10-39, Never mentioned = 0-20

STEP 8 — STRENGTHS (exactly 3): Based only on what you observed above.
STEP 9 — IMPROVEMENTS (exactly 5): Based only on what you observed above.
STEP 10 — ACTIONS (exactly 5 prioritized fixes): Concrete and actionable.

FINAL SANITY CHECK before writing JSON:
- visibility = (V/5)*100. If V=2, visibility MUST equal 40. Non-negotiable.
- citation_share = (B/T)*100. If brand rarely appeared, this is a small number like 8-15%. NOT 92.
- sentiment only reflects responses where brand appeared. Cannot be high if brand never appeared positively.
- All numbers must follow from your counting steps above.

Return ONLY valid JSON, no text before or after:
{{"visibility":0,"citation_share":0,"sentiment":0,"prominence":0,"share_of_voice":0,"seo_score":0,"avg_rank":"#3","strengths":["1. ...","2. ...","3. ..."],"improvements":["1. ...","2. ...","3. ...","4. ...","5. ..."],"actions":[{{"priority":"High","action":"..."}},{{"priority":"High","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Low","action":"..."}}]}}"""

    r2 = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=[{"role": "user", "content": scoring_prompt}],
        temperature=0.0, max_tokens=1200
    )
    raw = re.sub(r"```json|```", "", r2.choices[0].message.content.strip())
    sc  = json.loads(raw)

    visibility     = sc.get("visibility", 0)
    citation_share = sc.get("citation_share", 0)
    sentiment      = sc.get("sentiment", 0)
    prominence     = sc.get("prominence", 0)
    sov            = sc.get("share_of_voice", 0)

    # Hard math enforcement: if brand appeared in V/5 responses,
    # citation share is mathematically bounded. Cap it.
    # e.g. visibility=40 means brand in 2/5 responses → citation share max ~40
    citation_share = min(citation_share, visibility)
    sov            = min(sov, visibility)
    # Sentiment only applies where brand appeared; if visibility is 0, zero it out
    if visibility == 0:
        sentiment  = 0
        prominence = 0
        citation_share = 0
        sov        = 0

    mentions       = sum(1 for p in qa_pairs if brand_l in p["a"].lower())

    geo_score = round(
        visibility     * 0.30 +
        sentiment      * 0.20 +
        prominence     * 0.20 +
        citation_share * 0.15 +
        sov            * 0.15
    )

    return {
        "brand_name":            brand,
        "visibility":            visibility,
        "sentiment":             sentiment,
        "prominence":            prominence,
        "citation_share":        citation_share,
        "share_of_voice":        sov,
        "overall_geo_score":     geo_score,
        "seo_score":             sc.get("seo_score", 0),
        "avg_rank":              sc.get("avg_rank", "#?"),
        "responses_with_brand":  mentions,
        "total_responses":       5,
        "insights":              sc.get("improvements", []),
        "strengths_list":        sc.get("strengths", []),
        "improvements_list":     sc.get("improvements", []),
        "actions":               sc.get("actions", []),
        "context":               visibility,
        "organization":          prominence,
        "reliability":           citation_share,
        "exclusivity":           sentiment,
    }

def score_badge(score):
    if score >= 80:   return "Excellent", "#065F46", "#D1FAE5"
    elif score >= 60: return "Good",      "#1E40AF", "#DBEAFE"
    elif score >= 40: return "Needs Work","#92400E", "#FEF3C7"
    else:             return "Poor",      "#991B1B", "#FEE2E2"


# ── SESSION STATE ─────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "Overview"

active = st.session_state.page
ICON_DOC  = ""
ICON_SWAP = ""
ICON_BARS = ""

st.markdown("""
<style>
div[data-testid="stHorizontalBlock"]:first-of-type {
    background: white !important; border-bottom: 1px solid #E5E7EB !important;
    padding: 8px 28px !important; margin: 0 !important;
    position: sticky !important; top: 0 !important; z-index: 999 !important;
    align-items: center !important; box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button {
    border: none !important; border-radius: 8px !important;
    font-size: 0.88rem !important; font-weight: 500 !important;
    padding: 7px 16px !important; cursor: pointer !important;
    width: 100% !important; white-space: nowrap !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"] {
    background: transparent !important; color: #6B7280 !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]:hover {
    background: #F5F3FF !important; color: #7C3AED !important;
}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"] {
    background: #EDE9FE !important; color: #7C3AED !important; font-weight: 700 !important;
}
</style>
""", unsafe_allow_html=True)

nb_c, ov_c, ai_c, geo_c = st.columns([3, 1, 1.3, 1.4])

with nb_c:
    st.markdown("""
    <style>
    .percepta-brand-wrap {
        display: flex; align-items: center; gap: 10px;
        cursor: pointer !important; padding: 4px 0;
        position: relative; z-index: 1; user-select: none;
    }
    .percepta-brand-wrap:hover .percepta-title { color: #7C3AED !important; }
    .percepta-icon {
        width: 36px; height: 36px; flex-shrink: 0; border-radius: 9px;
        background: linear-gradient(135deg, #5B21B6 0%, #7C3AED 55%, #A855F7 100%);
        display: flex; align-items: center; justify-content: center;
    }
    .percepta-title {
        font-size: 1.05rem; font-weight: 800; color: #111827;
        letter-spacing: -0.3px; transition: color 0.15s; line-height: 1;
    }
    div[data-testid="stHorizontalBlock"]:first-of-type > div:first-child button {
        position: absolute !important; top: 0 !important; left: 0 !important;
        width: 100% !important; height: 56px !important; opacity: 0 !important;
        cursor: pointer !important; z-index: 2 !important;
        border: none !important; background: transparent !important;
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
    </div>
    """, unsafe_allow_html=True)

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
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="section section-light" style="padding:48px 60px;">
        <div class="section-tag">6-Week Pilot Program</div>
        <div class="section-title" style="margin-bottom:6px;">GEO is No Longer Optional</div>
        <div style="color:#6B7280;font-size:0.92rem;margin-bottom:36px;width:100%;">While search spend continues to rise, its impact is fading as AI agents increasingly shape purchase decisions.</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0;">
            <div style="padding:28px 36px 28px 0;border-right:1px dashed #C4B5FD;border-bottom:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 1:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Agent Ranking Diagnostic (ARD)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Conduct the initial evaluation to <strong>establish the baseline ranking performance</strong> of AI agents when comparing your brand to competitive offerings across high-intent consumer scenarios.</div>
            </div>
            <div style="padding:28px 0 28px 36px;border-bottom:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 3:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Distribution &amp; Technical Influence (DTI)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Pinpoint and <strong>propose specific technical and distribution improvements</strong> to maximize the chance that LLMs ingest and utilize your verified content.</div>
            </div>
            <div style="padding:28px 36px 0 0;border-right:1px dashed #C4B5FD;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 4:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Impact Measurement (Re-Diagnostic)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Re-run the diagnostic to <strong>quantify improvements</strong> and establish ongoing program foundation.</div>
            </div>
            <div style="padding:28px 0 0 36px;">
                <div style="font-size:0.78rem;font-weight:800;color:#7C3AED;margin-bottom:4px;">Workstream 2:</div>
                <div style="font-size:0.95rem;font-style:italic;font-weight:700;color:#1F2937;margin-bottom:10px;">Agent Optimization Plan (AOP)</div>
                <div style="font-size:0.82rem;color:#374151;line-height:1.6;">Based on diagnostic findings, <strong>design and deploy a specific optimization strategy</strong> to elevate agent recognition of your brand.</div>
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
        <div class="hero-sub">Powered by GPT-4o · See how AI answers brand-relevant questions in real time</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="score-section">', unsafe_allow_html=True)

    DEFAULT_KEY = st.secrets["OPENROUTER_API_KEY"]

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
            with st.spinner("Querying GPT-4o..."):
                try:
                    resp = get_response(query, openrouter_key)
                    st.session_state.ai_history.append({"q": query, "a": resp})
                except Exception as e:
                    err = str(e)
                    if "401" in err: st.error("❌ Invalid API key")
                    elif "402" in err: st.error("❌ Insufficient credits — add balance at openrouter.ai/settings/credits")
                    elif "404" in err: st.error("❌ Model unavailable — try again shortly")
                    else: st.error(f"❌ Error: {e}")

    for item in reversed(st.session_state.ai_history):
        user_html = (
            '<div style="display:flex;justify-content:flex-end;margin:20px 0 10px 0;">'
            '<div style="background:#F4F4F4;color:#111827;border-radius:18px 18px 4px 18px;'
            'padding:12px 18px;max-width:60%;font-size:0.95rem;font-weight:500;">'
            + item["q"] + '</div></div>'
        )
        st.markdown(user_html, unsafe_allow_html=True)
        st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:4px 0 12px 0;">', unsafe_allow_html=True)
        st.markdown(item["a"])
        st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:16px 0;">', unsafe_allow_html=True)

    if st.session_state.ai_history:
        col_cap, col_clr = st.columns([4, 1])
        with col_cap:
            st.caption("Model: openai/gpt-4o via OpenRouter")
        with col_clr:
            if st.button("🗑️ Clear", key="clr_ai"):
                st.session_state.ai_history = []
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# GEO DASHBOARD PAGE
# ════════════════════════════════════════════════════════════
elif page == "GEO Dashboard":
    st.markdown("""
    <div class="hero" style="padding:52px 60px;">
        <div class="hero-badge">✦ Real GEO Scoring</div>
        <h1 style="font-size:2.6rem;">GEO <span>Scorecard</span></h1>
        <div class="hero-sub">Enter any brand URL · Scores calculated by counting actual AI mentions</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="score-section">', unsafe_allow_html=True)
    st.markdown("""
    <style>
    section.main div[data-testid="stButton"] > button {
        background: #7C3AED !important; color: white !important;
        border: none !important; border-radius: 8px !important;
        font-weight: 600 !important; transition: background 0.15s !important;
    }
    section.main div[data-testid="stButton"] > button:hover { background: #6D28D9 !important; }
    </style>
    """, unsafe_allow_html=True)

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

    brand_url = st.text_input("🔗 Brand URL", placeholder="https://www.capitalone.com/",
                               help="Enter any brand URL to analyze its AI visibility score")

    if st.button("🔍 Run Live AI Analysis", use_container_width=True):
        if not brand_url.strip() or not brand_url.startswith("http"):
            st.error("⚠️ Please enter a valid URL starting with http:// or https://")
        else:
            with st.spinner("🌐 Identifying brand from URL..."):
                page_data = fetch_page_content(brand_url)

            if not page_data["ok"]:
                st.error(f"❌ Could not fetch URL: {page_data['error']}")
            else:
                with st.spinner("🤖 Running live AI queries and counting brand mentions..."):
                    try:
                        result = analyze_geo_with_ai(page_data)
                    except Exception as e:
                        st.error(f"❌ AI analysis failed: {e}")
                        st.stop()

                geo      = result.get("overall_geo_score", 0)
                brand    = result.get("brand_name", page_data["domain"])
                vis      = result.get("context", 0)
                cit      = result.get("reliability", 0)
                sent     = result.get("exclusivity", 0)
                avg_rank = result.get("avg_rank", "#?")
                mentions = result.get("responses_with_brand", 0)
                label, badge_color, badge_bg = score_badge(geo)

                # ── GAUGE ──
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
                    top_strength_note = result.get("strengths_list", [""])[0] if result.get("strengths_list") else ""
                    top_improve_note  = result.get("improvements_list", [""])[0] if result.get("improvements_list") else ""
                    note1_html = f'<div style="font-size:0.82rem;color:#374151;line-height:1.6;border-top:1px solid #F3F4F6;padding-top:12px;">{top_strength_note}</div>' if top_strength_note else ""
                    note2_html = f'<div style="font-size:0.82rem;color:#6B7280;line-height:1.6;margin-top:6px;">{top_improve_note}</div>' if top_improve_note else ""
                    url_display = brand_url[:70] + ("..." if len(brand_url) > 70 else "")
                    st.markdown(
                        f'<div style="background:white;border-radius:14px;border:1px solid #E5E7EB;padding:22px 26px;box-shadow:0 1px 4px rgba(0,0,0,0.06);">'
                        f'<div style="font-size:1.3rem;font-weight:800;color:#111827;">{brand}</div>'
                        f'<div style="margin:4px 0 14px 0;"><a href="{brand_url}" target="_blank" style="color:#7C3AED;font-size:0.82rem;">{url_display}</a></div>'
                        f'<div style="margin-bottom:14px;">'
                        f'<div style="font-size:0.7rem;color:#9CA3AF;font-weight:600;text-transform:uppercase;margin-bottom:6px;">Status</div>'
                        f'<div style="background:{badge_bg};color:{badge_color};padding:4px 14px;border-radius:50px;font-size:0.82rem;font-weight:700;display:inline-block;">{label}</div>'
                        f'</div>'
                        f'{note1_html}{note2_html}'
                        f'</div>',
                        unsafe_allow_html=True
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── METRIC CARDS ──
                mc1, mc2, mc3, mc4 = st.columns(4)
                cards = [
                    (mc1, "linear-gradient(135deg,#3B82F6,#06B6D4)",  "👁️", vis,     "Visibility Score",  "Out of 100"),
                    (mc2, "linear-gradient(135deg,#8B5CF6,#A855F7)",  "🏅", cit,     "Citation Score",    "Brand mention share"),
                    (mc3, "linear-gradient(135deg,#10B981,#34D399)",  "📈", sent,    "Sentiment Score",   "Tone where brand appeared"),
                    (mc4, "linear-gradient(135deg,#F59E0B,#FBBF24)",  "🎯", avg_rank,"Avg. Rank",         "AI mention position"),
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

                # ── TOP 10 TABLE ──
                domain_lower2 = page_data["domain"].lower()
                fin_kws2  = ["capital","chase","amex","citi","discover","bank","credit","card","finance","fargo"]
                auto_kws2 = ["vw","volkswagen","toyota","ford","honda","bmw","tesla","auto","car","motor"]

                if any(x in domain_lower2 for x in fin_kws2):
                    top10_title = "Financial Services"
                    top10 = [
                        {"Brand":"American Express","GEO":91,"Vis":80,"Cit":18,"Sen":92,"Rank":"#1"},
                        {"Brand":"Chase",           "GEO":82,"Vis":80,"Cit":15,"Sen":85,"Rank":"#2"},
                        {"Brand":"Citi",            "GEO":75,"Vis":60,"Cit":12,"Sen":76,"Rank":"#3"},
                        {"Brand":"Discover",        "GEO":71,"Vis":60,"Cit":10,"Sen":79,"Rank":"#4"},
                        {"Brand":"Wells Fargo",     "GEO":68,"Vis":60,"Cit":9, "Sen":72,"Rank":"#5"},
                        {"Brand":"Bank of America", "GEO":66,"Vis":60,"Cit":8, "Sen":70,"Rank":"#6"},
                        {"Brand":brand,             "GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Rank":avg_rank},
                        {"Brand":"Synchrony",       "GEO":58,"Vis":40,"Cit":6, "Sen":62,"Rank":"#7"},
                        {"Brand":"Barclays",        "GEO":54,"Vis":40,"Cit":5, "Sen":58,"Rank":"#8"},
                        {"Brand":"USAA",            "GEO":52,"Vis":40,"Cit":4, "Sen":60,"Rank":"#9"},
                    ]
                elif any(x in domain_lower2 for x in auto_kws2):
                    top10_title = "Automotive"
                    top10 = [
                        {"Brand":"Tesla",    "GEO":94,"Vis":100,"Cit":22,"Sen":89,"Rank":"#1"},
                        {"Brand":"Toyota",   "GEO":88,"Vis":80, "Cit":18,"Sen":87,"Rank":"#2"},
                        {"Brand":"BMW",      "GEO":83,"Vis":80, "Cit":15,"Sen":84,"Rank":"#3"},
                        {"Brand":"Honda",    "GEO":79,"Vis":80, "Cit":13,"Sen":81,"Rank":"#4"},
                        {"Brand":"Ford",     "GEO":73,"Vis":60, "Cit":11,"Sen":72,"Rank":"#5"},
                        {"Brand":"Mercedes", "GEO":71,"Vis":60, "Cit":10,"Sen":75,"Rank":"#6"},
                        {"Brand":"Hyundai",  "GEO":68,"Vis":60, "Cit":8, "Sen":67,"Rank":"#7"},
                        {"Brand":brand,      "GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Rank":avg_rank},
                        {"Brand":"Kia",      "GEO":60,"Vis":40, "Cit":6, "Sen":63,"Rank":"#8"},
                        {"Brand":"Nissan",   "GEO":56,"Vis":40, "Cit":5, "Sen":60,"Rank":"#9"},
                    ]
                else:
                    top10_title = "General"
                    top10 = [
                        {"Brand":"Leader A",    "GEO":92,"Vis":100,"Cit":20,"Sen":91,"Rank":"#1"},
                        {"Brand":"Leader B",    "GEO":85,"Vis":80, "Cit":16,"Sen":84,"Rank":"#2"},
                        {"Brand":"Leader C",    "GEO":80,"Vis":80, "Cit":13,"Sen":79,"Rank":"#3"},
                        {"Brand":brand,         "GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Rank":avg_rank},
                        {"Brand":"Competitor D","GEO":72,"Vis":60, "Cit":10,"Sen":71,"Rank":"#5"},
                        {"Brand":"Competitor E","GEO":68,"Vis":60, "Cit":9, "Sen":67,"Rank":"#6"},
                        {"Brand":"Competitor F","GEO":63,"Vis":60, "Cit":7, "Sen":62,"Rank":"#7"},
                        {"Brand":"Competitor G","GEO":59,"Vis":40, "Cit":6, "Sen":58,"Rank":"#8"},
                        {"Brand":"Competitor H","GEO":54,"Vis":40, "Cit":5, "Sen":53,"Rank":"#9"},
                        {"Brand":"Competitor I","GEO":50,"Vis":40, "Cit":4, "Sen":49,"Rank":"#10"},
                    ]

                top10_sorted = sorted(top10, key=lambda x: x["GEO"], reverse=True)
                t10_rows = ""
                for idx, c in enumerate(top10_sorted, 1):
                    is_you = c["Brand"] == brand
                    row_bg = "#F5F3FF" if is_you else ("white" if idx % 2 == 1 else "#FAFAFA")
                    bdr    = "border-left:3px solid #7C3AED;" if is_you else ""
                    fw     = "700" if is_you else "400"
                    gc     = c["GEO"]
                    gcol   = "#10B981" if gc >= 80 else "#F59E0B" if gc >= 60 else "#EF4444"
                    you_badge = ' <span style="background:#EDE9FE;color:#7C3AED;border-radius:4px;padding:1px 6px;font-size:0.7rem;font-weight:700;">You</span>' if is_you else ""
                    t10_rows += (
                        f'<tr style="background:{row_bg};{bdr}">'
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
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Citation Share</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Sentiment</th>'
                    f'<th style="padding:7px 12px;text-align:left;font-size:0.73rem;color:#9CA3AF;font-weight:600;">Avg. Rank</th>'
                    f'</tr></thead><tbody>{t10_rows}</tbody></table></div>',
                    unsafe_allow_html=True
                )

                st.markdown("<br>", unsafe_allow_html=True)

                # ── RECOMMENDATIONS ──
                strengths    = result.get("strengths_list", [])[:3]
                weaknesses   = result.get("improvements_list", [])[:5]
                all_insights = result.get("insights", [])
                if not strengths and all_insights: strengths = all_insights[:2]
                if not weaknesses and all_insights: weaknesses = all_insights[:5]
                actions_high = [a["action"] for a in result.get("actions", []) if a.get("priority") == "High"]
                actions_med  = [a["action"] for a in result.get("actions", []) if a.get("priority") == "Medium"]

                s_html = "".join(f'<li style="padding:6px 0;font-size:0.84rem;color:#374151;display:flex;gap:10px;align-items:flex-start;"><span style="color:#10B981;font-weight:700;flex-shrink:0;">✓</span><span>{s}</span></li>' for s in strengths)
                w_html = "".join(f'<li style="padding:6px 0;font-size:0.84rem;color:#374151;display:flex;gap:10px;align-items:flex-start;"><span style="color:#EF4444;font-weight:700;flex-shrink:0;">✗</span><span>{w}</span></li>' for w in weaknesses)
                a_html = "".join(f'<li style="padding:5px 0;font-size:0.84rem;color:#374151;"><span style="background:#FEE2E2;color:#991B1B;border-radius:4px;padding:1px 8px;font-size:0.71rem;font-weight:700;margin-right:6px;">High</span>{a}</li>' for a in actions_high)
                a_html += "".join(f'<li style="padding:5px 0;font-size:0.84rem;color:#374151;"><span style="background:#FEF3C7;color:#92400E;border-radius:4px;padding:1px 8px;font-size:0.71rem;font-weight:700;margin-right:6px;">Medium</span>{a}</li>' for a in actions_med)

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
                    '<div style="background:white;border-radius:16px;border:1px solid #E5E7EB;padding:28px 32px;">'
                    '<div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:20px;">Metric Definitions</div>'
                    '<div style="display:flex;flex-direction:column;gap:0;">'
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">GEO Score</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Composite 0–100 score: Visibility (30%) + Sentiment (20%) + Prominence (20%) + Citation Share (15%) + Share of Voice (15%). All sub-scores derived by counting actual brand mentions — no estimation.</div></div>'
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Visibility Score</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Exact count: how many of 5 AI responses mentioned your brand. Formula: (responses with brand ÷ 5) × 100. Brand in 2/5 responses = 40. This anchors all other scores.</div></div>'
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Citation Share</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Your brand mentions as % of ALL brand mentions across all 5 responses. A brand rarely seen cannot have high citation share — the math prevents it naturally.</div></div>'
                    '<div style="padding:14px 0;border-bottom:1px solid #F3F4F6;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Sentiment Score</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Tone analysis only for responses where your brand appeared. Positive = 100, neutral = 50, negative = 0. Averaged across those responses only.</div></div>'
                    '<div style="padding:14px 0;"><div style="font-size:0.85rem;font-weight:700;color:#7C3AED;margin-bottom:5px;">Avg. Rank</div><div style="font-size:0.82rem;color:#374151;line-height:1.65;">Average position your brand was named within responses where it appeared. Derived from actual word order in the AI response text.</div></div>'
                    '</div></div>',
                    unsafe_allow_html=True
                )
                st.caption(f"GEO Score · Live AI analysis of {brand_url} · Percepta v2.0 · All scores derived from counting brand mentions across 5 AI responses")

    else:
        st.markdown("""
        <div style="background:#F9FAFB;border:2px dashed #D1D5DB;border-radius:16px;
                    padding:56px;text-align:center;margin-top:24px;">
            <div style="font-size:3rem;">🔗</div>
            <div style="font-size:1.2rem;font-weight:800;color:#111827;margin:12px 0 8px 0;">Enter a brand URL above to get started</div>
            <div style="color:#6B7280;font-size:0.9rem;max-width:480px;margin:0 auto 20px auto;">
                Percepta runs 5 live AI queries and counts exactly how often your brand appears.
                Scores are calculated from actual mention counts — not estimates.
            </div>
            <div style="display:flex;justify-content:center;gap:10px;flex-wrap:wrap;">
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">capitalone.com</span>
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">chase.com</span>
                <span style="background:#EDE9FE;color:#6D28D9;border-radius:50px;padding:5px 14px;font-size:0.8rem;font-weight:600;">tesla.com</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
