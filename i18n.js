// ============================================================
// i18n — Traductions FR / EN / ES
// ============================================================

const I18N = {
  fr: {
    // Accueil
    appTitle: "🎬 Undercover Vidéo",
    appSubtitle: "L'app distribue les rôles. À vous de jouer.",
    catCounterTpl: "{n} catégories disponibles",
    playersLabel: "Nombre de joueurs",
    categoryLabel: "Catégorie",
    categoryRandom: "🎲 Aléatoire",
    btnNext: "Suivant",
    btnHelp: "?",
    btnPremium: "💎 Devenir Premium",

    // Aide
    helpTitle: "📖 Comment jouer",
    helpGoal: "<strong>🎯 Le but :</strong> démasquer l'undercover, le joueur qui n'a pas vu la même vidéo que les autres.",
    helpStep1: "<strong>1.</strong> L'app distribue les rôles. Tous les joueurs voient la <em>même</em> vidéo… <strong>sauf un</strong> (l'undercover) qui en voit une légèrement différente.",
    helpStep2: "<strong>2.</strong> Le téléphone passe de main en main. Chacun regarde sa vidéo en secret.",
    helpStep3: "<strong>3.</strong> À l'oral, chacun décrit sa vidéo à tour de rôle. Sois assez précis pour ne pas être soupçonné, mais assez vague pour ne pas griller l'undercover si c'est toi.",
    helpStep4: "<strong>4.</strong> Vous votez pour démasquer l'undercover.",
    helpWinCivils: "✅ Si le vote est bon → <strong>les civils gagnent</strong>",
    helpWrongVote: "❌ Si le vote est mauvais → ce joueur est éliminé, on recommence un tour",
    helpWinUndercover: "🕵️ Si tous les civils sont éliminés → <strong>l'undercover gagne</strong>",
    btnHelpClose: "J'ai compris",

    // Noms
    namesTitle: "👥 Noms des joueurs",
    namesSubtitle: "Laisse vide pour garder le nom par défaut.",
    btnLaunch: "Lancer la partie",
    btnBack: "Retour",
    playerPlaceholderTpl: "Joueur {n}",

    // Transition
    passPhoneTo: "📱 Passe le téléphone à",
    btnReady: "Je suis prêt à voir ma vidéo",

    // Vidéo
    btnHide: "✅ J'ai vu, cacher",

    // Tour de parole
    playTitle: "🎤 À vous de jouer !",
    playSubtitle: "Décrivez votre vidéo à tour de rôle.<br>Trouvez l'undercover.",
    speakingOrder: "Ordre de parole :",
    btnGoVote: "Passer au vote",
    btnAbandon: "Abandonner la partie",

    // Vote
    voteTitle: "🗳️ Qui est l'undercover ?",
    voteSubtitle: "Touchez le nom du joueur que vous voulez démasquer.",

    // Victoire civils
    victoryTitle: "🎉 Civils victorieux !",
    victorySubtitle: "était bien l'undercover.",
    btnNewGame: "Nouvelle partie",

    // Raté
    missTitle: "❌ Raté !",
    missSubtitle: "n'est <strong>pas</strong> l'undercover.<br>On repart pour un tour de parole.",
    btnNewRound: "Nouveau tour de parole",

    // Victoire undercover
    undercoverWinsTitle: "🕵️ L'undercover gagne !",
    undercoverWinsSubtitle: "a réussi à passer inaperçu jusqu'au bout.",

    // Compare
    compareCivils: "👥 CIVILS",
    compareUndercover: "🕵️ UNDERCOVER",

    // Erreur vidéo
    videoErrorTitle: "Impossible de charger la vidéo.",
    videoErrorSub: "Vérifie ta connexion internet.",

    // Premium / Paywall
    paywallTitle: "💎 Premium",
    paywallSubtitle: "Débloquez toutes les catégories",
    paywallFeatures: [
      "✅ Toutes les catégories débloquées",
      "✅ Mises à jour gratuites à vie",
      "✅ Soutien au développeur",
      "✅ Achat unique, sans abonnement",
    ],
    paywallPrice: "2,99 €",
    paywallCta: "Débloquer Premium",
    paywallSoon: "Bientôt disponible sur le Play Store",
    paywallDemo: "🧪 Activer la démo Premium",
    paywallActive: "✅ Premium activé",
    paywallLater: "Plus tard",
    categoryLocked: "🔒 Premium",
    alertCategoryLocked: "Cette catégorie est réservée aux utilisateurs Premium.",

    // Langue
    languageLabel: "Langue",

    // Mr White
    mrWhiteToggle: "Mode Mr White",
    mrWhiteToggleHint: "Un joueur n'a pas de vidéo et doit bluffer",
    mrWhiteTitle: "🃏 Tu es Mr White !",
    mrWhiteSubtitle: "Tu n'as pas de vidéo. À toi de bluffer pour ne pas te faire griller.",

    // Stats
    statsGames: "Parties",
    statsCivilsWin: "Civils",
    statsUndercoverWin: "Undercover",

    // Custom AI
    customAiOption: "✨ Personnalisé (IA)",
    customAiTitle: "✨ Mode Personnalisé",
    customAiSubtitle: "Entrez 2 idées proches. L'IA va générer une image pour chacune.",
    customAiIdea1: "Idée des civils",
    customAiIdea1Placeholder: "Ex : un chat qui danse",
    customAiIdea2: "Idée de l'undercover",
    customAiIdea2Placeholder: "Ex : un chien qui danse",
    customAiGenerate: "🎨 Générer & lancer",
    customAiBack: "Retour",
    customAiGenerating: "Génération des images en cours…",
    customAiPremiumOnly: "Le mode Personnalisé est réservé aux utilisateurs Premium.",
    customAiInvalid: "Renseigne les 2 idées avant de lancer.",
  },

  en: {
    appTitle: "🎬 Undercover Video",
    appSubtitle: "The app deals the roles. The game is up to you.",
    catCounterTpl: "{n} categories available",
    playersLabel: "Number of players",
    categoryLabel: "Category",
    categoryRandom: "🎲 Random",
    btnNext: "Next",
    btnHelp: "?",
    btnPremium: "💎 Get Premium",

    helpTitle: "📖 How to play",
    helpGoal: "<strong>🎯 The goal:</strong> unmask the undercover — the player who didn't see the same video as the others.",
    helpStep1: "<strong>1.</strong> The app deals the roles. All players see the <em>same</em> video… <strong>except one</strong> (the undercover) who sees a slightly different one.",
    helpStep2: "<strong>2.</strong> The phone is passed around. Each player watches their video in secret.",
    helpStep3: "<strong>3.</strong> Out loud, each player describes their video in turn. Be specific enough not to look suspicious, but vague enough not to expose the undercover if it's you.",
    helpStep4: "<strong>4.</strong> Everyone votes to unmask the undercover.",
    helpWinCivils: "✅ Right vote → <strong>civilians win</strong>",
    helpWrongVote: "❌ Wrong vote → that player is eliminated, new round starts",
    helpWinUndercover: "🕵️ All civilians eliminated → <strong>undercover wins</strong>",
    btnHelpClose: "Got it",

    namesTitle: "👥 Player names",
    namesSubtitle: "Leave blank to keep the default name.",
    btnLaunch: "Start the game",
    btnBack: "Back",
    playerPlaceholderTpl: "Player {n}",

    passPhoneTo: "📱 Pass the phone to",
    btnReady: "I'm ready to see my video",

    btnHide: "✅ I've seen it, hide",

    playTitle: "🎤 Your turn!",
    playSubtitle: "Describe your video in turn.<br>Find the undercover.",
    speakingOrder: "Speaking order:",
    btnGoVote: "Go to vote",
    btnAbandon: "Abandon game",

    voteTitle: "🗳️ Who is the undercover?",
    voteSubtitle: "Tap the name of the player you suspect.",

    victoryTitle: "🎉 Civilians win!",
    victorySubtitle: "was indeed the undercover.",
    btnNewGame: "New game",

    missTitle: "❌ Wrong!",
    missSubtitle: "is <strong>not</strong> the undercover.<br>Let's restart a round.",
    btnNewRound: "New speaking round",

    undercoverWinsTitle: "🕵️ The undercover wins!",
    undercoverWinsSubtitle: "managed to go unnoticed to the end.",

    compareCivils: "👥 CIVILIANS",
    compareUndercover: "🕵️ UNDERCOVER",

    videoErrorTitle: "Could not load the video.",
    videoErrorSub: "Check your internet connection.",

    paywallTitle: "💎 Premium",
    paywallSubtitle: "Unlock all categories",
    paywallFeatures: [
      "✅ All categories unlocked",
      "✅ Free lifetime updates",
      "✅ Support the developer",
      "✅ One-time purchase, no subscription",
    ],
    paywallPrice: "$2.99",
    paywallCta: "Unlock Premium",
    paywallSoon: "Coming soon to the Play Store",
    paywallDemo: "🧪 Enable Premium demo",
    paywallActive: "✅ Premium active",
    paywallLater: "Later",
    categoryLocked: "🔒 Premium",
    alertCategoryLocked: "This category is reserved for Premium users.",

    languageLabel: "Language",

    mrWhiteToggle: "Mr White mode",
    mrWhiteToggleHint: "One player has no video and must bluff",
    mrWhiteTitle: "🃏 You are Mr White!",
    mrWhiteSubtitle: "You have no video. Bluff your way through to avoid being caught.",

    statsGames: "Games",
    statsCivilsWin: "Civilians",
    statsUndercoverWin: "Undercover",

    customAiOption: "✨ Custom (AI)",
    customAiTitle: "✨ Custom Mode",
    customAiSubtitle: "Type 2 similar ideas. AI will generate an image for each.",
    customAiIdea1: "Civilians' idea",
    customAiIdea1Placeholder: "Ex: a dancing cat",
    customAiIdea2: "Undercover's idea",
    customAiIdea2Placeholder: "Ex: a dancing dog",
    customAiGenerate: "🎨 Generate & start",
    customAiBack: "Back",
    customAiGenerating: "Generating images…",
    customAiPremiumOnly: "Custom mode is reserved for Premium users.",
    customAiInvalid: "Fill in both ideas before starting.",
  },

  es: {
    appTitle: "🎬 Undercover Vídeo",
    appSubtitle: "La app reparte los roles. ¡A jugar!",
    catCounterTpl: "{n} categorías disponibles",
    playersLabel: "Número de jugadores",
    categoryLabel: "Categoría",
    categoryRandom: "🎲 Aleatorio",
    btnNext: "Siguiente",
    btnHelp: "?",
    btnPremium: "💎 Hazte Premium",

    helpTitle: "📖 Cómo jugar",
    helpGoal: "<strong>🎯 El objetivo:</strong> desenmascarar al infiltrado — el jugador que no vio el mismo vídeo que los demás.",
    helpStep1: "<strong>1.</strong> La app reparte los roles. Todos los jugadores ven el <em>mismo</em> vídeo… <strong>excepto uno</strong> (el infiltrado) que ve uno ligeramente diferente.",
    helpStep2: "<strong>2.</strong> El teléfono pasa de mano en mano. Cada uno mira su vídeo en secreto.",
    helpStep3: "<strong>3.</strong> En voz alta, cada uno describe su vídeo por turnos. Sé bastante preciso para no parecer sospechoso, pero bastante vago para no delatar al infiltrado si eres tú.",
    helpStep4: "<strong>4.</strong> Votad para desenmascarar al infiltrado.",
    helpWinCivils: "✅ Voto correcto → <strong>los civiles ganan</strong>",
    helpWrongVote: "❌ Voto incorrecto → ese jugador es eliminado, nueva ronda",
    helpWinUndercover: "🕵️ Todos los civiles eliminados → <strong>el infiltrado gana</strong>",
    btnHelpClose: "Entendido",

    namesTitle: "👥 Nombres de los jugadores",
    namesSubtitle: "Déjalo en blanco para mantener el nombre por defecto.",
    btnLaunch: "Empezar partida",
    btnBack: "Volver",
    playerPlaceholderTpl: "Jugador {n}",

    passPhoneTo: "📱 Pasa el teléfono a",
    btnReady: "Estoy listo para ver mi vídeo",

    btnHide: "✅ Lo he visto, ocultar",

    playTitle: "🎤 ¡Os toca!",
    playSubtitle: "Describid vuestro vídeo por turnos.<br>Encontrad al infiltrado.",
    speakingOrder: "Orden de palabra:",
    btnGoVote: "Pasar a la votación",
    btnAbandon: "Abandonar partida",

    voteTitle: "🗳️ ¿Quién es el infiltrado?",
    voteSubtitle: "Toca el nombre del jugador que sospechas.",

    victoryTitle: "🎉 ¡Civiles victoriosos!",
    victorySubtitle: "era el infiltrado.",
    btnNewGame: "Nueva partida",

    missTitle: "❌ ¡Fallaste!",
    missSubtitle: "<strong>no es</strong> el infiltrado.<br>Empezamos otra ronda.",
    btnNewRound: "Nueva ronda",

    undercoverWinsTitle: "🕵️ ¡El infiltrado gana!",
    undercoverWinsSubtitle: "logró pasar desapercibido hasta el final.",

    compareCivils: "👥 CIVILES",
    compareUndercover: "🕵️ INFILTRADO",

    videoErrorTitle: "No se pudo cargar el vídeo.",
    videoErrorSub: "Verifica tu conexión a internet.",

    paywallTitle: "💎 Premium",
    paywallSubtitle: "Desbloquea todas las categorías",
    paywallFeatures: [
      "✅ Todas las categorías desbloqueadas",
      "✅ Actualizaciones gratis de por vida",
      "✅ Apoya al desarrollador",
      "✅ Compra única, sin suscripción",
    ],
    paywallPrice: "2,99 €",
    paywallCta: "Desbloquear Premium",
    paywallSoon: "Próximamente en Play Store",
    paywallDemo: "🧪 Activar demo Premium",
    paywallActive: "✅ Premium activo",
    paywallLater: "Más tarde",
    categoryLocked: "🔒 Premium",
    alertCategoryLocked: "Esta categoría está reservada para usuarios Premium.",

    languageLabel: "Idioma",

    mrWhiteToggle: "Modo Mr White",
    mrWhiteToggleHint: "Un jugador no tiene vídeo y debe farolear",
    mrWhiteTitle: "🃏 ¡Eres Mr White!",
    mrWhiteSubtitle: "No tienes vídeo. Tienes que farolear para no ser descubierto.",

    statsGames: "Partidas",
    statsCivilsWin: "Civiles",
    statsUndercoverWin: "Infiltrado",

    customAiOption: "✨ Personalizado (IA)",
    customAiTitle: "✨ Modo Personalizado",
    customAiSubtitle: "Escribe 2 ideas parecidas. La IA generará una imagen para cada una.",
    customAiIdea1: "Idea de los civiles",
    customAiIdea1Placeholder: "Ej: un gato bailando",
    customAiIdea2: "Idea del infiltrado",
    customAiIdea2Placeholder: "Ej: un perro bailando",
    customAiGenerate: "🎨 Generar y empezar",
    customAiBack: "Volver",
    customAiGenerating: "Generando imágenes…",
    customAiPremiumOnly: "El modo Personalizado está reservado a los usuarios Premium.",
    customAiInvalid: "Rellena las 2 ideas antes de empezar.",
  },
};

const LANG_KEY = 'undercover_lang';

function detectLang() {
  // 1. Préférence stockée
  const stored = localStorage.getItem(LANG_KEY);
  if (stored && I18N[stored]) return stored;

  // 2. Langue navigateur
  const nav = (navigator.language || 'fr').slice(0, 2).toLowerCase();
  if (I18N[nav]) return nav;

  // 3. Fallback
  return 'fr';
}

let currentLang = detectLang();

function t(key, vars = {}) {
  const dict = I18N[currentLang] || I18N.fr;
  let val = dict[key] !== undefined ? dict[key] : (I18N.fr[key] || key);
  if (typeof val === 'string') {
    Object.entries(vars).forEach(([k, v]) => {
      val = val.replace(new RegExp(`\\{${k}\\}`, 'g'), v);
    });
  }
  return val;
}

function setLang(lang) {
  if (!I18N[lang]) return;
  currentLang = lang;
  try { localStorage.setItem(LANG_KEY, lang); } catch {}
  document.documentElement.lang = lang;
  applyI18n();
}

function applyI18n() {
  // Texte
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    el.innerHTML = t(key);
  });
  // Placeholder
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  // Aria-label
  document.querySelectorAll('[data-i18n-aria]').forEach(el => {
    el.setAttribute('aria-label', t(el.dataset.i18nAria));
  });
}

// Exposer globalement
window.i18n = { t, setLang, applyI18n, get current() { return currentLang; }, get all() { return Object.keys(I18N); } };
