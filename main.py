from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import os

app = FastAPI(title="YTHLS Trailer Stream Engine")

# Smart TV aur Browser ke liye CORS allow karna zaroori hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "message": "YTHLS FastAPI is running"}

@app.get("/api/stream")
def get_stream(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="YouTube ID required")
    
    video_url = f"https://www.youtube.com/watch?v={id}"
    
    # HLS (.m3u8) ya best MP4 stream nikalne ki settings
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            stream_url = info.get('url')
            if not stream_url:
                raise HTTPException(status_code=404, detail="Stream URL not found")
            return {"success": True, "streamUrl": stream_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
