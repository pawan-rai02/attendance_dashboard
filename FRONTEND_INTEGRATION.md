# Frontend Integration (Minimal)

Quick reference for developers who need to modify the UI.

---

## Where Things Live

| What | Location |
|------|----------|
| HTML templates | `backend/templates/` |
| CSS | `static/css/styles.css` |
| JavaScript | `static/js/app.js` |

---

## Pages & Routes

| URL | Template | Purpose |
|-----|----------|---------|
| `/` | `index.html` | Landing page, summary, defaulters |
| `/student` | `student.html` | Student dropdown, attendance details, charts |
| `/analytics` | `dashboard.html` | Class/subject analytics, bar charts |

All pages extend `base.html` (navbar, footer, shared CSS/JS).

---

## How It Works

1. FastAPI serves HTML from `backend/templates/`.
2. `app.js` fetches data from `/api/v1/*` and updates the page.
3. Chart.js (loaded via CDN) draws the charts.

---

## Quick Customization

**Change colors** – Edit `static/css/styles.css`:
```css
:root {
    --primary-color: #4f46e5;
    --success-color: #10b981;
    --danger-color: #ef4444;
}
```

**Add a page** – Create `backend/templates/newpage.html`, add route in `backend/main.py`:
```python
@app.get("/new-page", response_class=HTMLResponse)
async def new_page(request: Request):
    return templates.TemplateResponse("newpage.html", {"request": request})
```

**Change nav links** – Edit `backend/templates/base.html` (the `<ul class="navbar-nav">` section).

---

## Troubleshooting

- **Styles/JS not loading** – Check that `static/` is mounted in `main.py` and paths are correct.
- **API 404** – `app.js` uses `window.location.origin + '/api/v1'`; ensure the app runs on the expected port.
- **Charts blank** – Open browser DevTools → Console for errors; ensure Chart.js CDN loads.

---

For full API details, see `README.md` and `TECHNICAL_DOCS.md`.
