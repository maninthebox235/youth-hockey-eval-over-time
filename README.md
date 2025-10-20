# youth-hockey-eval-over-time

A mobile-first Progressive Web App for tracking and evaluating youth hockey players' performance over time.

## Live Demo

🏒 **[Try the App](https://hockey-eval-app-9iqh7vr7.devinapps.com)**

## Features

- **Offline-First**: Works without internet, syncs when online
- **Player Roster Management**: Add and track team players
- **Quick Evaluations**: Touch-optimized forms for rinkside use
- **Skill Tracking**: Rate 6 key skills (skating, shooting, passing, puck handling, hockey IQ, physicality)
- **Evaluation History**: View detailed progress over time
- **Mobile-Optimized**: Designed for cold rinks and one-handed use

## Project Structure

- `/hockey-eval-pwa` - Full-stack PWA application
  - `/backend` - FastAPI backend with RESTful API
  - `/frontend` - React + TypeScript PWA frontend

See [hockey-eval-pwa/README.md](hockey-eval-pwa/README.md) for detailed documentation.

## Quick Start

### Backend
```bash
cd hockey-eval-pwa/backend
poetry install
poetry run fastapi dev app/main.py
```

### Frontend
```bash
cd hockey-eval-pwa/frontend
npm install
npm run dev
```

## Tech Stack

- **Backend**: FastAPI, Python
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Deployment**: Fly.io (backend), Devin Apps (frontend)

## Development Notes

This is a proof of concept using in-memory storage. Data will reset when the backend restarts. Future versions will include persistent database storage.
