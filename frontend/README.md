# Quiply Frontend

Vanilla JavaScript SPA

## Structure

```
frontend/
├── index.html          # Entry point
├── css/
│   ├── reset.css
│   ├── style.css       # Global styles & variables
│   └── components/     # Component-specific styles
│       ├── buttons.css
│       ├── forms.css
│       ├── navbar.css
│       ├── cards.css
│       ├── profile.css
│       ├── modal.css
│       ├── comments.css
│       ├── auth.css
│       ├── feed.css
│       └── misc.css
└── js/
    ├── app.js          # Main entry point
    ├── api.js          # API client
    ├── router.js       # Hash-based router
    ├── state.js        # Global state management
    ├── utils.js        # Utility functions
    ├── components/     # Reusable UI components
    │   ├── Navbar.js
    │   ├── QuipCard.js
    │   ├── CreateQuip.js
    │   └── Comments.js
    └── pages/          # Page components
        ├── Feed.js
        ├── QuipDetail.js
        ├── Profile.js
        ├── Login.js
        └── Register.js
```

## Running

Serve the `frontend/` directory with any static file server:

```bash
# Python
python -m http.server 8080 -d frontend

# Node.js (npx)
npx serve frontend

# Or use VS Code Live Server extension
```

Then open http://localhost:8080

## Routes

| Route | Description |
|-------|-------------|
| `#/` | Feed (home) |
| `#/login` | Login page |
| `#/register` | Registration page |
| `#/quips/:id` | Quip detail with comments |
| `#/users/:username` | User profile |

## API Configuration

The API base URL is configured in `js/api.js`:

```javascript
const API_BASE = "https://api.quiply.yan-toples.ru/api/v1";
```
