# Replace the entire Overview page section (if nav=="Overview":) with the code below.
# Changes made:
# 1. Removed 10+ client section (stats bar)
# 2. Sections spread out with more padding, no dead white space
# 3. "Why This Matters" → intro to GEO Score + diagram in one section, not two
# 4. Removed "How It Works" section entirely
# 5. Changed "Competitors Give You Data. We Give You Everything." → "...We Give You Solution."
# 6. No hanging words (all headlines wrap cleanly to two lines)
# 7. CTA changed to "Ready to See Your Score?"
# 8. "Launch GEO Hub" button styled as highlighted/clickable card

if nav=="Overview":

    # HERO
    st.markdown("""
    <div style="background:#7C3AED;padding:100px 40px;">
        <div style="max-width:960px;margin:0 auto;text-align:center;">
            <div style="display:inline-block;border:1px solid rgba(255,255,255,0.35);border-radius:50px;padding:5px 16px;font-size:0.72rem;font-weight:600;letter-spacing:.1em;color:rgba(255,255,255,0.85);text-transform:uppercase;margin-bottom:28px;">Accenture's AI GEO Intelligence Platform</div>
            <h1 style="font-size:3.6rem;font-weight:900;color:white;line-height:1.08;margin:0 0 24px 0;letter-spacing:-1.5px;">Your Brand's Rank in AI<br>is Now a Business Metric.</h1>
            <p style="font-size:1.1rem;color:rgba(255,255,255,0.82);line-height:1.7;margin:0 auto 40px auto;max-width:600px;">Percepta measures, scores, and improves your brand's visibility across AI search engines — real time, with a team behind every insight.</p>
            <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;">
                <div style="border:1px solid rgba(255,255,255,0.35);border-radius:50px;padding:8px 20px;font-size:0.84rem;font-weight:500;color:rgba(255,255,255,0.9);">Live GEO Scoring</div>
                <div style="border:1px solid rgba(255,255,255,0.35);border-radius:50px;padding:8px 20px;font-size:0.84rem;font-weight:500;color:rgba(255,255,255,0.9);">Competitor Benchmarking</div>
                <div style="border:1px solid rgba(255,255,255,0.35);border-radius:50px;padding:8px 20px;font-size:0.84rem;font-weight:500;color:rgba(255,255,255,0.9);">Actionable Recommendations</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # THE AI SHIFT
    st.markdown("""
    <div style="background:white;padding:96px 40px;">
        <div style="max-width:960px;margin:0 auto;">
            <div style="text-align:center;margin-bottom:60px;">
                <div class="section-tag">The AI Shift</div>
                <h2 style="font-size:2.2rem;font-weight:800;color:#111827;margin:0 0 16px 0;">Search is Being Replaced.<br>Is Your Brand Ready?</h2>
                <p style="font-size:1rem;color:#6B7280;max-width:580px;margin:0 auto;line-height:1.8;">ChatGPT, Gemini, and Perplexity now answer questions your customers used to Google. If AI does not mention your brand, you do not exist in that moment.</p>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:28px;">
                <div style="padding:36px 28px;border:1px solid #E5E7EB;border-radius:14px;">
                    <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;margin-bottom:10px;">25%</div>
                    <div style="font-size:0.92rem;font-weight:700;color:#111827;margin-bottom:8px;">Drop in Traditional Search</div>
                    <div style="font-size:0.82rem;color:#6B7280;line-height:1.7;">Gartner forecasts traditional search engine traffic drops 25% by 2026 as users shift to AI</div>
                </div>
                <div style="padding:36px 28px;border:1px solid #E5E7EB;border-radius:14px;">
                    <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;margin-bottom:10px;">59%+</div>
                    <div style="font-size:0.92rem;font-weight:700;color:#111827;margin-bottom:8px;">Zero-Click Searches</div>
                    <div style="font-size:0.82rem;color:#6B7280;line-height:1.7;">Of Google searches now end without a click. AI summaries answer before users visit any site</div>
                </div>
                <div style="padding:36px 28px;border:1px solid #E5E7EB;border-radius:14px;">
                    <div style="font-size:2.6rem;font-weight:900;color:#7C3AED;margin-bottom:10px;">18B+</div>
                    <div style="font-size:0.92rem;font-weight:700;color:#111827;margin-bottom:8px;">Weekly AI Queries</div>
                    <div style="font-size:0.82rem;color:#6B7280;line-height:1.7;">ChatGPT processes 18B+ queries weekly from 700M+ users, all discovering brands through AI</div>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # WHY THIS MATTERS — GEO Score intro + diagram in one section
    st.markdown("""
    <div style="background:#F9F9FC;padding:96px 40px;border-top:1px solid #E5E7EB;">
        <div style="max-width:960px;margin:0 auto;">
            <div style="text-align:center;margin-bottom:64px;">
                <div class="section-tag">Why This Matters</div>
                <h2 style="font-size:2.2rem;font-weight:800;color:#111827;margin:0 0 16px 0;">Introducing the Percepta GEO Score —<br>Your Brand's AI Visibility Number.</h2>
                <p style="font-size:1rem;color:#6B7280;max-width:600px;margin:0 auto;line-height:1.8;">A single 0 to 100 number that tells you exactly how visible and favorably your brand appears across AI-generated responses. Every point you gain cascades through your entire growth funnel.</p>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr 1fr;gap:0;align-items:start;margin-bottom:0;">
    """, unsafe_allow_html=True)

    # GEO Score chain diagram — rendered inline via plotly + columns
    import plotly.graph_objects as go

    chain_items = [
        ("GEO Score","Measures how strongly your brand appears in AI responses","#7C3AED","white"),
        ("Ranking","Higher scores help your brand appear more competitively vs others","#EDE9FE","#7C3AED"),
        ("Visibility","More visibility — users see your brand in AI answers","#EDE9FE","#7C3AED"),
        ("Traffic","More visibility leads to more clicks and site visits","#EDE9FE","#7C3AED"),
        ("Conversion","More qualified traffic creates more calls and actions","#EDE9FE","#7C3AED"),
        ("Revenue","Better conversions translate into measurable growth","#7C3AED","white"),
    ]

    cols = st.columns([2,0.5,2,0.5,2,0.5,2,0.5,2,0.5,2])
    col_indices = [0,2,4,6,8,10]
    arrow_indices = [1,3,5,7,9]

    for i, (title, desc, bg, tc) in enumerate(chain_items):
        with cols[col_indices[i]]:
            st.markdown(f'''
            <div style="text-align:center;padding:28px 12px;background:{bg};border-radius:14px;min-height:160px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;">
                <div style="font-size:0.88rem;font-weight:800;color:{tc};margin-bottom:10px;">{title}</div>
                <div style="font-size:0.74rem;color:{"rgba(255,255,255,0.85)" if tc=="white" else "#6B7280"};line-height:1.6;">{desc}</div>
            </div>
            ''', unsafe_allow_html=True)
        if i < len(arrow_indices):
            with cols[arrow_indices[i]]:
                st.markdown('<div style="text-align:center;padding-top:60px;font-size:1.3rem;color:#7C3AED;font-weight:700;">→</div>', unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

    # WHAT YOU GAIN
    st.markdown("""
    <div style="background:white;padding:96px 40px;border-top:1px solid #E5E7EB;">
        <div style="max-width:960px;margin:0 auto;">
            <div style="text-align:center;margin-bottom:64px;">
                <div class="section-tag">What You Gain</div>
                <h2 style="font-size:2.2rem;font-weight:800;color:#111827;margin:0 0 16px 0;">Competitors Give You Data.<br>We Give You Solution.</h2>
                <p style="font-size:1rem;color:#6B7280;max-width:540px;margin:0 auto;line-height:1.8;">Every other GEO tool stops at the dashboard. Percepta is the only solution that combines measurement, strategy, and execution in one place.</p>
            </div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:32px;">
                <div style="border:1px solid #E5E7EB;border-radius:16px;padding:40px 36px;background:#FAFAFA;">
                    <div style="font-size:0.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#9CA3AF;margin-bottom:20px;">Other GEO Tools</div>
                    <div style="display:flex;flex-direction:column;gap:16px;">
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#9CA3AF;font-weight:700;font-size:1rem;">+</span>Raw visibility data</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#9CA3AF;font-weight:700;font-size:1rem;">+</span>Citation tracking</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#9CA3AF;font-weight:700;font-size:1rem;">+</span>A dashboard to check</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#9CA3AF;text-decoration:line-through;"><span style="color:#E5E7EB;font-weight:700;font-size:1rem;">+</span>Insights on what to do</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#9CA3AF;text-decoration:line-through;"><span style="color:#E5E7EB;font-weight:700;font-size:1rem;">+</span>Prioritized recommendations</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#9CA3AF;text-decoration:line-through;"><span style="color:#E5E7EB;font-weight:700;font-size:1rem;">+</span>A team to implement it</div>
                    </div>
                    <div style="margin-top:24px;padding-top:20px;border-top:1px solid #E5E7EB;font-size:0.78rem;color:#9CA3AF;">Profound, Scrunch, Peec AI, Semrush AI Toolkit</div>
                </div>
                <div style="border:2px solid #7C3AED;border-radius:16px;padding:40px 36px;background:white;position:relative;">
                    <div style="position:absolute;top:-14px;left:28px;background:#7C3AED;color:white;border-radius:50px;padding:4px 16px;font-size:0.72rem;font-weight:700;">Percepta by Accenture</div>
                    <div style="font-size:0.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:#7C3AED;margin-bottom:20px;margin-top:6px;">Your All-in-One GEO Solution</div>
                    <div style="display:flex;flex-direction:column;gap:16px;">
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;">+</span>Proprietary GEO Score (0 to 100)</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;">+</span>Competitor benchmarking across 10+ brands</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;">+</span>Source attribution with page-level detail</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;">+</span>Insights on exactly what is holding you back</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;">+</span>Prioritized recommendations tied to deliverables</div>
                        <div style="display:flex;align-items:center;gap:12px;font-size:0.9rem;color:#374151;font-weight:700;"><span style="color:#7C3AED;font-weight:700;font-size:1rem;">+</span>Accenture team to execute the strategy</div>
                    </div>
                </div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)

    # CTA — "Ready to See Your Score?" + highlighted Launch GEO Hub button
    st.markdown("""
    <div style="background:#F9F9FC;padding:96px 40px;border-top:1px solid #E5E7EB;text-align:center;">
        <div style="max-width:600px;margin:0 auto;">
            <div class="section-tag">Get Started</div>
            <h2 style="font-size:2.2rem;font-weight:800;color:#111827;margin:16px 0 16px 0;">Ready to See<br>Your Score?</h2>
            <p style="font-size:1rem;color:#6B7280;margin:0 0 40px 0;line-height:1.8;">Enter your brand URL and get a complete live GEO analysis in minutes. No setup required.</p>
        </div>
    </div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1.6, 1])
    with c2:
        st.markdown("""
        <style>
        div[data-testid="stButton"] > button[kind="primary"].geo-hub-btn {
            background: linear-gradient(135deg, #7C3AED 0%, #5B21B6 100%) !important;
            color: white !important;
            font-size: 1.05rem !important;
            font-weight: 800 !important;
            padding: 18px 0 !important;
            border-radius: 14px !important;
            border: none !important;
            box-shadow: 0 8px 32px rgba(124,58,237,0.35) !important;
            letter-spacing: 0.02em !important;
            transition: box-shadow 0.2s, transform 0.15s !important;
        }
        div[data-testid="stButton"] > button[kind="primary"].geo-hub-btn:hover {
            box-shadow: 0 12px 40px rgba(124,58,237,0.5) !important;
            transform: translateY(-2px) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Highlighted CTA card wrapping the button
        st.markdown("""
        <div style="background:linear-gradient(135deg,#7C3AED 0%,#5B21B6 100%);border-radius:18px;padding:32px 32px 28px 32px;text-align:center;box-shadow:0 12px 48px rgba(124,58,237,0.3);margin-bottom:4px;">
            <div style="font-size:1.35rem;font-weight:900;color:white;margin-bottom:8px;">Launch GEO Hub</div>
            <div style="font-size:0.88rem;color:rgba(255,255,255,0.78);margin-bottom:20px;">Analyse your brand's AI visibility now</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("→  Open GEO Hub", use_container_width=True):
            st.session_state.nav = "GEO Hub"
            st.rerun()
