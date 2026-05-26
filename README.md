# BiteRight 🍽️

A smart food ordering app with personalized, allergy-safe recommendations.

## Quick Start

### 1. Create & activate a virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Go into the Django project folder
```bash
cd biteright
```

### 4. Apply migrations
```bash
python manage.py migrate
```

### 5. (Optional) Seed the database with sample data
```bash
python seed_db.py
```

### 6. Run the development server
```bash
python manage.py runserver
```

### 7. Open in browser
Visit: http://127.0.0.1:8000

---

## Project Structure
```
biteright/              ← Django project root (manage.py lives here)
├── core/               ← settings, urls, wsgi/asgi
│   └── utils/
│       └── response.py ← success_response / error_response helpers
├── users/              ← UserProfile, auth, token login
├── restaurants/        ← Restaurant, MenuItem, Review, allergy NLP
│   └── services/
│       └── recommendation_service.py
├── orders/             ← Order, OrderItem, cart → order flow
├── templates/          ← HTML pages (index, menu, cart, orders…)
└── static/             ← app.js, api.js, style.css
```

## Bugs Fixed
| # | Bug | Fix |
|---|-----|-----|
| 1 | `recommendation_service.py` wrong location | Placed at `restaurants/services/` with `__init__.py` |
| 2 | `core/utils/response.py` missing | Created with `success_response` / `error_response` |
| 3 | `SECRET_KEY` crash on startup | Falls back to insecure dev key when `DEBUG=True` |
| 4 | `total_amount`/`order_time` rename | Aligned to `total_price`/`created_at` everywhere |
| 5 | `OrderItem` missing from migration | Included in `orders/migrations/0001_initial.py` |
| 6 | `STATIC_ROOT` missing | Added to `settings.py` for `collectstatic` |
| 7 | Ratings were random in frontend | Now uses `r.rating` from API with random fallback |
| 8 | `ReviewListView` GET required auth | `get_permissions()` → GET=AllowAny, POST=IsAuthenticated |
