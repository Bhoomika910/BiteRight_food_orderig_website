# BiteRight — v12 patch report

This patch fixes every critical bug listed in the v11 audit and fills in the
missing UI surfaces. All existing modules are preserved; nothing was rebuilt
from scratch.

## How to apply

1. Replace the project directory with this one (or merge the changed files).
2. Run migrations:
   ```bash
   python manage.py migrate
   ```
3. Restart `python manage.py runserver`.

## Bugs fixed

| # | Bug | Fix |
|---|-----|-----|
| 1 | `addresses.html` missing; checkout never passes address | New full CRUD page `templates/addresses.html`; `Cart → Address → Payment` flow; `UserAddress` extended with `full_name / phone / house / street / state` + new migration `users/0004_address_and_profile_fields`; `AddressDetailView` now supports `PATCH` and `set as default`; first address auto-default; default re-elected on delete. |
| 2 | Mixed-restaurant cart accepted by client | `Cart.add()` in `static/app.js` now blocks add and prompts the user to clear & start a new order. |
| 3 | Customization extras ignored in payment/order totals | `payment.html` and `orders.html` recompute line totals as `(price + Σ extras) × qty`. Cart already used `lineTotal`, now consistent across all surfaces. |
| 4 | COD shown as "Payment Successful / Amount paid" | `payment-success.html` branches on `payment_status === 'cod'`: title → *Order Confirmed*, status → *Pending collection (COD)*, amount label → *Amount due on delivery*, gold pill instead of green. `orders.html` mirrors the same labels. |
| 5 | Frontend/backend allergy logic diverged | Removed substring check in `static/app.js`. Allergy button now POSTs to `/api/check-allergy/` (synonym-aware `nlp_service`). New `checkAllergy()` and `getSafeMenu()` helpers in `api.js`. |
| 6 | Restaurant UI used random/placeholder values | `menu.html` now fetches the real restaurant via `getRestaurant()` and renders `rating`, `delivery_time`, `cuisine_type`, `location` from the DB. |
| 7 | CSS undefined vars (`--text2`, `--text3`) and missing Syne font | `style.css` adds `--text2` / `--text3` aliases and imports the **Syne** font alongside Poppins/Inter. |

## Features added / completed

- **Reviews UI** — `menu.html` gained a Reviews panel: list, star-rating, comment form (uses existing `/api/restaurants/<id>/reviews/` and `/api/reviews/`).
- **Order tracking timeline** — every order card on `orders.html` now shows a 4-step pipeline *Order Placed → Preparing → Out for Delivery → Delivered* with completed steps highlighted, plus the delivery address.
- **Profile management** — new `PATCH /api/users/profile/me/` and `PATCH /api/users/<id>/` endpoints (with `updateProfileMe()` JS helper) so any page can edit name / phone / allergies / diet.
- **Address management end-to-end** — full add/edit/delete/default flow with inline field validation and server-side validation in `UserAddressSerializer`.
- **Validation & error feedback** — `addresses.html` renders per-field server errors; toasts for network failures; retry button on load failure.

## Architecture cleanups

- Single source of truth for allergy checks (backend NLP via `/api/check-allergy/`).
- `OrderSerializer` now nests `address_detail` so payment & confirmation pages don't need a second fetch.
- `UserAddress.save()` auto-composes `address_line` from structured fields, preserving back-compat.

## Files changed

```
users/models.py                 (added phone, structured address fields)
users/serializers.py            (validation rules)
users/views.py                  (PATCH address, ProfileMeView, default rotation)
users/urls.py                   (added /profile/me/)
users/migrations/0004_address_and_profile_fields.py   NEW
orders/serializers.py           (nested address_detail)
restaurants/* — unchanged
static/api.js                   (updateAddress, checkAllergy, getSafeMenu, getRestaurant, profile/me)
static/app.js                   (mixed-cart guard, backend allergy check)
static/style.css                (Syne font, --text2/--text3 aliases)
templates/cart.html             (redirect to /addresses.html?from=cart)
templates/addresses.html        NEW — full address CRUD page
templates/payment.html          (line extras + delivery address card)
templates/payment-success.html  (COD-aware)
templates/orders.html           (timeline + extras totals + address line)
templates/menu.html             (real restaurant meta + reviews section)
```

## Remaining / known-future work

- Real payment provider (currently simulated; clearly labeled).
- Pagination on order history and restaurant list.
- Browser-level end-to-end tests (Playwright/Cypress).
- Profile page UI (backend ready via `/profile/me/`).
