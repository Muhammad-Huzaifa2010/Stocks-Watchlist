# Stocks Watchlist — Frontend

React + Vite frontend for the Stocks Watchlist app. It uses React Router and plain CSS.

## Setup

```bash
npm install
cp .env.example .env
npm run dev
```

The app runs at http://localhost:5173.

## Scripts

| Command | What it does |
| --- | --- |
| `npm run dev` | Start the development server |
| `npm run build` | Build for production into `dist/` |
| `npm run preview` | Preview the production build |
| `npm run lint` | Lint with oxlint |

## Environment

| Variable | Example | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | `http://127.0.0.1:8000` | FastAPI backend URL |

Anything starting with `VITE_` is visible in the browser. Never put backend secrets here.

## Routes

| Path | Page |
| --- | --- |
| `/` | Redirects to `/login` |
| `/login` | Login |
| `/signup` | Signup |
| `/dashboard` | Dashboard |
| anything else | 404 page |
