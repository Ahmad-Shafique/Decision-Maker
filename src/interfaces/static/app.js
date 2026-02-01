const API_URL = 'http://127.0.0.1:2947';

const els = {
    status: document.getElementById('status-indicator'),
    input: document.getElementById('situation-input'),
    btn: document.getElementById('analyze-btn'),
    btnText: document.querySelector('.btn-text'),
    loader: document.querySelector('.loader'),
    results: document.getElementById('results-section'),
    reasoning: document.getElementById('result-reasoning'),
    recommendation: document.getElementById('result-recommendation'),
    principles: document.getElementById('principles-list'),
    sops: document.getElementById('sops-list'),
    sopsContainer: document.getElementById('sops-container'),
    confidenceBar: document.getElementById('confidence-bar'),
    confidenceVal: document.getElementById('confidence-value'),
    alignmentVal: document.getElementById('alignment-value')
};

// Check Health
async function checkHealth() {
    try {
        const res = await fetch(`${API_URL}/health`);
        const data = await res.json();
        if (data.status === 'ok') {
            els.status.textContent = 'System Online';
            els.status.className = 'status online';
            els.btn.disabled = false;
        }
    } catch (e) {
        els.status.textContent = 'System Offline';
        els.status.className = 'status offline';
        els.btn.disabled = true;
    }
}

// Analyze
els.btn.addEventListener('click', async () => {
    const text = els.input.value.trim();
    if (!text) return;

    // Loading State
    els.btn.disabled = true;
    els.btnText.textContent = 'Analyzing...';
    els.loader.classList.remove('hidden');
    els.results.classList.add('hidden');

    try {
        const res = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: text })
        });

        if (!res.ok) throw new Error('Analysis failed');

        const data = await res.json();
        renderResults(data);

    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        // Reset State
        els.btn.disabled = false;
        els.btnText.textContent = 'Analyze Situation';
        els.loader.classList.add('hidden');
    }
});

function renderResults(data) {
    // Show Section
    els.results.classList.remove('hidden');

    // Text Content (Process markdown-like newlines)
    els.reasoning.innerHTML = formatText(data.reasoning);
    els.recommendation.innerHTML = formatText(data.recommendation);

    // Principles
    els.principles.innerHTML = data.applicable_principles.map(m => `
        <li>
            <strong>${m.principle.title}</strong>
            <span class="score">${(m.relevance_score * 100).toFixed(0)}% Match</span>
            <div style="font-size: 0.85rem; margin-top: 4px; opacity: 0.8;">${m.match_reason}</div>
        </li>
    `).join('');

    // SOPs
    if (data.triggered_sops && data.triggered_sops.length > 0) {
        els.sopsContainer.style.display = 'block';
        els.sops.innerHTML = data.triggered_sops.map(s => `
            <li style="border-left-color: var(--warning-color)">
                <strong>${s.name}</strong>
                <div>${s.purpose}</div>
            </li>
        `).join('');
    } else {
        els.sopsContainer.style.display = 'none';
    }

    // Metrics
    const confidencePct = Math.round(data.confidence * 100);
    els.confidenceVal.textContent = `${confidencePct}%`;
    els.confidenceBar.style.width = `${confidencePct}%`;

    // Value Alignment
    if (data.value_alignment && data.value_alignment.overall_score) {
        const alignPct = Math.round(data.value_alignment.overall_score * 100);
        els.alignmentVal.textContent = `${alignPct}%`;
    } else {
        els.alignmentVal.textContent = 'N/A';
    }

    // Smooth scroll
    els.results.scrollIntoView({ behavior: 'smooth' });
}

function formatText(text) {
    // Simple formatter: convert newlines to <br> and **bold** to <b>
    if (!text) return '';
    let formatted = text.replace(/\n/g, '<br>');
    formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    return formatted;
}

// Init
checkHealth();
// Poll every 10s
setInterval(checkHealth, 10000);
