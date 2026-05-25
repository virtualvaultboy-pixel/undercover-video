// ============================================================
// Play Billing via Digital Goods API
// Fonctionne dans un TWA (PWABuilder) install via Google Play Store.
// Documentation: https://web.dev/articles/digital-goods
// ============================================================

const SKU_PREMIUM = 'premium_unlock';
const PLAY_BILLING_URL = 'https://play.google.com/billing';

const playBilling = {
  available: false,
  service: null,

  async init() {
    // 1. Verifier que l'API Digital Goods est dispo (TWA Chrome Android)
    if (!('getDigitalGoodsService' in window)) {
      console.log('[Billing] Digital Goods API non disponible (PWA pure ou navigateur classique)');
      return false;
    }
    try {
      this.service = await window.getDigitalGoodsService(PLAY_BILLING_URL);
      this.available = true;
      console.log('[Billing] Service Google Play Billing connecte');

      // Au boot, on regarde si l'achat est deja possede et on debloque
      await this.checkExistingPurchases();
      return true;
    } catch (e) {
      console.warn('[Billing] Impossible de se connecter au service Play Billing :', e);
      return false;
    }
  },

  async fetchDetails() {
    if (!this.available) return null;
    try {
      const items = await this.service.getDetails([SKU_PREMIUM]);
      return items.length > 0 ? items[0] : null;
    } catch (e) {
      console.warn('[Billing] getDetails failed :', e);
      return null;
    }
  },

  async checkExistingPurchases() {
    if (!this.available) return false;
    try {
      const purchases = await this.service.listPurchases();
      const owned = purchases.find(p => p.itemId === SKU_PREMIUM);
      if (owned) {
        console.log('[Billing] Premium deja possede, deblocage');
        try { localStorage.setItem('undercover_premium', 'true'); } catch {}
        return true;
      }
    } catch (e) {
      console.warn('[Billing] listPurchases failed :', e);
    }
    return false;
  },

  async buy() {
    if (!this.available) {
      throw new Error('billing_unavailable');
    }
    const details = await this.fetchDetails();
    if (!details) throw new Error('sku_unavailable');

    const paymentMethod = [{
      supportedMethods: PLAY_BILLING_URL,
      data: { sku: SKU_PREMIUM },
    }];
    const paymentDetails = {
      total: {
        label: details.title || 'Premium',
        amount: { currency: details.price.currency, value: details.price.value },
      },
    };

    const request = new PaymentRequest(paymentMethod, paymentDetails);
    const response = await request.show();
    const token = response.details.purchaseToken;

    // Acquittement OBLIGATOIRE : sinon Google rembourse a J+3 silencieusement.
    // Si l'acknowledge echoue, on doit considerer l'achat comme echoue cote app
    // pour ne pas debloquer un Premium qui sera revoque.
    try {
      await this.service.acknowledge(token, 'onetime');
    } catch (e) {
      console.error('[Billing] acknowledge failed, marking purchase as failed:', e);
      try { await response.complete('fail'); } catch {}
      throw new Error('acknowledge_failed');
    }

    await response.complete('success');
    try { localStorage.setItem('undercover_premium', 'true'); } catch {}
    return true;
  },
};

window.playBilling = playBilling;
