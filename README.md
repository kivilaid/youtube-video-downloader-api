# YouTube Video Downloader

A Streamlit web application that allows you to download YouTube videos as audio (MP3) or video with audio.

## Features

- Input YouTube video URL
- Preview video before downloading
- Download options:
  - Audio only (MP3 format)
  - Video with audio (best quality)
- Downloads are saved in a local `downloads` folder

## Requirements

- Python 3.7+
- FFmpeg (required for audio extraction)

## Installation

1. Install FFmpeg if you haven't already:
   - Windows: Download from https://ffmpeg.org/download.html
   - Make sure FFmpeg is added to your system PATH

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided URL (usually http://localhost:8501)
3. Paste a YouTube video URL
4. Choose your preferred download option

## Note

Downloads will be saved in a `downloads` folder in the same directory as the application. 