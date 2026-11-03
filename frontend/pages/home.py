import streamlit as st
import streamlit.components.v1 as components


def render():
    # ── HANDLE NAVIGATION FROM IFRAME ──
    nav_target = st.query_params.get("nav", "")
    if nav_target:
        st.query_params.clear()
        st.session_state.page = nav_target
        st.rerun()

    components.html("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <title>AI Hiring System - home</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;900&family=Exo+2:wght@300;400;600;700&display=swap');

        * { margin: 0; padding: 0; box-sizing: border-box; }

        html, body {
            height: auto;
            background: #000510;
            font-family: 'Exo 2', sans-serif;
            overflow-x: hidden;
        }

        canvas {
            position: fixed;
            top: 0; left: 0;
            width: 100%; height: 100%;
            z-index: 0;
            pointer-events: none;
        }

        .content {
            position: relative;
            z-index: 1;
            padding: 40px 32px 32px;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1.5fr 1fr;
            gap: 32px;
            align-items: start;
        }

        .hero-badge {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 7px 20px; border-radius: 999px;
            background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.5);
            color: #c4b5fd; font-size: 13px; font-weight: 600;
            letter-spacing: 1px; margin-bottom: 20px;
            box-shadow: 0 0 25px rgba(139,92,246,0.25);
        }

        .hero-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 48px; line-height: 1.1; font-weight: 900;
            color: #fff; margin-bottom: 20px; letter-spacing: 1px;
        }

        .hero-title .glow {
            background: linear-gradient(90deg, #a78bfa, #60a5fa, #c084fc);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 25px rgba(139,92,246,0.8));
        }

        .hero-text {
            font-size: 15px; color: rgba(203,213,225,0.85);
            line-height: 1.9; margin-bottom: 28px;
        }

        .stats-wrapper {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px; margin-bottom: 24px;
        }

        .stat-item {
            background: rgba(139,92,246,0.1);
            border: 1px solid rgba(139,92,246,0.3);
            border-radius: 14px; padding: 14px 8px; text-align: center;
        }

        .stat-number {
            font-family: 'Orbitron', sans-serif; font-size: 22px; font-weight: 700;
            background: linear-gradient(90deg, #a78bfa, #60a5fa);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 10px rgba(139,92,246,0.8));
        }

        .stat-label {
            color: #94a3b8; font-size: 9px;
            letter-spacing: 1px; text-transform: uppercase; margin-top: 4px;
        }

        .btn-row { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

        .btn {
            padding: 14px 20px; border-radius: 10px; border: none;
            font-family: 'Exo 2', sans-serif; font-size: 14px; font-weight: 700;
            cursor: pointer; transition: all 0.2s; letter-spacing: 0.5px;
            white-space: nowrap; text-decoration: none; display: block;
            text-align: center;
        }

        .btn-primary {
            background: linear-gradient(135deg, #7c3aed, #4f46e5);
            color: white; box-shadow: 0 0 20px rgba(124,58,237,0.4);
        }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 0 30px rgba(124,58,237,0.6); }

        .btn-secondary {
            background: rgba(139,92,246,0.1);
            color: #a78bfa; border: 1px solid rgba(139,92,246,0.4);
        }
        .btn-secondary:hover { background: rgba(139,92,246,0.2); transform: translateY(-2px); }

        .side-panel {
            background: rgba(4,6,22,0.85);
            border: 1px solid rgba(139,92,246,0.25);
            border-radius: 20px; padding: 24px;
            position: relative; overflow: hidden;
            backdrop-filter: blur(16px);
            box-shadow: 0 0 30px rgba(139,92,246,0.1);
        }

        .side-panel::before {
            content:''; position:absolute; top:0; left:0; right:0; height:1.5px;
            background:linear-gradient(90deg,transparent,#8b5cf6,#60a5fa,transparent);
        }

        .panel-title {
            font-family: 'Orbitron', sans-serif; font-size: 10px;
            color: #a78bfa; letter-spacing: 3px; text-transform: uppercase;
            margin-bottom: 16px; padding-bottom: 12px;
            border-bottom: 1px solid rgba(139,92,246,0.15);
        }

        .panel-item {
            display: flex; align-items: flex-start; gap: 10px;
            margin-bottom: 12px; padding: 10px; border-radius: 10px;
            background: rgba(139,92,246,0.06); border: 1px solid rgba(139,92,246,0.12);
            transition: all 0.2s;
        }

        .panel-item:hover { border-color: rgba(139,92,246,0.3); }
        .panel-dot { width:7px; height:7px; border-radius:50%; background:#8b5cf6; box-shadow:0 0 8px rgba(139,92,246,1); margin-top:5px; flex-shrink:0; }
        .panel-item-text { color:#94a3b8; font-size:12px; line-height:1.5; }
        .panel-item-title { font-weight:700; color:#e2e8f0; margin-bottom:2px; display:block; }

        .neon-divider {
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(139,92,246,0.6), rgba(59,130,246,0.6), transparent);
            margin: 32px 0; border: none;
        }

        .section-heading {
            font-family: 'Orbitron', sans-serif; font-size: 24px; font-weight: 700;
            text-align: center; background: linear-gradient(90deg, #a78bfa, #60a5fa);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            margin-bottom: 6px; letter-spacing: 1px;
        }

        .section-sub { text-align:center; color:#94a3b8; font-size:12px; margin-bottom:24px; letter-spacing:1px; }

        .steps-grid {
            display: grid; grid-template-columns: repeat(4, 1fr);
            gap: 12px; margin-bottom: 16px;
        }

        .step {
            text-align: center; padding: 20px 12px;
            background: rgba(4,6,22,0.85); border: 1px solid rgba(139,92,246,0.2);
            border-radius: 14px; transition: all 0.3s;
        }

        .step:hover { border-color:rgba(139,92,246,.4); transform:translateY(-4px); }
        .step-num { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; background:linear-gradient(135deg,#8b5cf6,#3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }
        .step-title { font-weight:700; color:#e2e8f0; font-size:13px; margin-bottom:4px; }
        .step-text { color:#94a3b8; font-size:12px; line-height:1.5; }

        .feature-grid {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 12px; margin-bottom: 16px;
        }

        .feature-card {
            padding: 22px 18px; background: rgba(4,6,22,0.85);
            border: 1px solid rgba(139,92,246,0.2); border-radius: 16px;
            position: relative; overflow: hidden; transition: all 0.3s;
        }

        .feature-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1.5px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.5),transparent); }
        .feature-card:hover { border-color:rgba(139,92,246,.45); transform:translateY(-5px); }
        .feature-icon { font-size:28px; margin-bottom:10px; }
        .feature-title { font-family:'Orbitron',sans-serif; font-size:12px; font-weight:700; color:#e2e8f0; margin-bottom:6px; }
        .feature-text { color:#94a3b8; font-size:12px; line-height:1.6; }

        .cta-wrapper {
            background: radial-gradient(ellipse at center, rgba(139,92,246,0.15) 0%, transparent 70%);
            border: 1px solid rgba(139,92,246,0.3); border-radius: 24px;
            padding: 40px; text-align: center; position: relative; overflow: hidden;
            margin-bottom: 8px;
        }

        .cta-wrapper::before { content:''; position:absolute; top:0; left:0; right:0; height:1.5px; background:linear-gradient(90deg,transparent,#8b5cf6,#60a5fa,transparent); }
        .cta-title { font-family:'Orbitron',sans-serif; font-size:26px; font-weight:900; color:white; margin-bottom:8px; }
        .cta-text { color:#94a3b8; font-size:13px; margin-bottom:24px; }
        .cta-btn-row { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }

        @media (max-width: 700px) {
            .hero-grid { grid-template-columns: 1fr; }
            .hero-title { font-size: 30px; }
            .stats-wrapper { grid-template-columns: repeat(2, 1fr); }
            .steps-grid { grid-template-columns: repeat(2, 1fr); }
            .feature-grid { grid-template-columns: 1fr; }
            .cta-btn-row { grid-template-columns: 1fr; }
            .btn-row { grid-template-columns: 1fr; }
        }
            a.btn:focus-visible { outline: 3px solid #fbbf24; outline-offset: 3px; }
        @media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }
    </style>
    </head>
    <body>

    <canvas id="c" aria-hidden="true"></canvas>

    <div class="content">
        <div class="hero-grid">
            <div>
                <div class="hero-badge"> Next-Gen AI Recruitment Platform</div>
                <div class="hero-title">
                    Hire Smarter.<br>
                    <span class="glow">Think Faster.</span><br>
                    Win Better.
                </div>
                <div class="hero-text">
                    AI-assisted resume analysis and candidate scoring in one place.
                    The software ranks applicants; a person always makes the final decision.
                </div>
                <div class="stats-wrapper">
                    <div class="stat-item"><div class="stat-number">4</div><div class="stat-label">Scoring factors</div></div>
                    <div class="stat-item"><div class="stat-number">93</div><div class="stat-label">Skills recognised</div></div>
                    <div class="stat-item"><div class="stat-number">Free</div><div class="stat-label">No fees</div></div>
                    <div class="stat-item"><div class="stat-number">Human</div><div class="stat-label">Final decision</div></div>
                </div>
                <div class="btn-row">
                    <a class="btn btn-primary" href="#" role="button" onclick="navigateTo('Sign Up'); return false;" onkeydown="if (event.key === ' ') { event.preventDefault(); navigateTo('Sign Up'); }">🚀 Get Started — Free</a>
                    <a class="btn btn-secondary" href="#" role="button" onclick="navigateTo('Login'); return false;" onkeydown="if (event.key === ' ') { event.preventDefault(); navigateTo('Login'); }">🔐 Login</a>
                </div>
            </div>

            <div class="side-panel">
                <div class="panel-title">// Platform Capabilities</div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">AI Resume Parsing</span>Extract skills and years of experience from uploaded PDF or text resumes</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Intelligent Scoring</span>Rank candidates using text comparison, skill matching and experience scoring</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Consistency Checks</span>Flag patterns such as keyword stuffing or inconsistent dates for a person to look at</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Admin Control Center</span>See applications, shortlist or reject candidates, and email them</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Real-Time Rankings</span>Rankings update whenever a new application arrives</div></div>
            </div>
        </div>

        <div class="neon-divider"></div>

        <div class="section-heading">How It Works</div>
        <div class="section-sub">// Four steps to smarter hiring</div>
        <div class="steps-grid">
            <div class="step"><div class="step-num">01</div><div class="step-title">Post a Job</div><div class="step-text">Admin creates listings with required skills & experience level</div></div>
            <div class="step"><div class="step-num">02</div><div class="step-title">Upload Resume</div><div class="step-text">Candidates apply and upload CVs directly to the platform</div></div>
            <div class="step"><div class="step-num">03</div><div class="step-title">AI Analyzes</div><div class="step-text">Software scores and ranks each application against the job</div></div>
            <div class="step"><div class="step-num">04</div><div class="step-title">Hire the Best</div><div class="step-text">Recruiters review the ranked list and decide</div></div>
        </div>

        <div class="neon-divider"></div>

        <div class="section-heading">Platform Features</div>
        <div class="section-sub">// Everything for modern intelligent recruitment</div>
        <div class="feature-grid">
            <div class="feature-card"><div class="feature-icon"></div><div class="feature-title">Resume Intelligence</div><div class="feature-text">Upload PDF or text resumes and let the software extract skills and experience.</div></div>
            <div class="feature-card"><div class="feature-icon"></div><div class="feature-title">Transparent Scoring</div><div class="feature-text">Compares resume and job text, required skills and experience, and shows candidates how they matched.</div></div>
            <div class="feature-card"><div class="feature-icon"></div><div class="feature-title">Consistency Checks</div><div class="feature-text">Flags patterns such as keyword stuffing or inconsistent dates. A flag is a prompt for a human, not proof.</div></div>
            <div class="feature-card"><div class="feature-icon"></div><div class="feature-title">Real-Time Rankings</div><div class="feature-text">Rankings update whenever a new application arrives.</div></div>
            <div class="feature-card"><div class="feature-icon"></div><div class="feature-title">Smart Communication</div><div class="feature-text">Recruiters can email candidates from the platform. Candidates can unsubscribe from those emails.</div></div>
            <div class="feature-card"><div class="feature-icon"></div><div class="feature-title">Hiring Pipeline</div><div class="feature-text">See every application with its score and status in one list.</div></div>
        </div>

        <div class="neon-divider"></div>

        <div class="cta-wrapper">
            <div class="cta-title">Ready to try it?</div>
            <div class="cta-text">Create a free account in a minute. Candidates must be 18 or older.</div>
            <div class="cta-btn-row">
                <a class="btn btn-primary" href="#" role="button" onclick="navigateTo('Sign Up'); return false;" onkeydown="if (event.key === ' ') { event.preventDefault(); navigateTo('Sign Up'); }"> Create Free Account</a>
                <a class="btn btn-secondary" href="#" role="button" onclick="navigateTo('Login'); return false;" onkeydown="if (event.key === ' ') { event.preventDefault(); navigateTo('Login'); }"> Sign In</a>
                <a class="btn btn-secondary" href="#" role="button" onclick="navigateTo('Jobs'); return false;" onkeydown="if (event.key === ' ') { event.preventDefault(); navigateTo('Jobs'); }"> Browse Jobs</a>
            </div>
        </div>
    </div>

    <script>
        // The buttons live in a sandboxed iframe, so they cannot change the page themselves.
        // Instead they click the matching item in the app's own top menu (a Streamlit radio),
        // which makes Streamlit switch pages normally and keeps the user's session.
        // (A <script> placed in st.markdown is never executed by the browser, so it cannot do this.)
        function navigateTo(page) {
            try {
                var labels = window.parent.document.querySelectorAll('[data-testid="stRadio"] label');
                for (var i = 0; i < labels.length; i++) {
                    if (labels[i].innerText.trim() === page) { labels[i].click(); return; }
                }
            } catch (e) { /* parent not reachable: use the fallback below */ }
            // Fallback: reload the app with ?nav=<page>, which app.py also understands.
            try { window.parent.location.search = '?nav=' + encodeURIComponent(page); } catch (e) {}
        }

        function sendHeight() {
            const h = document.body.scrollHeight;
            window.parent.postMessage({type: 'streamlit:setFrameHeight', height: h}, '*');
        }

        if (document.fonts && document.fonts.ready) {
            document.fonts.ready.then(sendHeight);
        }

        const resizeObserver = new ResizeObserver(() => sendHeight());
        resizeObserver.observe(document.body);

        window.addEventListener('load', sendHeight);
        window.addEventListener('resize', sendHeight);
        setTimeout(sendHeight, 300);
        setTimeout(sendHeight, 800);
        setTimeout(sendHeight, 1500);

        const canvas = document.getElementById('c');
        const ctx = canvas.getContext('2d');

        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        resize();
        window.addEventListener('resize', resize);

        const COUNT = 80, MAX_DIST = 150;
        const particles = [];

        class Particle {
            constructor() { this.reset(); }
            reset() {
                this.x = Math.random() * canvas.width;
                this.y = Math.random() * canvas.height;
                this.vx = (Math.random() - 0.5) * 0.6;
                this.vy = (Math.random() - 0.5) * 0.6;
                this.r = Math.random() * 2 + 1;
                this.color = Math.random() > 0.5 ? '139,92,246' : '59,130,246';
            }
            update() {
                this.x += this.vx; this.y += this.vy;
                if (this.x < 0 || this.x > canvas.width)  this.vx *= -1;
                if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
            }
            draw() {
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(${this.color},0.35)`;
                ctx.shadowBlur = 4;
                ctx.shadowColor = `rgba(${this.color},0.2)`;
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }

        for (let i = 0; i < COUNT; i++) particles.push(new Particle());

        function animate() {
            ctx.fillStyle = 'rgba(0,5,16,0.25)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            for (let i = 0; i < particles.length; i++) {
                particles[i].update();
                particles[i].draw();
                for (let j = i + 1; j < particles.length; j++) {
                    const dx = particles[i].x - particles[j].x;
                    const dy = particles[i].y - particles[j].y;
                    const dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < MAX_DIST) {
                        const alpha = (1 - dist / MAX_DIST) * 0.15;
                        const grad = ctx.createLinearGradient(particles[i].x, particles[i].y, particles[j].x, particles[j].y);
                        grad.addColorStop(0, `rgba(139,92,246,${alpha})`);
                        grad.addColorStop(1, `rgba(59,130,246,${alpha})`);
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
    </script>
    </body>
    </html>
    """, height=1800, scrolling=False)