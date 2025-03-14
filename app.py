from flask import Flask, jsonify, request
import spotipy
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

app = Flask(__name__)

# Configuration
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')
SPOTIPY_SCOPE = os.getenv('SPOTIPY_SCOPE')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize Spotify client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET,
    redirect_uri=SPOTIPY_REDIRECT_URI,
    scope=SPOTIPY_SCOPE
))

# Configure Gemini AI
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-1.5-flash')

def get_spotify_client():
    """Create a new Spotify client with current auth token"""
    auth_manager = SpotifyOAuth(
        client_id=SPOTIPY_CLIENT_ID,
        client_secret=SPOTIPY_CLIENT_SECRET,
        redirect_uri=SPOTIPY_REDIRECT_URI,
        scope=SPOTIPY_SCOPE,
        cache_path=".spotify_cache"
    )
    return spotipy.Spotify(auth_manager=auth_manager)

@app.route('/auth')
def authenticate():
    try:
        auth_url = sp.auth_manager.get_authorize_url()
        return f'<a href="{auth_url}">Authenticate with Spotify</a>'
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/callback')
def callback():
    try:
        code = request.args.get('code')
        sp = get_spotify_client()
        sp.auth_manager.get_access_token(code)
        return jsonify({"status": "Authentication successful! You can now use the API endpoints."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/status', methods=['GET'])
def status():
    return jsonify({"status": "ok"})

@app.route('/mcp/actions', methods=['GET'])
def list_actions():
    actions = [
        {
            "name": "search_track",
            "description": "Search for a track on Spotify",
            "parameters": {
                "query": {"type": "string", "description": "Search query"}
            }
        },
        {
            "name": "create_playlist",
            "description": "Create a new playlist",
            "parameters": {
                "name": {"type": "string", "description": "Playlist name"},
                "description": {"type": "string", "optional": True}
            }
        },
        {
            "name": "add_to_playlist",
            "description": "Add track to playlist",
            "parameters": {
                "playlist_id": {"type": "string"},
                "track_uri": {"type": "string"}
            }
        }
    ]
    return jsonify({"actions": actions})

@app.route('/mcp/execute', methods=['POST'])
def execute():
    data = request.get_json()
    if not data or 'action' not in data:
        return jsonify({"error": "Missing action"}), 400
    
    action = data['action']
    params = data.get('parameters', {})

    try:
        if action == "search_track":
            return handle_search(params)
        elif action == "create_playlist":
            return handle_create_playlist(params)
        elif action == "add_to_playlist":
            return handle_add_to_playlist(params)
        else:
            return jsonify({"error": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/mcp/chat', methods=['POST'])
def ai_assistant():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing prompt"}), 400
    
    try:
        # Generate response with Gemini
        response = gemini_model.generate_content(
            f"{create_system_prompt()}\n\nUser Request: {data['prompt']}"
        )
        
        # Parse AI response
        command = parse_ai_response(response.text)
        
        # Create request context for execute endpoint
        with app.test_request_context('/mcp/execute', 
            method='POST',
            json={
                'action': command['action'],
                'parameters': command['parameters']
            }):
            
            # Call execute through proper request handling
            return execute()
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def create_system_prompt():
    return """You are a Spotify controller AI. Convert user requests into JSON commands using these actions:
    
    Available Actions:
    1. search_track - {query: string}
    2. create_playlist - {name: string, description?: string}
    3. add_to_playlist - {playlist_id: string, track_uri: string}
    
    Respond ONLY with valid JSON in this format:
    {
        "action": "action_name",
        "parameters": {
            "param1": "value1",
            "param2": "value2"
        }
    }"""

def parse_ai_response(response_text):
    try:
        # Extract JSON from response
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        json_str = response_text[start:end]
        return json.loads(json_str)
    except Exception as e:
        raise ValueError(f"Failed to parse AI response: {str(e)}")

def handle_search(params):
    query = params.get('query')
    if not query:
        return jsonify({"error": "Missing query parameter"}), 400
    
    results = sp.search(q=query, type='track', limit=1)
    if not results['tracks']['items']:
        return jsonify({"error": "No results found"}), 404
    
    track = results['tracks']['items'][0]
    return jsonify({
        "result": {
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "uri": track['uri']
        }
    })

def handle_create_playlist(params):
    sp = get_spotify_client()
    name = params.get('name')
    if not name:
        return jsonify({"error": "Missing name parameter"}), 400
    
    try:
        user = sp.current_user()
        playlist = sp.user_playlist_create(
            user['id'],
            name,
            public=True,
            description=params.get('description', '')
        )
        return jsonify({
            "result": {
                "id": playlist['id'],
                "name": playlist['name'],
                "url": playlist['external_urls']['spotify']
            }
        })
    except spotipy.SpotifyException as e:
        return jsonify({"error": f"Spotify API error: {e.msg}"}), e.http_status

def handle_add_to_playlist(params):
    playlist_id = params.get('playlist_id')
    track_uri = params.get('track_uri')
    
    if not playlist_id or not track_uri:
        return jsonify({"error": "Missing required parameters"}), 400
    
    sp.playlist_add_items(playlist_id, [track_uri])
    return jsonify({"result": "Track added successfully"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)