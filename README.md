# YouTube Video Downloader and Info API

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Description
The YouTube Video Downloader and Info API is a Flask-based Python project that enables video downloads and detailed information retrieval using Pytube. This versatile tool offers two core functionalities:

1. **Video Downloads:** Download YouTube videos by specifying the URL and desired resolution.

2. **Video Information:** Retrieve comprehensive video details including title, author, duration, view count, description, and publication date.

## Sponsor
This project is sponsored by HuntAPI. HuntAPI is a platform for downloading videos. Visit us at [huntapi.com](https://huntapi.com).

<a href="https://huntapi.com">
    <img src="./logo-dark.png" width="300" alt="HuntAPI Logo">
</a>

## Key Features
- Multi-resolution YouTube video downloads
- Comprehensive video metadata retrieval
- Robust error handling
- RESTful JSON API endpoints for seamless integration
- Cross-platform compatibility

## Technology Stack
- Python 3.x
- Flask (API framework)
- Pytube (YouTube integration)
- re (URL validation)

## Setup and Usage
1. Clone the repository: 
bash
git clone https://github.com/huntapi/youtube-video-downloader-api.git
```
2. Install dependencies:
```bash
pip install flask pytube
```
3. Launch the application:
```bash
python main.py
```

## API Endpoints

### Video Download
- **Endpoint:** `/download/<resolution>`
- **Method:** POST
- **Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```

### Video Information
- **Endpoint:** `/video_info`
- **Method:** POST
- **Request Body:**
```json
{
    "url": "https://www.youtube.com/watch?v=VIDEO_ID"
}
```
