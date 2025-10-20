# Hockey Evaluation Backend

FastAPI backend with PostgreSQL database for the Hockey Evaluation PWA.

## Features

- **PostgreSQL Database**: Persistent storage replacing in-memory data
- **User Authentication**: JWT-based authentication with secure password hashing
- **Multi-Coach Support**: Each coach has their own isolated data
- **Team Management**: Create and manage multiple teams
- **Player Management**: Add players with photos, track evaluations over time
- **Bulk Evaluations**: Evaluate multiple players quickly during tryouts
- **PDF Export**: Generate printable evaluation reports
- **Feedback Templates**: Save and reuse common feedback phrases
- **Search & Filters**: Find players quickly by name or team

## Setup

### Prerequisites

- Python 3.12+
- PostgreSQL database
- Poetry (Python package manager)

### Installation

1. Install dependencies:
```bash
poetry install
```

2. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update `.env` with your database credentials:
```
DATABASE_URL=postgresql://username:password@localhost:5432/hockey_eval
SECRET_KEY=your-secret-key-here
```

4. Create the database:
```bash
createdb hockey_eval
```

5. Run migrations:
```bash
poetry run alembic upgrade head
```

### Running the Server

Development mode (with auto-reload):
```bash
poetry run fastapi dev app/main.py
```

Production mode:
```bash
poetry run fastapi run app/main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new coach account
- `POST /api/auth/login` - Login and get access token
- `GET /api/auth/me` - Get current user info

### Teams

- `GET /api/teams` - List all teams for current coach
- `POST /api/teams` - Create new team

### Players

- `GET /api/players` - List all players (supports `?team_id=` and `?search=` filters)
- `POST /api/players` - Create new player
- `GET /api/players/{id}` - Get player with evaluation history
- `PUT /api/players/{id}` - Update player
- `DELETE /api/players/{id}` - Delete player
- `POST /api/players/{id}/photo` - Upload player photo
- `GET /api/players/{id}/pdf` - Download PDF evaluation report

### Evaluations

- `GET /api/evaluations` - List all evaluations (supports `?player_id=` filter)
- `POST /api/evaluations` - Create single evaluation
- `POST /api/evaluations/bulk` - Create multiple evaluations at once

### Feedback Templates

- `GET /api/feedback-templates` - List all templates
- `POST /api/feedback-templates` - Create new template
- `DELETE /api/feedback-templates/{id}` - Delete template

## Database Schema

### Users
- Email, username, password (hashed)
- Full name
- Created timestamp

### Teams
- Name, age group, season
- Belongs to coach (user)

### Players
- Name, jersey number, position, age group
- Photo URL (base64 encoded)
- Belongs to coach and optionally a team

### Evaluations
- Player reference
- Evaluator reference
- Date and evaluation type
- Six skill ratings (1-5): skating, shooting, passing, puck handling, hockey IQ, physicality
- Notes, strengths, areas for improvement

### Feedback Templates
- Name, category, text
- Belongs to coach
- Usage tracking

## Development

### Creating Migrations

After modifying models:
```bash
poetry run alembic revision --autogenerate -m "Description of changes"
poetry run alembic upgrade head
```

### Running Tests

```bash
poetry run pytest
```

## Deployment

The backend is designed to be deployed on Fly.io or similar platforms. Make sure to:

1. Set environment variables for `DATABASE_URL` and `SECRET_KEY`
2. Run migrations before starting the server
3. Use a production-grade PostgreSQL database

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens expire after 30 days
- All endpoints (except auth) require authentication
- Each coach can only access their own data
- CORS is enabled for development (configure for production)
