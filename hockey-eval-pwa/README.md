# Hockey Eval PWA

A mobile-first Progressive Web App for rinkside hockey player evaluations with offline support.

## Features

- **Offline-First Architecture**: Works without internet connection, syncs when online
- **Player Management**: Add and manage team rosters
- **Quick Evaluations**: Touch-optimized evaluation forms with skill ratings (1-10)
- **Evaluation History**: Track player progress over time with detailed breakdowns
- **Mobile-Optimized**: Designed for one-handed use with gloves in cold rinks
- **Real-time Sync**: Automatic data synchronization when connectivity returns

## Tech Stack

### Backend
- FastAPI (Python)
- In-memory storage (proof of concept)
- RESTful API with CORS enabled

### Frontend
- React + TypeScript
- Vite build system
- Tailwind CSS for styling
- shadcn/ui component library
- Lucide icons
- LocalStorage for offline data persistence

## Development

### Backend

```bash
cd backend
poetry install
poetry run fastapi dev app/main.py
```

Backend runs on http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on http://localhost:5173

## Deployment

### Backend
Deployed to Fly.io: https://app-alugplqg.fly.dev

### Frontend
Deployed PWA: https://hockey-eval-app-9iqh7vr7.devinapps.com

## API Endpoints

- `GET /api/players` - Get all players
- `POST /api/players` - Create a player
- `GET /api/players/{id}` - Get player by ID
- `PUT /api/players/{id}` - Update player
- `DELETE /api/players/{id}` - Delete player
- `GET /api/evaluations` - Get all evaluations (optional player_id filter)
- `POST /api/evaluations` - Create an evaluation
- `GET /api/evaluations/{id}` - Get evaluation by ID
- `PUT /api/evaluations/{id}` - Update evaluation
- `DELETE /api/evaluations/{id}` - Delete evaluation
- `POST /api/sync` - Sync offline data

## Data Models

### Player
- name (required)
- jersey_number (optional)
- position (optional)
- age_group (optional)
- team (optional)

### Evaluation
- player_id (required)
- player_name (required)
- evaluator (required)
- evaluation_type (practice, game, tryout, scrimmage)
- skills (skating, shooting, passing, puck_handling, hockey_iq, physicality) - rated 1-10
- strengths (optional)
- areas_for_improvement (optional)
- notes (optional)

## Future Enhancements

- Persistent database (PostgreSQL)
- User authentication
- Team management with multiple coaches
- Advanced analytics and charts
- Video upload and annotation
- Export to PDF reports
- Push notifications for offline sync
- Service worker for true PWA offline support
