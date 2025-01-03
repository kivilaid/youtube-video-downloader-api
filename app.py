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

# Check FFmpeg at startup
ffmpeg_available = check_ffmpeg()
if not ffmpeg_available:
    st.warning("""
    ⚠️ FFmpeg is not installed. Audio downloads will not work until FFmpeg is installed.
    
    Installation instructions:
    1. Windows:
       - Download from https://ffmpeg.org/download.html
       - Add FFmpeg to your system PATH
    2. Mac:
       - Use Homebrew: `brew install ffmpeg`
    3. Linux:
       - Ubuntu/Debian: `sudo apt-get install ffmpeg`
       - Fedora: `sudo dnf install ffmpeg`
    """)

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
    if download_type == "audio" and not ffmpeg_available:
        st.error("FFmpeg is required for audio downloads. Please install FFmpeg first.")
        return None, None

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
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        expected_ext = "mp3"
    else:  # video
        ydl_opts = {
            **common_opts,
            'format': 'best',  # Just get the best combined format
        }
        expected_ext = "mp4"
    
    try:
        # Generate a safe filename using video ID
        video_id = get_video_id(url)
        base_filename = f"downloads/video_{video_id}"
        ydl_opts['outtmpl'] = f"{base_filename}.%(ext)s"
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                # First try to get info
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get('title', f'video_{video_id}') if isinstance(info_dict, dict) else f'video_{video_id}'
                
                # Then download
                ydl.download([url])
                
                # Look for the downloaded file
                if download_type == "audio":
                    filename = f"{base_filename}.mp3"
                else:
                    # For video, check any extension
                    files = glob.glob(f"{base_filename}.*")
                    filename = files[0] if files else None
                
                if filename and os.path.exists(filename):
                    return title, filename
                else:
                    raise Exception("Downloaded file not found")
                    
            except Exception as e:
                raise Exception(f"Download failed: {str(e)}")
                
    except Exception as e:
        st.error(f"Error downloading: {str(e)}")
        if "ffprobe" in str(e) or "ffmpeg" in str(e):
            st.error("FFmpeg is required. Please install FFmpeg and try again.")
        else:
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
            if not ffmpeg_available:
                st.error("FFmpeg required for audio downloads")
            if st.button("Download Audio (MP3)", disabled=not ffmpeg_available):
                with st.spinner("Downloading audio... This may take a moment."):
                    title, file_path = download_video(url, "audio")
                    if title and file_path:
                        st.success(f"Successfully downloaded audio: {title}")
                        # Add download button
                        with open(file_path, 'rb') as f:
                            st.download_button(
                                label="Save Audio to Computer",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="audio/mp3"
                            )
    else:
        st.error("Invalid YouTube URL. Please enter a valid YouTube video URL.") 