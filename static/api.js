/**
 * BiteRight — api.js
 * All API calls live here. Import from this file, NOT from app.js.
 */

const BASE = '/api';

function buildAuthHeaders(extra = {}) {
  const headers = { ...extra };
  try {
    const raw = localStorage.getItem('br_user');
    if (raw) {
      const u = JSON.parse(raw);
      if (u?.token) headers.Authorization = `Token ${u.token}`;
    }
  } catch { /* ignore */ }
  return headers;
}

async function apiFetch(url, options = {}) {
  let res;
  try {
    res = await fetch(url, {
      headers: buildAuthHeaders({
        'Content-Type': 'application/json',
        ...options.headers,
      }),
      ...options,
    });
  } catch (networkErr) {
    throw new Error('Network error — is the server running?');
  }

  let json;
  try { json = await res.json(); }
  catch { throw new Error(`Server returned non-JSON (HTTP ${res.status})`); }

  if (!res.ok) {
    const msg =
      json?.message ||
      json?.detail ||
      json?.errors?.detail ||
      json?.errors?.message ||
      (json?.errors ? JSON.stringify(json.errors) : null) ||
      `HTTP ${res.status}`;

    if (res.status === 401 && /invalid token|credentials|token/i.test(msg)) {
      localStorage.removeItem('br_user');
      const returnTo = encodeURIComponent(location.pathname + location.search);
      location.replace(`/login.html?next=${returnTo}&reason=session_expired`);
      throw new Error('__auth_redirect__');
    }

    const err = new Error(msg);
    err.status = res.status;
    err.payload = json;
    throw err;
  }

  return json;
}

// ── Users ──────────────────────────────────────────────────────────────────
export async function createUser(payload) {
  const json = await apiFetch(`${BASE}/users/`, {
    method: 'POST',
    body:   JSON.stringify(payload),
  });
  return json.data;
}

// ── Restaurants ────────────────────────────────────────────────────────────
export async function getRestaurants() {
  const json = await apiFetch(`${BASE}/restaurants/`);
  return Array.isArray(json.data) ? json.data : [];
}

// ── Menu ───────────────────────────────────────────────────────────────────
export async function getMenu(restaurantId) {
  const json = await apiFetch(`${BASE}/restaurants/${restaurantId}/menu/`);
  return Array.isArray(json.data) ? json.data : [];
}

// ── Recommendations ────────────────────────────────────────────────────────
export async function getRecommendations(restaurantId, mood = '', time = '') {
  const params = new URLSearchParams();
  if (mood) params.set('mood', mood);
  if (time) params.set('time', time);
  const qs   = params.toString() ? `?${params}` : '';
  const json = await apiFetch(`${BASE}/recommendations/${restaurantId}/${qs}`);
  return Array.isArray(json.data) ? json.data : [];
}

// ── Search ─────────────────────────────────────────────────────────────────
export async function searchMenu(query) {
  const json = await apiFetch(`${BASE}/search-menu/?q=${encodeURIComponent(query)}`);
  return Array.isArray(json.data) ? json.data : [];
}

// ── Reviews ────────────────────────────────────────────────────────────────
export async function getReviews(restaurantId) {
  const json = await apiFetch(`${BASE}/restaurants/${restaurantId}/reviews/`);
  return Array.isArray(json.data) ? json.data : [];
}
export async function createReview({ restaurant, menu_item = null, rating, comment }) {
  const json = await apiFetch(`${BASE}/reviews/`, {
    method: 'POST',
    body: JSON.stringify({ restaurant, menu_item, rating, comment }),
  });
  return json.data;
}

// ── Addresses ──────────────────────────────────────────────────────────────
export async function getAddresses() {
  const json = await apiFetch(`${BASE}/users/addresses/`);
  return Array.isArray(json.data) ? json.data : [];
}
export async function createAddress(payload) {
  const json = await apiFetch(`${BASE}/users/addresses/`, {
    method: 'POST', body: JSON.stringify(payload),
  });
  return json.data;
}
export async function deleteAddress(id) {
  return apiFetch(`${BASE}/users/addresses/${id}/`, { method: 'DELETE' });
}

// ── Orders ─────────────────────────────────────────────────────────────────
/**
 * Items shape: [{ id, qty, ingredient_option_ids?: number[], special_instructions?: string }]
 */
export async function createOrder(items, restaurantId, addressId = null) {
  const payload = {
    restaurant: restaurantId ?? null,
    address:    addressId ?? null,
    items: items.map(item => ({
      menu_item: item.id,
      quantity:  item.qty ?? 1,
      ingredient_option_ids: item.ingredient_option_ids || [],
      special_instructions:  item.special_instructions || '',
    })),
  };
  const json = await apiFetch(`${BASE}/orders/`, {
    method: 'POST',
    body:   JSON.stringify(payload),
  });
  return json.data;
}

export async function getOrders() {
  const json = await apiFetch(`${BASE}/orders/`);
  return Array.isArray(json.data) ? json.data : [];
}

export async function getOrder(id) {
  const json = await apiFetch(`${BASE}/orders/${id}/`);
  return json.data;
}

// ── Payments ───────────────────────────────────────────────────────────────
export async function processPayment(payload) {
  // payload: { order_id, method, card_number?, cvv?, expiry?, cardholder_name?, upi_id? }
  const json = await apiFetch(`${BASE}/payments/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
  return json.data;
}

// ── Profile / Address extras ───────────────────────────────────────────────
export async function getProfileMe() {
  const json = await apiFetch(`${BASE}/users/profile/me/`);
  return json.data;
}
export async function updateProfileMe(payload) {
  const json = await apiFetch(`${BASE}/users/profile/me/`, {
    method: 'PATCH', body: JSON.stringify(payload),
  });
  return json.data;
}
export async function updateAddress(id, payload) {
  const json = await apiFetch(`${BASE}/users/addresses/${id}/`, {
    method: 'PATCH', body: JSON.stringify(payload),
  });
  return json.data;
}

// ── Allergy + safe menu ────────────────────────────────────────────────────
export async function checkAllergy({ allergies, text }) {
  const json = await apiFetch(`${BASE}/check-allergy/`, {
    method: 'POST',
    body: JSON.stringify({ allergies, text }),
  });
  return json.data; // { safe, matched_allergens }
}
export async function getSafeMenu(restaurantId) {
  const json = await apiFetch(`${BASE}/safe-menu/${restaurantId}/`);
  return Array.isArray(json.data) ? json.data : [];
}

// ── Single restaurant (derived from list) ──────────────────────────────────
export async function getRestaurant(id) {
  const list = await getRestaurants();
  return list.find(r => String(r.id) === String(id)) || null;
}
