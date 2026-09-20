/**
 * ===================================================================
 *  JARVIS Web Voice Assistant - Client-Side Controller & Audio Visualizer
 *  Author: Mohamed Anwar
 *  Features: Web Speech API, Web Audio Visualizer, Dual-Engine Fallback
 * ===================================================================
 */

class JarvisApp {
  constructor() {
    this.apiBaseUrl = window.location.origin.includes('http') ? window.location.origin : 'http://localhost:8000';
    this.isServerConnected = false;
    this.isListening = false;
    this.isSpeaking = false;
    this.audioMuted = false;
    this.selectedVoice = null;
    this.audioElement = null;

    // Speech Recognition & Synthesis
    this.recognition = null;
    this.synth = window.speechSynthesis || null;

    // Web Audio Visualizer
    this.audioCtx = null;
    this.analyser = null;
    this.micStream = null;
    this.canvas = document.getElementById('waveformCanvas');
    this.canvasCtx = this.canvas ? this.canvas.getContext('2d') : null;
    this.visualizerAnimationId = null;

    // Cache DOM Elements
    this.dom = {
      serverStatusBadge: document.getElementById('serverStatusBadge'),
      serverStatusText: document.getElementById('serverStatusText'),
      protocolStatus: document.getElementById('protocolStatus'),
      reactorCore: document.getElementById('reactorCore'),
      btnToggleMic: document.getElementById('btnToggleMic'),
      micButtonText: document.getElementById('micButtonText'),
      btnVoiceMute: document.getElementById('btnVoiceMute'),
      speakerIcon: document.getElementById('speakerIcon'),
      voiceSelect: document.getElementById('voiceSelect'),
      liveSubtitles: document.getElementById('liveSubtitles'),
      commandForm: document.getElementById('commandForm'),
      textCommandInput: document.getElementById('textCommandInput'),
      quickChipsContainer: document.getElementById('quickChipsContainer'),
      chatFeed: document.getElementById('chatFeed'),
      cpuPercentVal: document.getElementById('cpuPercentVal'),
      cpuFill: document.getElementById('cpuFill'),
      ramPercentVal: document.getElementById('ramPercentVal'),
      ramFill: document.getElementById('ramFill'),
      diskPercentVal: document.getElementById('diskPercentVal'),
      diskFill: document.getElementById('diskFill'),
      osPlatformTag: document.getElementById('osPlatformTag'),
      btnRefreshTelemetry: document.getElementById('btnRefreshTelemetry'),
      taskListContainer: document.getElementById('taskListContainer'),
      btnExportNotes: document.getElementById('btnExportNotes'),
      btnClearFeed: document.getElementById('btnClearFeed'),

      // Modals
      resumeModalOverlay: document.getElementById('resumeModalOverlay'),
      btnOpenResume: document.getElementById('btnOpenResume'),
      btnCloseResumeModal: document.getElementById('btnCloseResumeModal'),
      btnCopyBullets: document.getElementById('btnCopyBullets'),
      bulletPointsText: document.getElementById('bulletPointsText'),

      commandsModalOverlay: document.getElementById('commandsModalOverlay'),
      btnOpenCommands: document.getElementById('btnOpenCommands'),
      btnCloseCommandsModal: document.getElementById('btnCloseCommandsModal'),

      focusModalOverlay: document.getElementById('focusModalOverlay'),
      btnCloseFocusModal: document.getElementById('btnCloseFocusModal'),
      breathingCircle: document.getElementById('breathingCircle'),
      breathingInstruction: document.getElementById('breathingInstruction'),
      focusTimerClock: document.getElementById('focusTimerClock'),
      focusModalTitle: document.getElementById('focusModalTitle'),
      focusModalSub: document.getElementById('focusModalSub'),
      breathingCircleWrapper: document.getElementById('breathingCircleWrapper')
    };

    this.init();
  }

  async init() {
    this.initSpeechRecognition();
    this.initSpeechSynthesis();
    this.initEventListeners();
    this.startVisualizer();
    await this.checkServerHealth();
    this.fetchTelemetry();
    this.fetchNotes();

    // Periodic telemetry update every 10 seconds
    setInterval(() => {
      if (this.isServerConnected) this.fetchTelemetry();
    }, 10000);
  }

  // =================================================================
  // 1. SPEECH RECOGNITION (WEB SPEECH API)
  // =================================================================
  initSpeechRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      console.warn('Web Speech Recognition API is not supported in this browser.');
      this.dom.liveSubtitles.textContent = 'Microphone API unavailable. You can type commands below!';
      return;
    }

    this.recognition = new SpeechRecognition();
    this.recognition.continuous = false;
    this.recognition.interimResults = true;
    this.recognition.lang = 'en-US';

    this.recognition.onstart = () => {
      this.isListening = true;
      this.setSystemState('LISTENING', 'LISTENING // AUDIO DETECTED');
      this.dom.btnToggleMic.classList.add('active');
      this.dom.micButtonText.textContent = 'LISTENING...';
      this.dom.liveSubtitles.textContent = 'Listening to your voice...';
      this.connectMicrophoneVisualizer();
    };

    this.recognition.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) {
          finalTranscript += event.results[i][0].transcript;
        } else {
          interimTranscript += event.results[i][0].transcript;
        }
      }

      const displayTranscript = finalTranscript || interimTranscript;
      if (displayTranscript) {
        this.dom.liveSubtitles.textContent = `"${displayTranscript}"`;
      }

      if (finalTranscript) {
        this.handleUserQuery(finalTranscript.trim());
      }
    };

    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      this.stopListening();
      if (event.error === 'not-allowed') {
        this.dom.liveSubtitles.textContent = 'Microphone permission blocked. Use keyboard input below.';
      } else {
        this.dom.liveSubtitles.textContent = 'Speech interrupted. Click Initiate Voice to try again.';
      }
    };

    this.recognition.onend = () => {
      this.stopListening();
    };
  }

  toggleListening() {
    if (!this.recognition) {
      alert('Speech Recognition is not supported by your browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    if (this.isListening) {
      this.recognition.stop();
      this.stopListening();
    } else {
      try {
        if (this.synth && this.synth.speaking) {
          this.synth.cancel();
        }
        this.recognition.start();
      } catch (err) {
        console.warn('Recognition start exception:', err);
      }
    }
  }

  stopListening() {
    this.isListening = false;
    this.setSystemState('IDLE', 'IDLE // STANDBY');
    this.dom.btnToggleMic.classList.remove('active');
    this.dom.micButtonText.textContent = 'INITIATE VOICE';
  }

  // =================================================================
  // 2. SPEECH SYNTHESIS (VOICE OUTPUT)
  // =================================================================
  initSpeechSynthesis() {
    if (!this.synth) return;

    const populateVoices = () => {
      const voices = this.synth.getVoices();
      if (!voices.length) return;

      this.dom.voiceSelect.innerHTML = '';
      voices.forEach((v, idx) => {
        if (v.lang.includes('en')) {
          const opt = document.createElement('option');
          opt.value = idx;
          opt.textContent = `${v.name} (${v.lang})`;
          if (v.name.includes('Google') || v.name.includes('Natural') || v.default) {
            opt.selected = true;
            this.selectedVoice = v;
          }
          this.dom.voiceSelect.appendChild(opt);
        }
      });

      if (!this.selectedVoice && voices.length) {
        this.selectedVoice = voices[0];
      }
    };

    populateVoices();
    if (this.synth.onvoiceschanged !== undefined) {
      this.synth.onvoiceschanged = populateVoices;
    }

    this.dom.voiceSelect.addEventListener('change', (e) => {
      const voices = this.synth.getVoices();
      this.selectedVoice = voices[e.target.value] || null;
    });
  }

  speak(text) {
    if (!this.synth || this.audioMuted || !text) return;

    this.synth.cancel(); // Stop prior speech

    const utterance = new SpeechSynthesisUtterance(text);
    if (this.selectedVoice) {
      utterance.voice = this.selectedVoice;
    }
    utterance.rate = 1.0;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.setSystemState('SPEAKING', 'TRANSMITTING // AUDIO OUT');
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.setSystemState('IDLE', 'IDLE // STANDBY');
    };

    utterance.onerror = () => {
      this.isSpeaking = false;
      this.setSystemState('IDLE', 'IDLE // STANDBY');
    };

    this.synth.speak(utterance);
  }

  // =================================================================
  // 3. AUDIO VISUALIZER (WEB AUDIO API & CANVAS)
  // =================================================================
  async connectMicrophoneVisualizer() {
    try {
      if (!this.audioCtx) {
        this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (this.audioCtx.state === 'suspended') {
        await this.audioCtx.resume();
      }
      if (!this.micStream) {
        this.micStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
        const source = this.audioCtx.createMediaStreamSource(this.micStream);
        this.analyser = this.audioCtx.createAnalyser();
        this.analyser.fftSize = 64;
        source.connect(this.analyser);
      }
    } catch (e) {
      // Audio capture permission denied or unsupported; visualizer falls back to synthetic wave
    }
  }

  startVisualizer() {
    if (!this.canvas || !this.canvasCtx) return;

    let phase = 0;

    const render = () => {
      this.visualizerAnimationId = requestAnimationFrame(render);
      const width = this.canvas.width;
      const height = this.canvas.height;
      this.canvasCtx.clearRect(0, 0, width, height);

      if (this.isListening && this.analyser) {
        // Real microphone data
        const bufferLength = this.analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        this.analyser.getByteFrequencyData(dataArray);

        const barWidth = (width / bufferLength) * 1.5;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const barHeight = (dataArray[i] / 255) * height * 0.9;
          this.canvasCtx.fillStyle = `rgba(0, 240, 255, ${0.4 + dataArray[i] / 255})`;
          this.canvasCtx.fillRect(x, height - barHeight, barWidth - 2, barHeight);
          x += barWidth;
        }
      } else {
        // Synthetic animated sine wave (idle or speaking)
        phase += this.isSpeaking ? 0.08 : 0.03;
        this.canvasCtx.beginPath();
        this.canvasCtx.lineWidth = 2;
        this.canvasCtx.strokeStyle = this.isSpeaking ? '#a855f7' : 'rgba(0, 240, 255, 0.6)';

        const amplitude = this.isSpeaking ? 16 : 6;
        const frequency = 0.03;

        for (let x = 0; x < width; x++) {
          const y = height / 2 + Math.sin(x * frequency + phase) * amplitude;
          if (x === 0) this.canvasCtx.moveTo(x, y);
          else this.canvasCtx.lineTo(x, y);
        }
        this.canvasCtx.stroke();
      }
    };

    render();
  }

  setSystemState(state, protocolText) {
    this.dom.protocolStatus.textContent = protocolText;
    this.dom.reactorCore.className = 'reactor-core';
    if (state === 'LISTENING') {
      this.dom.reactorCore.classList.add('listening');
    } else if (state === 'SPEAKING') {
      this.dom.reactorCore.classList.add('speaking');
    }
  }

  // =================================================================
  // 4. COMMAND EXECUTION & DUAL-ENGINE ROUTING
  // =================================================================
  async handleUserQuery(query) {
    if (!query) return;

    // Render user message card
    this.appendMessage('user', query);
    this.setSystemState('PROCESSING', 'ANALYZING INTENT...');

    let response = null;

    if (this.isServerConnected) {
      try {
        const res = await fetch(`${this.apiBaseUrl}/api/command`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ command: query })
        });
        if (res.ok) {
          response = await res.json();
        }
      } catch (e) {
        console.warn('Backend API request failed, switching to client fallback engine.');
      }
    }

    // If backend unreachable or standalone, use embedded client-side brain
    if (!response) {
      response = this.clientSideCommandDispatcher(query);
    }

    this.processAssistantResponse(response);
  }

  processAssistantResponse(res) {
    const speech = res.speech || 'Command executed.';
    this.appendMessage('jarvis', speech, res.display);
    this.speak(speech);

    // Handle interactive actions
    if (res.action === 'START_POMODORO') {
      this.launchPomodoroTimer(res.pomodoro?.duration_minutes || 25);
    } else if (res.action === 'BREATHING_EXERCISE') {
      this.launchBreathingExercise();
    } else if (res.action === 'PLAY_AUDIO') {
      this.playAudio(res.audio?.url);
    } else if (res.action === 'STOP_AUDIO') {
      this.stopAudio();
    } else if (res.action === 'OPEN_URL') {
      window.open(res.url, '_blank');
    }

    // Refresh sidebars if notes/todos were updated
    if (res.category === 'notes' || res.category === 'todos') {
      this.fetchNotes();
    }
    if (res.category === 'system') {
      this.fetchTelemetry();
    }
  }

  // =================================================================
  // 5. CLIENT-SIDE INTENT FALLBACK ENGINE (ZERO-DEPENDENCY)
  // =================================================================
  clientSideCommandDispatcher(rawQuery) {
    const q = rawQuery.toLowerCase().trim();

    if (q.includes('hello') || q.includes('hi jarvis')) {
      return {
        speech: "Hello! I am Jarvis. All web client systems operational. How can I assist your productivity today?",
        display: { title: "Systems Online", status: "Client Engine Active" }
      };
    }

    if (q.includes('explain quantum computing')) {
      return {
        speech: "Quantum computing leverages superposition and entanglement to solve intractable computational problems exponentially faster than classical computers.",
        display: {
          title: "Knowledge Capsule: Quantum Computing",
          summary: "Operates on qubits capable of existing as both 0 and 1 simultaneously.",
          key_points: ["Superposition & Entanglement", "Shor's Algorithm", "Molecular Simulation"]
        }
      };
    }

    if (q.includes('explain microservices')) {
      return {
        speech: "Microservices is an architectural style arranging an application into loosely coupled, independently deployable services communicating via REST or message queues.",
        display: {
          title: "Knowledge Capsule: Microservices",
          summary: "Modular architecture enabling independent scaling, rapid deployment, and high fault tolerance."
        }
      };
    }

    if (q.includes('binary search')) {
      return {
        speech: "Generated O(log n) binary search implementation in Python.",
        display: {
          title: "Algorithm: Binary Search",
          language: "python",
          code: `def binary_search(arr, target):\n    low, high = 0, len(arr) - 1\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n    return -1`
        }
      };
    }

    if (q.includes('bitcoin') || q.includes('btc')) {
      return {
        speech: "Bitcoin is currently trading around $80,400 USD with positive momentum.",
        display: {
          title: "Crypto Tracker: BTC",
          price_usd: "$80,400.00",
          change_24h: "+2.1%",
          source: "Realtime Benchmark"
        }
      };
    }

    if (q.includes('pomodoro')) {
      return {
        action: 'START_POMODORO',
        speech: "Starting 25-minute Pomodoro focus session. Deep work protocol active.",
        pomodoro: { duration_minutes: 25 }
      };
    }

    if (q.includes('breathe') || q.includes('breathing')) {
      return {
        action: 'BREATHING_EXERCISE',
        speech: "Initiating 4-7-8 relaxation breathing protocol. Follow the guided circle.",
        display: { title: "4-7-8 Breathing" }
      };
    }

    if (q.includes('joke')) {
      const jokes = [
        "Why do programmers prefer dark mode? Because light attracts bugs!",
        "Why did the Python developer wear glasses? Because they couldn't C sharp!",
        "There are 10 types of people: those who understand binary, and those who don't."
      ];
      const joke = jokes[Math.floor(Math.random() * jokes.length)];
      return { speech: joke, display: { title: "Developer Joke 😂", joke } };
    }

    if (q.includes('time')) {
      const now = new Date().toLocaleTimeString();
      return { speech: `The current time is ${now}.`, display: { title: "Current Time", time: now } };
    }

    if (q.includes('play lofi')) {
      return {
        action: 'PLAY_AUDIO',
        speech: "Streaming Lofi chill beats for concentration.",
        audio: { url: "https://stream.zeno.fm/f3wvbbqmdg8uv" }
      };
    }

    return {
      speech: `Processed query: "${rawQuery}". Try asking about tech concepts, algorithms, Pomodoro timers, or crypto prices!`,
      display: { title: "Query Processed", input: rawQuery }
    };
  }

  // =================================================================
  // 6. UI CARD & CHAT FEED RENDERING
  // =================================================================
  appendMessage(sender, text, displayData = null) {
    const card = document.createElement('div');
    card.className = `message-card ${sender === 'user' ? 'user-msg' : 'jarvis-msg'}`;

    const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const senderLabel = sender === 'user' ? 'YOU' : 'JARVIS CORE';

    let displayHtml = '';

    if (displayData) {
      if (displayData.code) {
        displayHtml += `
          <div class="code-preview-box">
            <div class="code-header">
              <span>${(displayData.language || 'code').toUpperCase()}</span>
              <button class="copy-code-btn" onclick="navigator.clipboard.writeText(\`${displayData.code.replace(/`/g, '\\`')}\`); this.textContent = 'Copied!';">Copy</button>
            </div>
            <pre><code>${this.escapeHtml(displayData.code)}</code></pre>
          </div>
        `;
      } else if (displayData.price_usd) {
        displayHtml += `
          <div style="margin-top:8px; padding:8px 12px; background:rgba(0,240,255,0.06); border-radius:6px; font-family:var(--font-mono); font-size:13px;">
            <strong style="color:var(--cyan-primary);">${displayData.title || 'Market'}</strong>: ${displayData.price_usd} (${displayData.change_24h || '0.0%'})
          </div>
        `;
      }
    }

    card.innerHTML = `
      <div class="msg-meta">
        <span class="sender-tag">${senderLabel}</span>
        <span class="msg-time">${now}</span>
      </div>
      <div class="msg-body">${this.escapeHtml(text)}</div>
      ${displayHtml}
    `;

    this.dom.chatFeed.appendChild(card);
    this.dom.chatFeed.scrollTop = this.dom.chatFeed.scrollHeight;
  }

  escapeHtml(str) {
    return str ? str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;') : '';
  }

  // =================================================================
  // 7. TELEMETRY, TASKS & API INTEGRATION
  // =================================================================
  async checkServerHealth() {
    try {
      const res = await fetch(`${this.apiBaseUrl}/api/health`, { timeout: 3000 });
      if (res.ok) {
        this.isServerConnected = true;
        this.dom.serverStatusText.textContent = 'ONLINE [FASTAPI]';
        this.dom.serverStatusBadge.querySelector('.status-indicator').className = 'status-indicator live';
        return;
      }
    } catch (e) {
      // Backend not running
    }
    this.isServerConnected = false;
    this.dom.serverStatusText.textContent = 'STANDALONE [BROWSER]';
    this.dom.serverStatusBadge.querySelector('.status-indicator').className = 'status-indicator';
    this.dom.serverStatusBadge.querySelector('.status-indicator').style.background = '#38bdf8';
  }

  async fetchTelemetry() {
    if (!this.isServerConnected) {
      // Fallback synthetic telemetry
      this.updateTelemetryUI({
        cpu_percent: Math.floor(12 + Math.random() * 8),
        ram_percent: 48,
        disk_percent: 58,
        os: 'Web Platform'
      });
      return;
    }

    try {
      const res = await fetch(`${this.apiBaseUrl}/api/telemetry`);
      if (res.ok) {
        const data = await res.json();
        const telem = data.display?.telemetry || data;
        this.updateTelemetryUI(telem);
      }
    } catch (e) {
      console.warn('Telemetry fetch error:', e);
    }
  }

  updateTelemetryUI(telem) {
    const cpu = telem.cpu_percent || 15;
    const ram = telem.ram_percent || 45;
    const disk = telem.disk_percent || 55;

    this.dom.cpuPercentVal.textContent = `${cpu}%`;
    this.dom.cpuFill.style.width = `${cpu}%`;

    this.dom.ramPercentVal.textContent = `${ram}%`;
    this.dom.ramFill.style.width = `${ram}%`;

    this.dom.diskPercentVal.textContent = `${disk}%`;
    this.dom.diskFill.style.width = `${disk}%`;

    if (telem.os) {
      this.dom.osPlatformTag.textContent = `OS: ${telem.os.split(' ')[0]}`;
    }
  }

  async fetchNotes() {
    if (!this.isServerConnected) return;

    try {
      const res = await fetch(`${this.apiBaseUrl}/api/todos`);
      if (res.ok) {
        const data = await res.json();
        const todos = data.display?.todos || [];
        this.renderTasks(todos);
      }
    } catch (e) {
      console.warn('Task fetch error:', e);
    }
  }

  renderTasks(tasks) {
    if (!tasks || !tasks.length) return;
    this.dom.taskListContainer.innerHTML = '';
    tasks.slice(0, 5).forEach((t) => {
      const div = document.createElement('div');
      div.className = 'task-item';
      div.innerHTML = `
        <span class="task-bullet" style="color:${t.done ? '#10b981' : 'var(--cyan-primary)'}">▸</span>
        <span class="task-text" style="text-decoration:${t.done ? 'line-through' : 'none'}; color:${t.done ? '#64748b' : 'inherit'}">${this.escapeHtml(t.task)}</span>
      `;
      this.dom.taskListContainer.appendChild(div);
    });
  }

  // =================================================================
  // 8. INTERACTIVE MODALS & FOCUS TIMERS
  // =================================================================
  launchBreathingExercise() {
    this.dom.focusModalOverlay.classList.remove('hidden');
    this.dom.focusModalTitle.textContent = '4-7-8 Guided Breathing';
    this.dom.focusModalSub.textContent = 'Inhale 4s, Hold 7s, Exhale 8s. Center your mind.';
    this.dom.focusTimerClock.classList.add('hidden');
    this.dom.breathingCircleWrapper.style.display = 'flex';

    let step = 0;
    const cycle = () => {
      if (this.dom.focusModalOverlay.classList.contains('hidden')) return;

      if (step === 0) {
        this.dom.breathingInstruction.textContent = 'INHALE (4s)';
        this.dom.breathingCircle.style.transform = 'scale(1.5)';
        setTimeout(() => { step = 1; cycle(); }, 4000);
      } else if (step === 1) {
        this.dom.breathingInstruction.textContent = 'HOLD (7s)';
        setTimeout(() => { step = 2; cycle(); }, 7000);
      } else {
        this.dom.breathingInstruction.textContent = 'EXHALE (8s)';
        this.dom.breathingCircle.style.transform = 'scale(1.0)';
        setTimeout(() => { step = 0; cycle(); }, 8000);
      }
    };
    cycle();
  }

  launchPomodoroTimer(minutes = 25) {
    this.dom.focusModalOverlay.classList.remove('hidden');
    this.dom.focusModalTitle.textContent = 'Pomodoro Deep Focus';
    this.dom.focusModalSub.textContent = 'Stay immersed in your task. Silence distractions.';
    this.dom.breathingCircleWrapper.style.display = 'none';
    this.dom.focusTimerClock.classList.remove('hidden');

    let totalSeconds = minutes * 60;
    const interval = setInterval(() => {
      if (this.dom.focusModalOverlay.classList.contains('hidden') || totalSeconds <= 0) {
        clearInterval(interval);
        if (totalSeconds <= 0) {
          this.speak('Pomodoro focus session completed! Great job. Take a 5 minute break.');
          alert('⏰ Pomodoro session complete! Take a break.');
        }
        return;
      }
      totalSeconds--;
      const m = Math.floor(totalSeconds / 60).toString().padStart(2, '0');
      const s = (totalSeconds % 60).toString().padStart(2, '0');
      this.dom.focusTimerClock.textContent = `${m}:${s}`;
    }, 1000);
  }

  playAudio(url) {
    if (!url) return;
    this.stopAudio();
    this.audioElement = new Audio(url);
    this.audioElement.play().catch(e => console.warn('Audio play restricted by browser policy:', e));
  }

  stopAudio() {
    if (this.audioElement) {
      this.audioElement.pause();
      this.audioElement = null;
    }
  }

  // =================================================================
  // 9. EVENT LISTENERS & KEYBOARD SHORTCUTS
  // =================================================================
  initEventListeners() {
    // Mic Button Toggle
    this.dom.btnToggleMic.addEventListener('click', () => this.toggleListening());

    // Audio Voice Mute Toggle
    this.dom.btnVoiceMute.addEventListener('click', () => {
      this.audioMuted = !this.audioMuted;
      this.dom.btnVoiceMute.style.opacity = this.audioMuted ? '0.4' : '1.0';
      if (this.audioMuted && this.synth) this.synth.cancel();
    });

    // Form Submit
    this.dom.commandForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const val = this.dom.textCommandInput.value.trim();
      if (val) {
        this.dom.textCommandInput.value = '';
        this.handleUserQuery(val);
      }
    });

    // Quick Prompt Chips
    this.dom.quickChipsContainer.addEventListener('click', (e) => {
      const chip = e.target.closest('.chip-btn');
      if (chip) {
        const query = chip.getAttribute('data-query');
        this.handleUserQuery(query);
      }
    });

    // Refresh Telemetry Button
    this.dom.btnRefreshTelemetry.addEventListener('click', () => this.fetchTelemetry());

    // Clear Feed
    this.dom.btnClearFeed.addEventListener('click', () => {
      this.dom.chatFeed.innerHTML = '';
      this.appendMessage('jarvis', 'Feed cleared. Ready for your next query.');
    });

    // Export Notes as Markdown Download
    this.dom.btnExportNotes.addEventListener('click', () => {
      const mdContent = `# JARVIS Assistant Export\nGenerated: ${new Date().toLocaleString()}\n\n- [x] Tested Voice AI Web Platform\n- [x] Reviewed full-stack FastAPI architecture\n`;
      const blob = new Blob([mdContent], { type: 'text/markdown' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `jarvis_notes_${Date.now()}.md`;
      a.click();
    });

    // Resume Showcase Modal
    this.dom.btnOpenResume.addEventListener('click', () => this.dom.resumeModalOverlay.classList.remove('hidden'));
    this.dom.btnCloseResumeModal.addEventListener('click', () => this.dom.resumeModalOverlay.classList.add('hidden'));

    // Copy Bullets Button
    this.dom.btnCopyBullets.addEventListener('click', () => {
      const items = Array.from(this.dom.bulletPointsText.querySelectorAll('li')).map(li => li.innerText).join('\n\n');
      navigator.clipboard.writeText(items).then(() => {
        this.dom.btnCopyBullets.textContent = 'COPIED!';
        setTimeout(() => { this.dom.btnCopyBullets.textContent = 'Copy All Bullets'; }, 2000);
      });
    });

    // Tab Navigation in Resume Modal
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
        const target = document.getElementById(btn.getAttribute('data-tab'));
        if (target) target.classList.add('active');
      });
    });

    // Commands Modal
    this.dom.btnOpenCommands.addEventListener('click', () => this.dom.commandsModalOverlay.classList.remove('hidden'));
    this.dom.btnCloseCommandsModal.addEventListener('click', () => this.dom.commandsModalOverlay.classList.add('hidden'));

    // Focus Modal Close
    this.dom.btnCloseFocusModal.addEventListener('click', () => this.dom.focusModalOverlay.classList.add('hidden'));

    // Modal Background Clicks to Close
    [this.dom.resumeModalOverlay, this.dom.commandsModalOverlay, this.dom.focusModalOverlay].forEach(overlay => {
      overlay.addEventListener('click', (e) => {
        if (e.target === overlay) overlay.classList.add('hidden');
      });
    });

    // Keyboard Shortcuts: Space to speak, Escape to close
    window.addEventListener('keydown', (e) => {
      const isInputFocused = document.activeElement === this.dom.textCommandInput;
      if (e.code === 'Space' && !isInputFocused) {
        e.preventDefault();
        this.toggleListening();
      } else if (e.code === 'Escape') {
        this.dom.resumeModalOverlay.classList.add('hidden');
        this.dom.commandsModalOverlay.classList.add('hidden');
        this.dom.focusModalOverlay.classList.add('hidden');
        if (this.isListening) this.stopListening();
      }
    });
  }
}

// Instantiate App on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  window.jarvisApp = new JarvisApp();
});
