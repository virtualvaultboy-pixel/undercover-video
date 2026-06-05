// ============================================================
// Adult Mode (18+ gating)
// Activation manuelle via toggle dans Options. A chaque activation,
// modal de confirmation obligatoire (re-affichee toutes les 24h).
// Conformite : warning loi SREN France, decharge responsabilite.
// ============================================================

const ENABLED_KEY = 'adult_mode_on';
const CONFIRMED_KEY = 'adult_confirmed_at';
const CONFIRM_TTL_MS = 24 * 60 * 60 * 1000; // 24h

const adultMode = {
  isOn() {
    return localStorage.getItem(ENABLED_KEY) === '1';
  },

  setOn(on) {
    localStorage.setItem(ENABLED_KEY, on ? '1' : '0');
  },

  isConfirmationFresh() {
    const t = parseInt(localStorage.getItem(CONFIRMED_KEY) || '0', 10);
    return t > 0 && (Date.now() - t) < CONFIRM_TTL_MS;
  },

  markConfirmed() {
    localStorage.setItem(CONFIRMED_KEY, String(Date.now()));
  },

  clearConfirmation() {
    localStorage.removeItem(CONFIRMED_KEY);
  },

  /**
   * Affiche le modal de gating 18+. Retourne true si l'utilisateur confirme.
   * Si confirmation deja fraiche (< 24h) -> resolve(true) immediatement.
   */
  async requestConfirmation(force = false) {
    if (!force && this.isConfirmationFresh()) return true;

    return new Promise((resolve) => {
      const old = document.getElementById('adult-modal');
      if (old) old.remove();

      const modal = document.createElement('div');
      modal.id = 'adult-modal';
      modal.className = 'adult-modal';
      modal.innerHTML = `
        <div class="adult-modal-backdrop"></div>
        <div class="adult-modal-content">
          <h2>⚠️ Contenu réservé aux adultes 18+</h2>
          <p class="adult-modal-intro">
            Le Mode Adulte affiche du contenu à caractère <strong>sexuellement explicite</strong>
            depuis <strong>Redgifs.com</strong> (CDN tiers).
          </p>
          <ul class="adult-modal-list">
            <li>Je certifie avoir <strong>18 ans ou plus</strong></li>
            <li>Je reconnais avoir le droit légal d'accéder à ce contenu dans ma juridiction</li>
            <li>Je décharge l'application de toute responsabilité quant au contenu tiers</li>
            <li>Je m'engage à <strong>ne pas exposer ce contenu à des mineurs</strong></li>
          </ul>
          <p class="adult-modal-legal">
            ⚖️ Loi SREN France 2024 : contenu strictement interdit aux mineurs.
            En France, l'exposition d'un mineur à du contenu pornographique est punie
            de 3 ans de prison et 75 000 € d'amende (art. 227-24 Code pénal).
          </p>
          <div class="adult-modal-actions">
            <button type="button" class="primary adult-confirm-yes">J'ai 18 ans ou plus — Continuer</button>
            <button type="button" class="secondary adult-confirm-no">Annuler</button>
          </div>
        </div>
      `;
      document.body.appendChild(modal);

      modal.querySelector('.adult-confirm-yes').onclick = () => {
        this.markConfirmed();
        modal.remove();
        resolve(true);
      };
      modal.querySelector('.adult-confirm-no').onclick = () => {
        modal.remove();
        resolve(false);
      };
      modal.querySelector('.adult-modal-backdrop').onclick = () => {
        modal.remove();
        resolve(false);
      };
    });
  },
};

window.adultMode = adultMode;
