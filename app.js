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
  undercoverIndex: 0,
  mrWhiteMode: false,
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

  const pair = aiGenerator.generatePair(idea1, idea2, i18n.current);

  try {
    await Promise.all([
      preloadImage(pair.civils.url),
      preloadImage(pair.undercover.url),
    ]);
    state.customCivils = pair.civils;
    state.customUndercover = pair.undercover;
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

function preloadImage(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = () => reject(new Error('image_load_failed'));
    img.src = url;
    // Timeout 25s pour ne pas bloquer indefiniment
    setTimeout(() => reject(new Error('image_load_timeout')), 25000);
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

  state.undercoverIndex = Math.floor(Math.random() * state.playersCount);

  state.assignments = state.playerNames.map((name, i) => ({
    name,
    video: i === state.undercoverIndex ? state.undercoverVideo : state.civilsVideo,
    isUndercover: i === state.undercoverIndex,
  }));

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
  // Mr White : pas de vidéo, on affiche l'écran spécial bluff
  if (a.isUndercover && state.mrWhiteMode) {
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

  const remaining = state.assignments.filter(a => !state.wrongVotes.includes(a.name));
  const onlyUndercoverLeft = remaining.length === 1 && remaining[0].isUndercover;
  if (onlyUndercoverLeft) {
    showUndercoverWins();
  } else {
    showMiss(voted);
  }
}

function renderCompare(containerId) {
  const container = document.getElementById(containerId);
  container.innerHTML = '';
  const ucIsMrWhite = state.mrWhiteMode;
  const ucTitle = ucIsMrWhite ? '🃏 Mr White' : state.undercoverVideo.title;

  function buildHalf(labelKey, title) {
    const half = document.createElement('div');
    half.className = 'compare-half';
    const label = document.createElement('div');
    label.className = 'compare-label';
    label.textContent = i18n.t(labelKey); // safe (controlled)
    const video = document.createElement('div');
    video.className = 'compare-video';
    const t = document.createElement('div');
    t.className = 'compare-title';
    t.textContent = title; // safe (user input -> textContent)
    half.appendChild(label);
    half.appendChild(video);
    half.appendChild(t);
    return { half, video };
  }

  const civils = buildHalf('compareCivils', state.civilsVideo.title);
  const undercover = buildHalf('compareUndercover', ucTitle);
  container.appendChild(civils.half);
  container.appendChild(undercover.half);

  mountComparisonVideo(civils.video, state.civilsVideo);
  if (ucIsMrWhite) {
    const placeholder = document.createElement('div');
    placeholder.className = 'compare-placeholder';
    placeholder.textContent = '🃏';
    undercover.video.appendChild(placeholder);
  } else {
    mountComparisonVideo(undercover.video, state.undercoverVideo);
  }
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
