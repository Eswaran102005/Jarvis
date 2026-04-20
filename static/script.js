document.addEventListener('DOMContentLoaded', () => {
    const bootScreen = document.getElementById('boot-screen');
    const bootLog = document.getElementById('boot-log');
    const hudContainer = document.getElementById('hud-container');
    const progressFill = document.querySelector('.progress-fill');
    
    const historyContainer = document.getElementById('history-container');
    const orb = document.querySelector('.orb');
    const statusText = document.getElementById('status-text');
    const liveClock = document.getElementById('live-clock');
    const liveDate = document.getElementById('live-date');
    const cpuVal = document.getElementById('cpu-val');
    const netVal = document.getElementById('net-val');

    let currentStatus = 'idle';
    let lastUserText = '';
    let lastAssistantText = '';

    // 🚀 1. Cinematic Boot Sequence
    const logs = [
        "INITIALIZING CORE_OS v4.2...",
        "DECRYPTING NEURAL_LINK...",
        "ESTABLISHING A2141_HARDWARE_SYNC...",
        "LOADING VOICE_MODULE...",
        "AI_BRAIN_ONLINE: PHI_v2",
        "SYNCING HOLOGRAPHIC_HUD...",
        "CONNECTION ESTABLISHED."
    ];

    async function runBootSequence() {
        for (let i = 0; i < logs.length; i++) {
            const line = document.createElement('div');
            line.textContent = `> ${logs[i]}`;
            bootLog.appendChild(line);
            
            // Increment Progress
            const progress = ((i + 1) / logs.length) * 100;
            progressFill.style.width = `${progress}%`;
            
            await new Promise(r => setTimeout(r, 400));
        }

        // Transition to Main UI
        setTimeout(() => {
            bootScreen.classList.add('fade-out');
            hudContainer.classList.remove('hidden');
            startOperationalSystems();
        }, 500);
    }

    // ✨ 2. Background Particle System
    function initParticles() {
        const container = document.getElementById('particles-js');
        for (let i = 0; i < 50; i++) {
            const p = document.createElement('div');
            p.className = 'particle';
            const size = Math.random() * 3;
            p.style.width = `${size}px`;
            p.style.height = `${size}px`;
            p.style.left = `${Math.random() * 100}vw`;
            p.style.animationDuration = `${Math.random() * 10 + 10}s`;
            p.style.animationDelay = `${Math.random() * 5}s`;
            container.appendChild(p);
        }
    }

    // 🧬 3. Operational Systems
    function startOperationalSystems() {
        setInterval(updateClock, 1000);
        setInterval(updateMetrics, 2000);
        updateClock();
        pollState();
        appendLog('assistant', 'JARVIS ONLINE. READY FOR INPUT.');
    }

    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        liveClock.textContent = `${hours}:${minutes}:${seconds}`;

        const options = { weekday: 'long', day: 'numeric', month: 'long' };
        liveDate.textContent = now.toLocaleDateString('en-US', options).toUpperCase();
    }

    function updateMetrics() {
        const cpu = Math.floor(Math.random() * (45 - 28) + 28);
        cpuVal.textContent = `${cpu}%`;
    }

    function appendLog(sender, text) {
        if (!text) return;
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        
        if (sender === 'user') {
            entry.innerHTML = `<span class="log-user">USER ></span> ${text.toUpperCase()}`;
        } else {
            entry.innerHTML = `<span class="log-assistant">JARVIS ></span> ${text}`;
        }
        
        historyContainer.appendChild(entry);
        historyContainer.scrollTop = historyContainer.scrollHeight;
    }

    function updateUI(state) {
        if (state.status !== currentStatus) {
            currentStatus = state.status;
            orb.className = 'orb ' + state.status;
            statusText.textContent = state.status === 'idle' ? 'SYSTEM STANDBY' : state.status.toUpperCase();
        }

        if (state.user_text && state.user_text !== lastUserText) {
            lastUserText = state.user_text;
            appendLog('user', state.user_text);
        }

        if (state.assistant_text && state.assistant_text !== lastAssistantText) {
            lastAssistantText = state.assistant_text;
            appendLog('assistant', state.assistant_text);
        }

        // 🔍 Handle Search Results Panel
        if (state.search_results && state.search_results.length > 0) {
            const resultsSignature = JSON.stringify(state.search_results);
            if (window.lastResultsSignature !== resultsSignature) {
                window.lastResultsSignature = resultsSignature;
                renderSearchResults(state.search_results);
            }
        }
    }

    function renderSearchResults(results) {
        let html = '<div class="results-grid">';
        results.forEach((res, i) => {
            const fileName = res.path.split(/[\\/]/).pop();
            html += `
                <div class="result-item">
                    <span class="result-index">${i + 1}</span>
                    <span class="result-name">${fileName}</span>
                    <span class="result-path">${res.path}</span>
                </div>
            `;
        });
        html += '</div>';
        createPanel('SEARCH_RESULTS', html);
    }

    async function pollState() {
        try {
            const response = await fetch('/api/state');
            const state = await response.json();
            updateUI(state);
        } catch (error) {
            statusText.textContent = 'LINK_STATUS: OFFLINE';
        }
        setTimeout(pollState, 150);
    }

    // 🖥️ 4. Interactive Panel System Logic
    const panelLayer = document.getElementById('panel-layer');
    let panelCount = 0;
    let maxZIndex = 1000;

    function createPanel(type = 'SYSTEM', content = 'Initializing...') {
        panelCount++;
        const panel = document.createElement('div');
        panel.className = 'jarvis-panel';
        panel.id = `panel-${Date.now()}`;
        panel.style.zIndex = ++maxZIndex;

        // Header
        const header = document.createElement('div');
        header.className = 'panel-header';
        
        const title = document.createElement('div');
        title.className = 'panel-title';
        title.textContent = type;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'panel-close-btn';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = () => closePanel(panel);

        header.appendChild(title);
        header.appendChild(closeBtn);

        // Content
        const contentArea = document.createElement('div');
        contentArea.className = 'panel-content';
        contentArea.innerHTML = content;

        panel.appendChild(header);
        panel.appendChild(contentArea);
        
        panelLayer.appendChild(panel);

        // Positioning (Staggered)
        const offset = Math.min((panelCount - 1) * 30, 200);
        panel.style.top = `${150 + offset}px`;
        panel.style.left = `${100 + offset}px`;

        enableDrag(panel);
        bringToFront(panel);
        autoClosePanel(panel);

        // Interaction Listeners
        panel.addEventListener('mousedown', () => bringToFront(panel));
        
        return panel;
    }

    function closePanel(panel) {
        panel.classList.add('panel-closing');
        panel.addEventListener('animationend', () => {
            panel.remove();
        });
    }

    function autoClosePanel(panel) {
        let timeout;
        const startTimer = () => {
            timeout = setTimeout(() => closePanel(panel), 8000);
        };
        const resetTimer = () => clearTimeout(timeout);

        panel.addEventListener('mouseenter', resetTimer);
        panel.addEventListener('mouseleave', startTimer);
        panel.addEventListener('mousedown', resetTimer);

        startTimer();
    }

    function enableDrag(panel) {
        const header = panel.querySelector('.panel-header');
        let isDragging = false;
        let offsetX, offsetY;

        header.addEventListener('mousedown', (e) => {
            isDragging = true;
            offsetX = e.clientX - panel.offsetLeft;
            offsetY = e.clientY - panel.offsetTop;
            header.style.cursor = 'grabbing';
            bringToFront(panel);
        });

        document.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            
            let x = e.clientX - offsetX;
            let y = e.clientY - offsetY;

            // Keep within bounds (optional, but good for UX)
            x = Math.max(0, Math.min(x, window.innerWidth - panel.offsetWidth));
            y = Math.max(0, Math.min(y, window.innerHeight - panel.offsetHeight));

            panel.style.left = `${x}px`;
            panel.style.top = `${y}px`;
        });

        document.addEventListener('mouseup', () => {
            isDragging = false;
            header.style.cursor = 'grab';
        });
    }

    function bringToFront(panel) {
        maxZIndex++;
        panel.style.zIndex = maxZIndex;
    }

    // Expose for testing/demo
    window.jarvis = { createPanel };

    // 🔥 Initialize
    initParticles();
    runBootSequence();

    // Demo: Create a sample panel after boot
    setTimeout(() => {
        createPanel('NEWS', 'NEURAL_LINK_UPGRADE_SUCCESSFUL: NEW INTERACTIVE PANEL SYSTEM IS NOW ONLINE. DRAG TO MOVE, CLICK TO FOCUS.');
    }, 6000);
});
