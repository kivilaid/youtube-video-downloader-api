from flask import Flask, request, jsonify
from pytube import YouTube
import re

# Initialize Flask application
app = Flask(__name__)

def download_video(url, resolution):
    """
    Download YouTube video with specified resolution.
    
    Args:
        url (str): YouTube video URL
        resolution (str): Desired video resolution (e.g., '720p', '1080p')
    
    Returns:
        tuple: (success_status, error_message)
    """
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, 
                                 file_extension='mp4', 
                                 resolution=resolution).first()
        if stream:
            stream.download()
            return True, None
        else:
            return False, "Video with the specified resolution not found."
    except Exception as e:
        return False, str(e)

def get_video_info(url):
    """
    Retrieve metadata information for a YouTube video.
    
    Args:
        url (str): YouTube video URL
    
    Returns:
        tuple: (video_info_dict, error_message)
    """
    try:
        yt = YouTube(url)
        video_info = {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description,
            "publish_date": str(yt.publish_date),  # Convert datetime to string for JSON serialization
            "available_resolutions": [
                stream.resolution 
                for stream in yt.streams.filter(progressive=True, file_extension='mp4')
            ]
        }
        return video_info, None
    except Exception as e:
        return None, str(e)

def is_valid_youtube_url(url):
    """
    Validate if the provided URL is a valid YouTube video URL.
    
    Args:
        url (str): URL to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]+(&\S*)?$"
    return re.match(pattern, url) is not None

@app.route('/download/<resolution>', methods=['POST'])
def download_by_resolution(resolution):
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    
    success, error_message = download_video(url, resolution)
    
    if success:
        return jsonify({"message": f"Video with resolution {resolution} downloaded successfully."}), 200
    else:
        return jsonify({"error": error_message}), 500

@app.route('/video_info', methods=['POST'])
def video_info():
    data = request.get_json()
    url = data.get('url')
    
    if not url:
        return jsonify({"error": "Missing 'url' parameter in the request body."}), 400

    if not is_valid_youtube_url(url):
        return jsonify({"error": "Invalid YouTube URL."}), 400
    
    video_info, error_message = get_video_info(url)
    
    if video_info:
        return jsonify(video_info), 200
    else:
        return jsonify({"error": error_message}), 500

if __name__ == '__main__':
    app.run(debug=True)
