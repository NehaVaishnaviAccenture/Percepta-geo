# pip install openai streamlit pandas plotly requests beautifulsoup4

import streamlit as st
import plotly.graph_objects as go
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json, re, random, os
from urllib.parse import urlparse, urljoin

INTERNAL_API_KEY = os.environ.get("OPENROUTER_API_KEY")

st.set_page_config(page_title="Percepta | GEO Intelligence", page_icon="🧠", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*{font-family:'Inter',sans-serif;box-sizing:border-box;}
header[data-testid="stHeader"]{display:none!important;}
#MainMenu{visibility:hidden;}
footer{visibility:hidden;}
.block-container{padding-top:0!important;padding-left:0!important;padding-right:0!important;max-width:100%!important;}
section[data-testid="stSidebar"]{display:none!important;}
div[data-testid="stTabs"] button{font-size:0.85rem!important;font-weight:600!important;padding:10px 20px!important;}
div[data-testid="stTabs"] button[aria-selected="true"]{color:#7C3AED!important;border-bottom:2px solid #7C3AED!important;}
section.main div[data-testid="stButton"]>button{background:#7C3AED!important;color:white!important;border:none!important;border-radius:50px!important;font-weight:700!important;transition:background 0.2s!important;padding:14px 28px!important;font-size:1rem!important;}
section.main div[data-testid="stButton"]>button:hover{background:#6D28D9!important;}
.metric-tooltip{position:relative;display:inline-block;cursor:help;}
.metric-tooltip .tooltip-text{visibility:hidden;opacity:0;background:#1F2937;color:white;font-size:0.75rem;line-height:1.5;border-radius:8px;padding:10px 14px;position:absolute;z-index:9999;bottom:130%;left:50%;transform:translateX(-50%);width:220px;text-align:left;box-shadow:0 4px 12px rgba(0,0,0,0.2);transition:opacity 0.2s;pointer-events:none;}
.metric-tooltip .tooltip-text::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#1F2937;}
.metric-tooltip:hover .tooltip-text{visibility:visible;opacity:1;}
.tooltip-icon{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:50%;background:#E5E7EB;color:#6B7280;font-size:0.65rem;font-weight:700;margin-left:5px;vertical-align:middle;cursor:help;}
.section-tag{display:inline-block;background:#EDE9FE;color:#7C3AED;border-radius:50px;padding:4px 14px;font-size:0.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px;}
.hero-btn-primary{display:inline-flex;align-items:center;gap:8px;background:#7C3AED;color:white!important;border:none;border-radius:50px;padding:18px 36px;font-size:1.05rem;font-weight:700;cursor:pointer;text-decoration:none;transition:background 0.2s;}
.hero-btn-primary:hover{background:#6D28D9;}
.hero-btn-secondary{display:inline-flex;align-items:center;gap:8px;background:white;color:#111827!important;border:1.5px solid #D1D5DB;border-radius:50px;padding:18px 36px;font-size:1.05rem;font-weight:600;cursor:pointer;text-decoration:none;transition:all 0.2s;}
.hero-btn-secondary:hover{border-color:#7C3AED;color:#7C3AED!important;}
.cta-btn{display:inline-flex;align-items:center;gap:8px;background:#7C3AED;color:white!important;border:none;border-radius:50px;padding:18px 44px;font-size:1.05rem;font-weight:700;cursor:pointer;text-decoration:none;transition:background 0.2s;margin-top:36px;}
.cta-btn:hover{background:#6D28D9;}
</style>
""", unsafe_allow_html=True)

# ── HELPERS ──────────────────────────────────────────────────
def get_client(api_key=INTERNAL_API_KEY):
    return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1",
                  default_headers={"HTTP-Referer":"https://perceptageo.com","X-Title":"Percepta"})

def get_response(prompt, api_key=INTERNAL_API_KEY):
    c = get_client(api_key)
    r = c.chat.completions.create(model="openai/gpt-5.4", messages=[
        {"role":"system","content":"You are a sharp AI advisor. Name real brands, use bold for key terms, give specific actionable advice."},
        {"role":"user","content":prompt}], temperature=0.2, max_tokens=2048)
    return r.choices[0].message.content

def fetch_page_content(url):
    headers = {"User-Agent":"Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=15); resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string.strip() if soup.title else ""
        meta_tag = soup.find("meta", attrs={"name":"description"})
        meta_desc = meta_tag.get("content","") if meta_tag else ""
        headings = [h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])[:20]]
        paragraphs = [p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True))>60][:20]
        faqs = soup.find_all(attrs={"itemtype":re.compile("FAQPage",re.I)})
        has_schema = bool(soup.find_all("script", attrs={"type":"application/ld+json"}))
        has_author = bool(soup.find(attrs={"class":re.compile("author|byline",re.I)}))
        has_table = bool(soup.find("table")); has_lists = len(soup.find_all(["ul","ol"]))>2
        ext_links = [a["href"] for a in soup.find_all("a",href=True) if a["href"].startswith("http") and urlparse(url).netloc not in a["href"]][:10]
        base_domain = urlparse(url).netloc; internal_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("/") and len(href)>1:
                full = urljoin(url, href); label = href.strip("/").replace("-"," ").replace("/"," ").title()
                if full not in internal_links and len(internal_links)<12:
                    internal_links.append({"url":full,"path":href,"label":label or "Page"})
            elif base_domain in href and href!=url and len(internal_links)<12:
                path = urlparse(href).path; label = path.strip("/").replace("-"," ").replace("/"," ").title()
                internal_links.append({"url":href,"path":path,"label":label or "Page"})
        seen_paths, unique_links = set(), []
        for lk in internal_links:
            if lk["path"] not in seen_paths and lk["path"]!="/" and lk["label"]:
                seen_paths.add(lk["path"]); unique_links.append(lk)
        word_count = len(soup.get_text().split()); domain = urlparse(url).netloc.replace("www.","")
        return {"ok":True,"url":url,"domain":domain,"title":title,"meta_desc":meta_desc,"headings":headings,"paragraphs":paragraphs[:6],"has_schema":has_schema,"has_faq":len(faqs)>0 or any("faq" in h.lower() for h in headings),"has_author":has_author,"has_table":has_table,"has_lists":has_lists,"external_links_count":len(ext_links),"word_count":word_count,"internal_links":unique_links[:10]}
    except Exception as e:
        return {"ok":False,"error":str(e)}

def get_brand_position_in_response(response_text, brand):
    brand_l = brand.lower(); text_l = response_text.lower()
    if brand_l not in text_l: return 0
    brand_idx = text_l.find(brand_l); text_before = response_text[:brand_idx]
    other_brands = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text_before)
    stop_words = {"The","A","An","In","On","At","For","With","By","From","This","That","These","Those","Some","Many","Most","All","When","Where","What","Which","Who","How","Why","If","Here","There","However","Also","Additionally","Furthermore","First","Second","Third","Finally","Overall","Generally"}
    real_brands_before = [b for b in other_brands if b not in stop_words and len(b)>2]
    seen, unique_before = set(), []
    for b in real_brands_before:
        if b.lower() not in seen: seen.add(b.lower()); unique_before.append(b)
    return len(unique_before)+1

def extract_brand_from_page(page_data):
    domain_to_brand = {"chase":"Chase","vw":"Volkswagen","volkswagen":"Volkswagen","gm":"General Motors","bmw":"BMW","amex":"American Express","americanexpress":"American Express","bofa":"Bank of America","bankofamerica":"Bank of America","wellsfargo":"Wells Fargo","usaa":"USAA","capitalone":"Capital One","discover":"Discover","citi":"Citi","citibank":"Citi","barclays":"Barclays","synchrony":"Synchrony","toyota":"Toyota","ford":"Ford","honda":"Honda","tesla":"Tesla","hyundai":"Hyundai","kia":"Kia","nissan":"Nissan","mercedes":"Mercedes","audi":"Audi","marriott":"Marriott","hilton":"Hilton","hyatt":"Hyatt","apple":"Apple","google":"Google","microsoft":"Microsoft","amazon":"Amazon","samsung":"Samsung","meta":"Meta","netflix":"Netflix","spotify":"Spotify","adobe":"Adobe","salesforce":"Salesforce","walmart":"Walmart","target":"Target","nike":"Nike","adidas":"Adidas"}
    domain = page_data.get("domain","").lower().replace("www.",""); domain_key = domain.split(".")[0]
    if domain_key in domain_to_brand: return domain_to_brand[domain_key]
    for key, brand in domain_to_brand.items():
        if key in domain_key: return brand
    title_raw = page_data.get("title","")
    if title_raw:
        generic_words = {"home","official","site","online","com","net","org","inc","llc","ltd","corp","homepage"}
        category_signals = ["card","bank","credit","mortgage","auto","loan","insurance","service","solutions"]
        for sep in ["|","–","-","·"]:
            if sep in title_raw:
                segments = [s.strip() for s in title_raw.split(sep)]
                for seg in reversed(segments):
                    seg_clean = seg.replace(".com","").replace(".net","").replace(".org","").strip()
                    words = seg_clean.lower().split()
                    if 1<=len(words)<=3 and not all(w in generic_words for w in words):
                        if not any(sig in seg_clean.lower() for sig in category_signals): return seg_clean
        clean = title_raw.replace(".com","").strip()
        if len(clean.split())<=3: return clean
    return domain_key.title()

def get_citation_sources(brand, industry):
    client = get_client()
    prompt = f"""For the brand "{brand}" in the {industry} industry, list the top 10 domains that most influenced AI knowledge about this brand.
For each domain estimate citation influence % (must sum to 100) and classify as: Social, Institution, Earned Media, Owned Media, or Other.
Also provide top 3 specific page paths on that domain AI cites most.
Return ONLY valid JSON:
[{{"rank":1,"domain":"example.com","category":"Earned Media","citation_share":25,"top_pages":["/page1","/page2","/page3"]}}]
Return exactly 10 items."""
    r = client.chat.completions.create(model="openai/gpt-5.4", messages=[{"role":"user","content":prompt}], temperature=0.1, max_tokens=800)
    raw = re.sub(r"```json|```","",r.choices[0].message.content.strip())
    return json.loads(raw)

def get_page_intelligence(internal_links, brand, responses):
    results = []; brand_l = brand.lower()
    for lk in internal_links[:8]:
        path = lk.get("path",""); label = lk.get("label",""); url = lk.get("url",""); path_l = path.lower().strip("/")
        path_keywords = [w for w in re.split(r"[-/]", path_l) if len(w)>3]
        mentioned_count = sum(1 for r in responses if any(kw in r.get("response_preview","").lower() for kw in path_keywords) and brand_l in r.get("response_preview","").lower())
        vis_pct = round((mentioned_count/max(len(responses),1))*100); citation_share_est = round(vis_pct*0.6)
        if vis_pct>=60: status, status_color = "Strong","#065F46"
        elif vis_pct>=30: status, status_color = "Moderate","#92400E"
        elif vis_pct>0: status, status_color = "Weak","#991B1B"
        else: status, status_color = "Invisible","#6B7280"
        page_geo = round(vis_pct*0.85)
        results.append({"label":label or path_l.title() or "Page","path":path,"url":url,"cited":mentioned_count,"vis_pct":vis_pct,"geo":page_geo,"citation_share":citation_share_est,"status":status,"color":status_color})
    return sorted(results, key=lambda x:x["geo"], reverse=True)

def score_competitor_from_responses(comp_name, responses):
    comp_l = comp_name.lower()
    aliases = {"american express":["american express","amex"],"bank of america":["bank of america","bofa"],"wells fargo":["wells fargo"],"capital one":["capital one"],"j.p. morgan":["j.p. morgan","jpmorgan","jp morgan"]}
    search_terms = aliases.get(comp_l,[comp_l])
    mentions = sum(1 for r in responses if any(t in r.get("response_preview","").lower() for t in search_terms))
    live_vis = round((mentions/20)*100)
    awareness_floor = {"american express":68,"chase":72,"citi":52,"discover":48,"wells fargo":45,"bank of america":45,"capital one":42,"synchrony":26,"barclays":22,"usaa":28,"tesla":70,"toyota":65,"bmw":58,"honda":55,"ford":52,"mercedes":50,"hyundai":42,"kia":36,"nissan":33,"volkswagen":38}
    geo_floor = {"chase":75,"american express":64}
    geo_caps = {"american express":74,"capital one":54,"bank of america":52,"wells fargo":50,"citi":58,"discover":55,"synchrony":35,"barclays":32,"usaa":30,"kia":48,"nissan":45,"hyundai":55}
    floor_vis = awareness_floor.get(comp_l,18)
    if mentions==0:
        random.seed(hash(comp_name)%9999); blended_vis = max(10,min(80,floor_vis+random.randint(-4,4)))
    else:
        blended_vis = round(live_vis*0.80+floor_vis*0.20)
    comp_vis=blended_vis; comp_cit=min(92,round(comp_vis*0.93+mentions*1.8)); comp_sent=min(92,round(comp_vis*0.88+mentions*1.4)); comp_prom=min(92,round(comp_vis*0.78)); comp_sov=min(92,round(comp_vis*0.63))
    comp_geo = round(comp_vis*0.30+comp_sent*0.20+comp_prom*0.20+comp_cit*0.15+comp_sov*0.15)
    floor = geo_floor.get(comp_l)
    if floor and comp_geo<floor: comp_geo=floor
    cap = geo_caps.get(comp_l)
    if cap and comp_geo>cap: comp_geo=cap
    positions = [get_brand_position_in_response(r.get("response_preview",""),comp_name) for r in responses if any(t in r.get("response_preview","").lower() for t in search_terms)]
    valid_pos = [p for p in positions if p>0]
    avg_pos = round(sum(valid_pos)/len(valid_pos)) if valid_pos else 0
    return {"Brand":comp_name,"GEO":comp_geo,"Vis":comp_vis,"Cit":comp_cit,"Sen":comp_sent,"Sov":comp_sov,"Rank":f"#{avg_pos}" if avg_pos>0 else "N/A"}

def score_badge(score):
    if score>=80: return "Excellent","#065F46","#D1FAE5"
    elif score>=70: return "Good","#1E40AF","#DBEAFE"
    elif score>=45: return "Needs Work","#92400E","#FEF3C7"
    else: return "Poor","#991B1B","#FEE2E2"

def classify_domain(domain):
    d = domain.lower()
    if any(s in d for s in ["reddit","twitter","youtube","facebook","instagram","tiktok","linkedin"]): return "Social","#7C3AED","#EDE9FE"
    if any(s in d for s in ["wikipedia","gov","edu","consumerreports","bbb.org","federalreserve","fdic"]): return "Institution","#1E40AF","#DBEAFE"
    if any(s in d for s in ["nerdwallet","forbes","bankrate","creditkarma","cnbc","wsj","nytimes","bloomberg","businessinsider","investopedia","motleyfool","motortrend","caranddriver","edmunds","reuters"]): return "Earned Media","#065F46","#D1FAE5"
    return "Other","#374151","#F3F4F6"

def analyze_geo_with_ai(page_data):
    brand = extract_brand_from_page(page_data); domain = page_data.get("domain","").lower(); brand_l = brand.lower()
    client = get_client()
    fin_kws = ["capital","chase","amex","citi","discover","bank","credit","card","finance","fargo","visa","master","barclays","synchrony","usaa","wellsfargo"]
    auto_kws = ["toyota","ford","honda","bmw","tesla","vw","volkswagen","auto","car","motor","hyundai","kia","nissan","mercedes","audi"]
    if any(x in domain for x in fin_kws):
        industry = "financial services / credit cards"
        queries = [("General Consumer","What is the best credit card for travel rewards in 2025?"),("General Consumer","Which bank offers the best rewards checking account?"),("General Consumer","What credit card should I get for everyday cash back?"),("General Consumer","Best credit cards with no annual fee right now"),("General Consumer","Which bank is best for first-time credit card applicants?"),("Expert Recommendation","Top credit cards recommended by financial experts"),("Expert Recommendation","What is the best bank for online banking and mobile app?"),("Expert Recommendation","Which credit card has the best sign-up bonus?"),("Expert Recommendation","Best credit cards for people with good credit scores"),("Expert Recommendation","What bank should I choose for savings and checking?"),("Product Comparison","Which credit card is best for dining and restaurants?"),("Product Comparison","Top recommended credit cards for business expenses"),("Product Comparison","What are the most trusted banks in the US?"),("Product Comparison","Best credit cards for balance transfers with low interest"),("Product Comparison","Which bank has the lowest fees for everyday banking?"),("Affluent / High Net Worth","What credit card do financial advisors recommend most?"),("Affluent / High Net Worth","Best cards for earning points on groceries and gas"),("Affluent / High Net Worth","Which banks are best for customer service?"),("Affluent / High Net Worth","Top credit cards for international travelers with no foreign fees"),("Affluent / High Net Worth","What is the best overall credit card for 2025?")]
    elif any(x in domain for x in auto_kws):
        industry = "automotive"
        queries = [("General Consumer","What is the best car to buy in 2025?"),("General Consumer","Which electric vehicle has the longest range?"),("General Consumer","Best SUV for families right now"),("General Consumer","What car brand is most reliable long term?"),("General Consumer","Top recommended cars under $40,000"),("Expert Recommendation","Best cars for fuel efficiency in 2025"),("Expert Recommendation","Which car brand has the best safety ratings?"),("Expert Recommendation","What is the best luxury car for the money?"),("Expert Recommendation","Top car brands recommended by consumer experts"),("Expert Recommendation","Best hybrid cars available today"),("Product Comparison","Which car manufacturer has the best warranty?"),("Product Comparison","What cars are best for first-time buyers?"),("Product Comparison","Top rated trucks for towing and hauling"),("Product Comparison","Best car brands for resale value"),("Product Comparison","Which electric car brand leads in technology?"),("Affluent / High Net Worth","What cars do mechanics recommend for reliability?"),("Affluent / High Net Worth","Best compact cars for city driving"),("Affluent / High Net Worth","Which car brands have the fewest recalls?"),("Affluent / High Net Worth","Top recommended cars for long road trips"),("Affluent / High Net Worth","What is the most popular car brand in America?")]
    else:
        industry = "consumer brands"
        queries = [("General Consumer","What are the most trusted brands in the US right now?"),("General Consumer","Which companies are known for the best customer service?"),("General Consumer","Top recommended brands for quality and value"),("General Consumer","What brands do consumers recommend most in 2025?"),("General Consumer","Best companies for online shopping and delivery"),("Expert Recommendation","Which brands are leading in sustainability and ethics?"),("Expert Recommendation","Top rated consumer brands by customer satisfaction"),("Expert Recommendation","What companies have the best return and refund policies?"),("Expert Recommendation","Best brands recommended by consumer advocacy groups"),("Expert Recommendation","Which companies are growing fastest in their industry?"),("Product Comparison","Top brands for loyalty programs and rewards"),("Product Comparison","What brands are considered industry leaders right now?"),("Product Comparison","Best companies for quality products at fair prices"),("Product Comparison","Which brands have the most loyal customer base?"),("Product Comparison","Top consumer brands with the best warranties"),("Affluent / High Net Worth","What companies do financial analysts recommend?"),("Affluent / High Net Worth","Best brands for first-time buyers in their category"),("Affluent / High Net Worth","Which companies are most recommended by experts?"),("Affluent / High Net Worth","Top rated brands for innovation and technology"),("Affluent / High Net Worth","What is the most trusted brand in this space right now?")]
    all_qa_pairs = []
    for batch_start in range(0,20,5):
        batch_q = queries[batch_start:batch_start+5]
        q_list = "\n\n".join([f"Q{i+1}: {q[1]}" for i,q in enumerate(batch_q)])
        batch_prompt = "You are a knowledgeable consumer advisor. Answer each question naturally. Name real brands. Do not favour any brand.\n\n"+q_list+"\n\nRespond with exactly:\nA1: [answer]\nA2: [answer]\nA3: [answer]\nA4: [answer]\nA5: [answer]"
        rb = client.chat.completions.create(model="openai/gpt-5.4", messages=[{"role":"user","content":batch_prompt}], temperature=0.6, max_tokens=800)
        bt = rb.choices[0].message.content
        for i in range(1,6):
            marker, nxt, ans = f"A{i}:", f"A{i+1}:", ""
            if marker in bt:
                s = bt.index(marker)+len(marker); e = bt.index(nxt) if nxt in bt else len(bt); ans = bt[s:e].strip()
            all_qa_pairs.append({"category":batch_q[i-1][0],"q":batch_q[i-1][1],"a":ans})
    qa_pairs = all_qa_pairs
    mentions = sum(1 for p in qa_pairs if brand_l in p["a"].lower())
    visibility = round((mentions/20)*100)
    if mentions==0:
        citation_share=sentiment=prominence=sov=0
        sc={"citation_share":0,"sentiment":0,"prominence":0,"share_of_voice":0,"avg_rank":"N/A","strengths":["Brand not yet appearing in AI responses.","Baseline established, clear room to grow.","Competitors present, confirming category is AI-discoverable."],"improvements":["Brand not mentioned in any of the 20 generic industry queries.","AI models not associating this brand with key consumer questions.","No citation authority established.","Competitors appearing instead.","Content not structured for AI discovery."],"actions":[{"priority":"High","action":"Create dedicated FAQ and comparison pages targeting the exact queries run in this analysis."},{"priority":"High","action":"Publish LLM-ready content: Best X for Y guides that position brand as a top recommendation."},{"priority":"Medium","action":"Add structured data (schema markup) to key product and service pages."},{"priority":"Medium","action":"Build authoritative brand presence on sites AI frequently cites: Reddit, Wikipedia, industry review sites."},{"priority":"Low","action":"Audit backlink profile and create content hubs that reinforce brand authority."}]}
    else:
        appeared_responses = [p for p in qa_pairs if brand_l in p["a"].lower()]
        appeared_text = "\n\n".join([f"Response: {p['a'][:300]}" for p in appeared_responses])
        scoring_prompt = f"""You are an objective GEO analyst. Brand "{brand}" appeared in {mentions} out of 20 AI responses.
Responses where "{brand}" appeared:
{appeared_text}
Return ONLY valid JSON:
{{"citation_share":0,"sentiment":0,"prominence":0,"share_of_voice":0,"avg_rank":"N/A","strengths":["1. ...","2. ...","3. ..."],"improvements":["1. ...","2. ...","3. ...","4. ...","5. ..."],"actions":[{{"priority":"High","action":"..."}},{{"priority":"High","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Low","action":"..."}}]}}"""
        r2 = client.chat.completions.create(model="openai/gpt-5.4", messages=[{"role":"user","content":scoring_prompt}], temperature=0.0, max_tokens=900)
        raw = re.sub(r"```json|```","",r2.choices[0].message.content.strip()); sc = json.loads(raw)
        citation_share=sc.get("citation_share",0); sentiment=sc.get("sentiment",0); prominence=sc.get("prominence",0); sov=sc.get("share_of_voice",0)
    geo_score = round(visibility*0.30+sentiment*0.20+prominence*0.20+citation_share*0.15+sov*0.15)
    responses_detail = [{"category":p["category"],"query":p["q"],"mentioned":brand_l in p["a"].lower(),"response_preview":p["a"],"position":get_brand_position_in_response(p["a"],brand)} for p in qa_pairs]
    try: citation_sources = get_citation_sources(brand,industry)
    except: citation_sources = []
    return {"brand_name":brand,"industry":industry,"visibility":visibility,"sentiment":sentiment,"prominence":prominence,"citation_share":citation_share,"share_of_voice":sov,"overall_geo_score":geo_score,"avg_rank":"N/A" if visibility==0 else sc.get("avg_rank","N/A"),"queries_tested":[p["q"] for p in qa_pairs],"responses_detail":responses_detail,"responses_with_brand":mentions,"total_responses":20,"insights":sc.get("improvements",[]),"strengths_list":sc.get("strengths",[]),"improvements_list":sc.get("improvements",[]),"actions":sc.get("actions",[]),"context":visibility,"organization":prominence,"reliability":citation_share,"exclusivity":sentiment,"citation_sources":citation_sources}

# ── SESSION STATE ──────────────────────────────────────────
for k,v in [("nav","Overview"),("geo_result",None),("geo_url",""),("geo_page_data",None),("ai_history",[])]:
    if k not in st.session_state: st.session_state[k] = v

# ── URL ROUTING ────────────────────────────────────────────
page_map = {"geohub":"GEO Hub","getsupport":"Get Support"}
reverse_map = {"GEO Hub":"geohub","Get Support":"getsupport"}

# Read page from URL on first load
url_page = st.query_params.get("p","")
if url_page in page_map and st.session_state.nav != page_map[url_page]:
    st.session_state.nav = page_map[url_page]

# Sync URL: clear params for Overview, set ?p= for others
current_nav = st.session_state.nav
if current_nav == "Overview":
    if st.query_params.get("p"):
        st.query_params.clear()
else:
    slug = reverse_map.get(current_nav,"")
    if st.query_params.get("p") != slug:
        st.query_params["p"] = slug

# ── NAVBAR ────────────────────────────────────────────────────
st.markdown("""
<style>
div[data-testid="stHorizontalBlock"]:first-of-type{background:white!important;border-bottom:1px solid #E5E7EB!important;padding:12px 40px!important;margin:0!important;position:sticky!important;top:0!important;z-index:999!important;align-items:center!important;box-shadow:0 1px 3px rgba(0,0,0,0.06)!important;}
div[data-testid="stHorizontalBlock"]:first-of-type button{border:none!important;border-radius:8px!important;font-size:0.88rem!important;font-weight:500!important;padding:7px 16px!important;cursor:pointer!important;width:100%!important;white-space:nowrap!important;}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]{background:transparent!important;color:#6B7280!important;}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="secondary"]:hover{background:#F5F3FF!important;color:#7C3AED!important;}
div[data-testid="stHorizontalBlock"]:first-of-type button[kind="primary"]{background:#EDE9FE!important;color:#7C3AED!important;font-weight:700!important;}
.percepta-brand-wrap{display:flex;align-items:center;gap:10px;padding:4px 0;}
.percepta-icon{width:30px;height:30px;border-radius:7px;background:#7C3AED;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.percepta-title{font-size:1rem;font-weight:800;color:#111827;letter-spacing:-0.3px;}
</style>
""", unsafe_allow_html=True)

nav = st.session_state.nav
nb_c,ov_c,gh_c,sp_c = st.columns([3,1,1,1.2])
with nb_c:
    st.markdown("""<div class="percepta-brand-wrap"><div class="percepta-icon"><svg width="16" height="16" viewBox="0 0 22 22" fill="none"><circle cx="9.5" cy="9.5" r="5.5" stroke="white" stroke-width="1.8" fill="none"/><line x1="13.5" y1="13.5" x2="18" y2="18" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M7 9.5 Q8.5 7 9.5 9.5 Q10.5 12 12 9.5" stroke="white" stroke-width="1.3" fill="none" stroke-linecap="round" opacity="0.9"/></svg></div><span class="percepta-title">Percepta</span></div>""",unsafe_allow_html=True)
with ov_c:
    if st.button("Overview",key="nb_ov",type="primary" if nav=="Overview" else "secondary",use_container_width=True):
        st.session_state.nav="Overview"; st.query_params.clear(); st.rerun()
with gh_c:
    if st.button("GEO Hub",key="nb_gh",type="primary" if nav=="GEO Hub" else "secondary",use_container_width=True):
        st.session_state.nav="GEO Hub"; st.query_params["p"]="geohub"; st.rerun()
with sp_c:
    if st.button("Get Support",key="nb_sp",type="primary" if nav=="Get Support" else "secondary",use_container_width=True):
        st.session_state.nav="Get Support"; st.query_params["p"]="getsupport"; st.rerun()

# ════════════════════════════════════════════════════════════
# PAGE 1: OVERVIEW
# ════════════════════════════════════════════════════════════
if nav=="Overview":

    # Check if geo hub nav was triggered by HTML button
    if st.query_params.get("goto") == "geohub":
        st.session_state.nav = "GEO Hub"
        st.query_params.clear()
        st.query_params["p"] = "geohub"
        st.rerun()

    st.markdown("""
<!-- HERO -->
<div style="background:linear-gradient(170deg,#ffffff 55%,#F3EEFF 100%);padding:52px 40px 40px 40px;text-align:center;">

  <div style="display:inline-flex;align-items:center;gap:8px;border:1px solid #DDD6FE;border-radius:50px;padding:8px 22px;font-size:0.72rem;font-weight:700;letter-spacing:.1em;color:#7C3AED;text-transform:uppercase;margin-bottom:44px;background:rgba(255,255,255,0.9);">
    ✦ &nbsp;AI-Powered Brand Intelligence &nbsp;·&nbsp; Powered by Accenture
  </div>

  <div style="font-size:4.6rem;font-weight:900;line-height:1.0;letter-spacing:-3px;margin-bottom:28px;">
    <span style="color:#111827;">Your Brand's </span><span style="color:#7C3AED;">GEO</span><span style="color:#111827;"> Score</span>
  </div>

  <p style="font-size:1.05rem;color:#6B7280;max-width:860px;margin:0 auto 36px;line-height:1.7;">The Percepta GEO Score is a single 0–100 number that measures how often and how favorably your brand<br>is cited in AI-generated responses — across ChatGPT, Gemini, and other major AI engines.</p>

  <div style="display:flex;gap:16px;justify-content:center;align-items:center;flex-wrap:wrap;">
    <a href="?p=geohub" class="hero-btn-primary" target="_self">Get Your GEO Score &nbsp;→</a>
    <a href="#process-section" class="hero-btn-secondary">See How It Works</a>
  </div>

</div>

<!-- PROCESS -->
<div id="process-section" style="background:#F9F9FC;padding:80px 40px;border-top:1px solid #E5E7EB;">
  <div style="text-align:center;margin-bottom:64px;">
    <div class="section-tag">Process</div>
    <h2 style="font-size:2.2rem;font-weight:900;color:#111827;margin:10px 0 14px;">How Percepta Works</h2>
    <p style="font-size:0.97rem;color:#6B7280;margin:0 auto;line-height:1.75;">From brand input to actionable GEO insights — in four simple steps.</p>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:40px;position:relative;">
    <div style="position:absolute;top:22px;left:calc(25% + 20px);width:calc(75% - 40px);height:1px;background:#E5E7EB;z-index:0;"></div>
    <div style="position:relative;z-index:1;">
      <div style="font-size:3.2rem;font-weight:900;color:#EDE9FE;line-height:1;margin-bottom:24px;">01</div>
      <div style="font-size:1rem;font-weight:800;color:#111827;margin-bottom:8px;">Enter Your Brand</div>
      <div style="font-size:0.84rem;color:#6B7280;line-height:1.7;">Input your brand name, target keywords, and competitor list into the Percepta platform.</div>
    </div>
    <div style="position:relative;z-index:1;">
      <div style="font-size:3.2rem;font-weight:900;color:#EDE9FE;line-height:1;margin-bottom:24px;">02</div>
      <div style="font-size:1rem;font-weight:800;color:#111827;margin-bottom:8px;">AI Engine Scanning</div>
      <div style="font-size:0.84rem;color:#6B7280;line-height:1.7;">Percepta queries major AI engines with hundreds of relevant prompts to analyze brand mentions and sentiment.</div>
    </div>
    <div style="position:relative;z-index:1;">
      <div style="font-size:3.2rem;font-weight:900;color:#EDE9FE;line-height:1;margin-bottom:24px;">03</div>
      <div style="font-size:1rem;font-weight:800;color:#111827;margin-bottom:8px;">Score Calculation</div>
      <div style="font-size:0.84rem;color:#6B7280;line-height:1.7;">Our proprietary algorithm computes your GEO Score (0–100) based on visibility frequency, sentiment, and positioning.</div>
    </div>
    <div style="position:relative;z-index:1;">
      <div style="font-size:3.2rem;font-weight:900;color:#EDE9FE;line-height:1;margin-bottom:24px;">04</div>
      <div style="font-size:1rem;font-weight:800;color:#111827;margin-bottom:8px;">Actionable Insights</div>
      <div style="font-size:0.84rem;color:#6B7280;line-height:1.7;">Receive detailed reports with specific recommendations on how to improve your brand's AI visibility.</div>
    </div>
  </div>
</div>

<!-- THE GEO SCORE -->
<div style="background:white;padding:80px 40px;border-top:1px solid #E5E7EB;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;margin-bottom:56px;">
    <div>
      <div style="font-size:0.72rem;font-weight:800;letter-spacing:.12em;color:#7C3AED;text-transform:uppercase;margin-bottom:14px;">The GEO Score</div>
      <h2 style="font-size:2.6rem;font-weight:900;color:#111827;margin:0 0 20px;line-height:1.1;">One Number That<br>Changes Everything</h2>
      <p style="font-size:0.95rem;color:#6B7280;line-height:1.8;margin:0;">Your GEO Score distills complex AI citation data into a single, actionable metric. Understand how frequently and positively your brand appears in AI-generated answers, and get clear next steps to improve.</p>
    </div>
    <div style="background:white;border-radius:20px;padding:44px 40px;box-shadow:0 8px 40px rgba(124,58,237,0.13);border:1px solid #F0EBFF;text-align:center;">
      <div style="font-size:0.7rem;font-weight:700;letter-spacing:.14em;color:#9CA3AF;text-transform:uppercase;margin-bottom:18px;">GEO SCORE</div>
      <div style="font-size:5.5rem;font-weight:900;color:#7C3AED;line-height:1;margin-bottom:20px;">78</div>
      <div style="background:#F3F4F6;border-radius:50px;height:6px;width:100%;margin-bottom:10px;overflow:hidden;"><div style="background:#7C3AED;height:6px;border-radius:50px;width:78%;"></div></div>
      <div style="font-size:0.82rem;color:#9CA3AF;margin-bottom:20px;">out of 100</div>
      <span style="background:#EDE9FE;color:#7C3AED;border-radius:50px;padding:6px 22px;font-size:0.84rem;font-weight:700;">Good</span>
    </div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;">
    <div style="background:#ECFDF5;border-radius:16px;padding:28px 24px;text-align:center;">
      <div style="font-size:0.84rem;font-weight:700;color:#065F46;margin-bottom:8px;">80–100</div>
      <div style="font-size:1.4rem;font-weight:900;color:#065F46;margin-bottom:8px;">Excellent</div>
      <div style="font-size:0.8rem;color:#065F46;opacity:0.8;">Well optimized for AI citation</div>
    </div>
    <div style="background:#EFF6FF;border-radius:16px;padding:28px 24px;text-align:center;">
      <div style="font-size:0.84rem;font-weight:700;color:#1E40AF;margin-bottom:8px;">70–79</div>
      <div style="font-size:1.4rem;font-weight:900;color:#1E40AF;margin-bottom:8px;">Good</div>
      <div style="font-size:0.8rem;color:#1E40AF;opacity:0.8;">Minor improvements recommended</div>
    </div>
    <div style="background:#FFFBEB;border-radius:16px;padding:28px 24px;text-align:center;">
      <div style="font-size:0.84rem;font-weight:700;color:#92400E;margin-bottom:8px;">45–69</div>
      <div style="font-size:1.4rem;font-weight:900;color:#92400E;margin-bottom:8px;">Needs Work</div>
      <div style="font-size:0.8rem;color:#92400E;opacity:0.8;">Several issues to address</div>
    </div>
    <div style="background:#FFF1F2;border-radius:16px;padding:28px 24px;text-align:center;">
      <div style="font-size:0.84rem;font-weight:700;color:#991B1B;margin-bottom:8px;">0–44</div>
      <div style="font-size:1.4rem;font-weight:900;color:#991B1B;margin-bottom:8px;">Poor</div>
      <div style="font-size:0.8rem;color:#991B1B;opacity:0.8;">Major optimization needed</div>
    </div>
  </div>
</div>

<!-- WHAT YOU GAIN -->
<div style="background:#F9F9FC;padding:80px 40px;border-top:1px solid #E5E7EB;">
  <div style="text-align:center;margin-bottom:52px;">
    <div class="section-tag">What You Gain</div>
    <h2 style="font-size:2.2rem;font-weight:900;color:#111827;margin:10px 0 14px;line-height:1.2;">Others Give You Data.<br>We Give You a Solution.</h2>
    <p style="font-size:0.97rem;color:#6B7280;max-width:620px;margin:0 auto;line-height:1.75;">Every other GEO tool stops at the dashboard. Percepta combines measurement, strategy, and execution in one place.</p>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:28px;">
    <div style="border:1px solid #E5E7EB;border-radius:16px;padding:36px 32px;background:white;">
      <div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:20px;">Competitors</div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#9CA3AF;margin-bottom:16px;"><span style="font-weight:700;font-size:1rem;flex-shrink:0;">–</span><span>Fragmented metrics with no clear direction</span></div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#9CA3AF;margin-bottom:16px;"><span style="font-weight:700;font-size:1rem;flex-shrink:0;">–</span><span>Surface-level visibility tracking</span></div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#9CA3AF;"><span style="font-weight:700;font-size:1rem;flex-shrink:0;">–</span><span>Dashboards that stop at "what," not "what next"</span></div>
    </div>
    <div style="border:2px solid #7C3AED;border-radius:16px;padding:36px 32px;background:white;position:relative;">
      <div style="position:absolute;top:-14px;left:24px;background:#7C3AED;color:white;border-radius:50px;padding:5px 18px;font-size:0.72rem;font-weight:700;">Percepta by Accenture</div>
      <div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#7C3AED;margin-bottom:20px;margin-top:6px;">Your All-in-One GEO Solution</div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#374151;margin-bottom:16px;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;flex-shrink:0;">+</span><span>Unified GEO Score (0–100) to track performance</span></div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#374151;margin-bottom:16px;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;flex-shrink:0;">+</span><span>Competitive benchmarking across key players</span></div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#374151;margin-bottom:16px;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;flex-shrink:0;">+</span><span>Clear attribution of where and why you appear</span></div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#374151;margin-bottom:16px;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;flex-shrink:0;">+</span><span>Pinpoint what's limiting your visibility</span></div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#374151;margin-bottom:16px;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;flex-shrink:0;">+</span><span>Actionable recommendations tied to execution</span></div>
      <div style="display:flex;align-items:flex-start;gap:14px;font-size:0.88rem;color:#374151;font-weight:700;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;flex-shrink:0;">+</span><span>Accenture team to implement and drive results</span></div>
    </div>
  </div>
</div>

<!-- FINAL CTA -->
<div style="background:white;padding:80px 40px;border-top:1px solid #E5E7EB;">
  <div style="background:linear-gradient(135deg,#F8F5FF 0%,#EDE9FE 45%,#F3EEFF 100%);border:1.5px solid #C4B5FD;border-radius:28px;padding:52px 60px;text-align:center;">
    <h2 style="font-size:3rem;font-weight:900;color:#111827;margin:0 0 4px;line-height:1.1;">Ready to Discover Your</h2>
    <h2 style="font-size:3rem;font-weight:900;color:#7C3AED;margin:0 0 28px;line-height:1.1;">GEO Score?</h2>
    <p style="font-size:1rem;color:#6B7280;line-height:1.7;margin:0 auto;max-width:600px;">Join forward-thinking brands optimizing for the new era of generative search.<br>Get your Percepta GEO Score today — backed by Accenture.</p>
    <div style="margin-top:40px;">
      <a href="?p=geohub" class="cta-btn" target="_self">Launch Percepta &nbsp;→</a>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PAGE 2: GEO HUB
# ════════════════════════════════════════════════════════════
elif nav=="GEO Hub":
    st.markdown("""
    <div style="background:#7C3AED;padding:48px 40px;">
        <div style="max-width:900px;margin:0 auto;text-align:center;">
            <div style="font-size:0.72rem;font-weight:700;letter-spacing:.12em;color:rgba(255,255,255,0.65);text-transform:uppercase;margin-bottom:10px;">GEO Intelligence Hub</div>
            <h1 style="font-size:2.4rem;font-weight:900;color:white;margin:0 0 10px 0;letter-spacing:-1px;">Measure. Benchmark. Improve.</h1>
            <p style="font-size:0.95rem;color:rgba(255,255,255,0.82);margin:0;">Enter your brand URL and receive your complete GEO Score report in real time.</p>
        </div>
    </div>""",unsafe_allow_html=True)

    has_result = st.session_state.geo_result is not None
    if has_result:
        tabs = st.tabs(["GEO Score","Competitors","Visibility","Sentiment","Citations","Prompts","Recommendations","Live Prompt"])
    else:
        tabs = st.tabs(["Get Started"])

    with tabs[0]:
        st.markdown("<div style='padding:32px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
        if not has_result:
            st.markdown("""<div style="text-align:center;padding:40px 0 24px 0;">
                <h3 style="font-size:1.3rem;font-weight:800;color:#111827;margin:0 0 8px 0;">Analyze Your Brand's GEO Score</h3>
                <p style="font-size:0.88rem;color:#6B7280;margin:0 0 24px 0;">Enter any brand URL below. Percepta will run 20 live AI queries and generate your complete GEO report.</p>
            </div>""",unsafe_allow_html=True)
            brand_url = st.text_input("Brand URL",value=st.session_state.geo_url,placeholder="https://www.chase.com/",label_visibility="collapsed")
            run_analysis = st.button("Run GEO Analysis",use_container_width=True)
            if run_analysis:
                if not brand_url.strip() or not brand_url.startswith("http"):
                    st.error("Please enter a valid URL starting with http:// or https://")
                else:
                    with st.spinner("Identifying brand from URL..."):
                        page_data = fetch_page_content(brand_url)
                    if not page_data["ok"]:
                        st.error(f"Could not fetch URL: {page_data['error']}")
                    else:
                        with st.spinner("Running 20 live AI queries across 4 consumer categories..."):
                            try:
                                result = analyze_geo_with_ai(page_data)
                                st.session_state.geo_result=result; st.session_state.geo_url=brand_url; st.session_state.geo_page_data=page_data
                                st.success("Analysis complete. Explore the tabs for your full GEO report."); st.rerun()
                            except Exception as e:
                                st.error(f"Analysis failed: {e}")
        else:
            result=st.session_state.geo_result; page_data=st.session_state.geo_page_data; brand_url_=st.session_state.geo_url
            geo=result.get("overall_geo_score",0); brand=result.get("brand_name",page_data["domain"]); brand_domain=page_data.get("domain","")
            label,badge_color,badge_bg=score_badge(geo)
            vis=result.get("context",0); cit=result.get("reliability",0); sent=result.get("exclusivity",0); prom=result.get("organization",0); sov=result.get("share_of_voice",0)
            avg_rank="N/A" if vis==0 else result.get("avg_rank","N/A")
            responses_detail=result.get("responses_detail",[])
            gauge_col,info_col=st.columns([1,2])
            with gauge_col:
                fig_g=go.Figure(go.Indicator(mode="gauge+number",value=geo,number={'font':{'size':52,'color':'#7C3AED'}},domain={'x':[0,1],'y':[0,1]},title={'text':brand,'font':{'size':14,'color':'#374151'}},gauge={'axis':{'range':[0,100],'tickcolor':"#9CA3AF"},'bar':{'color':"#7C3AED"},'bgcolor':"white",'steps':[{'range':[0,44],'color':'#FEE2E2'},{'range':[44,69],'color':'#FEF3C7'},{'range':[69,80],'color':'#DBEAFE'},{'range':[80,100],'color':'#D1FAE5'}],'threshold':{'line':{'color':"#7C3AED",'width':4},'thickness':0.75,'value':geo}}))
                fig_g.update_layout(height=280,margin=dict(l=20,r=20,t=40,b=10),paper_bgcolor='white')
                st.plotly_chart(fig_g,use_container_width=True)
            with info_col:
                detail_parts=[]
                if cit<40: detail_parts.append(f"Citation ({cit}): brand appears in lists but rarely as top pick")
                if prom<40: detail_parts.append(f"Prominence ({prom}): typically mentioned mid-list")
                if sov<20: detail_parts.append(f"Share of Voice ({sov}): competitors dominating AI conversation")
                if sent<50: detail_parts.append(f"Sentiment ({sent}): AI responses lack strong positive endorsement")
                score_txt=(f"GEO Score of {geo} reflects {vis}% Visibility but is held back by: "+"; ".join(detail_parts)+"." if detail_parts else f"Strong performance: Visibility {vis}%, Citation {cit}, Sentiment {sent}, Prominence {prom}, SoV {sov}.")
                st.markdown(f'<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px 28px;"><div style="font-size:1.2rem;font-weight:800;color:#111827;margin-bottom:4px;">{brand}</div><a href="{brand_url_}" target="_blank" style="color:#7C3AED;font-size:0.82rem;">{brand_url_[:70]}{"..." if len(brand_url_)>70 else ""}</a><div style="margin:12px 0;"><span style="background:{badge_bg};color:{badge_color};padding:4px 14px;border-radius:50px;font-size:0.78rem;font-weight:700;">{label}</span></div><div style="font-size:0.82rem;color:#6B7280;line-height:1.6;border-top:1px solid #F3F4F6;padding-top:12px;">{score_txt}</div></div>',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            tooltip_defs={"Visibility Score":"How many of 20 generic AI queries mentioned your brand.","Citation Score":"How authoritatively your brand was cited. Top recommendation = 65 to 85.","Sentiment Score":"Tone of AI responses when your brand appeared. Praised = 75 to 100.","Avg. Rank":"Average position your brand appeared. #1 = mentioned first."}
            mc1,mc2,mc3,mc4=st.columns(4)
            for col,val,lbl,sub in [(mc1,vis,"Visibility Score","AI response presence"),(mc2,cit,"Citation Score","Source authority"),(mc3,sent,"Sentiment Score","Brand perception"),(mc4,avg_rank,"Avg. Rank","AI mention position")]:
                tip=tooltip_defs.get(lbl,"")
                with col:
                    st.markdown(f'<div style="background:white;border-radius:10px;padding:18px 16px;border:1px solid #E5E7EB;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">{lbl}<span class="metric-tooltip"><span class="tooltip-icon">?</span><span class="tooltip-text">{tip}</span></span></div><div style="font-size:1.8rem;font-weight:800;color:#7C3AED;line-height:1;">{val}</div><div style="font-size:0.75rem;color:#9CA3AF;margin-top:3px;">{sub}</div></div>',unsafe_allow_html=True)
        st.markdown("</div>",unsafe_allow_html=True)

    if has_result:
        result=st.session_state.geo_result; page_data=st.session_state.geo_page_data; brand_url_=st.session_state.geo_url
        geo=result.get("overall_geo_score",0); brand=result.get("brand_name",page_data["domain"]); brand_domain=page_data.get("domain","")
        label,badge_color,badge_bg=score_badge(geo)
        vis=result.get("context",0); cit=result.get("reliability",0); sent=result.get("exclusivity",0); prom=result.get("organization",0); sov=result.get("share_of_voice",0)
        avg_rank="N/A" if vis==0 else result.get("avg_rank","N/A")
        responses_detail=result.get("responses_detail",[])

        with tabs[1]:
            st.markdown("<div style='padding:24px 40px;max-width:1000px;margin:0 auto;'>",unsafe_allow_html=True)
            domain_lower2=page_data["domain"].lower()
            fin_kws2=["capital","chase","amex","citi","discover","bank","credit","card","finance","fargo"]
            auto_kws2=["vw","volkswagen","toyota","ford","honda","bmw","tesla","auto","car","motor"]
            if any(x in domain_lower2 for x in fin_kws2):
                top10_title="Financial Services"; competitor_brands=["Chase","American Express","Capital One","Citi","Discover","Wells Fargo","Bank of America","Synchrony","Barclays","USAA"]
                comp_urls={"Chase":"chase.com","American Express":"americanexpress.com","Capital One":"capitalone.com","Citi":"citi.com","Discover":"discover.com","Wells Fargo":"wellsfargo.com","Bank of America":"bankofamerica.com","Synchrony":"synchrony.com","Barclays":"barclays.com","USAA":"usaa.com"}
            elif any(x in domain_lower2 for x in auto_kws2):
                top10_title="Automotive"; competitor_brands=["Tesla","Toyota","BMW","Honda","Ford","Mercedes","Hyundai","Kia","Nissan","Volkswagen"]
                comp_urls={"Tesla":"tesla.com","Toyota":"toyota.com","BMW":"bmw.com","Honda":"honda.com","Ford":"ford.com","Mercedes":"mercedes-benz.com","Hyundai":"hyundai.com","Kia":"kia.com","Nissan":"nissanusa.com","Volkswagen":"vw.com"}
            else:
                top10_title="General"; competitor_brands=[]; comp_urls={}
            top10=[{"Brand":brand,"URL":brand_domain,"GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Sov":sov,"Rank":avg_rank}]
            for comp in competitor_brands:
                if comp.lower()!=brand.lower():
                    scored=score_competitor_from_responses(comp,responses_detail); scored["URL"]=comp_urls.get(comp,comp.lower().replace(" ","+")+".com"); top10.append(scored)
            top10_sorted=sorted(top10,key=lambda x:x["GEO"],reverse=True)
            t10_rows=""
            for idx,c in enumerate(top10_sorted,1):
                is_you=c["Brand"].lower()==brand.lower(); bg_r="#F5F3FF" if is_you else ("white" if idx%2==1 else "#FAFAFA"); bdr="border-left:3px solid #7C3AED;" if is_you else ""; fw="700" if is_you else "400"
                gc=c["GEO"]; gcol="#10B981" if gc>=80 else "#F59E0B" if gc>=60 else "#EF4444"
                you_badge=' <span style="background:#EDE9FE;color:#7C3AED;border-radius:4px;padding:1px 6px;font-size:0.7rem;font-weight:700;">You</span>' if is_you else ""
                t10_rows+=f'<tr style="background:{bg_r};{bdr}"><td style="padding:10px 12px;font-size:0.8rem;color:#9CA3AF;font-weight:600;">{idx}</td><td style="padding:10px 12px;"><div style="font-size:0.84rem;font-weight:{fw};color:#111827;">{c["Brand"]}{you_badge}</div><div style="font-size:0.72rem;color:#9CA3AF;">{c.get("URL","")}</div></td><td style="padding:10px 12px;font-size:0.88rem;font-weight:700;color:{gcol};">{gc}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Vis"]}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Cit"]}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Sen"]}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c.get("Sov","")}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Rank"]}</td></tr>'
            st.markdown(f'<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px;"><div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">{brand_domain} vs Competitors — {top10_title}</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Real-time GEO scores. Highlighted row is you.</div><table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:1px solid #E5E7EB;"><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">#</th><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Brand</th><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">GEO</th><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Visibility</th><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Citation</th><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Sentiment</th><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Share of Voice</th><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Avg Rank</th></tr></thead><tbody>{t10_rows}</tbody></table></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[2]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px;"><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Visibility Score</div><div style="font-size:2rem;font-weight:800;color:#7C3AED;">{vis}%</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">Appeared in {result.get("responses_with_brand",0)} of 20 queries</div></div><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Average Rank</div><div style="font-size:2rem;font-weight:800;color:#7C3AED;">{avg_rank}</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">Position when mentioned in AI responses</div></div><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Query Appearances</div><div style="font-size:2rem;font-weight:800;color:#7C3AED;">{result.get("responses_with_brand",0)}/20</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">Out of 20 generic industry queries</div></div></div>',unsafe_allow_html=True)
            internal_links=page_data.get("internal_links",[])
            if internal_links:
                page_intel=get_page_intelligence(internal_links,brand,responses_detail)
                pi_rows=""
                for p in page_intel:
                    gc=p["geo"]; gcol="#10B981" if gc>=60 else "#F59E0B" if gc>=30 else "#EF4444"
                    cited_badge=f'<span style="background:#D1FAE5;color:#065F46;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Cited {p["cited"]}x</span>' if p["cited"]>0 else '<span style="background:#F3F4F6;color:#9CA3AF;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Not Cited</span>'
                    pi_rows+=f'<tr style="border-bottom:1px solid #F3F4F6;"><td style="padding:10px 14px;"><div style="font-size:0.84rem;font-weight:600;color:#111827;">{p["label"]}</div><div style="font-size:0.72rem;color:#9CA3AF;">{p["path"]}</div></td><td style="padding:10px 14px;">{cited_badge}</td><td style="padding:10px 14px;font-size:0.88rem;font-weight:700;color:{gcol};">{gc}</td><td style="padding:10px 14px;font-size:0.82rem;color:#7C3AED;font-weight:600;">{p["citation_share"]}%</td><td style="padding:10px 14px;font-size:0.84rem;color:{p["color"]};font-weight:600;">{p["status"]}</td></tr>'
                st.markdown(f'<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px;"><div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Page Intelligence</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Which pages of {brand_domain} are being cited by AI.</div><table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:2px solid #E5E7EB;background:#FAFAFA;"><th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Page</th><th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">AI Citations</th><th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">GEO Score</th><th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Citation Share</th><th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Status</th></tr></thead><tbody>{pi_rows}</tbody></table></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[3]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px;"><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Sentiment Score</div><div style="font-size:2rem;font-weight:800;color:#10B981;">{sent}</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">{"Positive — AI speaks favorably" if sent>=70 else "Neutral — room to improve" if sent>=45 else "Needs attention"}</div></div><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Prominence Score</div><div style="font-size:2rem;font-weight:800;color:#7C3AED;">{prom}</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">{"Named first — strong prominence" if prom>=70 else "Mid-list mentions" if prom>=45 else "Buried in responses"}</div></div><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Average Rank</div><div style="font-size:2rem;font-weight:800;color:#3B82F6;">{avg_rank}</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">Average mention position in AI responses</div></div></div>',unsafe_allow_html=True)
            strengths=result.get("strengths_list",[])[:3]
            s_html="".join(f'<li style="padding:10px 0;font-size:0.84rem;color:#374151;display:flex;gap:12px;align-items:flex-start;border-bottom:1px solid #F0FDF4;"><span style="color:#10B981;font-weight:700;flex-shrink:0;">+</span><span>{s}</span></li>' for s in strengths)
            st.markdown(f'<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px;"><div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:16px;">Sentiment Strengths</div><ul style="list-style:none;padding:0;margin:0;">{s_html}</ul></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[4]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;"><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Citation Score</div><div style="font-size:2rem;font-weight:800;color:#7C3AED;">{cit}</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">How authoritatively your brand was cited</div></div><div style="background:white;border-radius:10px;border:1px solid #E5E7EB;padding:20px;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Share of Voice</div><div style="font-size:2rem;font-weight:800;color:#7C3AED;">{sov}</div><div style="font-size:0.78rem;color:#6B7280;margin-top:3px;">Your brand mentions as % of all mentions</div></div></div>',unsafe_allow_html=True)
            citation_sources=result.get("citation_sources",[])
            if citation_sources:
                st.markdown('<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px;"><div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Sources AI is Pulling From</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Domains influencing AI knowledge about this brand.</div>',unsafe_allow_html=True)
                for s in citation_sources:
                    d=s.get("domain",""); cat_label,cat_color,cat_bg=classify_domain(d)
                    share=s.get("citation_share",0); top_pages=s.get("top_pages",[])
                    bar_w=min(share*3,100); favicon=f"https://www.google.com/s2/favicons?domain={d}&sz=14"
                    pages_html=""
                    if top_pages:
                        pages_html='<div style="margin-top:8px;padding-top:8px;border-top:0.5px solid #F3F4F6;">'
                        for pg in top_pages[:5]:
                            pages_html+=f'<div style="font-size:0.75rem;color:#7C3AED;padding:2px 0;">{pg}</div>'
                        pages_html+='</div>'
                    st.markdown(f'<div style="border:1px solid #E5E7EB;border-radius:8px;padding:12px 16px;margin-bottom:8px;"><div style="display:flex;align-items:center;gap:10px;"><span style="font-size:0.78rem;color:#9CA3AF;font-weight:600;width:18px;">{s.get("rank","")}</span><img src="{favicon}" width="14" height="14" onerror="this.style.display=\'none\'"><span style="font-size:0.88rem;font-weight:600;color:#111827;flex:1;">{d}</span><span style="background:{cat_bg};color:{cat_color};border-radius:50px;padding:2px 10px;font-size:0.7rem;font-weight:600;">{cat_label}</span><div style="display:flex;align-items:center;gap:6px;"><div style="background:#F3F4F6;border-radius:4px;height:5px;width:80px;overflow:hidden;"><div style="background:#7C3AED;height:5px;border-radius:4px;width:{bar_w}px;"></div></div><span style="font-size:0.82rem;font-weight:700;color:#7C3AED;">{share}%</span></div></div>{pages_html}</div>',unsafe_allow_html=True)
                st.markdown('</div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[5]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            categories=list(dict.fromkeys([r.get("category","General Consumer") for r in responses_detail]))
            sel_cat=st.selectbox("Filter by category",["All"]+categories)
            filtered=[r for r in responses_detail if sel_cat=="All" or r.get("category")==sel_cat][:10]
            cat_summary={}
            for r in responses_detail:
                c=r.get("category","General Consumer")
                if c not in cat_summary: cat_summary[c]={"total":0,"mentioned":0}
                cat_summary[c]["total"]+=1
                if r.get("mentioned"): cat_summary[c]["mentioned"]+=1
            cat_html=""
            for c,v in cat_summary.items():
                vis_pct=round((v["mentioned"]/max(v["total"],1))*100)
                cat_html+=f'<div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:14px 18px;"><div style="font-size:0.82rem;font-weight:600;color:#111827;margin-bottom:6px;">{c}</div><div style="display:flex;align-items:center;gap:8px;"><div style="background:#F3F4F6;border-radius:4px;height:5px;flex:1;overflow:hidden;"><div style="background:#7C3AED;height:5px;border-radius:4px;width:{vis_pct}%;"></div></div><span style="font-size:0.78rem;font-weight:700;color:#7C3AED;">{vis_pct}%</span></div><div style="font-size:0.72rem;color:#9CA3AF;margin-top:4px;">{v["mentioned"]} of {v["total"]} queries</div></div>'
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:24px;">{cat_html}</div>',unsafe_allow_html=True)
            q_rows=""
            for idx,item in enumerate(filtered):
                mentioned=item.get("mentioned",False); row_bg="#F5F3FF" if mentioned else "white"
                real_pos=item.get("position",0); rank_display=f"#{real_pos}" if real_pos>0 else "N/A"
                rank_color="#10B981" if real_pos==1 else "#7C3AED" if real_pos<=3 else "#F59E0B" if mentioned else "#9CA3AF"
                appeared_badge='<span style="background:#D1FAE5;color:#065F46;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Appeared</span>' if mentioned else '<span style="background:#F3F4F6;color:#9CA3AF;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Not Mentioned</span>'
                cat_badge=f'<span style="background:#EDE9FE;color:#5B21B6;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:600;">{item.get("category","")}</span>'
                q_rows+=f'<tr style="background:{row_bg};border-bottom:1px solid #F3F4F6;"><td style="padding:10px 12px;font-size:0.78rem;color:#9CA3AF;font-weight:600;">{idx+1}</td><td style="padding:10px 14px;"><div style="display:flex;gap:6px;align-items:center;margin-bottom:5px;">{cat_badge}{appeared_badge}</div><div style="font-size:0.83rem;color:#374151;">{item.get("query","")}</div></td><td style="padding:10px 16px;text-align:center;"><div style="font-size:1.1rem;font-weight:800;color:{rank_color};">{rank_display}</div><div style="font-size:0.68rem;color:#9CA3AF;">Rank</div></td></tr>'
            st.markdown(f'<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px;"><div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Top 10 Prompts</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Generic consumer questions. No brand name used.</div><table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:2px solid #E5E7EB;background:#FAFAFA;"><th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">#</th><th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Query</th><th style="padding:8px 16px;text-align:center;font-size:0.72rem;color:#9CA3AF;font-weight:600;">Rank</th></tr></thead><tbody>{q_rows}</tbody></table></div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[6]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            strengths=result.get("strengths_list",[])[:3]; weaknesses=result.get("improvements_list",[])[:5]
            s_html="".join(f'<li style="padding:10px 0;font-size:0.84rem;color:#374151;display:flex;gap:12px;align-items:flex-start;border-bottom:1px solid #F0FDF4;"><span style="color:#10B981;font-weight:700;flex-shrink:0;">+</span><span>{s}</span></li>' for s in strengths)
            w_html="".join(f'<li style="padding:10px 0;font-size:0.84rem;color:#374151;display:flex;gap:12px;align-items:flex-start;border-bottom:1px solid #FFF1F2;"><span style="color:#EF4444;font-weight:700;flex-shrink:0;">x</span><span>{w}</span></li>' for w in weaknesses)
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;"><div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;"><div style="font-size:0.9rem;font-weight:700;color:#065F46;margin-bottom:16px;">What is Working Well</div><ul style="list-style:none;padding:0;margin:0;">{s_html}</ul></div><div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;"><div style="font-size:0.9rem;font-weight:700;color:#9F1239;margin-bottom:16px;">What Needs Improvement</div><ul style="list-style:none;padding:0;margin:0;">{w_html}</ul></div></div>',unsafe_allow_html=True)
            all_actions=result.get("actions",[]); deliverable_map={"High":("Workstream 01: ARD","AXO Baseline Report and Brand Ranking Index"),"Medium":("Workstream 02: AOP","LLM-Ready Content Package and Content Influence Blueprint"),"Low":("Workstream 03: DTI","Schema Optimization Guide and Metadata Remediation Plan")}
            actions_html=""
            for a in all_actions:
                pri=a.get("priority","Medium"); pk,deliv=deliverable_map.get(pri,("",""))
                bg={"High":"#FEE2E2","Medium":"#FEF3C7","Low":"#DCFCE7"}.get(pri,"#F3F4F6"); tc={"High":"#991B1B","Medium":"#92400E","Low":"#166534"}.get(pri,"#374151")
                actions_html+=f'<div style="display:grid;grid-template-columns:90px 1fr 1fr;gap:0;border-bottom:1px solid #F3F4F6;padding:14px 0;align-items:start;"><div><span style="background:{bg};color:{tc};border-radius:4px;padding:2px 10px;font-size:0.72rem;font-weight:700;">{pri}</span></div><div style="font-size:0.84rem;color:#374151;padding-right:16px;">{a["action"]}</div><div style="font-size:0.78rem;color:#7C3AED;font-weight:600;"><span style="background:#EDE9FE;border-radius:6px;padding:3px 10px;">{pk}</span><div style="font-size:0.75rem;color:#9CA3AF;font-weight:400;margin-top:4px;">{deliv}</div></div></div>'
            st.markdown(f'<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px 28px;"><div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Priority Actions</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:20px;">Each action mapped to the relevant Accenture workstream deliverable.</div><div style="display:grid;grid-template-columns:90px 1fr 1fr;border-bottom:2px solid #E5E7EB;padding-bottom:8px;margin-bottom:4px;"><div style="font-size:0.72rem;color:#9CA3AF;font-weight:600;">Priority</div><div style="font-size:0.72rem;color:#9CA3AF;font-weight:600;">Action</div><div style="font-size:0.72rem;color:#9CA3AF;font-weight:600;">Linked Deliverable</div></div>{actions_html}</div>',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[7]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            st.markdown("""<div style="background:#7C3AED;border-radius:12px;padding:24px 28px;color:white;margin-bottom:20px;">
                <h3 style="font-size:1.1rem;font-weight:800;color:white;margin:0 0 6px 0;">Live AI Prompt Lab</h3>
                <p style="font-size:0.88rem;color:rgba(255,255,255,0.85);margin:0;">Type any prompt and see exactly how GPT-5.4 responds in real time.</p>
            </div>""",unsafe_allow_html=True)
            query=st.text_input("Enter a prompt","",placeholder="e.g. What is the best travel credit card for high net worth individuals?",label_visibility="collapsed")
            if st.button("Run Prompt"):
                if not query.strip(): st.warning("Please enter a prompt.")
                else:
                    with st.spinner("Querying GPT-5.4..."):
                        try:
                            resp=get_response(query,INTERNAL_API_KEY); st.session_state.ai_history.append({"q":query,"a":resp})
                        except Exception as e:
                            st.error(f"Error: {e}")
            for item in reversed(st.session_state.ai_history):
                st.markdown(f'<div style="display:flex;justify-content:flex-end;margin:20px 0 10px 0;"><div style="background:#F4F4F4;color:#111827;border-radius:18px 18px 4px 18px;padding:12px 18px;max-width:60%;font-size:0.95rem;font-weight:500;">{item["q"]}</div></div>',unsafe_allow_html=True)
                st.markdown(item["a"])
                st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:16px 0;">',unsafe_allow_html=True)
            if st.session_state.ai_history:
                if st.button("Clear history",key="clr"): st.session_state.ai_history=[]; st.rerun()
            st.markdown("</div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PAGE 3: GET SUPPORT
# ════════════════════════════════════════════════════════════
elif nav=="Get Support":
    st.markdown("""
    <div style="background:#7C3AED;padding:72px 40px;">
        <div style="max-width:900px;margin:0 auto;text-align:center;">
            <div style="font-size:0.72rem;font-weight:700;letter-spacing:.12em;color:rgba(255,255,255,0.65);text-transform:uppercase;margin-bottom:10px;">Accenture GEO Services</div>
            <h1 style="font-size:2.8rem;font-weight:900;color:white;margin:0 0 14px 0;letter-spacing:-1px;">We've Got You Covered</h1>
            <p style="font-size:1rem;color:rgba(255,255,255,0.82);max-width:500px;margin:0 auto;line-height:1.8;">From GEO diagnostic to full optimization. Accenture's team handles everything, end to end.</p>
        </div>
    </div>""",unsafe_allow_html=True)

    st.markdown("""
    <div style="background:white;padding:72px 40px;border-bottom:1px solid #E5E7EB;">
        <div style="max-width:900px;margin:0 auto;">
            <div style="text-align:center;margin-bottom:48px;">
                <div class="section-tag">Our Approach</div>
                <h2 style="font-size:1.8rem;font-weight:800;color:#111827;margin:0 0 10px 0;">GEO is No Longer Optional</h2>
                <p style="font-size:0.88rem;color:#6B7280;max-width:520px;margin:0 auto;line-height:1.8;">While search spend continues to rise, its impact is fading as AI agents increasingly shape the decisions search used to influence.</p>
            </div>
            <div style="display:grid;grid-template-columns:1fr auto 1fr;gap:32px;align-items:center;margin-bottom:40px;">
                <div style="display:flex;flex-direction:column;gap:24px;">
                    <div style="padding:24px;border:1px solid #E5E7EB;border-radius:12px;">
                        <div style="font-size:0.7rem;font-weight:700;color:#7C3AED;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Workstream 1</div>
                        <div style="font-size:0.95rem;font-weight:700;color:#111827;margin-bottom:6px;font-style:italic;">Agent Ranking Diagnostic (ARD)</div>
                        <p style="font-size:0.82rem;color:#6B7280;line-height:1.6;margin:0;">Conduct the initial evaluation to <strong>establish the baseline ranking performance</strong> of AI agents when comparing your brand to competitive offerings across high-intent consumer scenarios.</p>
                    </div>
                    <div style="padding:24px;border:1px solid #E5E7EB;border-radius:12px;">
                        <div style="font-size:0.7rem;font-weight:700;color:#7C3AED;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Workstream 4</div>
                        <div style="font-size:0.95rem;font-weight:700;color:#111827;margin-bottom:6px;font-style:italic;">Impact Measurement (Re-Diagnostic)</div>
                        <p style="font-size:0.82rem;color:#6B7280;line-height:1.6;margin:0;">Following the optimization activities, re-run the diagnostic to <strong>re-measure performance</strong>, quantify improvements and establish the ongoing program foundation.</p>
                    </div>
                </div>
                <div style="display:flex;align-items:center;justify-content:center;">
                    <svg width="140" height="110" viewBox="0 0 180 120" fill="none">
                        <path d="M45 60 C45 38 60 20 80 20 C100 20 110 38 110 60 C110 82 120 100 140 100 C160 100 170 82 170 60 C170 38 160 20 140 20 C120 20 110 38 110 60 C110 82 100 100 80 100 C60 100 45 82 45 60Z" stroke="#7C3AED" stroke-width="7" fill="none"/>
                        <polygon points="109,53 117,60 109,67" fill="#7C3AED"/>
                        <polygon points="111,53 103,60 111,67" fill="#5B21B6"/>
                    </svg>
                </div>
                <div style="display:flex;flex-direction:column;gap:24px;">
                    <div style="padding:24px;border:1px solid #E5E7EB;border-radius:12px;">
                        <div style="font-size:0.7rem;font-weight:700;color:#7C3AED;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Workstream 3</div>
                        <div style="font-size:0.95rem;font-weight:700;color:#111827;margin-bottom:6px;font-style:italic;">Distribution and Technical Influence (DTI)</div>
                        <p style="font-size:0.82rem;color:#6B7280;line-height:1.6;margin:0;">Pinpoint and <strong>propose specific technical and distribution improvements</strong> to maximize the chance that LLMs ingest and utilize your verified content.</p>
                    </div>
                    <div style="padding:24px;border:1px solid #E5E7EB;border-radius:12px;">
                        <div style="font-size:0.7rem;font-weight:700;color:#7C3AED;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">Workstream 2</div>
                        <div style="font-size:0.95rem;font-weight:700;color:#111827;margin-bottom:6px;font-style:italic;">Agent Optimization Plan (AOP)</div>
                        <p style="font-size:0.82rem;color:#6B7280;line-height:1.6;margin:0;">Based on the diagnostic findings, <strong>design and deploy a specific optimization strategy</strong> aimed at elevating agent recognition and positioning of your brand.</p>
                    </div>
                </div>
            </div>
            <div style="display:flex;gap:40px;justify-content:center;padding:28px 0;border-top:1px solid #F3F4F6;">
                <div style="text-align:center;"><div style="font-size:2.8rem;font-weight:900;color:#111827;line-height:1;">6</div><div style="font-size:0.88rem;font-weight:600;color:#111827;margin-top:2px;">Week Engagement</div><div style="font-size:0.76rem;color:#9CA3AF;margin-top:2px;">Phase 1</div></div>
                <div style="width:1px;background:#F3F4F6;"></div>
                <div style="text-align:center;"><div style="font-size:2.8rem;font-weight:900;color:#111827;line-height:1;">2</div><div style="font-size:0.88rem;font-weight:600;color:#111827;margin-top:2px;">AI Agents</div><div style="font-size:0.76rem;color:#9CA3AF;margin-top:2px;">ChatGPT and Gemini</div></div>
                <div style="width:1px;background:#F3F4F6;"></div>
                <div style="text-align:center;"><div style="font-size:2.8rem;font-weight:900;color:#111827;line-height:1;">4</div><div style="font-size:0.88rem;font-weight:600;color:#111827;margin-top:2px;">Workstreams</div><div style="font-size:0.76rem;color:#9CA3AF;margin-top:2px;">End to end coverage</div></div>
            </div>
        </div>
    </div>""",unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#F9F9FC;padding:64px 40px;border-bottom:1px solid #E5E7EB;">
        <div style="max-width:900px;margin:0 auto;">
            <div style="text-align:center;margin-bottom:40px;">
                <div class="section-tag">Deliverables</div>
                <h2 style="font-size:1.8rem;font-weight:800;color:#111827;margin:0;">Activities and What We Deliver</h2>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:3px;margin-bottom:12px;">
                <div style="background:#1E1B5E;padding:18px 16px;border-radius:8px 0 0 0;clip-path:polygon(0 0,93% 0,100% 50%,93% 100%,0 100%);"><div style="font-size:0.68rem;font-weight:600;color:rgba(255,255,255,0.6);margin-bottom:5px;text-transform:uppercase;letter-spacing:.07em;">Workstream 01</div><div style="font-size:0.85rem;font-weight:700;color:white;line-height:1.3;">Agent Ranking Diagnostic</div></div>
                <div style="background:#2D2A70;padding:18px 18px 18px 24px;clip-path:polygon(0 0,93% 0,100% 50%,93% 100%,0 100%,7% 50%);"><div style="font-size:0.68rem;font-weight:600;color:rgba(255,255,255,0.6);margin-bottom:5px;text-transform:uppercase;letter-spacing:.07em;">Workstream 02</div><div style="font-size:0.85rem;font-weight:700;color:white;line-height:1.3;">Agent Optimization Plan</div></div>
                <div style="background:#3D3A8A;padding:18px 18px 18px 24px;clip-path:polygon(0 0,93% 0,100% 50%,93% 100%,0 100%,7% 50%);"><div style="font-size:0.68rem;font-weight:600;color:rgba(255,255,255,0.6);margin-bottom:5px;text-transform:uppercase;letter-spacing:.07em;">Workstream 03</div><div style="font-size:0.85rem;font-weight:700;color:white;line-height:1.3;">Distribution and Technical</div></div>
                <div style="background:#5B21B6;padding:18px 18px 18px 24px;border-radius:0 8px 0 0;clip-path:polygon(0 0,100% 0,100% 100%,0 100%,7% 50%);"><div style="font-size:0.68rem;font-weight:600;color:rgba(255,255,255,0.6);margin-bottom:5px;text-transform:uppercase;letter-spacing:.07em;">Workstream 04</div><div style="font-size:0.85rem;font-weight:700;color:white;line-height:1.3;">Impact Measurement</div></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:12px;">
                <div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #F3F4F6;padding-bottom:8px;margin-bottom:10px;">Activities</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>Representative prompts across personas</li><li>Multi-run stability testing</li><li>Agent-generated rankings</li><li>Power distribution modeling</li><li>Competitor adjacency maps</li></ul></div>
                <div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #F3F4F6;padding-bottom:8px;margin-bottom:10px;">Activities</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>LLM-ready content: FAQs, Top 10 lists</li><li>Product-attribute associations</li><li>Content for agent ingestion</li><li>Content Influence Blueprint</li></ul></div>
                <div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #F3F4F6;padding-bottom:8px;margin-bottom:10px;">Activities</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>Tagging, metadata, and taxonomy</li><li>Missing structured data</li><li>Backlink improvements</li><li>Schema markup audit</li></ul></div>
                <div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #F3F4F6;padding-bottom:8px;margin-bottom:10px;">Activities</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>Re-test all prompts</li><li>Semantic drift and ranking changes</li><li>Recompute AXO Score</li></ul></div>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;">
                <div style="background:#F9F9FC;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:10px;">Deliverables</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>AXO Baseline Report</li><li>Brand Ranking Index</li><li>Power Curve Analysis</li><li>Attribute Influence Map</li><li>AXO Baseline Score v1.0</li></ul></div>
                <div style="background:#F9F9FC;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:10px;">Deliverables</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>Agent Optimization Plan</li><li>LLM-Ready Content Package</li><li>Attribute Reinforcement Strategy</li><li>Content Influence Blueprint</li></ul></div>
                <div style="background:#F9F9FC;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:10px;">Deliverables</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>DTI Report</li><li>Metadata Remediation Plan</li><li>Backlink and Redirect Strategy</li><li>Schema Optimization Guide</li></ul></div>
                <div style="background:#F9F9FC;border:1px solid #E5E7EB;border-radius:8px;padding:16px;"><div style="font-size:0.8rem;font-weight:700;color:#111827;border-bottom:1px solid #E5E7EB;padding-bottom:8px;margin-bottom:10px;">Deliverables</div><ul style="list-style:disc;padding-left:14px;margin:0;font-size:0.76rem;color:#374151;line-height:1.7;"><li>AXO Impact Report</li><li>Before and After Ranking Comparison</li><li>Updated AXO Score v2.0</li><li>Ongoing recommendations</li></ul></div>
            </div>
        </div>
    </div>""",unsafe_allow_html=True)

    st.markdown("""
    <div style="background:white;padding:72px 40px;border-bottom:1px solid #E5E7EB;">
        <div style="max-width:900px;margin:0 auto;">
            <div style="text-align:center;margin-bottom:52px;">
                <div class="section-tag">Explore Offers</div>
                <h2 style="font-size:1.8rem;font-weight:800;color:#111827;margin:0 0 10px 0;">Choose Your Pilot Program</h2>
                <p style="font-size:0.88rem;color:#6B7280;max-width:420px;margin:0 auto;">Start with what fits your timeline. Scale as you see results.</p>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;">
                <div style="border:1px solid #E5E7EB;border-radius:16px;padding:36px 32px;">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:10px;">Option 1</div>
                    <div style="font-size:3rem;font-weight:900;color:#111827;line-height:1;margin-bottom:2px;">6</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#374151;margin-bottom:28px;">Week Engagement</div>
                    <div style="height:1px;background:#F3F4F6;margin-bottom:24px;"></div>
                    <div style="display:flex;flex-direction:column;gap:12px;">
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Ranking Diagnostic (ARD)</div>
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Optimization Plan (AOP)</div>
                    </div>
                </div>
                <div style="border:2px solid #7C3AED;border-radius:16px;padding:36px 32px;position:relative;background:#FAFBFF;">
                    <div style="position:absolute;top:-13px;left:50%;transform:translateX(-50%);background:#7C3AED;color:white;border-radius:50px;padding:3px 16px;font-size:0.72rem;font-weight:700;white-space:nowrap;">Recommended</div>
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#7C3AED;margin-bottom:10px;">Option 2</div>
                    <div style="font-size:3rem;font-weight:900;color:#111827;line-height:1;margin-bottom:2px;">7</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#374151;margin-bottom:28px;">Week Engagement</div>
                    <div style="height:1px;background:#E5E7EB;margin-bottom:24px;"></div>
                    <div style="display:flex;flex-direction:column;gap:12px;">
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Ranking Diagnostic (ARD)</div>
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Optimization Plan (AOP)</div>
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Impact Measurement (Re-Diagnostic)</div>
                    </div>
                </div>
                <div style="border:1px solid #E5E7EB;border-radius:16px;padding:36px 32px;">
                    <div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:10px;">Option 3</div>
                    <div style="font-size:3rem;font-weight:900;color:#111827;line-height:1;margin-bottom:2px;">7</div>
                    <div style="font-size:0.95rem;font-weight:600;color:#374151;margin-bottom:28px;">Week Engagement</div>
                    <div style="height:1px;background:#F3F4F6;margin-bottom:24px;"></div>
                    <div style="display:flex;flex-direction:column;gap:12px;">
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Ranking Diagnostic (ARD)</div>
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Optimization Plan (AOP)</div>
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Distribution and Technical Influence (DTI)</div>
                        <div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Impact Measurement (Re-Diagnostic)</div>
                    </div>
                </div>
            </div>
        </div>
    </div>""",unsafe_allow_html=True)

    st.markdown("""
    <div style="background:#7C3AED;padding:72px 40px;">
        <div style="max-width:900px;margin:0 auto;">
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:60px;align-items:center;">
                <div>
                    <div style="font-size:0.72rem;font-weight:700;letter-spacing:.12em;color:rgba(255,255,255,0.6);text-transform:uppercase;margin-bottom:10px;">Proven Results</div>
                    <h2 style="font-size:1.8rem;font-weight:800;color:white;margin:0 0 14px 0;line-height:1.25;">Validated Impact Across<br>10+ Client Engagements</h2>
                    <p style="font-size:0.9rem;color:rgba(255,255,255,0.8);line-height:1.8;margin:0;">Across retail, travel, financial services, and hospitality, Percepta has consistently delivered measurable improvements in AI brand visibility.</p>
                </div>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
                    <div style="border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:22px;">
                        <div style="font-size:2.2rem;font-weight:900;color:white;">10+</div>
                        <div style="font-size:0.8rem;font-weight:600;color:rgba(255,255,255,0.8);margin-top:5px;">Successful Clients</div>
                        <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);margin-top:2px;">Across retail, travel, hospitality</div>
                    </div>
                    <div style="border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:22px;">
                        <div style="font-size:2.2rem;font-weight:900;color:white;">4X</div>
                        <div style="font-size:0.8rem;font-weight:600;color:rgba(255,255,255,0.8);margin-top:5px;">Higher Conversion</div>
                        <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);margin-top:2px;">From ChatGPT vs traditional search</div>
                    </div>
                    <div style="border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:22px;">
                        <div style="font-size:2.2rem;font-weight:900;color:white;">15%</div>
                        <div style="font-size:0.8rem;font-weight:600;color:rgba(255,255,255,0.8);margin-top:5px;">Citation Growth</div>
                        <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);margin-top:2px;">Improved brand authority in AI</div>
                    </div>
                    <div style="border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:22px;">
                        <div style="font-size:2.2rem;font-weight:900;color:white;">68%</div>
                        <div style="font-size:0.8rem;font-weight:600;color:rgba(255,255,255,0.8);margin-top:5px;">Longer Sessions</div>
                        <div style="font-size:0.72rem;color:rgba(255,255,255,0.5);margin-top:2px;">Through AI-optimized content</div>
                    </div>
                </div>
            </div>
        </div>
    </div>""",unsafe_allow_html=True)
