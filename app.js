// ============================================================
// Undercover Vidéo — game master (avec i18n + freemium)
// ============================================================

const state = {
  playersCount: 4,
  categories: [],
  translations: {},
  selectedCategoryId: 'random',
  playerNames: [],
  civilsVideo: null,
  undercoverVideo: null,
  undercoverIndex: null,    // null si pas d'undercover dans la variante surprise
  mrWhiteIndex: null,       // null si pas de Mr White dans la variante surprise
  mrWhiteMode: false,       // toggle UI = "Mode Surprise"
  assignments: [],
  currentPlayerIndex: 0,
  wrongVotes: [],
};

// ----------- Stats locales -----------
const STATS_KEY = 'undercover_stats';
function getStats() {
  try {
    const s = JSON.parse(localStorage.getItem(STATS_KEY) || '{}');
    return { games: s.games || 0, civils: s.civils || 0, undercover: s.undercover || 0 };
  } catch { return { games: 0, civils: 0, undercover: 0 }; }
}
function bumpStats(winner) {
  const s = getStats();
  s.games++;
  if (winner === 'civils') s.civils++;
  if (winner === 'undercover') s.undercover++;
  try { localStorage.setItem(STATS_KEY, JSON.stringify(s)); } catch {}
  renderStats();
}
function renderStats() {
  const el = document.getElementById('stats-row');
  if (!el) return;
  const s = getStats();
  if (s.games === 0) { el.innerHTML = ''; return; }
  el.innerHTML = `
    <div class="stat"><div class="stat-num">${s.games}</div><div class="stat-lbl">${i18n.t('statsGames')}</div></div>
    <div class="stat"><div class="stat-num">${s.civils}</div><div class="stat-lbl">${i18n.t('statsCivilsWin')}</div></div>
    <div class="stat"><div class="stat-num">${s.undercover}</div><div class="stat-lbl">${i18n.t('statsUndercoverWin')}</div></div>
  `;
}

// Les 25 premières catégories du JSON sont gratuites, le reste = premium
const FREE_COUNT = 25;
const PREMIUM_KEY = 'undercover_premium';

// ----------- Premium -----------
function isPremium() {
  try { return localStorage.getItem(PREMIUM_KEY) === 'true'; }
  catch { return false; }
}
function unlockPremium() {
  try { localStorage.setItem(PREMIUM_KEY, 'true'); } catch {}
}

function isCategoryFree(catId) {
  const idx = state.categories.findIndex(c => c.id === catId);
  return idx >= 0 && idx < FREE_COUNT;
}
function isCategoryAvailable(cat) {
  if (cat.videos.length < 2) return false;
  return isPremium() || isCategoryFree(cat.id);
}

// ----------- Init -----------
async function init() {
  await loadVideos();
  buildLangSelect();
  i18n.applyI18n();
  buildCategorySelect();
  bindEvents();
  // Init Play Billing (silencieux si hors TWA)
  if (window.playBilling) {
    await window.playBilling.init();
  }
  refreshPremiumUI();
  updateCategoryCounter();
  renderStats();
}

async function loadVideos() {
  const [resV, resT] = await Promise.all([
    fetch('data/videos.json'),
    fetch('data/translations.json').catch(() => null),
  ]);
  const data = await resV.json();
  state.categories = data.categories;
  if (resT && resT.ok) {
    try {
      const tr = await resT.json();
      state.translations = tr.categories || {};
    } catch { state.translations = {}; }
  } else {
    state.translations = {};
  }
  updateCategoryCounter();
}

function categoryName(cat) {
  const lang = i18n.current;
  if (lang === 'fr') return cat.name;
  const tr = state.translations[cat.id];
  if (tr && tr[lang]) return tr[lang];
  return cat.name; // fallback FR
}

function updateCategoryCounter() {
  const el = document.getElementById('cat-counter');
  if (!el) return;
  const total = state.categories.filter(c => c.videos.length >= 2).length;
  const free = state.categories.slice(0, FREE_COUNT).filter(c => c.videos.length >= 2).length;
  const n = isPremium() ? total : free;
  el.textContent = i18n.t('catCounterTpl', { n: `${n}/${total}` });
}

function buildLangSelect() {
  const sel = document.getElementById('lang-select');
  sel.innerHTML = '';
  const labels = { fr: 'FR · Français', en: 'EN · English', es: 'ES · Español' };
  i18n.all.forEach(l => {
    const opt = document.createElement('option');
    opt.value = l;
    opt.textContent = labels[l] || l;
    if (l === i18n.current) opt.selected = true;
    sel.appendChild(opt);
  });
  sel.onchange = e => {
    i18n.setLang(e.target.value);
    buildCategorySelect();
    updateCategoryCounter();
    refreshPremiumUI();
    renderPaywallFeatures();
    renderStats(); // labels stats peuvent changer de langue
  };
}

function buildCategorySelect() {
  const sel = document.getElementById('category-select');
  sel.innerHTML = '';

  // Option Custom AI tout en haut
  const optCustom = document.createElement('option');
  optCustom.value = 'custom-ai';
  optCustom.textContent = i18n.t('customAiOption') + (isPremium() ? '' : '  ' + i18n.t('categoryLocked'));
  sel.appendChild(optCustom);

  const optRandom = document.createElement('option');
  optRandom.value = 'random';
  optRandom.textContent = i18n.t('categoryRandom');
  sel.appendChild(optRandom);

  state.categories.forEach(cat => {
    if (cat.videos.length < 2) return;
    const opt = document.createElement('option');
    opt.value = cat.id;
    const locked = !isCategoryAvailable(cat);
    opt.textContent = `${cat.emoji} ${categoryName(cat)}${locked ? '  ' + i18n.t('categoryLocked') : ''}`;
    opt.dataset.locked = locked ? '1' : '0';
    sel.appendChild(opt);
  });

  sel.value = state.selectedCategoryId === 'random' ? 'random' : state.selectedCategoryId;
}

function refreshPremiumUI() {
  const btn = document.getElementById('btn-show-paywall');
  if (!btn) return;
  if (isPremium()) {
    btn.textContent = i18n.t('paywallActive');
    btn.disabled = true;
  } else {
    btn.textContent = i18n.t('btnPremium');
    btn.disabled = false;
  }
}

function renderPaywallFeatures() {
  const list = document.getElementById('paywall-features');
  if (!list) return;
  const feats = i18n.t('paywallFeatures') || [];
  list.innerHTML = '';
  feats.forEach(f => {
    const div = document.createElement('div');
    div.className = 'paywall-feature';
    div.textContent = f;
    list.appendChild(div);
  });
  document.getElementById('paywall-price').textContent = i18n.t('paywallPrice');
}

function bindEvents() {
  document.getElementById('players-minus').onclick = () => changePlayers(-1);
  document.getElementById('players-plus').onclick = () => changePlayers(1);
  document.getElementById('category-select').onchange = e => {
    const val = e.target.value;
    // Custom AI : premium only
    if (val === 'custom-ai' && !isPremium()) {
      toast(i18n.t('customAiPremiumOnly'));
      e.target.value = state.selectedCategoryId;
      goToPaywall();
      return;
    }
    const cat = state.categories.find(c => c.id === val);
    if (cat && !isCategoryAvailable(cat)) {
      toast(i18n.t('alertCategoryLocked'));
      e.target.value = state.selectedCategoryId;
      goToPaywall();
      return;
    }
    state.selectedCategoryId = val;
  };
  document.getElementById('btn-start').onclick = handleStartClick;
  document.getElementById('btn-custom-back').onclick = () => switchScreen('screen-setup');
  document.getElementById('btn-custom-generate').onclick = handleCustomGenerate;
  document.getElementById('btn-help').onclick = () => switchScreen('screen-help');
  document.getElementById('btn-help-close').onclick = () => switchScreen('screen-setup');
  document.getElementById('btn-show-paywall').onclick = goToPaywall;
  document.getElementById('btn-paywall-close').onclick = () => switchScreen('screen-setup');
  document.getElementById('btn-paywall-buy').onclick = async () => {
    if (window.playBilling && window.playBilling.available) {
      try {
        await window.playBilling.buy();
        refreshPremiumUI();
        buildCategorySelect();
        updateCategoryCounter();
        switchScreen('screen-setup');
      } catch (e) {
        if (e && e.name === 'AbortError') return; // user cancelled
        toast(i18n.t('errorPurchase') + ' : ' + (e.message || e));
      }
    } else {
      // PWA web : pas d'achat possible, on redirige sur le Play Store
      toast(i18n.t('paywallSoon'));
    }
  };
  document.getElementById('btn-paywall-demo').onclick = () => {
    unlockPremium();
    refreshPremiumUI();
    buildCategorySelect();
    updateCategoryCounter();
    switchScreen('screen-setup');
  };
  document.getElementById('btn-names-back').onclick = () => switchScreen('screen-setup');
  document.getElementById('btn-names-confirm').onclick = startGame;
  document.getElementById('btn-ready').onclick = showVideo;
  document.getElementById('btn-hide').onclick = nextPlayer;
  document.getElementById('btn-hide-mrwhite').onclick = nextPlayer;
  const mrToggle = document.getElementById('mr-white-toggle');
  // Restaurer l'etat depuis localStorage
  try {
    state.mrWhiteMode = localStorage.getItem('undercover_mrwhite') === 'true';
    mrToggle.checked = state.mrWhiteMode;
  } catch {}
  mrToggle.onchange = e => {
    state.mrWhiteMode = e.target.checked;
    try { localStorage.setItem('undercover_mrwhite', String(state.mrWhiteMode)); } catch {}
  };
  document.getElementById('btn-go-vote').onclick = goToVote;
  document.getElementById('btn-new-round').onclick = newSpeakingRound;
  document.getElementById('btn-restart').onclick = restart;
  document.getElementById('btn-restart-play').onclick = restart;
  document.getElementById('btn-restart-miss').onclick = restart;
  document.getElementById('btn-restart-uc').onclick = restart;
}

function goToPaywall() {
  renderPaywallFeatures();
  switchScreen('screen-paywall');
}

// ----------- Setup -----------
function changePlayers(delta) {
  const next = state.playersCount + delta;
  if (next < 3 || next > 12) return;
  state.playersCount = next;
  document.getElementById('players-count').textContent = next;
}

// ----------- Aiguillage Suivant -----------
function handleStartClick() {
  if (state.selectedCategoryId === 'custom-ai') {
    if (!isPremium()) {
      toast(i18n.t('customAiPremiumOnly'));
      goToPaywall();
      return;
    }
    switchScreen('screen-custom-ai');
    return;
  }
  goToNamesScreen();
}

// ----------- Custom AI -----------
let _customGenerating = false;

async function handleCustomGenerate() {
  if (_customGenerating) return; // anti double-clic

  const idea1 = document.getElementById('custom-idea-1').value.trim();
  const idea2 = document.getElementById('custom-idea-2').value.trim();

  if (!idea1 || !idea2) {
    toast(i18n.t('customAiInvalid'));
    return;
  }

  _customGenerating = true;
  const btn = document.getElementById('btn-custom-generate');
  btn.disabled = true;
  switchScreen('screen-ai-loading');

  const pair = aiGenerator.generatePair(idea1, idea2);

  try {
    // Pour chaque image, essaie les URLs candidates en cascade (turbo puis flux)
    const [civilsUrl, ucUrl] = await Promise.all([
      tryLoadFirst(pair.civils.urls),
      tryLoadFirst(pair.undercover.urls),
    ]);
    state.customCivils = { ...pair.civils, url: civilsUrl };
    state.customUndercover = { ...pair.undercover, url: ucUrl };
    goToNamesScreen();
  } catch (e) {
    console.warn('[AI] Generation failed', e);
    toast(i18n.t('videoErrorTitle') + ' (' + (e.message || 'unknown') + ')');
    switchScreen('screen-custom-ai');
  } finally {
    btn.disabled = false;
    _customGenerating = false;
  }
}

// Charge la 1ere URL qui répond ; sinon throw après le dernier candidate.
async function tryLoadFirst(urls) {
  let lastErr = null;
  for (const u of urls) {
    try {
      await preloadImage(u, 60000);
      return u;
    } catch (e) {
      lastErr = e;
      console.warn('[AI] Candidate failed, trying next', u, e.message);
    }
  }
  throw lastErr || new Error('all_candidates_failed');
}

function preloadImage(url, timeoutMs = 25000) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    let done = false;
    const finish = (fn, val) => { if (done) return; done = true; fn(val); };
    img.onload = () => finish(resolve, img);
    img.onerror = () => finish(reject, new Error('image_load_failed'));
    img.src = url;
    setTimeout(() => finish(reject, new Error('image_load_timeout')), timeoutMs);
  });
}

// ----------- Saisie des noms -----------
function goToNamesScreen() {
  const list = document.getElementById('names-list');
  list.innerHTML = '';
  for (let i = 0; i < state.playersCount; i++) {
    const wrap = document.createElement('div');
    wrap.className = 'name-row';
    const label = document.createElement('span');
    label.className = 'name-num';
    label.textContent = `${i + 1}.`;
    const input = document.createElement('input');
    input.type = 'text';
    input.placeholder = i18n.t('playerPlaceholderTpl', { n: i + 1 });
    input.maxLength = 20;
    input.value = state.playerNames[i] || '';
    input.dataset.index = i;
    wrap.appendChild(label);
    wrap.appendChild(input);
    list.appendChild(wrap);
  }
  switchScreen('screen-names');
}

function collectNames() {
  const inputs = document.querySelectorAll('#names-list input');
  state.playerNames = [];
  inputs.forEach((inp, i) => {
    const val = inp.value.trim();
    state.playerNames.push(val || i18n.t('playerPlaceholderTpl', { n: i + 1 }));
  });
}

// ----------- Lancement de la partie -----------
function startGame() {
  collectNames();

  // Mode Custom AI : on utilise les images deja generees
  if (state.selectedCategoryId === 'custom-ai' && state.customCivils && state.customUndercover) {
    state.civilsVideo = state.customCivils;
    state.undercoverVideo = state.customUndercover;
  } else {
    const cat = state.selectedCategoryId === 'random'
      ? pickRandomCategory()
      : state.categories.find(c => c.id === state.selectedCategoryId);

    if (!cat || cat.videos.length < 2) {
      toast(i18n.t('categoryUnavailable'));
      return;
    }

    pushRecentCategory(cat.id);

    const shuffled = [...cat.videos].sort(() => Math.random() - 0.5);
    state.civilsVideo = shuffled[0];
    state.undercoverVideo = shuffled[1];
  }

  // ---- Détermine la composition des imposteurs ----
  // Par défaut : 1 undercover seul
  // En Mode Surprise : random entre (undercover seul) / (mr white seul) / (les 2)
  let hasUndercover = true;
  let hasMrWhite = false;
  if (state.mrWhiteMode) {
    // Pour avoir "les 2" il faut au moins 4 joueurs (sinon trop d'imposteurs)
    const can2 = state.playersCount >= 4;
    const variants = can2 ? ['undercover', 'mrwhite', 'both'] : ['undercover', 'mrwhite'];
    const variant = variants[Math.floor(Math.random() * variants.length)];
    hasUndercover = (variant === 'undercover' || variant === 'both');
    hasMrWhite   = (variant === 'mrwhite' || variant === 'both');
  }

  // Tire des indices distincts pour les imposteurs
  const allIndices = [...Array(state.playersCount).keys()].sort(() => Math.random() - 0.5);
  let cursor = 0;
  state.undercoverIndex = hasUndercover ? allIndices[cursor++] : null;
  state.mrWhiteIndex    = hasMrWhite    ? allIndices[cursor++] : null;

  state.assignments = state.playerNames.map((name, i) => {
    if (i === state.undercoverIndex) {
      return { name, video: state.undercoverVideo, role: 'undercover', isUndercover: true };
    }
    if (i === state.mrWhiteIndex) {
      return { name, video: null, role: 'mrwhite', isUndercover: true };
    }
    return { name, video: state.civilsVideo, role: 'civil', isUndercover: false };
  });

  state.currentPlayerIndex = 0;
  state.wrongVotes = [];
  showTransition();
}

// ----------- Boucle de distribution -----------
function showTransition() {
  const a = state.assignments[state.currentPlayerIndex];
  document.getElementById('transition-player').textContent = a.name;
  switchScreen('screen-transition');
}

function showVideo() {
  const a = state.assignments[state.currentPlayerIndex];
  // Mr White : pas de vidéo, écran spécial bluff
  if (a.role === 'mrwhite') {
    switchScreen('screen-mrwhite-video');
    return;
  }
  renderVideo(a.video);
  switchScreen('screen-video');
}

function nextPlayer() {
  document.getElementById('video-container').innerHTML = '';
  state.currentPlayerIndex++;

  if (state.currentPlayerIndex < state.assignments.length) {
    showTransition();
  } else {
    showPlayScreen();
  }
}

// ----------- Rendu vidéo -----------
function renderVideo(video) {
  const container = document.getElementById('video-container');
  container.innerHTML = '';

  if (video.source === 'ai-image') {
    const img = document.createElement('img');
    img.src = video.url;
    img.alt = video.title || '';
    img.className = 'ai-image-full';
    img.onerror = () => showVideoError(container);
    container.appendChild(img);
  } else if (video.source === 'local') {
    const vid = document.createElement('video');
    vid.src = video.url;
    vid.controls = true;
    vid.autoplay = true;
    vid.loop = true;
    vid.playsInline = true;
    vid.muted = false;
    vid.onerror = () => showVideoError(container);
    container.appendChild(vid);
  } else if (video.source === 'youtube') {
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${video.id}?autoplay=1&rel=0`;
    iframe.allow = 'autoplay; encrypted-media; fullscreen';
    iframe.allowFullscreen = true;
    container.appendChild(iframe);
  } else if (video.source === 'tiktok') {
    const block = document.createElement('blockquote');
    block.className = 'tiktok-embed';
    block.setAttribute('cite', `https://www.tiktok.com/embed/v2/${video.id}`);
    block.setAttribute('data-video-id', video.id);
    block.style.maxWidth = '605px';
    block.style.minWidth = '325px';
    block.innerHTML = '<section></section>';
    container.appendChild(block);

    const oldScript = document.getElementById('tiktok-embed-script');
    if (oldScript) oldScript.remove();
    const script = document.createElement('script');
    script.id = 'tiktok-embed-script';
    script.src = 'https://www.tiktok.com/embed.js';
    script.async = true;
    document.body.appendChild(script);
  }
}

function showVideoError(container) {
  container.innerHTML = `
    <div class="video-error">
      <div class="video-error-emoji">📡</div>
      <p>${i18n.t('videoErrorTitle')}</p>
      <p class="video-error-sub">${i18n.t('videoErrorSub')}</p>
    </div>
  `;
}

// ----------- Tour de parole -----------
function showPlayScreen() {
  const order = state.assignments
    .map(a => a.name)
    .filter(name => !state.wrongVotes.includes(name));
  order.sort(() => Math.random() - 0.5);
  document.getElementById('speaking-order').textContent = order.join(' → ');
  switchScreen('screen-play');
}

function newSpeakingRound() {
  showPlayScreen();
}

// ----------- Vote -----------
function goToVote() {
  const grid = document.getElementById('vote-grid');
  grid.innerHTML = '';
  state.assignments.forEach((a, idx) => {
    if (state.wrongVotes.includes(a.name)) return;
    const btn = document.createElement('button');
    btn.className = 'vote-btn';
    btn.textContent = a.name;
    btn.onclick = () => handleVote(idx);
    grid.appendChild(btn);
  });
  switchScreen('screen-vote');
}

function handleVote(idx) {
  const voted = state.assignments[idx];
  if (voted.isUndercover) {
    showVictory(voted);
    return;
  }

  state.wrongVotes.push(voted.name);

  // Imposteurs gagnent si plus aucun civil restant
  const remaining = state.assignments.filter(a => !state.wrongVotes.includes(a.name));
  const civilsLeft = remaining.filter(a => !a.isUndercover).length;
  if (civilsLeft === 0) {
    showUndercoverWins();
  } else {
    showMiss(voted);
  }
}

function renderCompare(containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';

  function buildHalf(labelText, title) {
    const half = document.createElement('div');
    half.className = 'compare-half';
    const label = document.createElement('div');
    label.className = 'compare-label';
    label.textContent = labelText;
    const video = document.createElement('div');
    video.className = 'compare-video';
    const t = document.createElement('div');
    t.className = 'compare-title';
    t.textContent = title;
    half.appendChild(label);
    half.appendChild(video);
    half.appendChild(t);
    return { half, video };
  }

  // 1) Case Civils — toujours présente
  const civils = buildHalf(i18n.t('compareCivils'), state.civilsVideo.title);
  container.appendChild(civils.half);
  mountComparisonVideo(civils.video, state.civilsVideo);

  // 2) Case Undercover (si la variante en contient un)
  if (state.undercoverIndex !== null) {
    const uc = buildHalf(i18n.t('compareUndercover'), state.undercoverVideo.title);
    container.appendChild(uc.half);
    mountComparisonVideo(uc.video, state.undercoverVideo);
  }

  // 3) Case Mr White (si la variante en contient un)
  if (state.mrWhiteIndex !== null) {
    const mw = buildHalf('🃏 Mr White', i18n.t('mrWhiteTitle').replace('🃏 ', ''));
    container.appendChild(mw.half);
    const placeholder = document.createElement('div');
    placeholder.className = 'compare-placeholder';
    placeholder.textContent = '🃏';
    mw.video.appendChild(placeholder);
  }

  // Layout adaptatif : 2 ou 3 cases
  container.dataset.cols = String(container.children.length);
}

function mountComparisonVideo(slot, video) {
  slot.innerHTML = '';
  if (video.source === 'ai-image') {
    const img = document.createElement('img');
    img.src = video.url;
    img.alt = video.title || '';
    img.className = 'ai-image-compare';
    slot.appendChild(img);
    return;
  }
  if (video.source === 'local') {
    const vid = document.createElement('video');
    vid.src = video.url;
    vid.autoplay = true;
    vid.loop = true;
    vid.muted = true;
    vid.playsInline = true;
    vid.controls = false;
    slot.appendChild(vid);
  } else if (video.source === 'youtube') {
    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${video.id}?autoplay=1&mute=1&loop=1&playlist=${video.id}&rel=0`;
    iframe.allow = 'autoplay; encrypted-media';
    slot.appendChild(iframe);
  }
}

function showVictory(voted) {
  document.getElementById('victory-name').textContent = voted.name;
  renderCompare('victory-compare');
  bumpStats('civils');
  switchScreen('screen-victory');
}

function showUndercoverWins() {
  const uc = state.assignments.find(a => a.isUndercover);
  document.getElementById('undercover-name').textContent = uc.name;
  renderCompare('undercover-compare');
  bumpStats('undercover');
  switchScreen('screen-undercover-wins');
}

function showMiss(voted) {
  document.getElementById('miss-name').textContent = voted.name;
  switchScreen('screen-miss');
}

// ----------- Restart -----------
function restart() {
  document.getElementById('video-container').innerHTML = '';
  const vc = document.getElementById('victory-compare');
  const uc = document.getElementById('undercover-compare');
  if (vc) vc.innerHTML = '';
  if (uc) uc.innerHTML = '';
  switchScreen('screen-setup');
}

// ----------- Utilitaires -----------
function switchScreen(id) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(id).classList.add('active');
  window.scrollTo(0, 0);
}

function pickRandom(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

// ----------- Toast system (remplace alert) -----------
let _toastTimer = null;
function toast(message, duration = 2800) {
  const el = document.getElementById('toast');
  if (!el) { console.log('[toast]', message); return; }
  el.textContent = message;
  el.classList.add('show');
  if (_toastTimer) clearTimeout(_toastTimer);
  _toastTimer = setTimeout(() => el.classList.remove('show'), duration);
}

// ----------- Mémoire des catégories récentes -----------
const RECENT_KEY = 'undercover_recent_categories';
const RECENT_MAX = 5;

function getRecentCategories() {
  try { return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]'); }
  catch { return []; }
}

function pushRecentCategory(catId) {
  const recent = getRecentCategories();
  recent.push(catId);
  while (recent.length > RECENT_MAX) recent.shift();
  try { localStorage.setItem(RECENT_KEY, JSON.stringify(recent)); } catch {}
}

function pickRandomCategory() {
  // En mode aléatoire, on ne pioche que dans les catégories accessibles à l'utilisateur
  const playable = state.categories.filter(c => isCategoryAvailable(c));
  if (playable.length === 0) return null;

  const recent = getRecentCategories();
  const excludeCount = Math.min(recent.length, playable.length - 1);
  const recentSet = new Set(recent.slice(-excludeCount));
  const eligible = playable.filter(c => !recentSet.has(c.id));
  return pickRandom(eligible.length > 0 ? eligible : playable);
}

// ----------- Service worker (PWA) -----------
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => {});
  });
}

// ----------- Go -----------
init();
