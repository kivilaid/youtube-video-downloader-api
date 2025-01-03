import streamlit as st
import yt_dlp
import os
import subprocess
from urllib.parse import urlparse, parse_qs

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        return True
    except FileNotFoundError:
        return False

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    return None

def download_video(url, download_type="video"):
    """Download video using yt-dlp with specified format"""
    # Common options to handle API issues
    common_opts = {
        'no_warnings': True,
        'quiet': True,
        'extract_flat': True,
        'no_check_certificates': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    
    if download_type == "audio":
        ydl_opts = {
            **common_opts,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:  # video
        ydl_opts = {
            **common_opts,
            'format': 'best[ext=mp4]/best',  # Simplified format selection
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First try to extract info
            try:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise Exception("Could not extract video information")
            except Exception as e:
                st.warning("Could not extract video information, trying direct download...")
                info = None
            
            # Proceed with download
            info = ydl.extract_info(url, download=True)
            if info:
                return info.get('title', 'Video')
            else:
                raise Exception("Download failed")
    except Exception as e:
        st.error(f"Error downloading: {str(e)}")
        st.info("If the error persists, try updating yt-dlp using: pip install -U yt-dlp")
        return None

# Set page config
st.set_page_config(page_title="YouTube Video Downloader", layout="wide")

# Main app
st.title("YouTube Video Downloader")

# Create downloads directory if it doesn't exist
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# URL input
url = st.text_input("Enter YouTube Video URL:")

if url:
    video_id = get_video_id(url)
    if video_id:
        try:
            # Display embedded video
            st.video(url)
        except Exception:
            st.warning("Could not preview video, but download may still work")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("📹 Video with Audio")
            if st.button("Download Video (Best Quality)"):
                with st.spinner("Downloading video... This may take a moment."):
                    title = download_video(url, "video")
                    if title:
                        st.success(f"Successfully downloaded video: {title}")
        
        with col2:
            st.write("🎵 Audio Only")
            if st.button("Download Audio (MP3)"):
                with st.spinner("Downloading audio... This may take a moment."):
                    title = download_video(url, "audio")
                    if title:
                        st.success(f"Successfully downloaded audio: {title}")
    else:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.") 