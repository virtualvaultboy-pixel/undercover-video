// ============================================================
// Undercover Vidéo — game master
// ============================================================

const state = {
  playersCount: 4,
  categories: [],
  selectedCategoryId: 'random',
  playerNames: [],          // ['Alice', 'Bob', ...]
  // état de la partie
  civilsVideo: null,
  undercoverVideo: null,
  undercoverIndex: 0,       // index dans assignments (0-based)
  assignments: [],          // [{ name, video, isUndercover }, ...]
  currentPlayerIndex: 0,
  wrongVotes: [],           // noms des joueurs déjà accusés à tort
};

// ----------- Init -----------
async function init() {
  await loadVideos();
  buildCategorySelect();
  bindEvents();
}

async function loadVideos() {
  const res = await fetch('data/videos.json');
  const data = await res.json();
  state.categories = data.categories;
}

function buildCategorySelect() {
  const sel = document.getElementById('category-select');
  sel.innerHTML = '<option value="random">🎲 Aléatoire</option>';
  state.categories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = `${cat.emoji} ${cat.name}`;
    sel.appendChild(opt);
  });
}

function bindEvents() {
  document.getElementById('players-minus').onclick = () => changePlayers(-1);
  document.getElementById('players-plus').onclick = () => changePlayers(1);
  document.getElementById('category-select').onchange = e => state.selectedCategoryId = e.target.value;
  document.getElementById('btn-start').onclick = goToNamesScreen;
  document.getElementById('btn-names-back').onclick = () => switchScreen('screen-setup');
  document.getElementById('btn-names-confirm').onclick = startGame;
  document.getElementById('btn-ready').onclick = showVideo;
  document.getElementById('btn-hide').onclick = nextPlayer;
  document.getElementById('btn-go-vote').onclick = goToVote;
  document.getElementById('btn-new-round').onclick = newSpeakingRound;
  document.getElementById('btn-restart').onclick = restart;
  document.getElementById('btn-restart-play').onclick = restart;
  document.getElementById('btn-restart-miss').onclick = restart;
  document.getElementById('btn-restart-uc').onclick = restart;
}

// ----------- Setup -----------
function changePlayers(delta) {
  const next = state.playersCount + delta;
  if (next < 3 || next > 12) return;
  state.playersCount = next;
  document.getElementById('players-count').textContent = next;
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
    input.placeholder = `Joueur ${i + 1}`;
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
    state.playerNames.push(val || `Joueur ${i + 1}`);
  });
}

// ----------- Lancement de la partie -----------
function startGame() {
  collectNames();

  // 1. Choisir une catégorie (en évitant les récentes en mode aléatoire)
  const cat = state.selectedCategoryId === 'random'
    ? pickRandomCategory()
    : state.categories.find(c => c.id === state.selectedCategoryId);

  if (!cat || cat.videos.length < 2) {
    alert("Cette catégorie n'a pas assez de vidéos (minimum 2).");
    return;
  }

  // Mémoriser pour éviter de retomber dessus tout de suite
  pushRecentCategory(cat.id);

  // 2. Piocher 2 vidéos différentes
  const shuffled = [...cat.videos].sort(() => Math.random() - 0.5);
  state.civilsVideo = shuffled[0];
  state.undercoverVideo = shuffled[1];

  // 3. Désigner l'undercover (index 0-based)
  state.undercoverIndex = Math.floor(Math.random() * state.playersCount);

  // 4. Construire les assignations dans l'ordre des joueurs
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

  if (video.source === 'local') {
    const vid = document.createElement('video');
    vid.src = video.url;
    vid.controls = true;
    vid.autoplay = true;
    vid.loop = true;
    vid.playsInline = true;
    vid.muted = false;
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
    if (state.wrongVotes.includes(a.name)) return; // déjà éliminé
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

  // Si tous les civils sont éliminés, l'undercover gagne
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
  container.innerHTML = `
    <div class="compare-half">
      <div class="compare-label">👥 Civils</div>
      <div class="compare-video" data-role="civils"></div>
      <div class="compare-title">${state.civilsVideo.title}</div>
    </div>
    <div class="compare-half">
      <div class="compare-label">🕵️ Undercover</div>
      <div class="compare-video" data-role="undercover"></div>
      <div class="compare-title">${state.undercoverVideo.title}</div>
    </div>
  `;
  const civilsSlot = container.querySelector('[data-role="civils"]');
  const undercoverSlot = container.querySelector('[data-role="undercover"]');
  mountComparisonVideo(civilsSlot, state.civilsVideo);
  mountComparisonVideo(undercoverSlot, state.undercoverVideo);
}

function mountComparisonVideo(slot, video) {
  slot.innerHTML = '';
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
  switchScreen('screen-victory');
}

function showUndercoverWins() {
  const uc = state.assignments.find(a => a.isUndercover);
  document.getElementById('undercover-name').textContent = uc.name;
  renderCompare('undercover-compare');
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

// ----------- Mémoire des catégories récentes -----------
const RECENT_KEY = 'undercover_recent_categories';
const RECENT_MAX = 5;

function getRecentCategories() {
  try {
    return JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
  } catch {
    return [];
  }
}

function pushRecentCategory(catId) {
  const recent = getRecentCategories();
  recent.push(catId);
  while (recent.length > RECENT_MAX) recent.shift();
  try { localStorage.setItem(RECENT_KEY, JSON.stringify(recent)); } catch { /* ignore */ }
}

function pickRandomCategory() {
  const playable = state.categories.filter(c => c.videos.length >= 2);
  if (playable.length === 0) return null;

  const recent = getRecentCategories();
  // On exclut au plus (playable.length - 1) catégories pour toujours avoir un choix
  const excludeCount = Math.min(recent.length, playable.length - 1);
  const recentSet = new Set(recent.slice(-excludeCount));
  const eligible = playable.filter(c => !recentSet.has(c.id));
  return pickRandom(eligible.length > 0 ? eligible : playable);
}

// ----------- Service worker (PWA) -----------
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('sw.js').catch(() => { /* offline non critique */ });
  });
}

// ----------- Go -----------
init();
