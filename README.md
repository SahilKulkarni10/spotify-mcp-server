# Spotify MCP Server with AI Integration

A Flask-based MCP (Modular Control Protocol) server that integrates with Spotify and uses Google's Gemini AI for natural language processing of music commands.

## Features

- 🎵 Spotify integration for playlist management
- 🤖 AI-powered natural language processing
- 🔒 OAuth2 authentication flow
- 📜 MCP protocol compliance
- 🚀 REST API endpoints for:
  - Track searching
  - Playlist creation
  - Playlist modification
  - AI-assisted command processing

## Prerequisites

- Python 3.9+
- Spotify Developer Account
- Google Gemini API Key
- Basic command line knowledge

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/spotify-mcp-server.git
cd spotify-mcp-server
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create `.env` file:
```env
SPOTIPY_CLIENT_ID=your_spotify_client_id
SPOTIPY_CLIENT_SECRET=your_spotify_secret
SPOTIPY_REDIRECT_URI=http://localhost:5001/callback
SPOTIPY_SCOPE=playlist-modify-public playlist-modify-private
GEMINI_API_KEY=your_gemini_api_key
```

2. Get credentials:
- [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
- [Google AI Studio](https://aistudio.google.com/app/apikey)

## Usage

1. Start the server:
```bash
python app.py
```

2. Authenticate with Spotify:



3. Use the API endpoints:

### AI-Powered Command
```bash
curl -X POST http://localhost:5001/mcp/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a workout playlist with rock songs"}'
```

### Direct API Calls
```bash
# Search track
curl -X POST http://localhost:5001/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"action": "search_track", "parameters": {"query": "Thriller Michael Jackson"}}'
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth` | GET | Initiate Spotify authentication |
| `/mcp/status` | GET | Server health check |
| `/mcp/actions` | GET | List available actions |
| `/mcp/execute` | POST | Execute direct commands |
| `/mcp/chat` | POST | Process natural language requests |

## Examples

### Create Playlist with AI
```bash
curl -X POST http://localhost:5001/mcp/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Make a jazz playlist with Miles Davis and John Coltrane"}'
```

Sample Response:
```json
{
  "result": {
    "id": "3jJ5VR3RJNA",
    "name": "Cool Jazz Night",
    "url": "https://open.spotify.com/playlist/3jJ5VR3RJNA"
  }
}
```

## Troubleshooting

**Invalid Access Token**
```bash
rm -rf .spotify_cache  # Clear cached credentials
# Re-authenticate via /auth endpoint
```

**Port Conflicts**
```bash
# Edit app.py and change port number
app.run(host='0.0.0.0', port=5001)  # Modify this line
```

**API Errors**
- Verify `.env` credentials
- Check Spotify developer dashboard settings
- Ensure proper OAuth scopes

## License

MIT License - See [LICENSE](LICENSE) for details

---

.