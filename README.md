# Revamp Backend

FastAPI backend for Revamp — an iOS app that parses Instagram Reels into savable notes.

## Architecture

```
POST /api/reels/parse   ← iOS Share Extension sends reel URL here
        ↓
Instagram oEmbed API    ← fetches caption + metadata
        ↓
AI Parser (GPT-4o/Claude) ← structures caption into a note
        ↓
POST /api/notes         ← user confirms and saves the note
```

## Quick Start

```bash
# 1. Clone and enter repo
git clone https://github.com/alexyao2/revamp-backend
cd revamp-backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY (minimum required)

# 5. Run the server
uvicorn app.main:app --reload
```

Server runs at: http://localhost:8000
Interactive API docs: http://localhost:8000/docs

## API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Get JWT token |

### Reels
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reels/parse` | Parse reel URL → note preview |

### Notes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/notes` | Save a note |
| GET | `/api/notes` | List notes (supports filters) |
| GET | `/api/notes/{id}` | Get single note |
| PATCH | `/api/notes/{id}` | Edit note |
| DELETE | `/api/notes/{id}` | Delete note |

### Habits
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/habits` | Create habit |
| GET | `/api/habits` | List habits |
| POST | `/api/habits/{id}/checkin` | Check in (increments streak) |
| PATCH | `/api/habits/{id}` | Update habit |
| DELETE | `/api/habits/{id}` | Delete habit |

## Testing a Reel Parse (No Instagram Token)

While setting up, use `caption_override` to test parsing without Instagram credentials:

```bash
curl -X POST http://localhost:8000/api/reels/parse \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.instagram.com/reel/ABC123/",
    "caption_override": "5 tips to sleep better:\n1. No screens 1hr before bed\n2. Keep room cool (65-68°F)\n3. Same bedtime every night\n4. Limit caffeine after 2pm\n5. Try magnesium glycinate"
  }'
```

## iOS Integration

The iOS Share Extension should:
1. Capture the shared Instagram URL via `NSExtensionItem`
2. Read the JWT from Keychain
3. POST to `/api/reels/parse`
4. Show the `note_preview` to the user for confirmation
5. On confirm, POST to `/api/notes` to save

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | SQLite (dev) or Postgres (prod) |
| `SECRET_KEY` | Yes | JWT signing secret |
| `OPENAI_API_KEY` | Recommended | For AI note parsing |
| `ANTHROPIC_API_KEY` | Optional | Fallback AI parser |
| `INSTAGRAM_ACCESS_TOKEN` | Optional | For auto-fetching captions |

## Deploying

**Railway (recommended):**
```bash
# Install Railway CLI
npm install -g @railway/cli
railway login
railway init
railway up
```
Set your env vars in the Railway dashboard. Use Postgres addon for production DB.

## Roadmap

- [x] Reel URL → AI-parsed note
- [x] Notes CRUD
- [x] Habit tracking with streaks
- [ ] Instagram oEmbed integration (requires Meta app approval)
- [ ] Push notifications for habit reminders
- [ ] Screen Time API integration (iOS FamilyControls framework)
- [ ] App usage analytics
