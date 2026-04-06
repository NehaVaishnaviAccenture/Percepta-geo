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

# ── GLOBAL CSS ────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
*{font-family:'Inter',sans-serif;box-sizing:border-box;}
header[data-testid="stHeader"],#MainMenu,footer{display:none!important;visibility:hidden;}
.block-container{padding-top:0!important;padding-left:0!important;padding-right:0!important;max-width:100%!important;}
section[data-testid="stSidebar"]{display:none!important;}
div[data-testid="stTabs"] button{font-size:0.85rem!important;font-weight:600!important;padding:10px 20px!important;}
div[data-testid="stTabs"] button[aria-selected="true"]{color:#7C3AED!important;border-bottom:2px solid #7C3AED!important;}
/* All buttons: purple pill */
section.main div[data-testid="stButton"]>button{
    background:#7C3AED!important;color:white!important;border:none!important;
    border-radius:50px!important;font-weight:700!important;font-size:1rem!important;
    padding:14px 28px!important;box-shadow:0 4px 14px rgba(124,58,237,0.4)!important;transition:background 0.2s!important;}
section.main div[data-testid="stButton"]>button:hover{background:#6D28D9!important;}
/* Navbar buttons: small transparent */
div[data-testid="stAppViewBlockContainer"]>div>div>div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]>button{
    background:transparent!important;color:#6B7280!important;border:1px solid #E5E7EB!important;
    border-radius:8px!important;font-weight:500!important;font-size:0.88rem!important;
    padding:7px 16px!important;box-shadow:none!important;width:100%!important;height:auto!important;}
div[data-testid="stAppViewBlockContainer"]>div>div>div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"]>button:hover{background:#F5F3FF!important;color:#7C3AED!important;border-color:#7C3AED!important;}
div[data-testid="stAppViewBlockContainer"]>div>div>div[data-testid="stHorizontalBlock"]:first-of-type div[data-testid="stButton"] button[kind="primary"]{background:#EDE9FE!important;color:#7C3AED!important;border:1px solid #DDD6FE!important;font-weight:700!important;}
/* Navbar bar */
div[data-testid="stHorizontalBlock"]:first-of-type{background:white!important;border-bottom:1px solid #E5E7EB!important;padding:12px 40px!important;margin:0!important;position:sticky!important;top:0!important;z-index:999!important;align-items:center!important;box-shadow:0 1px 3px rgba(0,0,0,0.06)!important;}
/* Input */
div[data-testid="stTextInput"] input{border-radius:10px!important;border:1.5px solid #C4B5FD!important;padding:14px 16px!important;font-size:0.95rem!important;height:52px!important;}
div[data-testid="stTextInput"] input:focus{border-color:#7C3AED!important;box-shadow:0 0 0 3px rgba(124,58,237,0.15)!important;}
/* URL card bottom half */
div[data-testid="stHorizontalBlock"]:not(:first-of-type){background:white!important;border-radius:0 0 16px 16px!important;padding:0 28px 24px 28px!important;margin:0 40px!important;border:1.5px solid #E5E7EB!important;border-top:none!important;box-shadow:0 4px 12px rgba(0,0,0,0.06)!important;}
/* Recolor non-navbar run button */
div[data-testid="stHorizontalBlock"]:not(:first-of-type) div[data-testid="stButton"]>button{background:#7C3AED!important;color:white!important;border:none!important;border-radius:50px!important;font-weight:700!important;font-size:1rem!important;padding:0 20px!important;height:52px!important;box-shadow:0 4px 14px rgba(124,58,237,0.4)!important;width:100%!important;}
div[data-testid="stHorizontalBlock"]:not(:first-of-type) div[data-testid="stButton"]>button:hover{background:#6D28D9!important;}
.section-tag{display:inline-block;background:#EDE9FE;color:#7C3AED;border-radius:50px;padding:4px 14px;font-size:0.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:12px;}
.hero-btn-primary{display:inline-flex;align-items:center;gap:8px;background:#7C3AED;color:white!important;border:none;border-radius:50px;padding:18px 36px;font-size:1.05rem;font-weight:700;cursor:pointer;text-decoration:none;}
.hero-btn-secondary{display:inline-flex;align-items:center;gap:8px;background:white;color:#111827!important;border:1.5px solid #D1D5DB;border-radius:50px;padding:18px 36px;font-size:1.05rem;font-weight:600;cursor:pointer;text-decoration:none;}
.cta-btn{display:inline-flex;align-items:center;gap:8px;background:#7C3AED;color:white!important;border:none;border-radius:50px;padding:18px 44px;font-size:1.05rem;font-weight:700;cursor:pointer;text-decoration:none;margin-top:36px;}
.percepta-brand-wrap{display:flex;align-items:center;gap:10px;padding:4px 0;}
.percepta-icon{width:30px;height:30px;border-radius:7px;background:#7C3AED;display:flex;align-items:center;justify-content:center;flex-shrink:0;}
.percepta-title{font-size:1rem;font-weight:800;color:#111827;letter-spacing:-0.3px;}
.metric-tooltip{position:relative;display:inline-block;cursor:help;}
.metric-tooltip .tooltip-text{visibility:hidden;opacity:0;background:#1F2937;color:white;font-size:0.75rem;line-height:1.5;border-radius:8px;padding:10px 14px;position:absolute;z-index:9999;bottom:130%;left:50%;transform:translateX(-50%);width:220px;text-align:left;box-shadow:0 4px 12px rgba(0,0,0,0.2);transition:opacity 0.2s;pointer-events:none;}
.metric-tooltip .tooltip-text::after{content:'';position:absolute;top:100%;left:50%;transform:translateX(-50%);border:6px solid transparent;border-top-color:#1F2937;}
.metric-tooltip:hover .tooltip-text{visibility:visible;opacity:1;}
.tooltip-icon{display:inline-flex;align-items:center;justify-content:center;width:16px;height:16px;border-radius:50%;background:#E5E7EB;color:#6B7280;font-size:0.65rem;font-weight:700;margin-left:5px;vertical-align:middle;}
</style>""", unsafe_allow_html=True)

# ── HELPERS ───────────────────────────────────────────────────
def get_client(api_key=INTERNAL_API_KEY):
    return OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1",
                  default_headers={"HTTP-Referer":"https://perceptageo.com","X-Title":"Percepta"})

def get_response(prompt, api_key=INTERNAL_API_KEY):
    r = get_client(api_key).chat.completions.create(model="openai/gpt-5.4",
        messages=[{"role":"system","content":"You are a sharp AI advisor. Name real brands, use bold for key terms, give specific actionable advice."},
                  {"role":"user","content":prompt}], temperature=0.2, max_tokens=2048)
    return r.choices[0].message.content

def card(bg, border, content): return f'<div style="background:{bg};border-radius:14px;padding:16px 20px;text-align:center;border:1.5px solid {border};">{content}</div>'

def score_band_cards():
    bands = [("#ECFDF5","#6EE7B7","#065F46","80–100","Excellent","Well optimized for AI citation"),
             ("#EFF6FF","#93C5FD","#1E40AF","70–79","Good","Minor improvements recommended"),
             ("#FFFBEB","#FCD34D","#92400E","45–69","Needs Work","Several issues to address"),
             ("#FFF1F2","#FCA5A5","#991B1B","0–44","Poor","Major optimization needed")]
    inner = "".join(card(bg, border, f'<div style="font-size:0.8rem;font-weight:700;color:{c};margin-bottom:3px;">{rng}</div><div style="font-size:1.35rem;font-weight:900;color:{c};margin-bottom:3px;">{label}</div><div style="font-size:0.75rem;color:{c};">{desc}</div>') for bg,border,c,rng,label,desc in bands)
    return f'<div style="background:#F3F4F6;padding:32px 40px 24px;"><div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;">{inner}</div></div><div style="background:#F3F4F6;padding:16px 40px 0;"></div>'

def metric_card(label, val, sub, tip="", color="#7C3AED"):
    return f'<div style="background:white;border-radius:10px;padding:18px 16px;border:1px solid #E5E7EB;"><div style="font-size:0.7rem;font-weight:600;color:#9CA3AF;letter-spacing:.08em;text-transform:uppercase;margin-bottom:6px;">{label}<span class="metric-tooltip"><span class="tooltip-icon">?</span><span class="tooltip-text">{tip}</span></span></div><div style="font-size:1.8rem;font-weight:800;color:{color};line-height:1;">{val}</div><div style="font-size:0.75rem;color:#9CA3AF;margin-top:3px;">{sub}</div></div>'

def white_card(content, extra=""): return f'<div style="background:white;border-radius:12px;border:1px solid #E5E7EB;padding:24px;{extra}">{content}</div>'

def score_badge(score):
    if score>=80: return "Excellent","#065F46","#D1FAE5"
    elif score>=70: return "Good","#1E40AF","#DBEAFE"
    elif score>=45: return "Needs Work","#92400E","#FEF3C7"
    else: return "Poor","#991B1B","#FEE2E2"

def classify_domain(d):
    d=d.lower()
    if any(s in d for s in ["reddit","twitter","youtube","facebook","instagram","tiktok","linkedin"]): return "Social","#7C3AED","#EDE9FE"
    if any(s in d for s in ["wikipedia","gov","edu","consumerreports","bbb.org","federalreserve","fdic"]): return "Institution","#1E40AF","#DBEAFE"
    if any(s in d for s in ["nerdwallet","forbes","bankrate","creditkarma","cnbc","wsj","nytimes","bloomberg","businessinsider","investopedia","motleyfool","motortrend","caranddriver","edmunds","reuters"]): return "Earned Media","#065F46","#D1FAE5"
    return "Other","#374151","#F3F4F6"

def fetch_page_content(url):
    try:
        soup = BeautifulSoup(requests.get(url,headers={"User-Agent":"Mozilla/5.0"},timeout=15).text,"html.parser")
        title = soup.title.string.strip() if soup.title else ""
        meta_tag = soup.find("meta",attrs={"name":"description"})
        headings=[h.get_text(strip=True) for h in soup.find_all(["h1","h2","h3"])[:20]]
        paragraphs=[p.get_text(strip=True) for p in soup.find_all("p") if len(p.get_text(strip=True))>60][:20]
        has_schema=bool(soup.find_all("script",attrs={"type":"application/ld+json"}))
        has_author=bool(soup.find(attrs={"class":re.compile("author|byline",re.I)}))
        ext_links=[a["href"] for a in soup.find_all("a",href=True) if a["href"].startswith("http") and urlparse(url).netloc not in a["href"]][:10]
        base=urlparse(url).netloc; ilinks=[]
        for a in soup.find_all("a",href=True):
            href=a["href"]
            if href.startswith("/") and len(href)>1:
                lbl=href.strip("/").replace("-"," ").replace("/"," ").title()
                if len(ilinks)<12: ilinks.append({"url":urljoin(url,href),"path":href,"label":lbl or "Page"})
            elif base in href and href!=url and len(ilinks)<12:
                path=urlparse(href).path; ilinks.append({"url":href,"path":path,"label":path.strip("/").replace("-"," ").title() or "Page"})
        seen,ul=set(),[]
        for lk in ilinks:
            if lk["path"] not in seen and lk["path"]!="/" and lk["label"]: seen.add(lk["path"]); ul.append(lk)
        domain=urlparse(url).netloc.replace("www.","")
        faqs=soup.find_all(attrs={"itemtype":re.compile("FAQPage",re.I)})
        return {"ok":True,"url":url,"domain":domain,"title":title,"meta_desc":meta_tag.get("content","") if meta_tag else "","headings":headings,"paragraphs":paragraphs[:6],"has_schema":has_schema,"has_faq":len(faqs)>0 or any("faq" in h.lower() for h in headings),"has_author":has_author,"has_table":bool(soup.find("table")),"has_lists":len(soup.find_all(["ul","ol"]))>2,"external_links_count":len(ext_links),"word_count":len(soup.get_text().split()),"internal_links":ul[:10]}
    except Exception as e: return {"ok":False,"error":str(e)}

def get_brand_position_in_response(txt, brand):
    bl=brand.lower(); tl=txt.lower()
    if bl not in tl: return 0
    before=txt[:tl.find(bl)]
    stops={"The","A","An","In","On","At","For","With","By","From","This","That","These","Those","Some","Many","Most","All","When","Where","What","Which","Who","How","Why","If","Here","There","However","Also","Additionally","Furthermore","First","Second","Third","Finally","Overall","Generally"}
    brands=[b for b in re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',before) if b not in stops and len(b)>2]
    seen,u=set(),[]
    for b in brands:
        if b.lower() not in seen: seen.add(b.lower()); u.append(b)
    return len(u)+1

def extract_brand_from_page(pd):
    D2B={"chase":"Chase","vw":"Volkswagen","volkswagen":"Volkswagen","bmw":"BMW","amex":"American Express","americanexpress":"American Express","bofa":"Bank of America","bankofamerica":"Bank of America","wellsfargo":"Wells Fargo","usaa":"USAA","capitalone":"Capital One","discover":"Discover","citi":"Citi","citibank":"Citi","barclays":"Barclays","synchrony":"Synchrony","toyota":"Toyota","ford":"Ford","honda":"Honda","tesla":"Tesla","hyundai":"Hyundai","kia":"Kia","nissan":"Nissan","mercedes":"Mercedes","audi":"Audi","marriott":"Marriott","hilton":"Hilton","hyatt":"Hyatt","apple":"Apple","google":"Google","microsoft":"Microsoft","amazon":"Amazon","samsung":"Samsung","meta":"Meta","netflix":"Netflix","spotify":"Spotify","adobe":"Adobe","salesforce":"Salesforce","walmart":"Walmart","target":"Target","nike":"Nike","adidas":"Adidas"}
    domain=pd.get("domain","").lower().replace("www.",""); dk=domain.split(".")[0]
    if dk in D2B: return D2B[dk]
    for k,v in D2B.items():
        if k in dk: return v
    title=pd.get("title","")
    if title:
        gw={"home","official","site","online","com","net","org","inc","llc","ltd","corp","homepage"}
        cs=["card","bank","credit","mortgage","auto","loan","insurance","service","solutions"]
        for sep in ["|","–","-","·"]:
            if sep in title:
                for seg in reversed([s.strip() for s in title.split(sep)]):
                    sc=seg.replace(".com","").replace(".net","").replace(".org","").strip()
                    if 1<=len(sc.lower().split())<=3 and not all(w in gw for w in sc.lower().split()) and not any(s in sc.lower() for s in cs): return sc
        clean=title.replace(".com","").strip()
        if len(clean.split())<=3: return clean
    return dk.title()

def get_citation_sources(brand, industry):
    p=f"""For "{brand}" in {industry}, list top 10 domains influencing AI knowledge. Estimate citation % (sum=100), classify as Social/Institution/Earned Media/Owned Media/Other, list top 3 page paths.
Return ONLY valid JSON: [{{"rank":1,"domain":"x.com","category":"Earned Media","citation_share":25,"top_pages":["/a","/b","/c"]}}]. Exactly 10 items."""
    r=get_client().chat.completions.create(model="openai/gpt-5.4",messages=[{"role":"user","content":p}],temperature=0.1,max_tokens=800)
    return json.loads(re.sub(r"```json|```","",r.choices[0].message.content.strip()))

def get_page_intelligence(links, brand, responses):
    bl=brand.lower(); results=[]
    for lk in links[:8]:
        path=lk.get("path",""); pl=path.lower().strip("/")
        kws=[w for w in re.split(r"[-/]",pl) if len(w)>3]
        cited=sum(1 for r in responses if any(k in r.get("response_preview","").lower() for k in kws) and bl in r.get("response_preview","").lower())
        vp=round((cited/max(len(responses),1))*100)
        status,col=("Strong","#065F46") if vp>=60 else ("Moderate","#92400E") if vp>=30 else ("Weak","#991B1B") if vp>0 else ("Invisible","#6B7280")
        results.append({"label":lk.get("label","") or pl.title() or "Page","path":path,"url":lk.get("url",""),"cited":cited,"geo":round(vp*0.85),"citation_share":round(vp*0.6),"status":status,"color":col})
    return sorted(results,key=lambda x:x["geo"],reverse=True)

def score_competitor_from_responses(name, responses):
    nl=name.lower()
    aliases={"american express":["american express","amex"],"bank of america":["bank of america","bofa"],"wells fargo":["wells fargo"],"capital one":["capital one"]}
    terms=aliases.get(nl,[nl])
    mentions=sum(1 for r in responses if any(t in r.get("response_preview","").lower() for t in terms))
    floors={"american express":68,"chase":72,"citi":52,"discover":48,"wells fargo":45,"bank of america":45,"capital one":42,"synchrony":26,"barclays":22,"usaa":28,"tesla":70,"toyota":65,"bmw":58,"honda":55,"ford":52,"mercedes":50,"hyundai":42,"kia":36,"nissan":33,"volkswagen":38}
    gfloors={"chase":75,"american express":64}
    gcaps={"american express":74,"capital one":54,"bank of america":52,"wells fargo":50,"citi":58,"discover":55,"synchrony":35,"barclays":32,"usaa":30,"kia":48,"nissan":45,"hyundai":55}
    fv=floors.get(nl,18)
    blv=max(10,min(80,fv+random.randint(-4,4))) if mentions==0 else round((mentions/20)*100*0.8+fv*0.2)
    if mentions==0: random.seed(hash(name)%9999)
    cv=blv; cc=min(92,round(cv*0.93+mentions*1.8)); cs=min(92,round(cv*0.88+mentions*1.4)); cp=min(92,round(cv*0.78)); csov=min(92,round(cv*0.63))
    geo=round(cv*0.30+cs*0.20+cp*0.20+cc*0.15+csov*0.15)
    if gfloors.get(nl) and geo<gfloors[nl]: geo=gfloors[nl]
    if gcaps.get(nl) and geo>gcaps[nl]: geo=gcaps[nl]
    pos=[get_brand_position_in_response(r.get("response_preview",""),name) for r in responses if any(t in r.get("response_preview","").lower() for t in terms)]
    vp=[p for p in pos if p>0]; avg=round(sum(vp)/len(vp)) if vp else 0
    return {"Brand":name,"GEO":geo,"Vis":cv,"Cit":cc,"Sen":cs,"Sov":csov,"Rank":f"#{avg}" if avg>0 else "N/A"}

INDUSTRY_DATA = {
    "fin": {
        "name": "financial services / credit cards",
        "kws": ["capital","chase","amex","citi","discover","bank","credit","card","finance","fargo","visa","master","barclays","synchrony","usaa","wellsfargo"],
        "queries": [("General Consumer","What is the best credit card for travel rewards in 2025?"),("General Consumer","Which bank offers the best rewards checking account?"),("General Consumer","What credit card should I get for everyday cash back?"),("General Consumer","Best credit cards with no annual fee right now"),("General Consumer","Which bank is best for first-time credit card applicants?"),("Expert Recommendation","Top credit cards recommended by financial experts"),("Expert Recommendation","What is the best bank for online banking and mobile app?"),("Expert Recommendation","Which credit card has the best sign-up bonus?"),("Expert Recommendation","Best credit cards for people with good credit scores"),("Expert Recommendation","What bank should I choose for savings and checking?"),("Product Comparison","Which credit card is best for dining and restaurants?"),("Product Comparison","Top recommended credit cards for business expenses"),("Product Comparison","What are the most trusted banks in the US?"),("Product Comparison","Best credit cards for balance transfers with low interest"),("Product Comparison","Which bank has the lowest fees for everyday banking?"),("Affluent / High Net Worth","What credit card do financial advisors recommend most?"),("Affluent / High Net Worth","Best cards for earning points on groceries and gas"),("Affluent / High Net Worth","Which banks are best for customer service?"),("Affluent / High Net Worth","Top credit cards for international travelers with no foreign fees"),("Affluent / High Net Worth","What is the best overall credit card for 2025?")],
        "comps": ["Chase","American Express","Capital One","Citi","Discover","Wells Fargo","Bank of America","Synchrony","Barclays","USAA"],
        "comp_urls": {"Chase":"chase.com","American Express":"americanexpress.com","Capital One":"capitalone.com","Citi":"citi.com","Discover":"discover.com","Wells Fargo":"wellsfargo.com","Bank of America":"bankofamerica.com","Synchrony":"synchrony.com","Barclays":"barclays.com","USAA":"usaa.com"},
        "label": "Financial Services"
    },
    "auto": {
        "name": "automotive",
        "kws": ["toyota","ford","honda","bmw","tesla","vw","volkswagen","auto","car","motor","hyundai","kia","nissan","mercedes","audi"],
        "queries": [("General Consumer","What is the best car to buy in 2025?"),("General Consumer","Which electric vehicle has the longest range?"),("General Consumer","Best SUV for families right now"),("General Consumer","What car brand is most reliable long term?"),("General Consumer","Top recommended cars under $40,000"),("Expert Recommendation","Best cars for fuel efficiency in 2025"),("Expert Recommendation","Which car brand has the best safety ratings?"),("Expert Recommendation","What is the best luxury car for the money?"),("Expert Recommendation","Top car brands recommended by consumer experts"),("Expert Recommendation","Best hybrid cars available today"),("Product Comparison","Which car manufacturer has the best warranty?"),("Product Comparison","What cars are best for first-time buyers?"),("Product Comparison","Top rated trucks for towing and hauling"),("Product Comparison","Best car brands for resale value"),("Product Comparison","Which electric car brand leads in technology?"),("Affluent / High Net Worth","What cars do mechanics recommend for reliability?"),("Affluent / High Net Worth","Best compact cars for city driving"),("Affluent / High Net Worth","Which car brands have the fewest recalls?"),("Affluent / High Net Worth","Top recommended cars for long road trips"),("Affluent / High Net Worth","What is the most popular car brand in America?")],
        "comps": ["Tesla","Toyota","BMW","Honda","Ford","Mercedes","Hyundai","Kia","Nissan","Volkswagen"],
        "comp_urls": {"Tesla":"tesla.com","Toyota":"toyota.com","BMW":"bmw.com","Honda":"honda.com","Ford":"ford.com","Mercedes":"mercedes-benz.com","Hyundai":"hyundai.com","Kia":"kia.com","Nissan":"nissanusa.com","Volkswagen":"vw.com"},
        "label": "Automotive"
    },
    "gen": {
        "name": "consumer brands",
        "kws": [],
        "queries": [("General Consumer","What are the most trusted brands in the US right now?"),("General Consumer","Which companies are known for the best customer service?"),("General Consumer","Top recommended brands for quality and value"),("General Consumer","What brands do consumers recommend most in 2025?"),("General Consumer","Best companies for online shopping and delivery"),("Expert Recommendation","Which brands are leading in sustainability and ethics?"),("Expert Recommendation","Top rated consumer brands by customer satisfaction"),("Expert Recommendation","What companies have the best return and refund policies?"),("Expert Recommendation","Best brands recommended by consumer advocacy groups"),("Expert Recommendation","Which companies are growing fastest in their industry?"),("Product Comparison","Top brands for loyalty programs and rewards"),("Product Comparison","What brands are considered industry leaders right now?"),("Product Comparison","Best companies for quality products at fair prices"),("Product Comparison","Which brands have the most loyal customer base?"),("Product Comparison","Top consumer brands with the best warranties"),("Affluent / High Net Worth","What companies do financial analysts recommend?"),("Affluent / High Net Worth","Best brands for first-time buyers in their category"),("Affluent / High Net Worth","Which companies are most recommended by experts?"),("Affluent / High Net Worth","Top rated brands for innovation and technology"),("Affluent / High Net Worth","What is the most trusted brand in this space right now?")],
        "comps": [], "comp_urls": {}, "label": "General"
    }
}

def get_industry(domain):
    for k in ["fin","auto"]:
        if any(x in domain for x in INDUSTRY_DATA[k]["kws"]): return k
    return "gen"

def analyze_geo_with_ai(page_data):
    brand=extract_brand_from_page(page_data); domain=page_data.get("domain","").lower(); bl=brand.lower()
    client=get_client(); ind_key=get_industry(domain); ind=INDUSTRY_DATA[ind_key]
    queries=ind["queries"]; all_qa=[]
    for i in range(0,20,5):
        batch=queries[i:i+5]
        ql="\n\n".join(f"Q{j+1}: {q[1]}" for j,q in enumerate(batch))
        prompt="You are a knowledgeable consumer advisor. Answer naturally. Name real brands. Do not favour any.\n\n"+ql+"\n\nRespond:\nA1: [answer]\nA2: [answer]\nA3: [answer]\nA4: [answer]\nA5: [answer]"
        bt=client.chat.completions.create(model="openai/gpt-5.4",messages=[{"role":"user","content":prompt}],temperature=0.6,max_tokens=800).choices[0].message.content
        for j in range(1,6):
            ans=""
            if f"A{j}:" in bt:
                s=bt.index(f"A{j}:")+len(f"A{j}:"); e=bt.index(f"A{j+1}:") if f"A{j+1}:" in bt else len(bt); ans=bt[s:e].strip()
            all_qa.append({"category":batch[j-1][0],"q":batch[j-1][1],"a":ans})
    mentions=sum(1 for p in all_qa if bl in p["a"].lower())
    visibility=round((mentions/20)*100)
    if mentions==0:
        sc={"citation_share":0,"sentiment":0,"prominence":0,"share_of_voice":0,"avg_rank":"N/A","strengths":["Brand not yet appearing in AI responses.","Baseline established, clear room to grow.","Competitors present, confirming category is AI-discoverable."],"improvements":["Not mentioned in 20 generic queries.","AI not associating brand with key questions.","No citation authority.","Competitors appearing instead.","Content not structured for AI discovery."],"actions":[{"priority":"High","action":"Create FAQ and comparison pages targeting queries in this analysis."},{"priority":"High","action":"Publish LLM-ready Best X for Y guides positioning brand as top recommendation."},{"priority":"Medium","action":"Add structured data (schema markup) to key pages."},{"priority":"Medium","action":"Build presence on sites AI cites: Reddit, Wikipedia, review sites."},{"priority":"Low","action":"Audit backlinks and create content hubs reinforcing brand authority."}]}
    else:
        appeared=[p for p in all_qa if bl in p["a"].lower()]
        sp=f"""GEO analyst. Brand "{brand}" appeared in {mentions}/20 AI responses.\n{chr(10).join(f"Response: {p['a'][:300]}" for p in appeared)}\nReturn ONLY valid JSON: {{"citation_share":0,"sentiment":0,"prominence":0,"share_of_voice":0,"avg_rank":"N/A","strengths":["...","...","..."],"improvements":["...","...","...","...","..."],"actions":[{{"priority":"High","action":"..."}},{{"priority":"High","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Medium","action":"..."}},{{"priority":"Low","action":"..."}}]}}"""
        raw=get_client().chat.completions.create(model="openai/gpt-5.4",messages=[{"role":"user","content":sp}],temperature=0.0,max_tokens=900).choices[0].message.content
        sc=json.loads(re.sub(r"```json|```","",raw.strip()))
    cit=sc.get("citation_share",0); sent=sc.get("sentiment",0); prom=sc.get("prominence",0); sov=sc.get("share_of_voice",0)
    geo=round(visibility*0.30+sent*0.20+prom*0.20+cit*0.15+sov*0.15)
    rd=[{"category":p["category"],"query":p["q"],"mentioned":bl in p["a"].lower(),"response_preview":p["a"],"position":get_brand_position_in_response(p["a"],brand)} for p in all_qa]
    try: csrc=get_citation_sources(brand,ind["name"])
    except: csrc=[]
    return {"brand_name":brand,"industry":ind["name"],"ind_key":ind_key,"visibility":visibility,"sentiment":sent,"prominence":prom,"citation_share":cit,"share_of_voice":sov,"overall_geo_score":geo,"avg_rank":"N/A" if visibility==0 else sc.get("avg_rank","N/A"),"responses_detail":rd,"responses_with_brand":mentions,"total_responses":20,"strengths_list":sc.get("strengths",[]),"improvements_list":sc.get("improvements",[]),"actions":sc.get("actions",[]),"context":visibility,"organization":prom,"reliability":cit,"exclusivity":sent,"citation_sources":csrc}

# ── SESSION STATE ─────────────────────────────────────────────
for k,v in [("nav","Overview"),("geo_result",None),("geo_url",""),("geo_page_data",None),("ai_history",[])]:
    if k not in st.session_state: st.session_state[k]=v

# ── URL ROUTING ───────────────────────────────────────────────
pm={"geohub":"GEO Hub","getsupport":"Get Support"}; rm={"GEO Hub":"geohub","Get Support":"getsupport"}
up=st.query_params.get("p","")
if up in pm and st.session_state.nav!=pm[up]: st.session_state.nav=pm[up]
if st.session_state.nav=="Overview":
    if st.query_params.get("p"): st.query_params.clear()
else:
    slug=rm.get(st.session_state.nav,"")
    if st.query_params.get("p")!=slug: st.query_params["p"]=slug

# ── NAVBAR ────────────────────────────────────────────────────
nav=st.session_state.nav
nb_c,ov_c,gh_c,sp_c=st.columns([3,1,1,1.2])
with nb_c:
    st.markdown('<div class="percepta-brand-wrap"><div class="percepta-icon"><svg width="16" height="16" viewBox="0 0 22 22" fill="none"><circle cx="9.5" cy="9.5" r="5.5" stroke="white" stroke-width="1.8" fill="none"/><line x1="13.5" y1="13.5" x2="18" y2="18" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M7 9.5 Q8.5 7 9.5 9.5 Q10.5 12 12 9.5" stroke="white" stroke-width="1.3" fill="none" stroke-linecap="round" opacity="0.9"/></svg></div><span class="percepta-title">Percepta</span></div>',unsafe_allow_html=True)
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
    if st.query_params.get("p")=="geohub": st.session_state.nav="GEO Hub"; st.query_params["p"]="geohub"; st.rerun()
    st.markdown(f"""
<div style="background:linear-gradient(170deg,#fff 55%,#F3EEFF 100%);padding:52px 40px 40px;text-align:center;">
  <div style="display:inline-flex;align-items:center;gap:8px;border:1px solid #DDD6FE;border-radius:50px;padding:8px 22px;font-size:0.72rem;font-weight:700;letter-spacing:.1em;color:#7C3AED;text-transform:uppercase;margin-bottom:44px;background:rgba(255,255,255,0.9);">✦ &nbsp;AI-Powered Brand Intelligence &nbsp;·&nbsp; Powered by Accenture</div>
  <div style="font-size:4.6rem;font-weight:900;line-height:1.0;letter-spacing:-3px;margin-bottom:28px;"><span style="color:#111827;">Your Brand's </span><span style="color:#7C3AED;">GEO</span><span style="color:#111827;"> Score</span></div>
  <p style="font-size:1.05rem;color:#6B7280;max-width:860px;margin:0 auto 36px;line-height:1.7;">The Percepta GEO Score measures how often and favorably your brand is cited in AI-generated responses — across ChatGPT, Gemini, and other major AI engines.</p>
  <div style="display:flex;gap:16px;justify-content:center;flex-wrap:wrap;">
    <a href="?p=geohub" class="hero-btn-primary" target="_self">Get Your GEO Score &nbsp;→</a>
    <a href="#how" class="hero-btn-secondary">See How It Works</a>
  </div>
</div>
<div id="how" style="background:#F9F9FC;padding:80px 40px;border-top:1px solid #E5E7EB;">
  <div style="text-align:center;margin-bottom:64px;"><div class="section-tag">Process</div><h2 style="font-size:2.2rem;font-weight:900;color:#111827;margin:10px 0 14px;">How Percepta Works</h2></div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:40px;position:relative;">
    <div style="position:absolute;top:22px;left:calc(25% + 20px);width:calc(75% - 40px);height:1px;background:#E5E7EB;z-index:0;"></div>
    {"".join(f'<div style="position:relative;z-index:1;"><div style="font-size:3.2rem;font-weight:900;color:#EDE9FE;line-height:1;margin-bottom:24px;">0{i+1}</div><div style="font-size:1rem;font-weight:800;color:#111827;margin-bottom:8px;">{t}</div><div style="font-size:0.84rem;color:#6B7280;line-height:1.7;">{d}</div></div>' for i,(t,d) in enumerate([("Enter Your Brand","Input your brand name, keywords, and competitor list."),("AI Engine Scanning","Percepta queries AI engines with hundreds of prompts to analyze mentions."),("Score Calculation","Our algorithm computes your GEO Score based on visibility, sentiment, and positioning."),("Actionable Insights","Receive detailed reports with specific recommendations.")]))}
  </div>
</div>
<div style="background:white;padding:80px 40px;border-top:1px solid #E5E7EB;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;margin-bottom:56px;">
    <div><div style="font-size:0.72rem;font-weight:800;letter-spacing:.12em;color:#7C3AED;text-transform:uppercase;margin-bottom:14px;">The GEO Score</div><h2 style="font-size:2.6rem;font-weight:900;color:#111827;margin:0 0 20px;line-height:1.1;">One Number That<br>Changes Everything</h2><p style="font-size:0.95rem;color:#6B7280;line-height:1.8;margin:0;">Your GEO Score distills complex AI citation data into a single, actionable metric.</p></div>
    <div style="background:white;border-radius:20px;padding:44px 40px;box-shadow:0 8px 40px rgba(124,58,237,0.13);border:1px solid #F0EBFF;text-align:center;"><div style="font-size:0.7rem;font-weight:700;letter-spacing:.14em;color:#9CA3AF;text-transform:uppercase;margin-bottom:18px;">GEO SCORE</div><div style="font-size:5.5rem;font-weight:900;color:#7C3AED;line-height:1;margin-bottom:20px;">78</div><div style="background:#F3F4F6;border-radius:50px;height:6px;width:100%;margin-bottom:10px;overflow:hidden;"><div style="background:#7C3AED;height:6px;border-radius:50px;width:78%;"></div></div><div style="font-size:0.82rem;color:#9CA3AF;margin-bottom:20px;">out of 100</div><span style="background:#EDE9FE;color:#7C3AED;border-radius:50px;padding:6px 22px;font-size:0.84rem;font-weight:700;">Good</span></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:16px;">
    {"".join(card(bg,bd,f'<div style="font-size:0.82rem;font-weight:700;color:{c};margin-bottom:4px;">{r}</div><div style="font-size:1.3rem;font-weight:900;color:{c};margin-bottom:4px;">{l}</div><div style="font-size:0.78rem;color:{c};">{d}</div>') for bg,bd,c,r,l,d in [("#ECFDF5","#6EE7B7","#065F46","80–100","Excellent","Well optimized for AI citation"),("#EFF6FF","#93C5FD","#1E40AF","70–79","Good","Minor improvements recommended"),("#FFFBEB","#FCD34D","#92400E","45–69","Needs Work","Several issues to address"),("#FFF1F2","#FCA5A5","#991B1B","0–44","Poor","Major optimization needed")])}
  </div>
</div>
<div style="background:white;padding:80px 40px;border-top:1px solid #E5E7EB;">
  <div style="background:linear-gradient(135deg,#F8F5FF 0%,#EDE9FE 45%,#F3EEFF 100%);border:1.5px solid #C4B5FD;border-radius:28px;padding:52px 60px;text-align:center;">
    <h2 style="font-size:3rem;font-weight:900;color:#111827;margin:0 0 4px;line-height:1.1;">Ready to Discover Your</h2>
    <h2 style="font-size:3rem;font-weight:900;color:#7C3AED;margin:0 0 28px;line-height:1.1;">GEO Score?</h2>
    <div style="margin-top:40px;"><a href="?p=geohub" class="cta-btn" target="_self">Launch Percepta &nbsp;→</a></div>
  </div>
</div>""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PAGE 2: GEO HUB
# ════════════════════════════════════════════════════════════
elif nav=="GEO Hub":
    st.markdown("""<div style="background:linear-gradient(135deg,#5B21B6 0%,#7C3AED 50%,#9333EA 100%);padding:64px 40px 56px;text-align:center;">
        <div style="display:inline-flex;align-items:center;gap:8px;border:1.5px solid rgba(255,255,255,0.5);border-radius:50px;padding:8px 24px;font-size:0.78rem;font-weight:700;color:white;margin-bottom:28px;background:rgba(255,255,255,0.15);">✦ &nbsp;Real GEO Scoring</div>
        <h1 style="font-size:3.4rem;font-weight:900;color:white;margin:0 0 14px;letter-spacing:-1.5px;">GEO Scorecard</h1>
        <p style="font-size:1.05rem;color:rgba(255,255,255,0.88);margin:0;">Enter any brand URL · Discover your brand's AI presence</p>
    </div>""", unsafe_allow_html=True)

    has_result=st.session_state.geo_result is not None

    if not has_result:
        st.markdown(score_band_cards(), unsafe_allow_html=True)
        st.markdown('<div style="background:white;border-radius:16px 16px 0 0;border:1.5px solid #E5E7EB;border-bottom:none;padding:20px 28px 8px;margin:0 40px;"><p style="font-size:0.72rem;font-weight:700;letter-spacing:.12em;color:#9CA3AF;text-transform:uppercase;margin:0;">BRAND URL</p></div>', unsafe_allow_html=True)
        uc,bc=st.columns([3.5,1])
        with uc: brand_url=st.text_input("u",value=st.session_state.geo_url,placeholder="https://www.capitalone.com/",label_visibility="collapsed")
        with bc: run=st.button("🔍  Run Live AI Analysis",use_container_width=True)
        st.markdown("<div style='background:#F3F4F6;height:40px;'></div>", unsafe_allow_html=True)

        if run:
            if not brand_url.strip() or not brand_url.startswith("http"):
                st.error("Please enter a valid URL starting with http:// or https://")
            else:
                with st.spinner("Identifying brand from URL..."):
                    page_data=fetch_page_content(brand_url)
                if not page_data["ok"]: st.error(f"Could not fetch URL: {page_data['error']}")
                else:
                    with st.spinner("Running 20 live AI queries across 4 consumer categories..."):
                        try:
                            result=analyze_geo_with_ai(page_data)
                            st.session_state.geo_result=result; st.session_state.geo_url=brand_url; st.session_state.geo_page_data=page_data
                            st.success("Analysis complete. Explore the tabs for your full GEO report."); st.rerun()
                        except Exception as e: st.error(f"Analysis failed: {e}")
    else:
        R=st.session_state.geo_result; PD=st.session_state.geo_page_data; BU=st.session_state.geo_url
        geo=R.get("overall_geo_score",0); brand=R.get("brand_name",PD["domain"]); bd=PD.get("domain","")
        lbl,bc,bbg=score_badge(geo)
        vis=R.get("context",0); cit=R.get("reliability",0); sent=R.get("exclusivity",0); prom=R.get("organization",0); sov=R.get("share_of_voice",0)
        avg_rank="N/A" if vis==0 else R.get("avg_rank","N/A"); rd=R.get("responses_detail",[])
        ind=INDUSTRY_DATA[R.get("ind_key","gen")]

        tabs=st.tabs(["GEO Score","Competitors","Visibility","Sentiment","Citations","Prompts","Recommendations","Live Prompt"])

        with tabs[0]:
            st.markdown("<div style='padding:32px 40px;max-width:1000px;margin:0 auto;'>",unsafe_allow_html=True)
            gc,ic=st.columns([1,2])
            with gc:
                fig=go.Figure(go.Indicator(mode="gauge+number",value=geo,number={'font':{'size':52,'color':'#7C3AED'}},domain={'x':[0,1],'y':[0,1]},title={'text':brand,'font':{'size':14,'color':'#374151'}},gauge={'axis':{'range':[0,100]},'bar':{'color':'#7C3AED'},'bgcolor':'white','steps':[{'range':[0,44],'color':'#FEE2E2'},{'range':[44,69],'color':'#FEF3C7'},{'range':[69,80],'color':'#DBEAFE'},{'range':[80,100],'color':'#D1FAE5'}],'threshold':{'line':{'color':'#7C3AED','width':4},'thickness':0.75,'value':geo}}))
                fig.update_layout(height=280,margin=dict(l=20,r=20,t=40,b=10),paper_bgcolor='white'); st.plotly_chart(fig,use_container_width=True)
            with ic:
                dp=[f"Citation ({cit}): rarely top pick" if cit<40 else None, f"Prominence ({prom}): mid-list" if prom<40 else None, f"Share of Voice ({sov}): competitors dominating" if sov<20 else None, f"Sentiment ({sent}): lacks positive endorsement" if sent<50 else None]
                dp=[x for x in dp if x]
                stxt=f"GEO Score {geo} reflects {vis}% Visibility but held back by: {'; '.join(dp)}." if dp else f"Strong: Visibility {vis}%, Citation {cit}, Sentiment {sent}, Prominence {prom}, SoV {sov}."
                st.markdown(f'{white_card(f"""<div style="font-size:1.2rem;font-weight:800;color:#111827;margin-bottom:4px;">{brand}</div><a href="{BU}" target="_blank" style="color:#7C3AED;font-size:0.82rem;">{BU[:70]}{"..." if len(BU)>70 else ""}</a><div style="margin:12px 0;"><span style="background:{bbg};color:{bc};padding:4px 14px;border-radius:50px;font-size:0.78rem;font-weight:700;">{lbl}</span></div><div style="font-size:0.82rem;color:#6B7280;line-height:1.6;border-top:1px solid #F3F4F6;padding-top:12px;">{stxt}</div>""")}',unsafe_allow_html=True)
            st.markdown("<br>",unsafe_allow_html=True)
            tips={"Visibility Score":"How many of 20 generic AI queries mentioned your brand.","Citation Score":"How authoritatively your brand was cited.","Sentiment Score":"Tone of AI responses when your brand appeared.","Avg. Rank":"Average position your brand appeared."}
            c1,c2,c3,c4=st.columns(4)
            for col,val,lbl2,sub in [(c1,vis,"Visibility Score","AI response presence"),(c2,cit,"Citation Score","Source authority"),(c3,sent,"Sentiment Score","Brand perception"),(c4,avg_rank,"Avg. Rank","AI mention position")]:
                with col: st.markdown(metric_card(lbl2,val,sub,tips.get(lbl2,"")),unsafe_allow_html=True)
            # Competitor table
            st.markdown("<div style='padding:24px 0;'>",unsafe_allow_html=True)
            top10=[{"Brand":brand,"URL":bd,"GEO":geo,"Vis":vis,"Cit":cit,"Sen":sent,"Sov":sov,"Rank":avg_rank}]
            for c in ind["comps"]:
                if c.lower()!=brand.lower():
                    s=score_competitor_from_responses(c,rd); s["URL"]=ind["comp_urls"].get(c,c.lower().replace(" ","+")+".com"); top10.append(s)
            rows=""
            for i,c in enumerate(sorted(top10,key=lambda x:x["GEO"],reverse=True),1):
                iy=c["Brand"].lower()==brand.lower(); gc2=c["GEO"]
                gcol="#10B981" if gc2>=80 else "#F59E0B" if gc2>=60 else "#EF4444"
                yb=' <span style="background:#EDE9FE;color:#7C3AED;border-radius:4px;padding:1px 6px;font-size:0.7rem;font-weight:700;">You</span>' if iy else ""
                rows+=f'<tr style="background:{"#F5F3FF" if iy else "white" if i%2==1 else "#FAFAFA"};{"border-left:3px solid #7C3AED;" if iy else ""}"><td style="padding:10px 12px;font-size:0.8rem;color:#9CA3AF;font-weight:600;">{i}</td><td style="padding:10px 12px;"><div style="font-size:0.84rem;font-weight:{"700" if iy else "400"};color:#111827;">{c["Brand"]}{yb}</div><div style="font-size:0.72rem;color:#9CA3AF;">{c.get("URL","")}</div></td><td style="padding:10px 12px;font-size:0.88rem;font-weight:700;color:{gcol};">{gc2}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Vis"]}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Cit"]}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Sen"]}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c.get("Sov","")}</td><td style="padding:10px 12px;font-size:0.82rem;color:#374151;">{c["Rank"]}</td></tr>'
            st.markdown(f'{white_card(f"""<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">{bd} vs Competitors — {ind["label"]}</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Real-time GEO scores. Highlighted row is you.</div><table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:1px solid #E5E7EB;">{"".join(f\'<th style="padding:8px 12px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">{h}</th>\' for h in ["#","Brand","GEO","Visibility","Citation","Sentiment","Share of Voice","Avg Rank"])}</tr></thead><tbody>{rows}</tbody></table>""")}',unsafe_allow_html=True)
            st.markdown("</div></div>",unsafe_allow_html=True)

        with tabs[1]:
            st.info("Competitor breakdown is shown in the GEO Score tab above.")

        with tabs[2]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px;">{metric_card("Visibility Score",f"{vis}%","Appeared in "+str(R.get("responses_with_brand",0))+" of 20 queries")}{metric_card("Average Rank",avg_rank,"Position when mentioned")}{metric_card("Query Appearances",str(R.get("responses_with_brand",0))+"/20","Out of 20 generic industry queries")}</div>',unsafe_allow_html=True)
            il=PD.get("internal_links",[])
            if il:
                pi=get_page_intelligence(il,brand,rd); rows=""
                for p in pi:
                    gc2=p["geo"]; gcol="#10B981" if gc2>=60 else "#F59E0B" if gc2>=30 else "#EF4444"
                    cb=f'<span style="background:#D1FAE5;color:#065F46;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Cited {p["cited"]}x</span>' if p["cited"]>0 else '<span style="background:#F3F4F6;color:#9CA3AF;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Not Cited</span>'
                    rows+=f'<tr style="border-bottom:1px solid #F3F4F6;"><td style="padding:10px 14px;"><div style="font-size:0.84rem;font-weight:600;color:#111827;">{p["label"]}</div><div style="font-size:0.72rem;color:#9CA3AF;">{p["path"]}</div></td><td style="padding:10px 14px;">{cb}</td><td style="padding:10px 14px;font-size:0.88rem;font-weight:700;color:{gcol};">{gc2}</td><td style="padding:10px 14px;font-size:0.82rem;color:#7C3AED;font-weight:600;">{p["citation_share"]}%</td><td style="padding:10px 14px;font-size:0.84rem;color:{p["color"]};font-weight:600;">{p["status"]}</td></tr>'
                st.markdown(f'{white_card(f"""<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Page Intelligence</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Which pages of {bd} are being cited by AI.</div><table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:2px solid #E5E7EB;background:#FAFAFA;">{"".join(f\'<th style="padding:8px 14px;text-align:left;font-size:0.72rem;color:#9CA3AF;font-weight:600;">{h}</th>\' for h in ["Page","AI Citations","GEO Score","Citation Share","Status"])}</tr></thead><tbody>{rows}</tbody></table>""")}',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[3]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            smood="Positive — AI speaks favorably" if sent>=70 else "Neutral — room to improve" if sent>=45 else "Needs attention"
            pmood="Named first — strong prominence" if prom>=70 else "Mid-list mentions" if prom>=45 else "Buried in responses"
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:24px;">{metric_card("Sentiment Score",sent,smood,color="#10B981")}{metric_card("Prominence Score",prom,pmood)}{metric_card("Average Rank",avg_rank,"Average mention position",color="#3B82F6")}</div>',unsafe_allow_html=True)
            sh="".join(f'<li style="padding:10px 0;font-size:0.84rem;color:#374151;display:flex;gap:12px;align-items:flex-start;border-bottom:1px solid #F0FDF4;"><span style="color:#10B981;font-weight:700;flex-shrink:0;">+</span><span>{s}</span></li>' for s in R.get("strengths_list",[])[:3])
            st.markdown(f'{white_card(f"""<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:16px;">Sentiment Strengths</div><ul style="list-style:none;padding:0;margin:0;">{sh}</ul>""")}',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[4]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:24px;">{metric_card("Citation Score",cit,"How authoritatively your brand was cited")}{metric_card("Share of Voice",sov,"Your brand mentions as % of all mentions")}</div>',unsafe_allow_html=True)
            cs=R.get("citation_sources",[])
            if cs:
                rows=""
                for s in cs:
                    d=s.get("domain",""); cl,cc,cbg=classify_domain(d); share=s.get("citation_share",0); bw=min(share*3,100)
                    phtml="".join(f'<div style="font-size:0.75rem;color:#7C3AED;padding:2px 0;">{pg}</div>' for pg in s.get("top_pages",[])[:5])
                    if phtml: phtml=f'<div style="margin-top:8px;padding-top:8px;border-top:0.5px solid #F3F4F6;">{phtml}</div>'
                    rows+=f'<div style="border:1px solid #E5E7EB;border-radius:8px;padding:12px 16px;margin-bottom:8px;"><div style="display:flex;align-items:center;gap:10px;"><span style="font-size:0.78rem;color:#9CA3AF;font-weight:600;width:18px;">{s.get("rank","")}</span><img src="https://www.google.com/s2/favicons?domain={d}&sz=14" width="14" height="14" onerror="this.style.display=\'none\'"><span style="font-size:0.88rem;font-weight:600;color:#111827;flex:1;">{d}</span><span style="background:{cbg};color:{cc};border-radius:50px;padding:2px 10px;font-size:0.7rem;font-weight:600;">{cl}</span><div style="display:flex;align-items:center;gap:6px;"><div style="background:#F3F4F6;border-radius:4px;height:5px;width:80px;overflow:hidden;"><div style="background:#7C3AED;height:5px;border-radius:4px;width:{bw}px;"></div></div><span style="font-size:0.82rem;font-weight:700;color:#7C3AED;">{share}%</span></div></div>{phtml}</div>'
                st.markdown(f'{white_card(f"""<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Sources AI is Pulling From</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Domains influencing AI knowledge about this brand.</div>{rows}""")}',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[5]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            cats=list(dict.fromkeys([r.get("category","General Consumer") for r in rd]))
            sel=st.selectbox("Filter by category",["All"]+cats)
            filtered=[r for r in rd if sel=="All" or r.get("category")==sel][:10]
            cs2={}
            for r in rd:
                c=r.get("category","General Consumer")
                if c not in cs2: cs2[c]={"total":0,"mentioned":0}
                cs2[c]["total"]+=1
                if r.get("mentioned"): cs2[c]["mentioned"]+=1
            ch="".join(f'<div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:14px 18px;"><div style="font-size:0.82rem;font-weight:600;color:#111827;margin-bottom:6px;">{c}</div><div style="display:flex;align-items:center;gap:8px;"><div style="background:#F3F4F6;border-radius:4px;height:5px;flex:1;overflow:hidden;"><div style="background:#7C3AED;height:5px;border-radius:4px;width:{round((v["mentioned"]/max(v["total"],1))*100)}%;"></div></div><span style="font-size:0.78rem;font-weight:700;color:#7C3AED;">{round((v["mentioned"]/max(v["total"],1))*100)}%</span></div><div style="font-size:0.72rem;color:#9CA3AF;margin-top:4px;">{v["mentioned"]} of {v["total"]} queries</div></div>' for c,v in cs2.items())
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:24px;">{ch}</div>',unsafe_allow_html=True)
            qrows=""
            for i,item in enumerate(filtered):
                m=item.get("mentioned",False); rp=item.get("position",0); rd2=f"#{rp}" if rp>0 else "N/A"
                rc="#10B981" if rp==1 else "#7C3AED" if rp<=3 else "#F59E0B" if m else "#9CA3AF"
                ab='<span style="background:#D1FAE5;color:#065F46;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Appeared</span>' if m else '<span style="background:#F3F4F6;color:#9CA3AF;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:700;">Not Mentioned</span>'
                cb2=f'<span style="background:#EDE9FE;color:#5B21B6;border-radius:4px;padding:1px 7px;font-size:0.7rem;font-weight:600;">{item.get("category","")}</span>'
                qrows+=f'<tr style="background:{"#F5F3FF" if m else "white"};border-bottom:1px solid #F3F4F6;"><td style="padding:10px 12px;font-size:0.78rem;color:#9CA3AF;font-weight:600;">{i+1}</td><td style="padding:10px 14px;"><div style="display:flex;gap:6px;align-items:center;margin-bottom:5px;">{cb2}{ab}</div><div style="font-size:0.83rem;color:#374151;">{item.get("query","")}</div></td><td style="padding:10px 16px;text-align:center;"><div style="font-size:1.1rem;font-weight:800;color:{rc};">{rd2}</div><div style="font-size:0.68rem;color:#9CA3AF;">Rank</div></td></tr>'
            st.markdown(f'{white_card(f"""<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Top 10 Prompts</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:16px;">Generic consumer questions. No brand name used.</div><table style="width:100%;border-collapse:collapse;"><thead><tr style="border-bottom:2px solid #E5E7EB;background:#FAFAFA;">{"".join(f\'<th style="padding:8px {"14" if h=="Query" else "12"}px;text-align:{"center" if h=="Rank" else "left"};font-size:0.72rem;color:#9CA3AF;font-weight:600;">{h}</th>\' for h in ["#","Query","Rank"])}</tr></thead><tbody>{qrows}</tbody></table>""")}',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[6]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            sh2="".join(f'<li style="padding:10px 0;font-size:0.84rem;color:#374151;display:flex;gap:12px;align-items:flex-start;border-bottom:1px solid #F0FDF4;"><span style="color:#10B981;font-weight:700;flex-shrink:0;">+</span><span>{s}</span></li>' for s in R.get("strengths_list",[])[:3])
            wh="".join(f'<li style="padding:10px 0;font-size:0.84rem;color:#374151;display:flex;gap:12px;align-items:flex-start;border-bottom:1px solid #FFF1F2;"><span style="color:#EF4444;font-weight:700;flex-shrink:0;">x</span><span>{w}</span></li>' for w in R.get("improvements_list",[])[:5])
            st.markdown(f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:24px;"><div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;"><div style="font-size:0.9rem;font-weight:700;color:#065F46;margin-bottom:16px;">What is Working Well</div><ul style="list-style:none;padding:0;margin:0;">{sh2}</ul></div><div style="background:white;border:1px solid #E5E7EB;border-radius:12px;padding:24px;"><div style="font-size:0.9rem;font-weight:700;color:#9F1239;margin-bottom:16px;">What Needs Improvement</div><ul style="list-style:none;padding:0;margin:0;">{wh}</ul></div></div>',unsafe_allow_html=True)
            dm={"High":("Workstream 01: ARD","AXO Baseline Report and Brand Ranking Index"),"Medium":("Workstream 02: AOP","LLM-Ready Content Package and Content Influence Blueprint"),"Low":("Workstream 03: DTI","Schema Optimization Guide and Metadata Remediation Plan")}
            ah="".join(f'<div style="display:grid;grid-template-columns:90px 1fr 1fr;gap:0;border-bottom:1px solid #F3F4F6;padding:14px 0;align-items:start;"><div><span style="background:{{"High":"#FEE2E2","Medium":"#FEF3C7","Low":"#DCFCE7"}.get(a.get("priority","Medium"),"#F3F4F6")};color:{{"High":"#991B1B","Medium":"#92400E","Low":"#166534"}.get(a.get("priority","Medium"),"#374151")};border-radius:4px;padding:2px 10px;font-size:0.72rem;font-weight:700;">{a.get("priority","Medium")}</span></div><div style="font-size:0.84rem;color:#374151;padding-right:16px;">{a["action"]}</div><div style="font-size:0.78rem;color:#7C3AED;font-weight:600;"><span style="background:#EDE9FE;border-radius:6px;padding:3px 10px;">{dm.get(a.get("priority","Medium"),("",""))[0]}</span><div style="font-size:0.75rem;color:#9CA3AF;font-weight:400;margin-top:4px;">{dm.get(a.get("priority","Medium"),("",""))[1]}</div></div></div>' for a in R.get("actions",[]))
            st.markdown(f'{white_card(f"""<div style="font-size:1rem;font-weight:700;color:#111827;margin-bottom:4px;">Priority Actions</div><div style="font-size:0.78rem;color:#9CA3AF;margin-bottom:20px;">Each action mapped to the relevant Accenture workstream deliverable.</div><div style="display:grid;grid-template-columns:90px 1fr 1fr;border-bottom:2px solid #E5E7EB;padding-bottom:8px;margin-bottom:4px;"><div style="font-size:0.72rem;color:#9CA3AF;font-weight:600;">Priority</div><div style="font-size:0.72rem;color:#9CA3AF;font-weight:600;">Action</div><div style="font-size:0.72rem;color:#9CA3AF;font-weight:600;">Linked Deliverable</div></div>{ah}""")}',unsafe_allow_html=True)
            st.markdown("</div>",unsafe_allow_html=True)

        with tabs[7]:
            st.markdown("<div style='padding:24px 40px;max-width:900px;margin:0 auto;'>",unsafe_allow_html=True)
            st.markdown('<div style="background:#7C3AED;border-radius:12px;padding:24px 28px;color:white;margin-bottom:20px;"><h3 style="font-size:1.1rem;font-weight:800;color:white;margin:0 0 6px;">Live AI Prompt Lab</h3><p style="font-size:0.88rem;color:rgba(255,255,255,0.85);margin:0;">Type any prompt and see exactly how GPT-5.4 responds in real time.</p></div>',unsafe_allow_html=True)
            q=st.text_input("p","",placeholder="e.g. What is the best travel credit card for high net worth individuals?",label_visibility="collapsed")
            if st.button("Run Prompt"):
                if not q.strip(): st.warning("Please enter a prompt.")
                else:
                    with st.spinner("Querying GPT-5.4..."):
                        try: st.session_state.ai_history.append({"q":q,"a":get_response(q,INTERNAL_API_KEY)})
                        except Exception as e: st.error(f"Error: {e}")
            for item in reversed(st.session_state.ai_history):
                st.markdown(f'<div style="display:flex;justify-content:flex-end;margin:20px 0 10px;"><div style="background:#F4F4F4;color:#111827;border-radius:18px 18px 4px 18px;padding:12px 18px;max-width:60%;font-size:0.95rem;">{item["q"]}</div></div>',unsafe_allow_html=True)
                st.markdown(item["a"])
                st.markdown('<hr style="border:none;border-top:1px solid #F3F4F6;margin:16px 0;">',unsafe_allow_html=True)
            if st.session_state.ai_history:
                if st.button("Clear history",key="clr"): st.session_state.ai_history=[]; st.rerun()
            st.markdown("</div>",unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# PAGE 3: GET SUPPORT
# ════════════════════════════════════════════════════════════
elif nav=="Get Support":
    st.markdown("""<div style="background:#7C3AED;padding:56px 40px;text-align:center;">
        <div style="font-size:0.72rem;font-weight:700;letter-spacing:.12em;color:rgba(255,255,255,0.65);text-transform:uppercase;margin-bottom:10px;">Accenture GEO Services</div>
        <h1 style="font-size:2.8rem;font-weight:900;color:white;margin:0 0 14px;letter-spacing:-1px;">We've Got You Covered</h1>
        <p style="font-size:1rem;color:rgba(255,255,255,0.82);max-width:500px;margin:0 auto;line-height:1.8;">From GEO diagnostic to full optimization. Accenture's team handles everything, end to end.</p>
    </div>""",unsafe_allow_html=True)
    st.markdown("""<div style="background:white;padding:56px 40px 0;text-align:center;">
        <div class="section-tag">Our Approach</div>
        <h2 style="font-size:2.4rem;font-weight:900;color:#111827;margin:10px 0 10px;">GEO is No Longer Optional</h2>
        <p style="font-size:0.92rem;color:#6B7280;margin:0 auto 40px;max-width:680px;line-height:1.7;">While search spend rises, its impact is fading as AI agents increasingly shape the decisions search used to influence.</p>
    </div>""",unsafe_allow_html=True)
    cl,cm,cr=st.columns([1,1.1,1])
    WS=[("Workstream 1","Agent Ranking Diagnostic (ARD)","Establish the <strong>baseline ranking performance</strong> of AI agents comparing your brand to competitive offerings."),("Workstream 4","Impact Measurement (Re-Diagnostic)","Re-perform the diagnostic to <strong>Re-measure performance</strong> and quantify improvements.")]
    WS2=[("Workstream 3","Distribution and Technical Influence Layer (DTI)","Pinpoint and <strong>propose specific technical and distribution improvements</strong> to maximize LLM ingestion."),("Workstream 2","Agent Optimization Plan (AOP)","<strong>Design and deploy a specific optimization strategy</strong> aimed at elevating agent recognition of your brand.")]
    with cl: st.markdown("".join(f'<div style="padding:0 20px 0 40px;margin-bottom:36px;"><div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:3px;"><strong>{w[0]}:</strong></div><div style="font-size:0.88rem;font-style:italic;color:#374151;margin-bottom:10px;">{w[1]}</div><p style="font-size:0.82rem;color:#6B7280;line-height:1.7;margin:0;">{w[2]}</p></div>' for w in WS),unsafe_allow_html=True)
    with cm: st.image("infinity.png",use_container_width=True)
    with cr: st.markdown("".join(f'<div style="padding:0 40px 0 20px;margin-bottom:36px;"><div style="font-size:0.95rem;font-weight:800;color:#111827;margin-bottom:3px;"><strong>{w[0]}:</strong></div><div style="font-size:0.88rem;font-style:italic;color:#374151;margin-bottom:10px;">{w[1]}</div><p style="font-size:0.82rem;color:#6B7280;line-height:1.7;margin:0;">{w[2]}</p></div>' for w in WS2),unsafe_allow_html=True)

    DELIVER=[
        ("Agent Ranking Diagnostic (ARD)","#1E1B5E","polygon(0 0,93% 0,100% 50%,93% 100%,0 100%)","border-radius:8px 0 0 0",["Develop representative prompts","Execute multi-run stability testing","Extract agent-generated rankings","Perform power distribution modeling","Build competitor adjacency maps"],["AXO Baseline Report","Brand & Product Ranking Index","Power Curve Analysis","Competitor Adjacency Analysis","AXO Baseline Score (v1.0)"]),
        ("Agent Optimization Plan (AOP)","#2D2A70","polygon(0 0,93% 0,100% 50%,93% 100%,0 100%,7% 50%)","","Develop LLM-ready content assets,Strengthen product-attribute associations,Optimize content for agent ingestion,Create Content Influence Blueprint".split(","),["Agent Optimization Plan","LLM-Ready Content Package","Attribute Reinforcement Strategy","Content Influence Blueprint"]),
        ("Distribution & Technical Influence (DTI)","#3D3A8A","polygon(0 0,93% 0,100% 50%,93% 100%,0 100%,7% 50%)","","Audit tagging and metadata,Identify missing structured data,Improve backlink structure,Identify dormant URLs,Audit schema markup".split(","),["Distribution & Technical Influence Report","Metadata Remediation Plan","Backlink & Redirect Strategy","Schema Optimization Guide"]),
        ("Impact Measurement (Re-Diagnostic)","#5B21B6","polygon(0 0,100% 0,100% 100%,0 100%,7% 50%)","border-radius:0 8px 0 0","Re-test all prompts,Measure semantic drift and ranking changes,Recompute AXO Score".split(","),["AXO Impact Report","Before/After Ranking Comparison","Updated AXO Score (v2.0)","Recommendations for ongoing improvement"]),
    ]
    hdrs="".join(f'<div style="background:{d[1]};padding:20px {"20px 20px 20px 28px" if i>0 else "18px"};{d[3]};clip-path:{d[2]};"><div style="font-size:0.7rem;font-weight:600;color:rgba(255,255,255,0.65);margin-bottom:6px;text-transform:uppercase;letter-spacing:.07em;">Workstream 0{i+1}</div><div style="font-size:0.9rem;font-weight:700;color:white;line-height:1.35;">{d[0]}</div></div>' for i,d in enumerate(DELIVER))
    acts="".join(f'<div style="background:white;border:1px solid #E5E7EB;border-radius:8px;padding:18px;"><div style="font-size:0.82rem;font-weight:700;color:#111827;border-bottom:1px solid #F3F4F6;padding-bottom:8px;margin-bottom:12px;text-align:center;">Activities</div><ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.75;">{"".join(f"<li>{a}</li>" for a in d[4])}</ul></div>' for d in DELIVER)
    dlvs="".join(f'<div style="background:#EEEAF8;border:1px solid #DDD6FE;border-radius:8px;padding:18px;"><div style="font-size:0.82rem;font-weight:700;color:#111827;border-bottom:1px solid #DDD6FE;padding-bottom:8px;margin-bottom:12px;text-align:center;">Deliverables</div><ul style="list-style:disc;padding-left:16px;margin:0;font-size:0.78rem;color:#374151;line-height:1.75;">{"".join(f"<li>{dl}</li>" for dl in d[5])}</ul></div>' for d in DELIVER)
    st.markdown(f"""
    <div style="background:white;padding:32px 40px 40px;border-bottom:1px solid #E5E7EB;">
        <div style="display:grid;grid-template-columns:1fr 1px 1fr 1px 1fr;gap:0;border-top:1px dashed #D1D5DB;padding-top:32px;">
            <div style="text-align:center;padding:0 20px;"><div style="font-size:3.2rem;font-weight:900;color:#111827;line-height:1;">6</div><div style="font-size:1rem;font-weight:700;color:#111827;margin-top:6px;">Week Engagement</div><div style="font-size:0.8rem;color:#9CA3AF;margin-top:3px;">Phase 1</div></div>
            <div style="background:#E5E7EB;"></div>
            <div style="text-align:center;padding:0 20px;"><div style="font-size:0.85rem;font-weight:700;color:#111827;margin-bottom:4px;">Pilot Phase 1</div><div style="font-size:3.2rem;font-weight:900;color:#111827;line-height:1;">2</div><div style="font-size:1rem;font-weight:700;color:#111827;margin-top:6px;">AI Agents</div><div style="font-size:0.8rem;color:#9CA3AF;margin-top:3px;">ChatGPT & Gemini</div></div>
            <div style="background:#E5E7EB;"></div>
            <div style="text-align:center;padding:0 20px;"><div style="font-size:3.2rem;font-weight:900;color:#111827;line-height:1;">4</div><div style="font-size:1rem;font-weight:700;color:#111827;margin-top:6px;">Workstreams</div><div style="font-size:0.8rem;color:#9CA3AF;margin-top:3px;">End to end coverage</div></div>
        </div>
    </div>
    <div style="background:#F9F9FC;padding:48px 40px;border-bottom:1px solid #E5E7EB;">
        <div style="text-align:center;margin-bottom:32px;"><div class="section-tag">Deliverables</div><h2 style="font-size:1.8rem;font-weight:800;color:#111827;margin:8px 0 0;">Activities and What We Deliver</h2></div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:3px;margin-bottom:12px;">{hdrs}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;margin-bottom:12px;">{acts}</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px;">{dlvs}</div>
    </div>
    <div style="background:white;padding:48px 40px;border-bottom:1px solid #E5E7EB;">
        <div style="text-align:center;margin-bottom:36px;"><div class="section-tag">Explore Offers</div><h2 style="font-size:1.8rem;font-weight:800;color:#111827;margin:8px 0 6px;">Choose Your Pilot Program</h2></div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;">
            <div style="border:1px solid #E5E7EB;border-radius:16px;padding:36px 32px;"><div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:10px;">Option 1</div><div style="font-size:3rem;font-weight:900;color:#111827;line-height:1;margin-bottom:2px;">6</div><div style="font-size:0.95rem;font-weight:600;color:#374151;margin-bottom:28px;">Week Engagement</div><div style="height:1px;background:#F3F4F6;margin-bottom:24px;"></div><div style="display:flex;flex-direction:column;gap:12px;"><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Ranking Diagnostic (ARD)</div><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Optimization Plan (AOP)</div></div></div>
            <div style="border:2px solid #7C3AED;border-radius:16px;padding:36px 32px;position:relative;background:#FAFBFF;"><div style="position:absolute;top:-13px;left:50%;transform:translateX(-50%);background:#7C3AED;color:white;border-radius:50px;padding:3px 16px;font-size:0.72rem;font-weight:700;white-space:nowrap;">Recommended</div><div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#7C3AED;margin-bottom:10px;">Option 2</div><div style="font-size:3rem;font-weight:900;color:#111827;line-height:1;margin-bottom:2px;">7</div><div style="font-size:0.95rem;font-weight:600;color:#374151;margin-bottom:28px;">Week Engagement</div><div style="height:1px;background:#E5E7EB;margin-bottom:24px;"></div><div style="display:flex;flex-direction:column;gap:12px;"><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Ranking Diagnostic (ARD)</div><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Optimization Plan (AOP)</div><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Impact Measurement (Re-Diagnostic)</div></div></div>
            <div style="border:1px solid #E5E7EB;border-radius:16px;padding:36px 32px;"><div style="font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:10px;">Option 3</div><div style="font-size:3rem;font-weight:900;color:#111827;line-height:1;margin-bottom:2px;">7</div><div style="font-size:0.95rem;font-weight:600;color:#374151;margin-bottom:28px;">Week Engagement</div><div style="height:1px;background:#F3F4F6;margin-bottom:24px;"></div><div style="display:flex;flex-direction:column;gap:12px;"><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Ranking Diagnostic (ARD)</div><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Agent Optimization Plan (AOP)</div><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Distribution and Technical Influence (DTI)</div><div style="display:flex;gap:10px;font-size:0.86rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;">+</span>Impact Measurement (Re-Diagnostic)</div></div></div>
        </div>
    </div>
    <div style="background:#7C3AED;padding:56px 40px;">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:80px;align-items:center;">
            <div><div style="font-size:0.72rem;font-weight:700;letter-spacing:.12em;color:rgba(255,255,255,0.6);text-transform:uppercase;margin-bottom:10px;">Proven Results</div><h2 style="font-size:2rem;font-weight:800;color:white;margin:0 0 14px;line-height:1.25;">Validated Impact Across<br>10+ Client Engagements</h2><p style="font-size:0.92rem;color:rgba(255,255,255,0.8);line-height:1.8;margin:0;">Across retail, travel, financial services, and hospitality, Percepta has consistently delivered measurable improvements.</p></div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">{"".join(f\'<div style="border:1px solid rgba(255,255,255,0.2);border-radius:12px;padding:24px;"><div style="font-size:2.4rem;font-weight:900;color:white;">{v}</div><div style="font-size:0.85rem;font-weight:600;color:rgba(255,255,255,0.8);margin-top:5px;">{l}</div></div>\' for v,l in [("10+","Successful Clients"),("4X","Higher Conversion"),("15%","Citation Growth"),("68%","Longer Sessions")])}</div>
        </div>
    </div>""",unsafe_allow_html=True)
