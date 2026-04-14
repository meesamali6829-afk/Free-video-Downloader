from flask import Flask, request, jsonify, render_template
import yt_dlp
import os

app = Flask(__name__, template_folder='templates')

# List to store only successful downloads
completed_downloads = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
def fetch_video():
    url = request.json.get('url')
    mode = request.json.get('mode', 'video') # Detect if user wants mp3 or video
    
    if not url:
        return jsonify({"error": "Link blank hai", "status": "fail"}), 400

    # Default options for Video
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True, # Security bypass ke liye zaroori hai
    }

    # If mode is mp3, change format to bestaudio
    if mode == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # Use audio_url if mode is mp3, else video_url
            media_url = info.get('url')
            
            video_data = {
                "title": info.get('title', 'Video File'),
                "video_url": media_url if mode == 'video' else None,
                "audio_url": media_url if mode == 'mp3' else None,
                "thumbnail": info.get('thumbnail'),
                "status": "success"
            }
            return jsonify(video_data)
    except Exception as e:
        return jsonify({"error": str(e), "status": "fail"}), 500

# Save to history ONLY when user clicks download and it completes
@app.route('/save-history', methods=['POST'])
def save_history():
    data = request.json
    if data:
        completed_downloads.insert(0, data)
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 400

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(completed_downloads)

if __name__ == '__main__':
    # Isse app har hosting platform (Render/HuggingFace) par sahi chalegi
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
