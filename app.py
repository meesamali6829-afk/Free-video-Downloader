from flask import Flask, request, jsonify, render_template
import yt_dlp

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
        # Niche wali 2 lines APK/Mobile download guarantee ke liye hain
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # If mode is mp3, change format to bestaudio
    if mode == 'mp3':
        ydl_opts['format'] = 'bestaudio/best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            # --- GUARANTEED LINK LOGIC START ---
            # Pehle direct URL check karega, agar nahi mila toh formats mein se best wala nikalega
            media_url = info.get('url')
            if not media_url and 'formats' in info:
                for f in reversed(info['formats']):
                    if mode == 'mp3' and f.get('acodec') != 'none':
                        media_url = f.get('url')
                        break
                    elif mode == 'video' and f.get('vcodec') != 'none':
                        media_url = f.get('url')
                        break
            # --- GUARANTEED LINK LOGIC END ---
            
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
    app.run(debug=True, host='0.0.0.0', port=5000)
