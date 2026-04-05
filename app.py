<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Percepta | GEO Intelligence</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{font-family:'Inter',sans-serif;box-sizing:border-box;margin:0;padding:0;}
body{background:#fff;}
.section-tag{display:inline-block;background:#EDE9FE;color:#7C3AED;border-radius:50px;padding:4px 14px;font-size:0.72rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;margin-bottom:14px;}

/* NAV */
nav{background:white;border-bottom:1px solid #E5E7EB;padding:12px 40px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:999;box-shadow:0 1px 3px rgba(0,0,0,0.06);}
.nav-brand{display:flex;align-items:center;gap:10px;text-decoration:none;}
.nav-icon{width:30px;height:30px;border-radius:7px;background:#7C3AED;display:flex;align-items:center;justify-content:center;}
.nav-title{font-size:1rem;font-weight:800;color:#111827;}
.nav-links{display:flex;gap:6px;}
.nav-links a{text-decoration:none;padding:7px 16px;border-radius:8px;font-size:0.88rem;font-weight:500;color:#6B7280;transition:all .15s;}
.nav-links a:hover,.nav-links a.active{background:#EDE9FE;color:#7C3AED;font-weight:700;}

/* HERO */
.hero{background:#7C3AED;padding:100px 40px;text-align:center;}
.hero-badge{display:inline-block;border:1px solid rgba(255,255,255,0.35);border-radius:50px;padding:5px 16px;font-size:0.72rem;font-weight:600;letter-spacing:.1em;color:rgba(255,255,255,0.85);text-transform:uppercase;margin-bottom:28px;}
.hero h1{font-size:3.4rem;font-weight:900;color:white;line-height:1.08;margin:0 0 22px;letter-spacing:-1.5px;}
.hero p{font-size:1.05rem;color:rgba(255,255,255,0.82);line-height:1.7;max-width:660px;margin:0 auto 36px;}
.hero-pills{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;}
.hero-pill{border:1px solid rgba(255,255,255,0.35);border-radius:50px;padding:7px 18px;font-size:0.82rem;font-weight:500;color:rgba(255,255,255,0.9);}

/* SECTIONS */
section{padding:80px 40px;}
.inner{width:100%;max-width:100%;}
.section-head{text-align:center;margin-bottom:52px;}
.section-head h2{font-size:2.1rem;font-weight:800;color:#111827;margin:0 0 14px;line-height:1.2;}
.section-head p{font-size:0.97rem;color:#6B7280;max-width:620px;margin:0 auto;line-height:1.75;}

/* STATS */
.stats-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:24px;}
.stat-card{padding:32px 28px;border:1px solid #E5E7EB;border-radius:14px;}
.stat-num{font-size:2.6rem;font-weight:900;color:#7C3AED;margin-bottom:8px;line-height:1;}
.stat-title{font-size:0.92rem;font-weight:700;color:#111827;margin-bottom:6px;}
.stat-desc{font-size:0.82rem;color:#6B7280;line-height:1.65;}

/* GEO CHAIN */
.chain{display:grid;grid-template-columns:1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr 24px 1fr;gap:0;align-items:stretch;}
.chain-node{text-align:center;padding:24px 12px;border-radius:14px;display:flex;flex-direction:column;justify-content:flex-start;}
.chain-node.primary{background:#7C3AED;}
.chain-node.secondary{background:#EDE9FE;}
.chain-node-title{font-size:0.86rem;font-weight:800;margin-bottom:8px;}
.chain-node.primary .chain-node-title{color:white;}
.chain-node.secondary .chain-node-title{color:#7C3AED;}
.chain-node-desc{font-size:0.73rem;line-height:1.55;}
.chain-node.primary .chain-node-desc{color:rgba(255,255,255,0.85);}
.chain-node.secondary .chain-node-desc{color:#6B7280;}
.chain-arrow{text-align:center;font-size:1.2rem;color:#7C3AED;font-weight:700;display:flex;align-items:center;justify-content:center;}

/* COMPARISON */
.compare-grid{display:grid;grid-template-columns:1fr 1fr;gap:28px;}
.compare-card{border:1px solid #E5E7EB;border-radius:16px;padding:36px 32px;background:#FAFAFA;}
.compare-card.featured{border:2px solid #7C3AED;background:white;position:relative;}
.compare-label{font-size:0.7rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;margin-bottom:18px;}
.compare-item{display:flex;align-items:center;gap:12px;font-size:0.88rem;color:#374151;margin-bottom:14px;}
.compare-item.muted{color:#9CA3AF;text-decoration:line-through;}
.compare-item.bold{font-weight:700;}
.compare-plus{font-weight:700;font-size:1rem;flex-shrink:0;}
.compare-plus.active{color:#7C3AED;}
.compare-plus.muted{color:#E5E7EB;}
.featured-badge{position:absolute;top:-13px;left:28px;background:#7C3AED;color:white;border-radius:50px;padding:4px 16px;font-size:0.72rem;font-weight:700;}

/* CTA */
.cta-section{background:#F9F9FC;border-top:1px solid #E5E7EB;padding:88px 40px;text-align:center;}
.cta-inner{max-width:520px;margin:0 auto;}
.cta-card{background:linear-gradient(135deg,#7C3AED 0%,#5B21B6 100%);border-radius:18px;padding:38px 40px;box-shadow:0 12px 48px rgba(124,58,237,0.28);cursor:pointer;transition:transform .2s,box-shadow .2s;display:block;text-decoration:none;max-width:400px;margin:32px auto 0;}
.cta-card:hover{transform:translateY(-3px);box-shadow:0 18px 56px rgba(124,58,237,0.36);}
.cta-card-title{font-size:1.3rem;font-weight:900;color:white;margin-bottom:6px;}
.cta-card-sub{font-size:0.88rem;color:rgba(255,255,255,0.8);}
.cta-arrow{font-size:1.5rem;margin-bottom:10px;}
</style>
</head>
<body>

<!-- NAV -->
<nav>
  <a class="nav-brand" href="#">
    <div class="nav-icon">
      <svg width="16" height="16" viewBox="0 0 22 22" fill="none"><circle cx="9.5" cy="9.5" r="5.5" stroke="white" stroke-width="1.8" fill="none"/><line x1="13.5" y1="13.5" x2="18" y2="18" stroke="white" stroke-width="1.8" stroke-linecap="round"/><path d="M7 9.5 Q8.5 7 9.5 9.5 Q10.5 12 12 9.5" stroke="white" stroke-width="1.3" fill="none" stroke-linecap="round" opacity="0.9"/></svg>
    </div>
    <span class="nav-title">Percepta</span>
  </a>
  <div class="nav-links">
    <a href="#" class="active">Overview</a>
    <a href="#">GEO Hub</a>
    <a href="#">Get Support</a>
  </div>
</nav>

<!-- HERO -->
<div class="hero">
  <div class="hero-badge">Accenture's AI GEO Intelligence Platform</div>
  <h1>Your Brand's Rank in AI<br>is Now a Business Metric.</h1>
  <p>Percepta measures, scores, and improves your brand's visibility across AI search engines — real time, with a team behind every insight.</p>
  <div class="hero-pills">
    <span class="hero-pill">Live GEO Scoring</span>
    <span class="hero-pill">Competitor Benchmarking</span>
    <span class="hero-pill">Actionable Recommendations</span>
  </div>
</div>

<!-- THE AI SHIFT -->
<section style="background:white;">
  <div class="inner">
    <div class="section-head">
      <div class="section-tag">The AI Shift</div>
      <h2>Search is Being Replaced.<br>Is Your Brand Ready?</h2>
      <p>ChatGPT, Gemini, and Perplexity now answer questions your customers used to Google. If AI doesn't mention your brand, you don't exist in that moment.</p>
    </div>
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-num">25%</div>
        <div class="stat-title">Drop in Traditional Search</div>
        <div class="stat-desc">Gartner forecasts traditional search engine traffic drops 25% by 2026 as users shift to AI.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">59%+</div>
        <div class="stat-title">Zero-Click Searches</div>
        <div class="stat-desc">Of Google searches now end without a click — AI summaries answer before users visit any site.</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">18B+</div>
        <div class="stat-title">Weekly AI Queries</div>
        <div class="stat-desc">ChatGPT processes 18B+ queries weekly from 700M+ users, all discovering brands through AI.</div>
      </div>
    </div>
  </div>
</section>

<!-- WHY THIS MATTERS -->
<section style="background:#F9F9FC;border-top:1px solid #E5E7EB;">
  <div class="inner">
    <div class="section-head">
      <div class="section-tag">Why This Matters</div>
      <h2>Introducing the Percepta GEO Score —<br>Your Brand's AI Visibility Number.</h2>
      <p>A single 0–100 number that tells you how visible and favorably your brand appears across AI-generated responses. Every point you gain cascades through your entire growth funnel.</p>
    </div>
    <div class="chain">
      <div class="chain-node primary">
        <div class="chain-node-title">GEO Score</div>
        <div class="chain-node-desc">Measures your brand's presence and strength in AI-generated responses</div>
      </div>
      <div class="chain-arrow">→</div>
      <div class="chain-node secondary">
        <div class="chain-node-title">Ranking</div>
        <div class="chain-node-desc">Higher scores improve your competitive position vs. peers</div>
      </div>
      <div class="chain-arrow">→</div>
      <div class="chain-node secondary">
        <div class="chain-node-title">Visibility</div>
        <div class="chain-node-desc">Greater visibility means your brand appears more often in AI answers</div>
      </div>
      <div class="chain-arrow">→</div>
      <div class="chain-node secondary">
        <div class="chain-node-title">Traffic</div>
        <div class="chain-node-desc">Increased visibility drives more clicks and site visits</div>
      </div>
      <div class="chain-arrow">→</div>
      <div class="chain-node secondary">
        <div class="chain-node-title">Conversion</div>
        <div class="chain-node-desc">More qualified traffic leads to higher engagement and actions</div>
      </div>
      <div class="chain-arrow">→</div>
      <div class="chain-node primary">
        <div class="chain-node-title">Revenue</div>
        <div class="chain-node-desc">Higher conversions translate into measurable business growth</div>
      </div>
    </div>
  </div>
</section>

<!-- WHAT YOU GAIN -->
<section style="background:white;border-top:1px solid #E5E7EB;">
  <div class="inner">
    <div class="section-head">
      <div class="section-tag">What You Gain</div>
      <h2>Competitors Give You Data.<br>We Give You a Solution.</h2>
      <p>Every other GEO tool stops at the dashboard. Percepta combines measurement, strategy, and execution in one place.</p>
    </div>
    <div class="compare-grid">
      <div class="compare-card">
        <div class="compare-label" style="color:#9CA3AF;">Other GEO Tools</div>
        <div class="compare-item"><span class="compare-plus active">+</span> Raw visibility data</div>
        <div class="compare-item"><span class="compare-plus active">+</span> Citation tracking</div>
        <div class="compare-item"><span class="compare-plus active">+</span> A dashboard to check</div>
        <div class="compare-item muted"><span class="compare-plus muted">+</span> Insights on what to do</div>
        <div class="compare-item muted"><span class="compare-plus muted">+</span> Prioritized recommendations</div>
        <div class="compare-item muted"><span class="compare-plus muted">+</span> A team to implement it</div>
      </div>
      <div class="compare-card featured">
        <div class="featured-badge">Percepta by Accenture</div>
        <div class="compare-label" style="color:#7C3AED;margin-top:6px;">Your All-in-One GEO Solution</div>
        <div class="compare-item"><span class="compare-plus active">+</span> Proprietary GEO Score (0 to 100)</div>
        <div class="compare-item"><span class="compare-plus active">+</span> Competitor benchmarking across 10+ brands</div>
        <div class="compare-item"><span class="compare-plus active">+</span> Source attribution with page-level detail</div>
        <div class="compare-item"><span class="compare-plus active">+</span> Insights on exactly what is holding you back</div>
        <div class="compare-item"><span class="compare-plus active">+</span> Prioritized recommendations tied to deliverables</div>
        <div class="compare-item bold"><span class="compare-plus active">+</span> Accenture team to execute the strategy</div>
      </div>
    </div>
  </div>
</section>

<!-- CTA -->
<div class="cta-section">
  <div class="cta-inner">
    <div class="section-tag">Get Started</div>
    <h2 style="font-size:2.1rem;font-weight:800;color:#111827;margin:0 0 14px;line-height:1.2;">Ready to See Your Score?</h2>
    <p style="font-size:0.97rem;color:#6B7280;line-height:1.75;">Enter your brand URL and get a complete live GEO analysis in minutes. No setup required.</p>
    <a class="cta-card" href="#">
      <div class="cta-arrow">🔍</div>
      <div class="cta-card-title">Discover Your GEO Score Now</div>
      <div class="cta-card-sub">Run your free AI visibility analysis →</div>
    </a>
  </div>
</div>

</body>
</html>
