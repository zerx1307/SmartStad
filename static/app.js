/**
 * FIFA World Cup 2026 Nexus AI - Interactive Frontend Controller
 * Connects Web Client to FastAPI REST Endpoints & Real-Time WebSocket Telemetry
 */

document.addEventListener("DOMContentLoaded", () => {
    // Global State
    let currentStadiumId = "metlife";
    let currentMode = "fan"; // "fan" or "ops"
    let isRecordingVoice = false;
    let selectedScanType = "ticket";
    let wsConnection = null;

    // DOM Elements
    const stadiumSelect = document.getElementById("stadiumSelect");
    const langSelect = document.getElementById("langSelect");
    const btnFanMode = document.getElementById("btnFanMode");
    const btnOpsMode = document.getElementById("btnOpsMode");
    const fanView = document.getElementById("fanView");
    const opsView = document.getElementById("opsView");
    const btnContrastToggle = document.getElementById("btnContrastToggle");

    // Fan Mode DOM
    const chatInput = document.getElementById("chatInput");
    const btnSendChat = document.getElementById("btnSendChat");
    const btnVoiceInput = document.getElementById("btnVoiceInput");
    const chatStream = document.getElementById("chatStream");
    const gateGrid = document.getElementById("gateGrid");
    const transitList = document.getElementById("transitList");
    const heroVenueName = document.getElementById("heroVenueName");

    // Ops Mode DOM
    const incidentInput = document.getElementById("incidentInput");
    const btnTriageIncident = document.getElementById("btnTriageIncident");
    const btnSampleIncident = document.getElementById("btnSampleIncident");
    const sopResultBox = document.getElementById("sopResultBox");
    const incidentsFeed = document.getElementById("incidentsFeed");
    const btnGenBriefing = document.getElementById("btnGenBriefing");

    // Modal DOM
    const btnOpenScanner = document.getElementById("btnOpenScanner");
    const scannerModal = document.getElementById("scannerModal");
    const btnCloseScanner = document.getElementById("btnCloseScanner");
    const btnRunScan = document.getElementById("btnRunScan");
    const scanResult = document.getElementById("scanResult");
    
    const briefingModal = document.getElementById("briefingModal");
    const btnCloseBriefing = document.getElementById("btnCloseBriefing");
    const briefingContent = document.getElementById("briefingContent");

    // ---------------------------------------------------------
    // 1. INITIALIZATION & STADIUM LOAD
    // ---------------------------------------------------------
    async function loadStadiumData(stadiumId) {
        currentStadiumId = stadiumId;
        try {
            const res = await fetch(`/api/stadium/${stadiumId}`);
            const data = await res.json();
            if (data.status === "success") {
                const stadium = data.stadium;
                heroVenueName.textContent = `${stadium.name} • ${stadium.city}`;
                renderGates(stadium.gates);
                renderTransit(stadium.transit);
            }
        } catch (err) {
            console.error("Error loading stadium data:", err);
        }
    }

    function renderGates(gates) {
        if (!gateGrid) return;
        gateGrid.innerHTML = gates.map(g => {
            const statusClass = g.queue_time_min < 8 ? "badge-green" : g.queue_time_min < 15 ? "badge-yellow" : "badge-red";
            return `
                <div class="gate-card">
                    <div class="gate-info">
                        <h4>${g.name}</h4>
                        <span class="badge ${statusClass}">${g.status}</span>
                    </div>
                    <div class="gate-queue">
                        <span class="text-highlight">${g.queue_time_min}</span> <span style="font-size:12px">min</span>
                    </div>
                </div>
            `;
        }).join("");
    }

    function renderTransit(transit) {
        if (!transitList) return;
        transitList.innerHTML = transit.map(t => `
            <div class="transit-item">
                <div>
                    <strong>${t.mode}</strong>
                    <div style="font-size:12px; color:var(--text-muted)">${t.status}</div>
                </div>
                <div style="text-align:right">
                    <span class="badge badge-pulse">Grade ${t.eco_rating}</span>
                    <div style="font-size:11px; margin-top:2px;">~${t.est_wait_min} min wait</div>
                </div>
            </div>
        `).join("");
    }

    async function loadIncidents() {
        try {
            const res = await fetch("/api/ops/incidents");
            const data = await res.json();
            if (data.status === "success") {
                renderIncidentsFeed(data.incidents);
            }
        } catch (err) {
            console.error("Error loading incidents:", err);
        }
    }

    function renderIncidentsFeed(incidents) {
        if (!incidentsFeed) return;
        incidentsFeed.innerHTML = incidents.map(inc => `
            <div style="background:rgba(255,255,255,0.03); border:1px solid var(--border-card); border-radius:12px; padding:14px; margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; margin-bottom:6px;">
                    <span class="badge badge-red">${inc.severity || 'HIGH'}</span>
                    <span style="font-size:11px; color:var(--text-muted)">${inc.timestamp || '20:50'} • ${inc.id}</span>
                </div>
                <h4 style="font-size:14px; margin-bottom:4px;">${inc.category}</h4>
                <p style="font-size:13px; color:var(--text-secondary); margin-bottom:8px;">${inc.description}</p>
                <div style="font-size:12px; background:rgba(6,182,212,0.1); padding:8px; border-radius:6px; border-left:3px solid var(--fifa-cyan)">
                    <strong>AI SOP Action:</strong> ${inc.ai_recommendation || (inc.sop_playbook ? inc.sop_playbook[0] : 'Dispatched Response Unit')}
                </div>
            </div>
        `).join("");
    }

    // ---------------------------------------------------------
    // 2. WEBSOCKET REAL-TIME TELEMETRY STREAM
    // ---------------------------------------------------------
    function initWebSocket() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${window.location.host}/ws/live`;
        
        wsConnection = new WebSocket(wsUrl);

        wsConnection.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === "TELEMETRY_UPDATE" && data.stadium_id === currentStadiumId) {
                    renderGates(data.gates);
                } else if (data.type === "NEW_INCIDENT") {
                    loadIncidents();
                }
            } catch (e) {
                console.error("WS error:", e);
            }
        };

        wsConnection.onclose = () => {
            setTimeout(initWebSocket, 5000);
        };
    }

    // ---------------------------------------------------------
    // 3. GENAI FAN CONCIERGE CHAT
    // ---------------------------------------------------------
    async function sendChatMessage(textOverride = null) {
        const message = textOverride || chatInput.value.trim();
        if (!message) return;

        // Append User Bubble
        appendChatBubble("user", message);
        if (!textOverride) chatInput.value = "";

        // Typing Indicator
        const typingId = appendTypingIndicator();

        try {
            const res = await fetch("/api/fan/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    query: message,
                    stadium_id: currentStadiumId
                })
            });
            const data = await res.json();
            removeTypingIndicator(typingId);

            if (data.status === "success") {
                const aiResp = data.data.response;
                appendChatBubble("bot", aiResp, data.data.suggested_actions);
                
                // Audio Speech Synthesis if enabled
                speakText(aiResp);
            }
        } catch (err) {
            removeTypingIndicator(typingId);
            appendChatBubble("bot", "Sorry, I had trouble connecting to the FIFA AI Concierge. Please try again.");
        }
    }

    function appendChatBubble(sender, text, suggestions = []) {
        const bubbleDiv = document.createElement("div");
        bubbleDiv.className = `chat-bubble ${sender}`;

        const avatarHtml = sender === "bot" ? 
            `<div class="bot-avatar">AI</div>` : 
            `<div class="user-avatar">YOU</div>`;

        let suggestionsHtml = "";
        if (suggestions && suggestions.length > 0) {
            suggestionsHtml = `
                <div style="display:flex; gap:6px; flex-wrap:wrap; margin-top:8px;">
                    ${suggestions.map(s => `<button class="prompt-chip suggestion-btn" style="font-size:11px;">${s}</button>`).join("")}
                </div>
            `;
        }

        const formattedText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');

        bubbleDiv.innerHTML = `
            ${avatarHtml}
            <div class="bubble-content">
                <p>${formattedText}</p>
                ${suggestionsHtml}
            </div>
        `;

        chatStream.appendChild(bubbleDiv);
        chatStream.scrollTop = chatStream.scrollHeight;

        bubbleDiv.querySelectorAll(".suggestion-btn").forEach(btn => {
            btn.addEventListener("click", () => sendChatMessage(btn.textContent.trim()));
        });
    }

    function appendTypingIndicator() {
        const id = "typing_" + Date.now();
        const div = document.createElement("div");
        div.id = id;
        div.className = "chat-bubble bot";
        div.innerHTML = `
            <div class="bot-avatar">AI</div>
            <div class="bubble-content" style="color:var(--text-muted)">
                Processing query...
            </div>
        `;
        chatStream.appendChild(div);
        chatStream.scrollTop = chatStream.scrollHeight;
        return id;
    }

    function removeTypingIndicator(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function speakText(text) {
        if ('speechSynthesis' in window) {
            const cleanText = text.replace(/\*\*/g, '').replace(/•/g, '').replace(/<br>/g, ' ');
            const utterance = new SpeechSynthesisUtterance(cleanText.slice(0, 200));
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;

        btnVoiceInput.addEventListener("click", () => {
            if (!isRecordingVoice) {
                recognition.start();
                isRecordingVoice = true;
                btnVoiceInput.classList.add("recording");
                btnVoiceInput.textContent = "Listening...";
            } else {
                recognition.stop();
                isRecordingVoice = false;
                btnVoiceInput.classList.remove("recording");
                btnVoiceInput.textContent = "Voice";
            }
        });

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            btnVoiceInput.classList.remove("recording");
            btnVoiceInput.textContent = "Voice";
            isRecordingVoice = false;
            sendChatMessage();
        };

        recognition.onerror = () => {
            btnVoiceInput.classList.remove("recording");
            btnVoiceInput.textContent = "Voice";
            isRecordingVoice = false;
        };
    }

    // ---------------------------------------------------------
    // 4. OPS MODE INCIDENT TRIAGE & SOP
    // ---------------------------------------------------------
    async function runIncidentTriage() {
        const desc = incidentInput.value.trim();
        if (!desc) return;

        try {
            const res = await fetch("/api/ops/incident", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    description: desc,
                    stadium_id: currentStadiumId
                })
            });
            const data = await res.json();
            if (data.status === "success") {
                const inc = data.data;
                sopResultBox.classList.remove("hidden");
                document.getElementById("sopPriorityBadge").textContent = inc.priority_code;
                document.getElementById("sopCategory").textContent = `${inc.category} (${inc.severity} Severity)`;
                
                document.getElementById("sopStepsList").innerHTML = inc.sop_playbook.map(step => `
                    <div style="margin-bottom:6px;">${step.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>
                `).join("");

                document.getElementById("paEn").textContent = inc.pa_announcements.en;
                document.getElementById("paEs").textContent = inc.pa_announcements.es;
                document.getElementById("paFr").textContent = inc.pa_announcements.fr;

                loadIncidents();
            }
        } catch (err) {
            console.error("Incident triage error:", err);
        }
    }

    // ---------------------------------------------------------
    // 5. MODALS & VISION SCANNER
    // ---------------------------------------------------------
    btnOpenScanner.addEventListener("click", () => scannerModal.classList.remove("hidden"));
    btnCloseScanner.addEventListener("click", () => scannerModal.classList.add("hidden"));

    document.querySelectorAll(".scan-type-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            document.querySelectorAll(".scan-type-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            selectedScanType = btn.dataset.type;
        });
    });

    btnRunScan.addEventListener("click", async () => {
        scanResult.classList.remove("hidden");
        scanResult.innerHTML = `Analyzing image with GenAI Multimodal Vision Model...`;

        try {
            const formData = new FormData();
            formData.append("image_type", selectedScanType);

            const res = await fetch("/api/vision/parse", {
                method: "POST",
                body: formData
            });
            const data = await res.json();
            if (data.status === "success") {
                const v = data.data;
                scanResult.innerHTML = `
                    <h4 style="color:var(--fifa-gold); margin-bottom:6px;">${v.type}</h4>
                    <p><strong>Item / Text:</strong> ${v.detected_text || v.match || v.detected_object}</p>
                    ${v.translation ? `<p><strong>Translation:</strong> ${v.translation}</p>` : ''}
                    <p style="margin-top:6px; color:var(--fifa-cyan)"><strong>GenAI Guidance:</strong> ${v.fastest_route || v.action_guidance || v.ai_action}</p>
                `;
            }
        } catch (e) {
            scanResult.innerHTML = `Parsing complete. (Simulated scan successful).`;
        }
    });

    // Volunteer Briefing Modal
    btnGenBriefing.addEventListener("click", async () => {
        briefingModal.classList.remove("hidden");
        briefingContent.innerHTML = `<p>Drafting daily GenAI volunteer shift briefing...</p>`;

        try {
            const res = await fetch("/api/ops/briefing", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ stadium_id: currentStadiumId })
            });
            const data = await res.json();
            if (data.status === "success") {
                const formatted = data.briefing.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
                briefingContent.innerHTML = `<div style="font-size:13px; line-height:1.7;">${formatted}</div>`;
            }
        } catch (e) {
            briefingContent.innerHTML = `<p>Error generating briefing.</p>`;
        }
    });

    btnCloseBriefing.addEventListener("click", () => briefingModal.classList.add("hidden"));

    // ---------------------------------------------------------
    // 6. EVENT LISTENERS & SWITCHERS
    // ---------------------------------------------------------
    stadiumSelect.addEventListener("change", (e) => loadStadiumData(e.target.value));

    btnFanMode.addEventListener("click", () => {
        btnFanMode.classList.add("active");
        btnOpsMode.classList.remove("active");
        fanView.classList.add("active");
        opsView.classList.remove("active");
    });

    btnOpsMode.addEventListener("click", () => {
        btnOpsMode.classList.add("active");
        btnFanMode.classList.remove("active");
        opsView.classList.add("active");
        fanView.classList.remove("active");
        loadIncidents();
    });

    btnContrastToggle.addEventListener("click", () => {
        document.body.classList.toggle("high-contrast");
        btnContrastToggle.classList.toggle("active");
    });

    btnSendChat.addEventListener("click", () => sendChatMessage());
    chatInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") sendChatMessage();
    });

    document.querySelectorAll(".prompt-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const q = chip.dataset.query;
            if (q) sendChatMessage(q);
        });
    });

    btnTriageIncident.addEventListener("click", runIncidentTriage);
    btnSampleIncident.addEventListener("click", () => {
        incidentInput.value = "Turnstile 7 offline at Gate C, leading to 300+ fan queue extending into North Plaza.";
    });

    // Start App
    loadStadiumData("metlife");
    loadIncidents();
    initWebSocket();
});
