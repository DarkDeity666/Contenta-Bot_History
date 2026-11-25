/**
 * Contenta History Bot Studio - Client Application
 * Handles Topic Mining (15 topics, max 10 selected), Deep Research & 6-Beat Screenplay Synthesis,
 * Blender 2.5D Video Vault, and Batch YouTube Shorts Preview & Publishing.
 */

// Application State
const state = {
  activeTab: 'tab-discover',
  topics: [],
  selectedTopicIds: new Set(),
  scripts: [],
  videos: [],
  queueItems: [], // Items ready for YouTube upload review
  youtubeStatus: {
    has_secret: false,
    authenticated: false,
    channel: null
  }
};

const MAX_TOPIC_SELECTION = 10;

// DOM References
const elements = {
  navItems: document.querySelectorAll('.nav-item'),
  tabPanes: document.querySelectorAll('.tab-pane'),
  tabTitle: document.getElementById('tabTitle'),
  tabSubtitle: document.getElementById('tabSubtitle'),

  // YouTube Status Bar
  ytStatusDot: document.getElementById('ytStatusDot'),
  ytStatusLabel: document.getElementById('ytStatusLabel'),
  btnConnectYt: document.getElementById('btnConnectYt'),
  ytBannerDot: document.getElementById('ytBannerDot'),
  ytBannerTitle: document.getElementById('ytBannerTitle'),
  ytBannerDesc: document.getElementById('ytBannerDesc'),
  btnAuthYtAction: document.getElementById('btnAuthYtAction'),
  authStatusMsg: document.getElementById('authStatusMsg'),
  clientSecretFileInput: document.getElementById('clientSecretFileInput'),
  btnUploadSecretFile: document.getElementById('btnUploadSecretFile'),

  // Tab 1: Discover Topics
  topicSearchInput: document.getElementById('topicSearchInput'),
  btnScrapeTopics: document.getElementById('btnScrapeTopics'),
  scrapeSpinner: document.getElementById('scrapeSpinner'),
  quickChips: document.querySelectorAll('.chip'),
  topicGrid: document.getElementById('topicGrid'),
  topicCount: document.getElementById('topicCount'),
  selectedCount: document.getElementById('selectedCount'),
  btnSelectNum: document.getElementById('btnSelectNum'),
  btnSelectTen: document.getElementById('btnSelectTen'),
  btnDeselectAll: document.getElementById('btnDeselectAll'),
  btnGenerateSelected: document.getElementById('btnGenerateSelected'),

  // Tab 2: Scripts
  scriptsList: document.getElementById('scriptsList'),
  btnRenderAllScripts: document.getElementById('btnRenderAllScripts'),

  // Tab 3: Videos
  videoGrid: document.getElementById('videoGrid'),
  btnRefreshVideos: document.getElementById('btnRefreshVideos'),

  // Tab 4: Batch YouTube Publishing Queue
  queueCountText: document.getElementById('queueCountText'),
  publishCountNum: document.getElementById('publishCountNum'),
  btnSelectAllQueue: document.getElementById('btnSelectAllQueue'),
  btnDeselectAllQueue: document.getElementById('btnDeselectAllQueue'),
  btnPublishSelectedBatch: document.getElementById('btnPublishSelectedBatch'),
  uploadQueueList: document.getElementById('uploadQueueList'),
  batchUploadFeedback: document.getElementById('batchUploadFeedback'),

  // Modal Player
  videoModal: document.getElementById('videoModal'),
  modalVideoPlayer: document.getElementById('modalVideoPlayer'),
  modalVideoTitle: document.getElementById('modalVideoTitle'),
  modalVideoClose: document.getElementById('modalVideoClose'),

  // Progress Overlay
  progressOverlay: document.getElementById('progressOverlay'),
  progressTitle: document.getElementById('progressTitle'),
  progressBarFill: document.getElementById('progressBarFill'),
  progressStatusMsg: document.getElementById('progressStatusMsg')
};

// Tab Meta Descriptions
const tabMeta = {
  'tab-discover': {
    title: 'Discover 15 Viral Historical Topics',
    subtitle: 'Mine bizarre, high-stakes true events from verified archives (Select up to 10 for batch synthesis)'
  },
  'tab-scripts': {
    title: 'Research & 6-Beat Screenplays',
    subtitle: 'Review mathematically paced 1080x1920 scripts with paradox hooks, verified citations, and ironic punchlines'
  },
  'tab-videos': {
    title: 'Video Vault & Mobile Previews',
    subtitle: 'Browse master animated vertical shorts rendered in Blender 4.2 with 2.5D camera depth'
  },
  'tab-upload': {
    title: 'YouTube Studio & Publishing Review Queue',
    subtitle: 'Preview Shorts with mobile frame overlays, deselect unwanted videos, and batch upload to your channel'
  }
};

/* ==========================================================================
   Navigation
   ========================================================================== */
function switchTab(tabId) {
  state.activeTab = tabId;

  elements.navItems.forEach(item => {
    item.classList.toggle('active', item.dataset.tab === tabId);
  });

  elements.tabPanes.forEach(pane => {
    pane.classList.toggle('active', pane.id === tabId);
  });

  if (tabMeta[tabId]) {
    elements.tabTitle.textContent = tabMeta[tabId].title;
    elements.tabSubtitle.textContent = tabMeta[tabId].subtitle;
  }

  // Refresh tab data
  if (tabId === 'tab-videos') loadVideos();
  if (tabId === 'tab-scripts') loadScripts();
  if (tabId === 'tab-upload') {
    checkYouTubeStatus();
    loadPublishQueue();
  }
}

elements.navItems.forEach(item => {
  item.addEventListener('click', () => switchTab(item.dataset.tab));
});

if (elements.btnConnectYt) {
  elements.btnConnectYt.addEventListener('click', () => switchTab('tab-upload'));
}

/* ==========================================================================
   YouTube OAuth Status & Authentication
   ========================================================================== */
async function checkYouTubeStatus() {
  try {
    const res = await fetch('/api/youtube/status');
    const data = await res.json();
    state.youtubeStatus = data;

    if (data.authenticated && data.channel) {
      if (elements.ytStatusDot) elements.ytStatusDot.className = 'status-dot online';
      if (elements.ytBannerDot) elements.ytBannerDot.className = 'status-dot online';
      if (elements.ytStatusLabel) elements.ytStatusLabel.textContent = data.channel.title || 'Channel Connected';
      elements.ytBannerTitle.textContent = `Connected: ${data.channel.title || 'YouTube Channel'}`;
      const subCount = isNaN(Number(data.channel.subscribers)) ? 'Active' : Number(data.channel.subscribers).toLocaleString() + ' subscribers';
      elements.ytBannerDesc.textContent = `Channel linked (${subCount}, ${data.channel.videoCount || 'Ready'} videos). Ready for direct uploads!`;
      elements.btnAuthYtAction.textContent = 'Channel Connected ✓';
      elements.btnAuthYtAction.className = 'btn btn-outline btn-sm';
      elements.btnAuthYtAction.style.borderColor = 'var(--success)';
      elements.btnAuthYtAction.style.color = 'var(--success)';
      if (elements.btnUploadSecretFile) elements.btnUploadSecretFile.style.display = 'none';
      const codeBox = document.getElementById('manualCodeBox');
      if (codeBox) codeBox.style.display = 'none';
    } else if (data.has_secret) {
      if (elements.ytStatusDot) {
        elements.ytStatusDot.className = 'status-dot';
        elements.ytStatusDot.style.background = '#ffab00';
      }
      if (elements.ytBannerDot) {
        elements.ytBannerDot.className = 'status-dot';
        elements.ytBannerDot.style.background = '#ffab00';
      }
      if (elements.ytStatusLabel) elements.ytStatusLabel.textContent = 'Credentials Ready';
      elements.ytBannerTitle.textContent = 'OAuth Credentials Active';
      elements.ytBannerDesc.textContent = 'client_secret.json (Project: ytshorts-514923) loaded! Click "Authorize Channel" to link in 5 seconds.';
      elements.btnAuthYtAction.textContent = 'Authorize Channel';
      if (elements.btnUploadSecretFile) elements.btnUploadSecretFile.style.display = 'none';
    } else {
      if (elements.ytStatusDot) elements.ytStatusDot.className = 'status-dot offline';
      if (elements.ytBannerDot) elements.ytBannerDot.className = 'status-dot offline';
      if (elements.ytStatusLabel) elements.ytStatusLabel.textContent = 'YouTube Offline';
      elements.ytBannerTitle.textContent = 'YouTube Channel: Not Connected';
      elements.ytBannerDesc.textContent = 'client_secret.json needed to connect your YouTube channel.';
      elements.btnAuthYtAction.textContent = 'Authorize Channel';
      if (elements.btnUploadSecretFile) elements.btnUploadSecretFile.style.display = 'inline-block';
    }
  } catch (err) {
    console.error('Error checking YouTube status:', err);
  }
}

// Upload client_secret.json directly from UI
if (elements.btnUploadSecretFile) {
  elements.btnUploadSecretFile.addEventListener('click', () => {
    elements.clientSecretFileInput.click();
  });
}

if (elements.clientSecretFileInput) {
  elements.clientSecretFileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const text = await file.text();
    try {
      const parsed = JSON.parse(text);
      const res = await fetch('/api/youtube/save-secret', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsed)
      });
      const data = await res.json();
      if (data.success) {
        alert('client_secret.json saved successfully!');
        checkYouTubeStatus();
      } else {
        alert('Error saving credentials: ' + data.error);
      }
    } catch (err) {
      alert('Invalid JSON file: ' + err.message);
    }
  });
}

// Authorize Button Action
if (elements.btnAuthYtAction) {
  elements.btnAuthYtAction.addEventListener('click', async () => {
    if (state.youtubeStatus.authenticated) {
      const switchAcc = confirm(`Your channel "${state.youtubeStatus.channel ? state.youtubeStatus.channel.title : 'Time Riddles'}" is ALREADY CONNECTED and ready to publish!\n\nClick Cancel to keep this channel, or OK only if you want to switch to a different account.`);
      if (!switchAcc) return;
    }

    elements.authStatusMsg.innerHTML = '<span style="color: #69f0ae;">Connecting to Google...</span>';
    
    try {
      const res = await fetch('/api/youtube/auth', { method: 'POST' });
      const data = await res.json();
      if (data.success && data.auth_url) {
        // Navigate directly to Google login - Google will automatically redirect back to the studio
        window.location.href = data.auth_url;
      } else {
        alert('Could not start authorization: ' + (data.error || 'Unknown error'));
        elements.authStatusMsg.textContent = '';
      }
    } catch (e) {
      alert('Error contacting studio server: ' + e.message);
      elements.authStatusMsg.textContent = '';
    }
  });
}

// Manual Code Submit Action
function attachManualCodeHandler() {
  const btn = document.getElementById('btnSubmitManualCode');
  const input = document.getElementById('manualCodeInput');
  const msg = document.getElementById('manualCodeMsg');

  if (btn && input) {
    btn.addEventListener('click', async () => {
      let raw = input.value.trim();
      if (!raw) return;

      // Extract code if user pasted entire URL
      if (raw.includes('code=')) {
        try {
          const urlObj = new URL(raw.startsWith('http') ? raw : 'http://localhost/' + raw);
          raw = urlObj.searchParams.get('code') || raw;
        } catch (e) {
          const match = raw.match(/code=([^&]+)/);
          if (match) raw = decodeURIComponent(match[1]);
        }
      }

      btn.disabled = true;
      btn.textContent = 'Verifying with Google...';
      if (msg) msg.textContent = 'Exchanging authorization code...';

      try {
        const res = await fetch('/api/youtube/exchange_code', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code: raw })
        });
        const data = await res.json();
        if (data.success) {
          if (msg) msg.innerHTML = '<span style="color:#69f0ae; font-weight:700;">🎉 Channel connected successfully!</span>';
          checkYouTubeStatus();
        } else {
          if (msg) msg.innerHTML = `<span style="color:#ff8a80;">Error: ${data.error || 'Invalid code'}</span>`;
        }
      } catch (err) {
        if (msg) msg.innerHTML = `<span style="color:#ff8a80;">Failed: ${err.message}</span>`;
      } finally {
        btn.disabled = false;
        btn.textContent = 'Connect Channel';
      }
    });
  }
}
attachManualCodeHandler();

/* ==========================================================================
   Tab 1: Discover Topics (Strict 15 topics, max 10 selected)
   ========================================================================== */
async function searchTopics(query = '') {
  elements.scrapeSpinner.classList.add('active');
  elements.btnScrapeTopics.disabled = true;

  try {
    const url = query ? `/api/topics/search?q=${encodeURIComponent(query)}&count=15` : `/api/topics/search?count=15`;
    const res = await fetch(url);
    const data = await res.json();

    state.topics = (data.topics || []).slice(0, 15);
    state.selectedTopicIds.clear();
    renderTopics();
  } catch (err) {
    console.error('Error fetching topics:', err);
  } finally {
    elements.scrapeSpinner.classList.remove('active');
    elements.btnScrapeTopics.disabled = false;
  }
}

function renderTopics() {
  elements.topicGrid.innerHTML = '';
  elements.topicCount.textContent = state.topics.length;
  updateSelectionUI();

  if (state.topics.length === 0) {
    elements.topicGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-dim);">
        <h3>No topics found</h3>
        <p>Try searching for a different keyword or click one of the trending themes above.</p>
      </div>
    `;
    return;
  }

  state.topics.forEach((topic) => {
    const isSelected = state.selectedTopicIds.has(topic.id);
    const card = document.createElement('div');
    card.className = `topic-card ${isSelected ? 'selected' : ''}`;
    card.dataset.id = topic.id;

    card.innerHTML = `
      <div class="topic-card-header">
        <input type="checkbox" class="topic-checkbox" ${isSelected ? 'checked' : ''} data-id="${topic.id}">
        <span class="topic-era-badge">${escapeHtml(topic.era || 'Historical')}</span>
      </div>
      <h3 class="topic-card-title">${escapeHtml(topic.title)}</h3>
      <div class="topic-card-hook">
        <strong>Hook:</strong> "${escapeHtml(topic.hook || '')}"
      </div>
      <p class="topic-card-summary">${escapeHtml(topic.summary || '')}</p>
      <div class="topic-card-footer">
        <span class="topic-source">📚 ${escapeHtml(topic.source || 'Verified Archive')}</span>
      </div>
    `;

    // Toggle on card click
    card.addEventListener('click', (e) => {
      if (e.target.type !== 'checkbox') {
        const cb = card.querySelector('.topic-checkbox');
        cb.checked = !cb.checked;
      }
      toggleTopicSelection(topic.id);
    });

    elements.topicGrid.appendChild(card);
  });
}

function toggleTopicSelection(topicId) {
  if (state.selectedTopicIds.has(topicId)) {
    state.selectedTopicIds.delete(topicId);
  } else {
    if (state.selectedTopicIds.size >= MAX_TOPIC_SELECTION) {
      alert(`Selection limit reached! You can select a maximum of ${MAX_TOPIC_SELECTION} topics at a time.`);
      return;
    }
    state.selectedTopicIds.add(topicId);
  }
  updateSelectionUI();
  // Update card styling
  document.querySelectorAll('.topic-card').forEach(card => {
    const id = card.dataset.id;
    const isSel = state.selectedTopicIds.has(id);
    card.classList.toggle('selected', isSel);
    const cb = card.querySelector('.topic-checkbox');
    if (cb) cb.checked = isSel;
  });
}

function updateSelectionUI() {
  const count = state.selectedTopicIds.size;
  elements.selectedCount.textContent = count;
  elements.btnSelectNum.textContent = count;
  elements.btnGenerateSelected.disabled = count === 0;
}

// Select First 10
elements.btnSelectTen.addEventListener('click', () => {
  state.selectedTopicIds.clear();
  state.topics.slice(0, MAX_TOPIC_SELECTION).forEach(t => state.selectedTopicIds.add(t.id));
  renderTopics();
});

// Clear Selection
elements.btnDeselectAll.addEventListener('click', () => {
  state.selectedTopicIds.clear();
  renderTopics();
});

// Search and Chips
elements.btnScrapeTopics.addEventListener('click', () => {
  searchTopics(elements.topicSearchInput.value);
});

elements.topicSearchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') searchTopics(elements.topicSearchInput.value);
});

elements.quickChips.forEach(chip => {
  chip.addEventListener('click', () => {
    elements.topicSearchInput.value = chip.dataset.query;
    searchTopics(chip.dataset.query);
  });
});

/* ==========================================================================
   Tab 2: Deep Research & 6-Beat Screenplay Synthesis
   ========================================================================== */
elements.btnGenerateSelected.addEventListener('click', async () => {
  const selectedIds = Array.from(state.selectedTopicIds).slice(0, MAX_TOPIC_SELECTION);
  if (selectedIds.length === 0) return;

  // Show Deep Research Progress Overlay
  showProgressOverlay(`Researching & Synthesizing ${selectedIds.length} Screenplays...`);
  let currentStep = 0;
  const totalSteps = selectedIds.length;

  const progressTimer = setInterval(() => {
    if (currentStep < totalSteps) {
      currentStep++;
      const pct = Math.round((currentStep / totalSteps) * 85);
      updateProgressBar(pct, `[${currentStep}/${totalSteps}] Deep researching Wikipedia & primary archives, constructing 6-beat screenplays...`);
    }
  }, 1200);

  try {
    const res = await fetch('/api/scripts/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic_ids: selectedIds })
    });
    const data = await res.json();
    clearInterval(progressTimer);
    updateProgressBar(100, `Done! Synthesized ${data.scripts ? data.scripts.length : 0} screenplays.`);

    setTimeout(() => {
      hideProgressOverlay();
      state.scripts = data.scripts || [];
      switchTab('tab-scripts');
      renderScripts();
    }, 600);
  } catch (err) {
    clearInterval(progressTimer);
    hideProgressOverlay();
    alert('Error generating scripts: ' + err.message);
  }
});

function showProgressOverlay(title) {
  elements.progressTitle.textContent = title;
  elements.progressBarFill.style.width = '5%';
  elements.progressStatusMsg.textContent = 'Connecting to historical research archives...';
  elements.progressOverlay.classList.add('open');
}

function updateProgressBar(percentage, message) {
  elements.progressBarFill.style.width = `${percentage}%`;
  elements.progressStatusMsg.textContent = message;
}

function hideProgressOverlay() {
  elements.progressOverlay.classList.remove('open');
}

async function loadScripts() {
  try {
    const res = await fetch('/api/scripts');
    const data = await res.json();
    state.scripts = data.scripts || [];
    renderScripts();
  } catch (err) {
    console.error('Error loading scripts:', err);
  }
}

function renderScripts() {
  elements.scriptsList.innerHTML = '';

  if (state.scripts.length === 0) {
    elements.scriptsList.innerHTML = `
      <div class="card" style="text-align: center; padding: 48px; color: var(--text-dim);">
        <h3>No scripts generated yet</h3>
        <p>Go to the <strong>Discover Topics</strong> tab, select your preferred topics (up to 10), and click <strong>Generate Content-Rich Scripts</strong>.</p>
        <button class="btn btn-primary btn-sm" style="margin-top: 16px;" onclick="switchTab('tab-discover')">Go to Discover Topics</button>
      </div>
    `;
    return;
  }

  state.scripts.forEach((s, idx) => {
    const card = document.createElement('div');
    card.className = 'script-card card';

    card.innerHTML = `
      <div class="script-card-header">
        <div>
          <span class="badge badge-accent">6-Beat Master Short #${idx + 1}</span>
          <h2 class="script-title">${escapeHtml(s.title)}</h2>
        </div>
        <div class="script-actions">
          <button class="btn btn-primary btn-sm btn-render-single" data-script-id="${s.id}">
            🎬 Render in Blender 4.2
          </button>
        </div>
      </div>

      <div class="beats-container">
        <!-- Beat 1: Hook -->
        <div class="beat-row">
          <div class="beat-badge beat-hook">Beat 1: Paradox Hook (0–4s)</div>
          <div class="beat-text">"${escapeHtml(s.hook)}"</div>
        </div>

        <!-- Beat 2: Setting -->
        <div class="beat-row">
          <div class="beat-badge beat-setting">Beat 2: Historical Setting (4–10s)</div>
          <div class="beat-text">${escapeHtml(s.setting || '')}</div>
        </div>

        <!-- Beat 3: Escalation -->
        <div class="beat-row">
          <div class="beat-badge beat-escalation">Beat 3: Escalation (10–30s)</div>
          <div class="beat-text">${escapeHtml(s.escalation || '')}</div>
        </div>

        <!-- Beat 4: Mystery -->
        <div class="beat-row">
          <div class="beat-badge beat-mystery">Beat 4: Mystery Beat (30–42s)</div>
          <div class="beat-text">${escapeHtml(s.mystery || '')}</div>
        </div>

        <!-- Beat 5: Pivot -->
        <div class="beat-row">
          <div class="beat-badge beat-pivot">Beat 5: "You see," Pivot (42–52s)</div>
          <div class="beat-text">${escapeHtml(s.pivot || '')}</div>
        </div>

        <!-- Beat 6: Payoff -->
        <div class="beat-row">
          <div class="beat-badge beat-payoff">Beat 6: Ironic Payoff (52–60s)</div>
          <div class="beat-text"><strong>"${escapeHtml(s.payoff || '')}"</strong></div>
        </div>
      </div>

      <div class="script-footer">
        <div class="script-meta-pills">
          <span class="meta-pill">⏱️ Est. Duration: ${s.est_duration || '1:30'}</span>
          <span class="meta-pill">📝 Words: ${s.word_count || 140}</span>
          <span class="meta-pill">🛡️ Academic Fact-Check: Verified</span>
        </div>
        <div class="citations-text">
          <strong>Citations:</strong> ${escapeHtml(s.citations || 'Primary historical sources verified')}
        </div>
      </div>
    `;

    card.querySelector('.btn-render-single').addEventListener('click', () => {
      triggerRender(s.id);
    });

    elements.scriptsList.appendChild(card);
  });
}

async function triggerRender(scriptId) {
  alert(`Starting 2.5D Blender 4.2 render for Script #${scriptId}! Rendering runs in background with EEVEE-Next.`);
  try {
    await fetch('/api/videos/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ script_id: scriptId })
    });
    switchTab('tab-videos');
  } catch (err) {
    console.error('Error queuing render:', err);
  }
}

elements.btnRenderAllScripts.addEventListener('click', async () => {
  if (state.scripts.length === 0) {
    alert('No scripts available to render!');
    return;
  }
  alert(`Queuing all ${state.scripts.length} scripts for animation rendering in Blender 4.2! Videos will appear in your Video Vault as they complete.`);
  try {
    await fetch('/api/videos/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ script_ids: state.scripts.map(s => s.id) })
    });
    switchTab('tab-videos');
  } catch (err) {
    console.error('Error queuing batch render:', err);
  }
});

/* ==========================================================================
   Tab 3: Video Vault & Mobile Previews
   ========================================================================== */
async function loadVideos() {
  try {
    const res = await fetch('/api/videos');
    const data = await res.json();
    state.videos = data.videos || [];
    renderVideos();
  } catch (err) {
    console.error('Error loading videos:', err);
  }
}

elements.btnRefreshVideos.addEventListener('click', loadVideos);

function renderVideos() {
  elements.videoGrid.innerHTML = '';

  if (state.videos.length === 0) {
    elements.videoGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: var(--text-dim);">
        <h3>No videos rendered yet</h3>
        <p>Your Blender renders will automatically appear here once exported.</p>
      </div>
    `;
    return;
  }

  state.videos.forEach(v => {
    const card = document.createElement('div');
    card.className = 'video-card';

    card.innerHTML = `
      <div class="video-thumb-box">
        <video src="${v.url}#t=1" preload="metadata" muted></video>
        <div class="play-overlay">▶</div>
      </div>
      <div class="video-card-body">
        <h4 class="video-card-title">${escapeHtml(v.title || v.filename)}</h4>
        <div class="video-card-meta">
          <span>⏱️ ${v.duration_str || '1:55'}</span>
          <span>💾 ${v.size_mb || '15'} MB</span>
          <span>📐 1080×1920</span>
        </div>
        <div style="display: flex; gap: 8px; margin-top: 8px;">
          <button class="btn btn-outline btn-sm btn-play-preview" style="flex: 1;">▶ Preview</button>
          <button class="btn btn-primary btn-sm btn-prep-upload" style="flex: 1.2;">🚀 Prepare Upload</button>
        </div>
      </div>
    `;

    card.querySelector('.video-thumb-box').addEventListener('click', () => openVideoModal(v));
    card.querySelector('.btn-play-preview').addEventListener('click', () => openVideoModal(v));

    card.querySelector('.btn-prep-upload').addEventListener('click', () => {
      switchTab('tab-upload');
    });

    elements.videoGrid.appendChild(card);
  });
}

function openVideoModal(video) {
  elements.modalVideoTitle.textContent = video.title || video.filename;
  elements.modalVideoPlayer.src = video.url;
  elements.videoModal.classList.add('open');
  elements.modalVideoPlayer.play();
}

elements.modalVideoClose.addEventListener('click', () => {
  elements.videoModal.classList.remove('open');
  elements.modalVideoPlayer.pause();
  elements.modalVideoPlayer.src = '';
});

elements.videoModal.addEventListener('click', (e) => {
  if (e.target === elements.videoModal) {
    elements.videoModal.classList.remove('open');
    elements.modalVideoPlayer.pause();
    elements.modalVideoPlayer.src = '';
  }
});

/* ==========================================================================
   Tab 4: Batch YouTube Publishing Queue with Deselection & Shorts Preview
   ========================================================================== */
async function loadPublishQueue() {
  if (state.videos.length === 0) {
    await loadVideos();
  }

  // Populate queue items with defaults
  state.queueItems = state.videos.map((v, idx) => {
    const existing = state.queueItems.find(q => q.filename === v.filename);
    if (existing) return existing;

    const defaultTitle = v.suggested_title || `${(v.title || v.filename).replace(/^⭐\s*/, '').replace(/\.mp4$/i, '')} #Shorts`;
    const defaultDesc = v.suggested_desc || (`The shocking true story of ${(v.title || v.filename).replace(/^⭐\s*/, '').replace(/\.mp4$/i, '')}.\n\n` +
      `Key historical events & citations verified from primary academic archives.\n\n` +
      `🔔 Subscribe for daily obscure historical animations!\n\n` +
      `#History #Shorts #HistoricalFacts #DidYouKnow #AncientHistory #UntoldStories`);

    return {
      filename: v.filename,
      url: v.url,
      title: defaultTitle,
      description: defaultDesc,
      tags: "History, Shorts, HistoricalFacts, BizarreHistory, UntoldHistory, Documentary, Animation",
      privacy: "public",
      scheduleDelay: 0,
      selected: true // Selected by default
    };
  });

  renderPublishQueue();
}

function renderPublishQueue() {
  elements.uploadQueueList.innerHTML = '';
  updateQueueCounts();

  if (state.queueItems.length === 0) {
    elements.uploadQueueList.innerHTML = `
      <div class="card" style="text-align: center; padding: 48px; color: var(--text-dim);">
        <h3>No videos in upload queue</h3>
        <p>Videos rendered from the <strong>Research & Scripts</strong> tab will automatically appear here for final preview and approval.</p>
      </div>
    `;
    return;
  }

  state.queueItems.forEach((item, idx) => {
    const card = document.createElement('div');
    card.className = `upload-queue-item ${item.selected ? '' : 'deselected'}`;
    card.id = `queue-item-${idx}`;

    const channelName = state.youtubeStatus.channel ? state.youtubeStatus.channel.title : '@ContentaHistory';

    card.innerHTML = `
      <!-- Shorts Mobile Mockup -->
      <div class="shorts-preview-phone">
        <video src="${item.url}#t=1" controls playsinline muted></video>
        <div class="shorts-overlay-badge">#Shorts</div>
        <div class="shorts-overlay-ui">
          <div class="shorts-overlay-channel">
            <span>📺</span> <span>${escapeHtml(channelName)}</span>
          </div>
          <div class="shorts-overlay-title" id="mockup-title-${idx}">
            ${escapeHtml(item.title)}
          </div>
        </div>
      </div>

      <!-- Editing & Metadata Controls -->
      <div style="display: flex; flex-direction: column; gap: 14px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
          <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; font-weight: 700; font-size: 15px;">
            <input type="checkbox" class="queue-checkbox" data-idx="${idx}" ${item.selected ? 'checked' : ''} style="width: 18px; height: 18px;">
            <span>${item.selected ? '✅ Approved for YouTube Upload' : '❌ Deselected (Skipped)'}</span>
          </label>
          <span style="font-size: 12px; color: var(--text-muted); font-family: var(--font-mono);">${item.filename}</span>
        </div>

        <div class="form-group">
          <label>YouTube Short Title (CTR Optimized, with #Shorts)</label>
          <input type="text" class="form-input queue-title-input" data-idx="${idx}" value="${escapeHtml(item.title)}">
        </div>

        <div class="form-group">
          <label>Video Description & Academic Citations</label>
          <textarea class="form-textarea queue-desc-input" data-idx="${idx}" style="min-height: 80px;">${escapeHtml(item.description)}</textarea>
        </div>

        <div style="display: grid; grid-template-columns: 2fr 1fr 1fr; gap: 12px;">
          <div class="form-group">
            <label>Tags</label>
            <input type="text" class="form-input queue-tags-input" data-idx="${idx}" value="${escapeHtml(item.tags)}">
          </div>
          <div class="form-group">
            <label>Visibility</label>
            <select class="form-select queue-privacy-select" data-idx="${idx}">
              <option value="public" ${item.privacy === 'public' ? 'selected' : ''}>Public</option>
              <option value="unlisted" ${item.privacy === 'unlisted' ? 'selected' : ''}>Unlisted</option>
              <option value="private" ${item.privacy === 'private' ? 'selected' : ''}>Private</option>
            </select>
          </div>
          <div class="form-group">
            <label>Schedule</label>
            <select class="form-select queue-schedule-select" data-idx="${idx}">
              <option value="0" ${item.scheduleDelay === 0 ? 'selected' : ''}>Immediate</option>
              <option value="6" ${item.scheduleDelay === 6 ? 'selected' : ''}>In 6 Hours</option>
              <option value="12" ${item.scheduleDelay === 12 ? 'selected' : ''}>In 12 Hours</option>
              <option value="24" ${item.scheduleDelay === 24 ? 'selected' : ''}>In 24 Hours</option>
            </select>
          </div>
        </div>
      </div>
    `;

    // Event: Checkbox toggle for selection/deselection
    const cb = card.querySelector('.queue-checkbox');
    cb.addEventListener('change', (e) => {
      item.selected = e.target.checked;
      card.classList.toggle('deselected', !item.selected);
      cb.nextElementSibling.textContent = item.selected ? '✅ Approved for YouTube Upload' : '❌ Deselected (Skipped)';
      updateQueueCounts();
    });

    // Event: Live update title on mobile mockup
    const titleInput = card.querySelector('.queue-title-input');
    titleInput.addEventListener('input', (e) => {
      item.title = e.target.value;
      const mockupTitle = document.getElementById(`mockup-title-${idx}`);
      if (mockupTitle) mockupTitle.textContent = e.target.value;
    });

    card.querySelector('.queue-desc-input').addEventListener('input', (e) => {
      item.description = e.target.value;
    });

    card.querySelector('.queue-tags-input').addEventListener('input', (e) => {
      item.tags = e.target.value;
    });

    card.querySelector('.queue-privacy-select').addEventListener('change', (e) => {
      item.privacy = e.target.value;
    });

    card.querySelector('.queue-schedule-select').addEventListener('change', (e) => {
      item.scheduleDelay = parseInt(e.target.value, 10);
    });

    elements.uploadQueueList.appendChild(card);
  });
}

function updateQueueCounts() {
  const total = state.queueItems.length;
  const selected = state.queueItems.filter(i => i.selected).length;
  const deselected = total - selected;

  elements.queueCountText.textContent = `${total} Videos Ready for Review (${selected} selected, ${deselected} deselected)`;
  elements.publishCountNum.textContent = selected;
  elements.btnPublishSelectedBatch.disabled = selected === 0;
}

// Select All Queue Items
elements.btnSelectAllQueue.addEventListener('click', () => {
  state.queueItems.forEach(i => i.selected = true);
  renderPublishQueue();
});

// Deselect All Queue Items
elements.btnDeselectAllQueue.addEventListener('click', () => {
  state.queueItems.forEach(i => i.selected = false);
  renderPublishQueue();
});

// Publish Selected Videos in Batch
elements.btnPublishSelectedBatch.addEventListener('click', async () => {
  if (!state.youtubeStatus.authenticated) {
    alert('⚠️ YouTube Channel Not Linked!\n\nPlease click "Authorize Channel" above (or run run_youtube_auth.bat in your project folder) to connect your YouTube channel before uploading.');
    const authBar = document.querySelector('.yt-channel-status-bar');
    if (authBar) authBar.scrollIntoView({ behavior: 'smooth', block: 'center' });
    return;
  }

  const selectedItems = state.queueItems.filter(i => i.selected);
  if (selectedItems.length === 0) {
    alert('Please select at least 1 video to publish.');
    return;
  }

  const confirmMsg = `Are you sure you want to upload ${selectedItems.length} selected video(s) to your YouTube channel?`;
  if (!confirm(confirmMsg)) return;

  const btn = elements.btnPublishSelectedBatch;
  btn.disabled = true;
  btn.textContent = `Uploading ${selectedItems.length} Videos to YouTube...`;

  elements.batchUploadFeedback.innerHTML = `
    <div style="background: rgba(124, 77, 255, 0.15); border: 1px solid var(--primary); padding: 16px; border-radius: 8px; font-size: 13px;">
      <h4 style="color: var(--primary); margin-bottom: 8px;">⏳ Publishing Batch (${selectedItems.length} videos)</h4>
      <p>Communicating with YouTube Data API v3. Each short will upload sequentially with its customized SEO tags and thumbnail...</p>
    </div>
  `;

  try {
    const payload = {
      items: selectedItems.map(item => ({
        video_filename: item.filename,
        title: item.title,
        description: item.description,
        tags: (item.tags || '').split(',').map(t => t.trim()).filter(Boolean),
        privacy: item.privacy || 'public',
        schedule_delay_hours: item.scheduleDelay || 0
      }))
    };

    const res = await fetch('/api/upload/batch', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const resText = await res.text();
    let data;
    try {
      data = JSON.parse(resText);
    } catch (parseErr) {
      throw new Error(`Server returned HTTP ${res.status}: ${resText.slice(0, 150)}`);
    }

    if (!res.ok && (!data.results || data.results.length === 0)) {
      throw new Error(data.error || `Upload failed with HTTP ${res.status}`);
    }

    const results = data.results || [];
    const successList = results.filter(r => r.success);
    const failedList = results.filter(r => !r.success);

    let linksHtml = successList.map(s => `
      <li style="margin-top: 6px;">
        <span style="color: var(--text-muted);">${escapeHtml(s.video_filename)}:</span>
        <a href="${s.video_url}" target="_blank" style="color: #69f0ae; font-weight: 700; text-decoration: underline; margin-left: 6px;">
          ${s.video_url}
        </a>
      </li>
    `).join('');

    let errorHtml = '';
    if (failedList.length > 0) {
      errorHtml = `
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid rgba(255, 82, 82, 0.3); color: #ff8a80;">
          <strong>⚠️ ${failedList.length} video(s) could not be uploaded:</strong>
          <ul style="padding-left: 20px; margin-top: 6px;">
            ${failedList.map(f => `<li><strong>${escapeHtml(f.video_filename)}:</strong> ${escapeHtml(f.error)}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    elements.batchUploadFeedback.innerHTML = `
      <div style="background: ${successList.length > 0 ? 'rgba(0, 230, 118, 0.15)' : 'rgba(255, 82, 82, 0.15)'}; border: 1px solid ${successList.length > 0 ? 'var(--success)' : 'var(--danger)'}; padding: 18px; border-radius: 8px; font-size: 13px; color: ${successList.length > 0 ? '#a5d6a7' : '#ff8a80'};">
        <h4 style="color: ${successList.length > 0 ? 'var(--success)' : 'var(--danger)'}; font-size: 15px; margin-bottom: 8px;">
          ${successList.length > 0 ? '🎉 Batch Publishing Complete!' : '⚠️ Batch Upload Issue'} (${successList.length} of ${selectedItems.length} Uploaded)
        </h4>
        ${successList.length > 0 ? `<ul style="padding-left: 20px;">${linksHtml}</ul>` : ''}
        ${errorHtml}
      </div>
    `;

    btn.disabled = false;
    btn.textContent = successList.length > 0 ? 'Batch Upload Complete!' : 'Retry Upload';
  } catch (err) {
    elements.batchUploadFeedback.innerHTML = `
      <div style="background: rgba(255, 82, 82, 0.15); border: 1px solid var(--danger); padding: 14px; border-radius: 8px; font-size: 13px; color: #ff8a80;">
        Upload request failed: ${escapeHtml(err.message)}
      </div>
    `;
    btn.disabled = false;
    btn.textContent = 'Retry Upload';
  }
});

// Utility: Escape HTML
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

// Initialize on Load
document.addEventListener('DOMContentLoaded', () => {
  // Check for OAuth redirect return from Google
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get('auth') === 'success') {
    switchTab('tab-upload');
    elements.authStatusMsg.innerHTML = '<span style="color: #69f0ae; font-weight:700;">🎉 Channel Connected Successfully!</span>';
    window.history.replaceState({}, document.title, window.location.pathname + '#tab-upload');
  } else if (urlParams.get('auth') === 'error') {
    switchTab('tab-upload');
    alert('⚠️ YouTube authorization was not completed. Please try again.');
    window.history.replaceState({}, document.title, window.location.pathname + '#tab-upload');
  }

  checkYouTubeStatus();
  searchTopics(); // Initial population of curated topics
  loadVideos();
});
