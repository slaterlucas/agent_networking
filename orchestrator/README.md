# Orchestrator Service

The orchestrator service handles user authentication, preferences storage, and personal agent lifecycle management for the agent networking platform.

## Features

- Google OAuth authentication
- JWT-based session management
- User preferences storage (SQLite)
- Personal agent spawning and management

## Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Configure Google OAuth**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Create OAuth 2.0 credentials (Web application)
   - Add authorized redirect URIs (e.g., `http://localhost:3000/auth/callback`)

3. **Environment setup**:
   ```bash
   cp orchestrator/config.example.env orchestrator/.env
   # Edit .env with your actual Google OAuth credentials
   ```

4. **Run the service**:
   ```bash
   uv run uvicorn orchestrator.main:app --reload --port 8000
   ```

## API Endpoints

### Authentication
- `POST /auth/google/callback` - Handle Google OAuth callback
- `GET /auth/me` - Get current user info

### Preferences
- `GET /preferences` - Get user preferences
- `PUT /preferences` - Update user preferences

### Health
- `GET /health` - Health check
- `GET /` - Service info

## Database

The service uses SQLite for local development. The database file is automatically created at `orchestrator/orchestrator.db` on first run.

### User Table Schema
- `id` - Internal UUID (primary key)
- `google_sub` - Google user identifier (unique)
- `email` - User email
- `name` - User display name
- `refresh_token` - Google refresh token (for calendar access)
- `preferences` - JSON preferences blob

## Frontend Integration

The frontend should:

1. Redirect users to Google OAuth with scopes:
   - `openid email profile`
   - `https://www.googleapis.com/auth/calendar.events`

2. Send the OAuth code to `/auth/google/callback`

3. Store the returned JWT for authenticated requests

4. Use the JWT in `Authorization: Bearer <token>` header for API calls

## Development

Run with auto-reload:
```bash
uv run uvicorn orchestrator.main:app --reload --port 8000
```

The service will be available at `http://localhost:8000` 