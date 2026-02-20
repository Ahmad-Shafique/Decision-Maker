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
    alignmentVal: document.getElementById('alignment-value'),
    matchingMethod: document.getElementById('matching-method'),
    llmProvider: document.getElementById('llm-provider'),
    analysisStatus: document.getElementById('analysis-status')
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

function updateStatus(message) {
    if (els.analysisStatus) {
        els.analysisStatus.textContent = message;
        els.analysisStatus.style.opacity = '1';
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

    updateStatus('⏳ Awaiting model response...');

    try {
        updateStatus('🔍 Sending to semantic matching...');

        const res = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ description: text })
        });

        if (!res.ok) throw new Error('Analysis failed');

        updateStatus('✅ Processing results...');
        const data = await res.json();
        renderResults(data);
        updateStatus('');

    } catch (e) {
        updateStatus('❌ Error: ' + e.message);
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
        els.sops.innerHTML = data.triggered_sops.map(s => {
            let modesHtml = '';
            // Check if modes exist and has keys
            if (s.modes && Object.keys(s.modes).length > 0) {
                modesHtml = `<div class="sop-modes">
                    <div style="margin-bottom:0.25rem"><strong>Modes:</strong></div>
                    ${Object.entries(s.modes).map(([name, steps]) => `
                        <details style="margin-bottom: 0.5rem">
                            <summary>Mode ${name}</summary>
                            <ol class="sop-steps">
                                ${steps.map(step => `<li>${step.instruction}</li>`).join('')}
                            </ol>
                        </details>
                    `).join('')}
                </div>`;
            }

            let stepsHtml = '';
            if (s.steps && s.steps.length > 0) {
                stepsHtml = `<div class="sop-steps-container">
                    <div style="margin-bottom:0.25rem"><strong>Steps:</strong></div>
                    <ol class="sop-steps">
                        ${s.steps.map(step => `<li>${step.instruction}</li>`).join('')}
                    </ol>
                </div>`;
            }

            return `
            <li style="border-left-color: var(--warning-color)">
                <div class="sop-header">
                    <strong style="font-size: 1.1em">${s.name}</strong>
                    <div class="sop-purpose">${s.purpose}</div>
                </div>
                ${modesHtml}
                ${stepsHtml}
            </li>
        `}).join('');
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

    // Matching Metadata
    if (data.matching_metadata) {
        const meta = data.matching_metadata;
        els.matchingMethod.textContent = meta.strategies_succeeded?.join(' + ') || 'Unknown';
        els.llmProvider.textContent = meta.llm_provider_used || 'Heuristic';

        // Style the badges
        els.matchingMethod.className = 'value badge ' + (meta.strategies_succeeded?.includes('semantic') ? 'semantic' : 'keyword');
        els.llmProvider.className = 'value badge ' + (meta.llm_provider_used ? 'llm' : 'fallback');
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

// --- Historical Analysis & Tabs ---

const tabs = document.querySelectorAll('.tab-btn');
const liveSection = document.getElementById('live-section');
const histSection = document.getElementById('historical-section');
const histResults = document.getElementById('hist-results-section');

// Tab Switching
tabs.forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Toggle sections
        if (tab.dataset.tab === 'live') {
            liveSection.classList.remove('hidden');
            histSection.classList.add('hidden');
            histResults.classList.add('hidden');
            if (!els.results.classList.contains('hidden')) {
                els.results.classList.remove('hidden');
            }
        } else {
            liveSection.classList.add('hidden');
            histSection.classList.remove('hidden');
            els.results.classList.add('hidden');
            // Don't auto-show results, wait for analysis
        }
    });
});

// Historical Analysis
const histBtn = document.getElementById('hist-analyze-btn');
const histInputs = {
    situation: document.getElementById('hist-situation'),
    decision: document.getElementById('hist-decision'),
    outcome: document.getElementById('hist-outcome')
};

histBtn.addEventListener('click', async () => {
    const sit = histInputs.situation.value.trim();
    const dec = histInputs.decision.value.trim();
    const out = histInputs.outcome.value.trim();

    if (!sit || !dec || !out) {
        alert('Please fill in all fields');
        return;
    }

    // UI State
    histBtn.disabled = true;
    const btnText = histBtn.querySelector('.btn-text');
    const loader = histBtn.querySelector('.loader');
    const originalText = btnText.textContent;

    btnText.textContent = 'Analyzing...';
    loader.classList.remove('hidden');
    histResults.classList.add('hidden');

    try {
        const res = await fetch(`${API_URL}/analyze/historical`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                description: sit,
                actual_decision: dec,
                actual_outcome: out
            })
        });

        if (!res.ok) throw new Error('Analysis failed');

        const data = await res.json();
        renderHistoricalResults(data);

    } catch (e) {
        alert('Error: ' + e.message);
    } finally {
        histBtn.disabled = false;
        btnText.textContent = originalText;
        loader.classList.add('hidden');
    }
});

function renderHistoricalResults(data) {
    histResults.classList.remove('hidden');

    // Score
    const scoreEl = document.getElementById('hist-score');
    const score = Math.round(data.principle_adherence_score * 100);
    scoreEl.textContent = `${score}%`;
    scoreEl.style.color = score > 80 ? 'var(--success-color)' : (score > 50 ? '#fbbf24' : 'var(--warning-color)');

    // Gaps
    const gapsList = document.getElementById('hist-gaps');
    if (data.gaps && data.gaps.length > 0) {
        gapsList.innerHTML = data.gaps.map(g => `
            <li>
                <strong>${g.gap_type.replace('_', ' ')}</strong>
                <p>${g.description}</p>
                <div style="font-size:0.8rem; margin-top:0.5rem; opacity:0.7">Severity: ${g.severity}/10</div>
            </li>
        `).join('');
    } else {
        gapsList.innerHTML = '<li>No significant gaps identified. Excellent adherence!</li>';
    }

    // Lessons
    const lessonsList = document.getElementById('hist-lessons');
    if (data.lessons && data.lessons.length > 0) {
        lessonsList.innerHTML = data.lessons.map(l => `
            <li>
                <strong>Insight</strong>
                <p>${l.insight}</p>
                <div style="margin-top:0.5rem; color:var(--accent-color)">👉 ${l.actionable}</div>
            </li>
        `).join('');
    } else {
        lessonsList.innerHTML = '<li>No specific lessons extracted.</li>';
    }

    // Comparison
    document.getElementById('hist-actual').textContent = data.actual_decision;
    document.getElementById('hist-recommended').innerHTML = formatText(data.recommended_decision.recommendation);

    histResults.scrollIntoView({ behavior: 'smooth' });
}

// Init
checkHealth();
// Poll every 10s
setInterval(checkHealth, 10000);
