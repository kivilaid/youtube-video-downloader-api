import streamlit as st
import yt_dlp
import os
import subprocess
from urllib.parse import urlparse, parse_qs
import glob
import re

def check_ffmpeg():
    """Check if ffmpeg is installed"""
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True)
        ffmpeg = True
    except FileNotFoundError:
        ffmpeg = False

    try:
        subprocess.run(['ffprobe', '-version'], capture_output=True)
        ffprobe = True
    except FileNotFoundError:
        ffprobe = False
        
    return ffmpeg and ffprobe

# Set page config
st.set_page_config(
    page_title="YouTube Video Downloader",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    },
    page_icon="📹"
)

# Set dark theme and video size
st.markdown("""
    <style>
        .stApp {
            background-color: #0E1117;
            color: #FAFAFA;
        }
        .stButton>button {
            background-color: #262730;
            color: #FAFAFA;
        }
        .stTextInput>div>div>input {
            background-color: #262730;
            color: #FAFAFA;
        }
        /* Make video preview 50% smaller */
        div.stVideo > div {
            max-width: 50%;
            margin: auto;
        }
        div.stVideo > div > div {
            position: relative;
            padding-bottom: 28.125%; /* 16:9 aspect ratio at 50% size */
        }
        div.stVideo > div > div > iframe {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
        }
    </style>
""", unsafe_allow_html=True)

def get_video_id(url):
    """Extract video ID from YouTube URL"""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ['www.youtube.com', 'youtube.com']:
        return parse_qs(parsed_url.query).get('v', [None])[0]
    elif parsed_url.hostname in ['youtu.be']:
        return parsed_url.path[1:]
    return None

def sanitize_filename(title):
    """Sanitize the filename to remove invalid characters"""
    # Remove invalid characters
    title = re.sub(r'[<>:"/\\|?*]', '', title)
    # Remove or replace other problematic characters
    title = title.replace('&', 'and')
    title = title.replace("'", '')
    title = title.replace('"', '')
    return title

def download_video(url, download_type="video"):
    """Download video using yt-dlp with specified format"""
    # Common options to handle API issues
    common_opts = {
        'no_warnings': True,
        'quiet': True,
        'ignoreerrors': True,
        'nocheckcertificate': True,
    }
    
    if download_type == "audio":
        ydl_opts = {
            **common_opts,
            'format': 'bestaudio/best',  # Get best audio quality
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
    else:  # video
        ydl_opts = {
            **common_opts,
            'format': 'best',  # Just get the best combined format
            'outtmpl': 'downloads/%(title)s.%(ext)s',
        }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download the video/audio
            info = ydl.extract_info(url, download=True)
            if info:
                title = info.get('title', 'download')
                # Find the downloaded file
                files = glob.glob(f"downloads/{title}.*")
                if files:
                    return title, files[0]
            return None, None
    except Exception as e:
        st.error(f"Error downloading: {str(e)}")
        st.info("If the error persists, try updating yt-dlp using: pip install -U yt-dlp")
        return None, None

# Main app
st.title("YouTube Video Downloader")

# Create downloads directory if it doesn't exist
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# URL input
url = st.text_input("Enter YouTube URL:")

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
                    title, file_path = download_video(url, "video")
                    if title and file_path:
                        st.success(f"Successfully downloaded video: {title}")
                        # Add download button
                        with open(file_path, 'rb') as f:
                            st.download_button(
                                label="Save Video to Computer",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="video/mp4"
                            )
        
        with col2:
            st.write("🎵 Audio Only")
            if st.button("Download Audio"):
                with st.spinner("Downloading audio... This may take a moment."):
                    title, file_path = download_video(url, "audio")
                    if title and file_path:
                        st.success(f"Successfully downloaded audio: {title}")
                        # Add download button
                        with open(file_path, 'rb') as f:
                            ext = os.path.splitext(file_path)[1][1:]  # Get file extension
                            mime_type = "audio/mp3" if ext == "mp3" else "audio/m4a"
                            st.download_button(
                                label="Save Audio to Computer",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime=mime_type
                            )
    else:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.") 