/**
 * BiteRight — app.js
 * UI helpers: User session, Cart, Toast, Nav, dish card helpers.
 * API calls live in api.js.
 */

// ── Diet helpers ───────────────────────────────────────────────────────────
/**
 * Returns true only when the item is vegetarian/vegan.
 * Uses EXACT matching so "non_veg" is never mistaken for "veg".
 * diet_tags values from DB: "veg", "non_veg", "vegan", or empty.
 */
export function isVeg(dietTags) {
  const t = (dietTags || '').toLowerCase().trim();
  if (t === 'non_veg' || t === 'non-veg' || t === 'nonveg') return false;
  if (t.startsWith('non')) return false;
  if (t === 'veg' || t === 'vegetarian' || t === 'vegan') return true;
  return /(?<!non.?)veg/i.test(t);
}
export function dietLabel(d)    { return isVeg(d) ? '🌿 Veg'  : '🍖 Non-veg'; }
export function dietDotClass(d) { return isVeg(d) ? 'veg'     : 'nonveg'; }
export function dietEmoji(d)    { return isVeg(d) ? '🥦'      : '🍗'; }
export function dietTagClass(d) { return isVeg(d) ? 'tag-veg' : 'tag-nonveg'; }

// ── User Session ───────────────────────────────────────────────────────────
export const User = {
  get:   ()  => JSON.parse(localStorage.getItem('br_user') || 'null'),
  set:   (u) => localStorage.setItem('br_user', JSON.stringify(u)),
  clear: ()  => localStorage.removeItem('br_user'),
  id:    ()  => User.get()?.id ?? null,
  name:  ()  => User.get()?.name ?? 'Guest',
  token: ()  => User.get()?.token ?? null,
};

// ── Auth Guard ─────────────────────────────────────────────────────────────
// Sentinel thrown by requireAuth — caught silently by page catch blocks
export class AuthRedirect extends Error {
  constructor() { super('__auth_redirect__'); this.name = 'AuthRedirect'; }
}

export function requireAuth() {
  if (!User.get()) {
    const returnTo = encodeURIComponent(location.pathname + location.search);
    location.replace(`/login.html?next=${returnTo}`);
    throw new AuthRedirect();   // stops ALL further script execution
  }
  return true;
}

// ── Cart ───────────────────────────────────────────────────────────────────
// Each cart entry has a stable `lineKey` so two customizations of the same
// dish stay as separate lines (Task 1 requirement).
function _hash(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) { h = (h << 5) - h + str.charCodeAt(i); h |= 0; }
  return Math.abs(h).toString(36);
}
function _makeLineKey(dish) {
  const optIds = [...(dish.ingredient_option_ids || [])].sort((a, b) => a - b).join(',');
  const notes  = (dish.special_instructions || '').trim().toLowerCase();
  return `${dish.id}|${optIds}|${_hash(notes)}`;
}

export const Cart = {
  get:   ()      => JSON.parse(localStorage.getItem('br_cart') || '[]'),
  save:  (items) => { localStorage.setItem('br_cart', JSON.stringify(items)); Cart._notify(); },

  add(dish, restaurantId, restaurantName) {
    const items2   = Cart.get();
    // Mixed-restaurant guard: cart can only hold items from one restaurant.
    if (items2.length && String(items2[0].restaurantId) !== String(restaurantId)) {
      const ok = confirm(
        `Your cart has items from ${items2[0].restaurantName || 'another restaurant'}.\n` +
        `Clear it and start a new order from ${restaurantName || 'this restaurant'}?`
      );
      if (!ok) return false;
      localStorage.removeItem('br_cart');
    }
    const qty     = dish.qty || 1;
    const lineKey = _makeLineKey(dish);
    const idx     = items2.findIndex(i => i.lineKey === lineKey);
    if (idx >= 0) {
      items2[idx].qty += qty;
    } else {
      items2.push({
        ...dish,
        qty,
        restaurantId,
        restaurantName,
        lineKey,
        ingredient_option_ids: dish.ingredient_option_ids || [],
        ingredient_option_names: dish.ingredient_option_names || [],
        ingredient_extra_total: dish.ingredient_extra_total || 0,
        special_instructions: dish.special_instructions || '',
      });
    }
    Cart.save(items2);
  },

  remove(lineKey)     { Cart.save(Cart.get().filter(i => i.lineKey !== lineKey)); },

  updateQty(lineKey, qty) {
    if (qty <= 0) { Cart.remove(lineKey); return; }
    const items = Cart.get();
    const idx   = items.findIndex(i => i.lineKey === lineKey);
    if (idx >= 0) { items[idx].qty = qty; Cart.save(items); }
  },

  lineTotal(item) {
    return (Number(item.price) + Number(item.ingredient_extra_total || 0)) * item.qty;
  },

  clear: () => { localStorage.removeItem('br_cart'); Cart._notify(); },
  total: () => Cart.get().reduce((s, i) => s + Cart.lineTotal(i), 0),
  count: () => Cart.get().reduce((s, i) => s + i.qty, 0),


  _notify() {
    document.querySelectorAll('.cart-badge').forEach(el => { el.textContent = Cart.count(); });
    const fc = document.querySelector('.float-cart');
    if (fc) {
      if (Cart.count() > 0) {
        fc.classList.add('visible');
        const cc = fc.querySelector('.fc-count');
        const ct = fc.querySelector('.fc-total');
        if (cc) cc.textContent = Cart.count();
        if (ct) ct.textContent = `₹${Cart.total()}`;
      } else {
        fc.classList.remove('visible');
      }
    }
  },

  init() { Cart._notify(); },
};

// ── Toast ──────────────────────────────────────────────────────────────────
let _toastContainer;
function getToastContainer() {
  if (!_toastContainer) {
    _toastContainer = document.createElement('div');
    _toastContainer.className = 'toast-container';
    document.body.appendChild(_toastContainer);
  }
  return _toastContainer;
}

export function toast(msg, type = 'info', duration = 3000) {
  const icons  = { success: '✓', error: '✕', info: 'ℹ', cart: '🛒' };
  const colors = { success: '#2ECC71', error: '#E74C3C', info: '#FF4D00', cart: '#FF4D00' };
  const tc = getToastContainer();
  const el = document.createElement('div');
  el.className = `toast ${type}`;
  el.innerHTML = `<span style="color:${colors[type]};font-weight:700">${icons[type] || '·'}</span><span>${msg}</span>`;
  tc.appendChild(el);
  setTimeout(() => {
    el.style.animation = 'toastOut 0.3s ease forwards';
    setTimeout(() => el.remove(), 300);
  }, duration);
}

// ── Nav ────────────────────────────────────────────────────────────────────
export function renderNav(activePage = '') {
  const user  = User.get();
  const pages = [
    { href: '/index.html',           label: 'Home' },
    { href: '/restaurants.html',     label: 'Restaurants' },
    { href: '/recommendations.html', label: 'For You' },
    { href: '/orders.html',          label: 'Orders' },
  ];
  const links = pages.map(p =>
    `<a href="${p.href}" class="${activePage === p.href ? 'active' : ''}">${p.label}</a>`
  ).join('');

  const userArea = user
    ? `<span style="font-size:0.88rem;color:var(--text-secondary);font-weight:500;">Hi, ${user.name.split(' ')[0]} 👋</span>
       <a href="/login.html" class="btn btn-ghost btn-sm">Profile</a>`
    : `<a href="/login.html" class="btn btn-ghost btn-sm">Sign in</a>`;

  return `
  <nav class="nav">
    <a href="/index.html" class="nav-logo">🔥<span>Bite</span>Right</a>
    <div class="nav-links">${links}</div>
    <div class="nav-right">
      ${userArea}
      <a href="/cart.html" class="nav-cart-btn">
        🛒 Cart <span class="cart-badge">0</span>
      </a>
      <button class="nav-mobile-toggle" onclick="document.querySelector('.nav-links-mobile').classList.toggle('active')">☰</button>
    </div>
    <div class="nav-links-mobile">
      ${links}
    </div>
  </nav>`;
}

// ── Float Cart ─────────────────────────────────────────────────────────────
export function renderFloatCart() {
  return `
  <a href="/cart.html" class="float-cart">
    🛒 <span class="fc-count">0</span> items &nbsp;·&nbsp; <span class="fc-total">₹0</span> &nbsp;→ View Cart
  </a>`;
}

// ── Mood / Time Config ─────────────────────────────────────────────────────
export const MOODS = [
  { id: 'comfort',    emoji: '🤗', label: 'Comfort',    color: '#FF6B2B' },
  { id: 'healthy',    emoji: '🥗', label: 'Healthy',    color: '#2ECC71' },
  { id: 'spicy',      emoji: '🌶️', label: 'Spicy',      color: '#E74C3C' },
  { id: 'cheat_meal', emoji: '🍔', label: 'Cheat Meal', color: '#FFBE00' },
];

export const TIMES = [
  { id: 'morning',    label: 'Morning',    emoji: '🌅' },
  { id: 'afternoon',  label: 'Afternoon',  emoji: '☀️' },
  { id: 'night',      label: 'Night',      emoji: '🌙' },
  { id: 'late_night', label: 'Late Night', emoji: '🦉' },
];

// ── Dish Card ──────────────────────────────────────────────────────────────
/**
 * Renders a dish card.
 * opts.showAllergy  — show allergy-check button
 * opts.clickDetail  — clicking card opens item.html (default: true)
 */
export function dishCard(dish, restaurantId, restaurantName, opts = {}) {
  const veg        = isVeg(dish.diet_tags);
  const scoreTag   = dish.score != null ? `<span class="tag tag-score">⭐ ${dish.score}</span>` : '';
  const allergyBtn = opts.showAllergy
    ? `<button class="btn btn-ghost btn-sm allergy-check"
         data-name="${(dish.name||'').replace(/"/g, '&quot;')}"
         data-ingredients="${dish.ingredients || ''}">🔍 Allergy</button>` : '';

  const detailUrl    = `/item.html?id=${dish.id}&restaurant=${restaurantId}&restaurantName=${encodeURIComponent(restaurantName || '')}`;
  const clickDetail  = opts.clickDetail !== false;

  return `
  <div class="card dish-card fade-up${clickDetail ? ' dish-card-clickable' : ''}" data-id="${dish.id}"
       ${clickDetail ? `data-detail-url="${detailUrl}" style="cursor:pointer"` : ''}>
    <div class="dish-img-wrap">
      <div class="dish-img-placeholder">${dietEmoji(dish.diet_tags)}</div>
      <div class="dish-dot ${dietDotClass(dish.diet_tags)}"></div>
    </div>
    <div class="dish-body">
      <div class="flex-between mb-8">
        <h3 class="dish-name">${dish.name}</h3>${scoreTag}
      </div>
      <div class="dish-tags mb-8">
        <span class="tag ${dietTagClass(dish.diet_tags)}">${dietLabel(dish.diet_tags)}</span>
        ${dish.mood_tags ? `<span class="tag tag-mood">${dish.mood_tags}</span>` : ''}
      </div>
      <p class="dish-price">₹${dish.price}</p>
      <div class="dish-actions">
        <button class="btn btn-primary btn-sm add-to-cart"
          data-id="${dish.id}" data-name="${dish.name}" data-price="${dish.price}"
          data-diet="${dish.diet_tags || ''}" data-mood="${dish.mood_tags || ''}"
          data-ingredients="${dish.ingredients || ''}"
          data-restaurant-id="${restaurantId}"
          data-restaurant-name="${restaurantName || ''}">
          + Add
        </button>
        ${allergyBtn}
      </div>
    </div>
  </div>`;
}

// ── Cart button event binding ──────────────────────────────────────────────
export function bindCartButtons(container) {
  container.addEventListener('click', e => {
    // + Add button
    const addBtn = e.target.closest('.add-to-cart');
    if (addBtn) {
      e.stopPropagation();
      const dish = {
        id:          +addBtn.dataset.id,
        name:         addBtn.dataset.name,
        price:       +addBtn.dataset.price,
        diet_tags:    addBtn.dataset.diet,
        mood_tags:    addBtn.dataset.mood,
        ingredients:  addBtn.dataset.ingredients,
      };
      Cart.add(dish, addBtn.dataset.restaurantId, addBtn.dataset.restaurantName);
      toast(`${dish.name} added to cart!`, 'cart');
      addBtn.textContent = '✓ Added';
      addBtn.classList.replace('btn-primary', 'btn-secondary');
      setTimeout(() => {
        addBtn.textContent = '+ Add';
        addBtn.classList.replace('btn-secondary', 'btn-primary');
      }, 1500);
      return;
    }

    // Allergy button — uses backend NLP service for consistency.
    const allergyBtn = e.target.closest('.allergy-check');
    if (allergyBtn) {
      e.stopPropagation();
      const user      = User.get();
      const allergy   = (user?.allergies || '').trim();
      if (!allergy) { toast('No allergies on file. Update your profile.', 'info'); return; }
      const allergens = allergy.split(',').map(a => a.trim()).filter(Boolean);
      const text      = [
        allergyBtn.dataset.name || '',
        allergyBtn.dataset.ingredients || '',
      ].join(' ');
      import('/static/api.js').then(({ checkAllergy }) =>
        checkAllergy({ allergies: allergens, text })
          .then(res => {
            if (res.safe) toast('✓ Safe for your allergies!', 'success');
            else toast(`⚠️ Contains: ${(res.matched_allergens||[]).join(', ') || 'allergens'}`, 'error', 5000);
          })
          .catch(() => toast('Could not check allergens — try again.', 'error'))
      );
      return;
    }

    // Card click → navigate to item detail
    const card = e.target.closest('[data-detail-url]');
    if (card) location.href = card.dataset.detailUrl;
  });
}

// ── Currency formatter ─────────────────────────────────────────────────────
export const fmt = (n) => `₹${Number(n).toLocaleString('en-IN')}`;
