import streamlit as st


def render():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

    .stApp { background: #000510 !important; }

    /* ── PARTICLE CANVAS as fixed background ── */
    #neural-bg {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        z-index: 0;
        pointer-events: none;
    }

    /* push all Streamlit content above the canvas */
    .stApp > * { position: relative; z-index: 1; }
    [data-testid="stAppViewContainer"] { background: transparent !important; }
    [data-testid="stHeader"] { background: transparent !important; }

    .hero-badge {
        display: inline-flex; align-items: center; gap: 8px;
        padding: 7px 20px; border-radius: 999px;
        background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.5);
        color: #c4b5fd; font-family:'Exo 2',sans-serif; font-size:13px;
        letter-spacing:1px; margin-bottom: 20px;
        box-shadow: 0 0 25px rgba(139,92,246,0.25);
    }

    .hero-title {
        font-family: 'Orbitron', sans-serif;
        font-size: 52px; line-height: 1.1; font-weight: 900;
        color: #ffffff; margin-bottom: 20px; letter-spacing: 1px;
    }

    .hero-title .glow {
        background: linear-gradient(90deg, #a78bfa, #60a5fa, #c084fc);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 25px rgba(139,92,246,0.8));
    }

    .hero-text {
        font-family: 'Exo 2', sans-serif; font-size: 16px;
        color: rgba(203,213,225,0.85); line-height: 1.9; margin-bottom: 28px;
    }

    .stats-wrapper {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
        gap: 12px; margin-bottom: 24px;
    }

    .stat-item {
        background: rgba(139,92,246,0.1);
        border: 1px solid rgba(139,92,246,0.3);
        border-radius: 14px; padding: 16px 12px; text-align: center;
        box-shadow: 0 0 20px rgba(139,92,246,0.1);
    }

    .stat-number {
        font-family: 'Orbitron', sans-serif; font-size: 26px; font-weight: 700;
        background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 12px rgba(139,92,246,0.8));
    }

    .stat-label {
        font-family: 'Exo 2', sans-serif; color: #94a3b8;
        font-size: 10px; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px;
    }

    .side-panel {
        background: rgba(4,6,22,0.85);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 20px; padding: 28px;
        position: relative; overflow: hidden;
        backdrop-filter: blur(16px);
        box-shadow: 0 0 30px rgba(139,92,246,0.1);
    }

    .side-panel::before {
        content:''; position:absolute; top:0; left:0; right:0; height:1.5px;
        background:linear-gradient(90deg,transparent,#8b5cf6,#60a5fa,transparent);
        box-shadow:0 0 10px rgba(139,92,246,.6);
    }

    .panel-title {
        font-family: 'Orbitron', sans-serif; font-size: 11px;
        color: #a78bfa; letter-spacing: 3px;
        text-transform: uppercase; margin-bottom: 20px;
        padding-bottom: 12px; border-bottom: 1px solid rgba(139,92,246,0.15);
    }

    .panel-item {
        display: flex; align-items: flex-start; gap: 12px;
        margin-bottom: 14px; padding: 12px; border-radius: 10px;
        background: rgba(139,92,246,0.06); border: 1px solid rgba(139,92,246,0.12);
        transition: all 0.2s ease;
    }

    .panel-item:hover { border-color:rgba(139,92,246,.3); box-shadow:0 0 15px rgba(139,92,246,.1); }
    .panel-dot { width:8px; height:8px; border-radius:50%; background:#8b5cf6; box-shadow:0 0 10px rgba(139,92,246,1); margin-top:5px; flex-shrink:0; }
    .panel-item-text { font-family:'Exo 2',sans-serif; color:#94a3b8; font-size:13px; line-height:1.5; }
    .panel-item-title { font-weight:700; color:#e2e8f0; margin-bottom:2px; display:block; }

    .neon-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.6), rgba(59,130,246,0.6), transparent);
        margin: 36px 0; border: none;
        box-shadow: 0 0 10px rgba(139,92,246,0.3);
    }

    .section-heading {
        font-family: 'Orbitron', sans-serif; font-size: 26px; font-weight: 700;
        text-align: center; background: linear-gradient(90deg, #a78bfa, #60a5fa);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        filter: drop-shadow(0 0 15px rgba(139,92,246,0.5));
        margin-bottom: 8px; letter-spacing: 1px;
    }

    .section-sub {
        font-family: 'Exo 2', sans-serif; text-align: center;
        color: #64748b; font-size: 13px; margin-bottom: 28px; letter-spacing: 1px;
    }

    .steps-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
        gap: 14px; margin-bottom: 20px;
    }

    .step {
        text-align: center; padding: 24px 14px;
        background: rgba(4,6,22,0.85); border: 1px solid rgba(139,92,246,0.2);
        border-radius: 14px; transition: all 0.3s;
        box-shadow: 0 0 15px rgba(139,92,246,0.05);
        backdrop-filter: blur(12px);
    }

    .step:hover { border-color:rgba(139,92,246,.4); transform:translateY(-4px); box-shadow:0 0 25px rgba(139,92,246,.15); }
    .step-num { font-family:'Orbitron',sans-serif; font-size:2.2rem; font-weight:900; background:linear-gradient(135deg,#8b5cf6,#3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; filter:drop-shadow(0 0 15px rgba(139,92,246,.7)); margin-bottom:10px; }
    .step-title { font-family:'Exo 2',sans-serif; font-weight:700; color:#e2e8f0; font-size:14px; margin-bottom:6px; }
    .step-text { font-family:'Exo 2',sans-serif; color:#64748b; font-size:12px; line-height:1.6; }

    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 14px; margin-bottom: 20px;
    }

    .feature-card {
        padding: 24px 20px; background: rgba(4,6,22,0.85);
        border: 1px solid rgba(139,92,246,0.2); border-radius: 16px;
        position: relative; overflow: hidden; transition: all 0.3s;
        box-shadow: 0 0 15px rgba(139,92,246,0.05);
        backdrop-filter: blur(12px);
    }

    .feature-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1.5px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.5),transparent); }
    .feature-card:hover { border-color:rgba(139,92,246,.45); transform:translateY(-5px); box-shadow:0 0 30px rgba(139,92,246,.2); }
    .feature-icon { font-size:32px; margin-bottom:12px; filter:drop-shadow(0 0 12px rgba(139,92,246,.7)); }
    .feature-title { font-family:'Orbitron',sans-serif; font-size:13px; font-weight:700; color:#e2e8f0; margin-bottom:8px; }
    .feature-text { font-family:'Exo 2',sans-serif; color:#64748b; font-size:12px; line-height:1.7; }

    .cta-wrapper {
        background: radial-gradient(ellipse at center, rgba(139,92,246,0.15) 0%, transparent 70%);
        border: 1px solid rgba(139,92,246,0.3); border-radius: 24px;
        padding: 48px 40px; text-align: center; position: relative; overflow: hidden;
        box-shadow: 0 0 40px rgba(139,92,246,0.1);
        backdrop-filter: blur(12px);
    }

    .cta-wrapper::before { content:''; position:absolute; top:0; left:0; right:0; height:1.5px; background:linear-gradient(90deg,transparent,#8b5cf6,#60a5fa,transparent); box-shadow:0 0 15px rgba(139,92,246,.5); }
    .cta-title { font-family:'Orbitron',sans-serif; font-size:28px; font-weight:900; color:white; margin-bottom:10px; letter-spacing:1px; }
    .cta-text { font-family:'Exo 2',sans-serif; color:#94a3b8; font-size:14px; margin-bottom:28px; }

    @media (max-width: 640px) {
        .hero-title { font-size: 28px; }
        .stats-wrapper { grid-template-columns: repeat(2, 1fr); }
        .steps-grid { grid-template-columns: repeat(2, 1fr); }
        .feature-grid { grid-template-columns: 1fr; }
        .cta-wrapper { padding: 28px 18px; }
        .cta-title { font-size: 20px; }
    }
    </style>

    <!-- Particle canvas injected into page DOM as fixed background -->
    <canvas id="neural-bg"></canvas>
    <script>
    (function() {
        const canvas = document.getElementById('neural-bg');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        const COUNT = 80, MAX_DIST = 150;
        const particles = [];

        function Particle() {
            this.reset = function() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.6;
                this.vy = (Math.random() - 0.5) * 0.6;
                this.r = Math.random() * 2 + 1;
                this.color = Math.random() > 0.5 ? '139,92,246' : '59,130,246';
            };
            this.reset();
            this.update = function() {
                this.x += this.vx; this.y += this.vy;
                if (this.x < 0 || this.x > canvas.width)  this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            };
            this.draw = function() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(' + this.color + ',0.9)';
                ctx.shadowBlur = 10;
                ctx.shadowColor = 'rgba(' + this.color + ',0.8)';
                ctx.fill();
                ctx.shadowBlur = 0;
            };
        }

        for (var i = 0; i < COUNT; i++) particles.push(new Particle());

        function animate() {
            ctx.fillStyle = 'rgba(0,5,16,0.15)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            for (var i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();
                for (var j = i + 1; j < particles.length; j++) {
                    var dx = particles[i].x - particles[j].x;
                    var dy = particles[i].y - particles[j].y;
                    var dist = Math.sqrt(dx * dx + dy * dy);
                    if (dist < MAX_DIST) {
                        var alpha = (1 - dist / MAX_DIST) * 0.5;
                        var grad = ctx.createLinearGradient(particles[i].x, particles[i].y, particles[j].x, particles[j].y);
                        grad.addColorStop(0, 'rgba(139,92,246,' + alpha + ')');
                        grad.addColorStop(1, 'rgba(59,130,246,' + alpha + ')');
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = grad;
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        }
        animate();
    })();
    </script>
    """, unsafe_allow_html=True)

    # ── HERO ──
    left, right = st.columns([1.5, 1])

    with left:
        st.markdown("""
        <div class="hero-badge">⚡ Next-Gen AI Recruitment Platform</div>
        <div class="hero-title">
            Hire Smarter.<br>
            <span class="glow">Think Faster.</span><br>
            Win Better.
        </div>
        <div class="hero-text">
            Transform your recruitment with AI-powered resume analysis,
            intelligent candidate scoring, and data-driven hiring decisions —
            all in one unified platform built for the future.
        </div>
        <div class="stats-wrapper">
            <div class="stat-item"><div class="stat-number">98%</div><div class="stat-label">Match Accuracy</div></div>
            <div class="stat-item"><div class="stat-number">10x</div><div class="stat-label">Faster Hiring</div></div>
            <div class="stat-item"><div class="stat-number">500+</div><div class="stat-label">Jobs Matched</div></div>
            <div class="stat-item"><div class="stat-number">24/7</div><div class="stat-label">AI Active</div></div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🚀 Get Started — Free", use_container_width=True):
                st.session_state.page = "Sign Up"
                st.rerun()
        with b2:
            if st.button("🔐 Login", use_container_width=True):
                st.session_state.page = "Login"
                st.rerun()

    with right:
        st.markdown("""
        <div class="side-panel">
            <div class="panel-title">// Platform Capabilities</div>
            <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">AI Resume Parsing</span>Automatically extract skills, experience, and qualifications from uploaded CVs</div></div>
            <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Intelligent Scoring</span>Rank candidates using semantic analysis, skill matching, and experience scoring</div></div>
            <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Fraud Detection</span>Verify resume authenticity and flag suspicious or exaggerated claims</div></div>
            <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Admin Control Center</span>Full visibility into applications, shortlisting, rejection, and email communication</div></div>
            <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Real-Time Rankings</span>Live candidate leaderboards updated instantly as new applications arrive</div></div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── HOW IT WORKS ──
    st.markdown('<div class="section-heading">How It Works</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">// Four steps to smarter hiring</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="steps-grid">
        <div class="step"><div class="step-num">01</div><div class="step-title">Post a Job</div><div class="step-text">Admin creates listings with required skills & experience level</div></div>
        <div class="step"><div class="step-num">02</div><div class="step-title">Upload Resume</div><div class="step-text">Candidates apply and upload CVs directly to the platform</div></div>
        <div class="step"><div class="step-num">03</div><div class="step-title">AI Analyzes</div><div class="step-text">AI scores, ranks and verifies each application instantly</div></div>
        <div class="step"><div class="step-num">04</div><div class="step-title">Hire the Best</div><div class="step-text">Admins review top candidates and make confident decisions</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="neon-divider"></div>', unsafe_allow_html=True)

    # ── FEATURES ──
    st.markdown('<div class="section-heading">Platform Features</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-sub">// Everything for modern intelligent recruitment</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card"><div class="feature-icon">📄</div><div class="feature-title">Resume Intelligence</div><div class="feature-text">Upload PDFs and let AI parse, extract, and analyze candidate data with high precision.</div></div>
        <div class="feature-card"><div class="feature-icon">🧠</div><div class="feature-title">Semantic AI Scoring</div><div class="feature-text">Goes beyond keywords — understands context, experience depth, and skill relevance.</div></div>
        <div class="feature-card"><div class="feature-icon">🛡️</div><div class="feature-title">Verification Engine</div><div class="feature-text">Detects inconsistencies, flags risk factors, and verifies resume authenticity.</div></div>
        <div class="feature-card"><div class="feature-icon">⚡</div><div class="feature-title">Real-Time Rankings</div><div class="feature-text">Candidate leaderboards update instantly as new applications arrive.</div></div>
        <div class="feature-card"><div class="feature-icon">📧</div><div class="feature-title">Smart Communication</div><div class="feature-text">Send personalized emails directly from the platform with one click.</div></div>
        <div class="feature-card"><div class="feature-icon">📊</div><div class="feature-title">Hiring Analytics</div><div class="feature-text">Full visibility into your pipeline — scores, statuses, and hiring trends.</div></div>
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

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("🚀 Create Free Account", use_container_width=True):
            st.session_state.page = "Sign Up"
            st.rerun()
    with c2:
        if st.button("🔐 Sign In", use_container_width=True):
            st.session_state.page = "Login"
            st.rerun()
    with c3:
        if st.button("💼 Browse Jobs", use_container_width=True):
            st.session_state.page = "Jobs"
            st.rerun()