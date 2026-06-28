import streamlit as st
import streamlit.components.v1 as components


def render():

    result = components.html("""
    <!DOCTYPE html>
    <html>
    <head>
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
            padding: 12px 20px; border-radius: 10px; border: none;
            font-family: 'Exo 2', sans-serif; font-size: 14px; font-weight: 700;
            cursor: pointer; transition: all 0.2s; letter-spacing: 0.5px;
            white-space: nowrap;
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

        .section-sub { text-align:center; color:#64748b; font-size:12px; margin-bottom:24px; letter-spacing:1px; }

        .steps-grid {
            display: grid; grid-template-columns: repeat(4, 1fr);
            gap: 12px; margin-bottom: 16px;
        }

        .step {
            text-align: center; padding: 20px 12px;
            background: rgba(4,6,22,0.85); border: 1px solid rgba(139,92,246,0.2);
            border-radius: 14px; transition: all 0.3s; backdrop-filter: blur(12px);
        }

        .step:hover { border-color:rgba(139,92,246,.4); transform:translateY(-4px); }
        .step-num { font-family:'Orbitron',sans-serif; font-size:2rem; font-weight:900; background:linear-gradient(135deg,#8b5cf6,#3b82f6); -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:8px; }
        .step-title { font-weight:700; color:#e2e8f0; font-size:13px; margin-bottom:4px; }
        .step-text { color:#64748b; font-size:11px; line-height:1.5; }

        .feature-grid {
            display: grid; grid-template-columns: repeat(3, 1fr);
            gap: 12px; margin-bottom: 16px;
        }

        .feature-card {
            padding: 22px 18px; background: rgba(4,6,22,0.85);
            border: 1px solid rgba(139,92,246,0.2); border-radius: 16px;
            position: relative; overflow: hidden; transition: all 0.3s;
            backdrop-filter: blur(12px);
        }

        .feature-card::before { content:''; position:absolute; top:0; left:0; right:0; height:1.5px; background:linear-gradient(90deg,transparent,rgba(139,92,246,.5),transparent); }
        .feature-card:hover { border-color:rgba(139,92,246,.45); transform:translateY(-5px); }
        .feature-icon { font-size:28px; margin-bottom:10px; }
        .feature-title { font-family:'Orbitron',sans-serif; font-size:12px; font-weight:700; color:#e2e8f0; margin-bottom:6px; }
        .feature-text { color:#64748b; font-size:11px; line-height:1.6; }

        .cta-wrapper {
            background: radial-gradient(ellipse at center, rgba(139,92,246,0.15) 0%, transparent 70%);
            border: 1px solid rgba(139,92,246,0.3); border-radius: 24px;
            padding: 40px; text-align: center; position: relative; overflow: hidden;
            backdrop-filter: blur(12px); margin-bottom: 8px;
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
    </style>
    </head>
    <body>

    <canvas id="c"></canvas>

    <div class="content">
        <div class="hero-grid">
            <div>
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
                <div class="btn-row">
                    <button class="btn btn-primary" onclick="navigate('Sign Up')">🚀 Get Started — Free</button>
                    <button class="btn btn-secondary" onclick="navigate('Login')">🔐 Login</button>
                </div>
            </div>

            <div class="side-panel">
                <div class="panel-title">// Platform Capabilities</div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">AI Resume Parsing</span>Automatically extract skills, experience, and qualifications from uploaded CVs</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Intelligent Scoring</span>Rank candidates using semantic analysis, skill matching, and experience scoring</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Fraud Detection</span>Verify resume authenticity and flag suspicious or exaggerated claims</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Admin Control Center</span>Full visibility into applications, shortlisting, rejection, and email communication</div></div>
                <div class="panel-item"><div class="panel-dot"></div><div class="panel-item-text"><span class="panel-item-title">Real-Time Rankings</span>Live candidate leaderboards updated instantly as new applications arrive</div></div>
            </div>
        </div>

        <div class="neon-divider"></div>

        <div class="section-heading">How It Works</div>
        <div class="section-sub">// Four steps to smarter hiring</div>
        <div class="steps-grid">
            <div class="step"><div class="step-num">01</div><div class="step-title">Post a Job</div><div class="step-text">Admin creates listings with required skills & experience level</div></div>
            <div class="step"><div class="step-num">02</div><div class="step-title">Upload Resume</div><div class="step-text">Candidates apply and upload CVs directly to the platform</div></div>
            <div class="step"><div class="step-num">03</div><div class="step-title">AI Analyzes</div><div class="step-text">AI scores, ranks and verifies each application instantly</div></div>
            <div class="step"><div class="step-num">04</div><div class="step-title">Hire the Best</div><div class="step-text">Admins review top candidates and make confident decisions</div></div>
        </div>

        <div class="neon-divider"></div>

        <div class="section-heading">Platform Features</div>
        <div class="section-sub">// Everything for modern intelligent recruitment</div>
        <div class="feature-grid">
            <div class="feature-card"><div class="feature-icon">📄</div><div class="feature-title">Resume Intelligence</div><div class="feature-text">Upload PDFs and let AI parse, extract, and analyze candidate data with high precision.</div></div>
            <div class="feature-card"><div class="feature-icon">🧠</div><div class="feature-title">Semantic AI Scoring</div><div class="feature-text">Goes beyond keywords — understands context, experience depth, and skill relevance.</div></div>
            <div class="feature-card"><div class="feature-icon">🛡️</div><div class="feature-title">Verification Engine</div><div class="feature-text">Detects inconsistencies, flags risk factors, and verifies resume authenticity.</div></div>
            <div class="feature-card"><div class="feature-icon">⚡</div><div class="feature-title">Real-Time Rankings</div><div class="feature-text">Candidate leaderboards update instantly as new applications arrive.</div></div>
            <div class="feature-card"><div class="feature-icon">📧</div><div class="feature-title">Smart Communication</div><div class="feature-text">Send personalized emails directly from the platform with one click.</div></div>
            <div class="feature-card"><div class="feature-icon">📊</div><div class="feature-title">Hiring Analytics</div><div class="feature-text">Full visibility into your pipeline — scores, statuses, and hiring trends.</div></div>
        </div>

        <div class="neon-divider"></div>

        <div class="cta-wrapper">
            <div class="cta-title">Ready to Transform Your Hiring?</div>
            <div class="cta-text">Join the future of recruitment. Set up in minutes, hire better forever.</div>
            <div class="cta-btn-row">
                <button class="btn btn-primary" onclick="navigate('Sign Up')">🚀 Create Free Account</button>
                <button class="btn btn-secondary" onclick="navigate('Login')">🔐 Sign In</button>
                <button class="btn btn-secondary" onclick="navigate('Jobs')">💼 Browse Jobs</button>
            </div>
        </div>
    </div>

    <script>
        function navigate(page) {
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: page}, '*');
        }

        // ── AUTO-RESIZE iframe to full content height ──
        function sendHeight() {
            const h = document.body.scrollHeight;
            window.parent.postMessage({type: 'streamlit:setFrameHeight', height: h}, '*');
        }
        window.addEventListener('load', sendHeight);
        window.addEventListener('resize', sendHeight);
        setTimeout(sendHeight, 300);
        setTimeout(sendHeight, 800);

        // ── PARTICLE ANIMATION ──
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
    """, height=4500, scrolling=False)

    if result and isinstance(result, str):
        st.session_state.page = result
        st.rerun()