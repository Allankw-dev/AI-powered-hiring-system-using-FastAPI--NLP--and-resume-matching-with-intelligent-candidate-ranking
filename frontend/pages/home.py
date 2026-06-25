import streamlit as st


def render():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    /* ── HERO ── */
    .hero-wrapper {
        position: relative;
        padding: 70px 50px;
        border-radius: 24px;
        background: radial-gradient(ellipse at 30% 50%, rgba(139,92,246,0.15) 0%, rgba(59,130,246,0.08) 50%, transparent 70%);
        border: 1px solid rgba(139,92,246,0.2);
        margin-bottom: 20px;
        overflow: hidden;
    }

    .hero-wrapper::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -10%;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-wrapper::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: 20%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(59,130,246,0.1) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-badge {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 999px;
        background: rgba(139,92,246,0.12);
        color: #a78bfa;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 24px;
        border: 1px solid rgba(139,92,246,0.3);
        box-shadow: 0 0 15px rgba(139,92,246,0.2);
        font-family: 'Exo 2', sans-serif;
        letter-spacing: 1px;
    }

    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 52px;
        line-height: 1.15;
        font-weight: 900;
        color: #ffffff;
        margin-bottom: 20px;
        letter-spacing: 1px;
    }

    .hero-title .glow {
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 20px rgba(139,92,246,0.6));
    }

    .hero-text {
        font-family: 'Exo 2', sans-serif;
        font-size: 17px;
        color: #94a3b8;
        max-width: 600px;
        line-height: 1.9;
        margin-bottom: 30px;
    }

    /* ── STATS ── */
    .stats-wrapper {
        display: flex;
        gap: 16px;
        margin-bottom: 30px;
        flex-wrap: wrap;
    }

    .stat-item {
        background: rgba(139,92,246,0.06);
        border: 1px solid rgba(139,92,246,0.18);
        border-radius: 14px;
        padding: 16px 24px;
        text-align: center;
        flex: 1;
        min-width: 120px;
        box-shadow: 0 0 20px rgba(139,92,246,0.06);
    }

    .stat-number {
        font-family: 'Orbitron', sans-serif;
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 10px rgba(139,92,246,0.5));
    }

    .stat-label {
        font-family: 'Exo 2', sans-serif;
        color: #64748b;
        font-size: 12px;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-top: 4px;
    }

    /* ── FEATURE CARDS ── */
    .feature-card {
        background: rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 20px;
        padding: 28px 22px;
        min-height: 200px;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.5), transparent);
    }

    .feature-card:hover {
        border-color: rgba(139,92,246,0.4);
        box-shadow: 0 0 30px rgba(139,92,246,0.15), 0 20px 40px rgba(0,0,0,0.3);
        transform: translateY(-5px);
    }

    .feature-icon {
        font-size: 36px;
        margin-bottom: 14px;
        filter: drop-shadow(0 0 10px rgba(139,92,246,0.5));
    }

    .feature-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 10px;
        letter-spacing: 0.5px;
    }

    .feature-text {
        font-family: 'Exo 2', sans-serif;
        font-size: 14px;
        color: #64748b;
        line-height: 1.7;
    }

    /* ── HOW IT WORKS ── */
    .steps-wrapper {
        display: flex;
        gap: 0;
        margin: 20px 0;
        position: relative;
    }

    .step-item {
        flex: 1;
        text-align: center;
        padding: 24px 16px;
        position: relative;
    }

    .step-number {
        font-family: 'Orbitron', sans-serif;
        font-size: 36px;
        font-weight: 900;
        background: linear-gradient(135deg, #8b5cf6, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.6));
        margin-bottom: 12px;
    }

    .step-title {
        font-family: 'Exo 2', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 8px;
    }

    .step-text {
        font-family: 'Exo 2', sans-serif;
        font-size: 13px;
        color: #64748b;
        line-height: 1.6;
    }

    /* ── SECTION TITLES ── */
    .section-heading {
        font-family: 'Orbitron', sans-serif;
        font-size: 28px;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.4));
        margin-bottom: 8px;
        letter-spacing: 1px;
    }

    .section-sub {
        font-family: 'Exo 2', sans-serif;
        text-align: center;
        color: #475569;
        font-size: 15px;
        margin-bottom: 30px;
        letter-spacing: 0.5px;
    }

    .neon-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.5), rgba(59,130,246,0.5), transparent);
        margin: 40px 0;
        border: none;
        box-shadow: 0 0 10px rgba(139,92,246,0.3);
    }

    /* ── CTA ── */
    .cta-wrapper {
        background: radial-gradient(ellipse at center, rgba(139,92,246,0.12) 0%, transparent 70%);
        border: 1px solid rgba(139,92,246,0.2);
        border-radius: 24px;
        padding: 50px 40px;
        text-align: center;
        position: relative;
        overflow: hidden;
        margin-top: 20px;
    }

    .cta-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 32px;
        font-weight: 900;
        color: white;
        margin-bottom: 12px;
        letter-spacing: 1px;
    }

    .cta-text {
        font-family: 'Exo 2', sans-serif;
        color: #64748b;
        font-size: 16px;
        margin-bottom: 30px;
    }

    /* ── SIDE PANEL ── */
    .side-panel {
        background: rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.15);
        border-radius: 20px;
        padding: 28px;
        height: 100%;
        position: relative;
        overflow: hidden;
    }

    .side-panel::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.6), transparent);
    }

    .panel-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 14px;
        color: #a78bfa;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid rgba(139,92,246,0.15);
    }

    .panel-item {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin-bottom: 18px;
        padding: 12px;
        border-radius: 10px;
        background: rgba(139,92,246,0.04);
        border: 1px solid rgba(139,92,246,0.08);
        transition: all 0.2s ease;
    }

    .panel-item:hover {
        border-color: rgba(139,92,246,0.25);
        box-shadow: 0 0 15px rgba(139,92,246,0.08);
    }

    .panel-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #8b5cf6;
        box-shadow: 0 0 8px rgba(139,92,246,0.8);
        margin-top: 5px;
        flex-shrink: 0;
    }

    .panel-item-text {
        font-family: 'Exo 2', sans-serif;
        color: #94a3b8;
        font-size: 14px;
        line-height: 1.5;
    }

    .panel-item-title {
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 2px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── HERO ──
    left, right = st.columns([1.5, 1])

    with left:
        st.markdown("""
        <div class="hero-wrapper">
            <div class="hero-badge">⚡ Next-Gen AI Recruitment Platform</div>
            <div class="hero-title">
                Hire Smarter.<br>
                <span class="glow">Think Faster.</span><br>
                Win Better.
            </div>
            <div class="hero-text">
                Transform your recruitment process with AI-powered resume analysis,
                intelligent candidate scoring, and data-driven hiring decisions —
                all in one unified platform built for the future.
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Stats
        st.markdown("""
        <div class="stats-wrapper">
            <div class="stat-item">
                <div class="stat-number">98%</div>
                <div class="stat-label">Match Accuracy</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">10x</div>
                <div class="stat-label">Faster Hiring</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">500+</div>
                <div class="stat-label">Jobs Matched</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">AI</div>
                <div class="stat-label">Powered</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🚀 Get Started — It's Free"):
                st.session_state.page = "Sign Up"
                st.rerun()
        with b2:
            if st.button("🔐 Login to Dashboard"):
                st.session_state.page = "Login"
                st.rerun()

    with right:
        st.markdown("""
        <div class="side-panel">
            <div class="panel-title">// Platform Capabilities</div>

            <div class="panel-item">
                <div class="panel-dot"></div>
                <div class="panel-item-text">
                    <div class="panel-item-title">AI Resume Parsing</div>
                    Automatically extract skills, experience, and qualifications from uploaded CVs
                </div>
            </div>

            <div class="panel-item">
                <div class="panel-dot"></div>
                <div class="panel-item-text">
                    <div class="panel-item-title">Intelligent Scoring</div>
                    Rank candidates using semantic analysis, skill matching, and experience scoring
                </div>
            </div>

            <div class="panel-item">
                <div class="panel-dot"></div>
                <div class="panel-item-text">
                    <div class="panel-item-title">Fraud Detection</div>
                    Verify resume authenticity and flag suspicious or exaggerated claims
                </div>
            </div>

            <div class="panel-item">
                <div class="panel-dot"></div>
                <div class="panel-item-text">
                    <div class="panel-item-title">Admin Control Center</div>
                    Full visibility into applications, shortlisting, rejection, and email communication
                </div>
            </div>

            <div class="panel-item">
                <div class="panel-dot"></div>
                <div class="panel-item-text">
                    <div class="panel-item-title">Real-Time Rankings</div>
                    Live candidate leaderboards updated instantly as new applications arrive
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── HOW IT WORKS ──
    st.markdown('<div class="section-heading">How It Works</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Four simple steps to smarter hiring</div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)

    steps = [
        ("01", "Post a Job", "Admin creates a job listing with required skills and experience level"),
        ("02", "Upload Resume", "Candidates apply and upload their CVs directly to the platform"),
        ("03", "AI Analyzes", "Our AI engine scores, ranks, and verifies each application instantly"),
        ("04", "Hire the Best", "Admins review top candidates and make confident hiring decisions"),
    ]

    for col, (num, title, text) in zip([s1, s2, s3, s4], steps):
        with col:
            st.markdown(f"""
            <div style="text-align:center; padding: 20px 10px;">
                <div class="step-number">{num}</div>
                <div class="step-title">{title}</div>
                <div class="step-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── FEATURES ──
    st.markdown('<div class="section-heading">Platform Features</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">Everything you need for a modern, intelligent recruitment workflow</div>', unsafe_allow_html=True)

    f1, f2, f3 = st.columns(3)

    features = [
        ("📄", "Resume Intelligence", "Upload PDFs and let our AI parse, extract, and analyze candidate data automatically with high precision."),
        ("🧠", "Semantic AI Scoring", "Goes beyond keywords — understands context, experience depth, and skill relevance to rank candidates fairly."),
        ("🛡️", "Verification Engine", "Detects inconsistencies, flags risk factors, and verifies the authenticity of submitted resumes."),
    ]

    for col, (icon, title, text) in zip([f1, f2, f3], features):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    f4, f5, f6 = st.columns(3)

    features2 = [
        ("⚡", "Real-Time Rankings", "Candidate leaderboards update instantly as new applications come in — always see the top talent first."),
        ("📧", "Smart Communication", "Send personalized shortlist or rejection emails directly from the platform with one click."),
        ("📊", "Hiring Analytics", "Get full visibility into your pipeline — scores, statuses, skill gaps, and hiring trends at a glance."),
    ]

    for col, (icon, title, text) in zip([f4, f5, f6], features2):
        with col:
            st.markdown(f"""
            <div class="feature-card">
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-text">{text}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── CTA ──
    st.markdown("""
    <div class="cta-wrapper">
        <div class="cta-title">Ready to Transform Your Hiring?</div>
        <div class="cta-text">Join the future of recruitment. Set up in minutes, hire better forever.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("🚀 Create Free Account"):
            st.session_state.page = "Sign Up"
            st.rerun()
    with c2:
        if st.button("🔐 Sign In"):
            st.session_state.page = "Login"
            st.rerun()
    with c3:
        if st.button("💼 Browse Jobs"):
            st.session_state.page = "Jobs"
            st.rerun()