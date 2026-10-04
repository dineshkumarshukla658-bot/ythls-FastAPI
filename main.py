from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import requests
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
    return {"status": "online", "message": "YTHLS FastAPI is running with Smart Fallback"}

@app.get("/api/stream")
def get_stream(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="YouTube ID required")
    
    # -------------------------------------------------------------
    # METHOD 1: Piped API (Bypasses YouTube IP Blocks on Render)
    # -------------------------------------------------------------
    try:
        piped_url = f"https://pipedapi.kavin.rocks/streams/{id}"
        # Alternative Piped API instances if one is down:
        # https://pipedapi.in.projectsegfau.lt/streams/{id}
        # https://de.api.piped.yt/streams/{id}
        
        res = requests.get(piped_url, timeout=8)
        if res.status_code == 200:
            data = res.json()
            video_streams = data.get("videoStreams", [])
            if video_streams:
                # 720p ya 1080p MP4 stream nikalna jisme audio aur video dono ho
                for stream in video_streams:
                    if stream.get("videoOnly") == False and stream.get("mimeType") == "video/mp4":
                        return {"success": True, "streamUrl": stream["url"], "source": "piped"}
                
                # Agar combined na mile, toh list ki sabse aakhri stream (best quality) bhej do
                return {"success": True, "streamUrl": video_streams[-1]["url"], "source": "piped-fallback"}
    except Exception as e:
        print(f"Piped API failed: {e}")
        pass # Agar Piped fail ho jaye, toh next method (yt-dlp) par jao

    # -------------------------------------------------------------
    # METHOD 2: Standard yt-dlp (Agar IP blocked nahi hai)
    # -------------------------------------------------------------
    video_url = f"https://www.youtube.com/watch?v={id}"
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
            return {"success": True, "streamUrl": stream_url, "source": "yt-dlp"}
    except Exception as e:
        # Agar dono method fail ho jayein toh fallback dummy video bhej do taaki frontend crash na ho
        fallback_dummy = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        return {"success": True, "streamUrl": fallback_dummy, "source": "dummy-fallback", "error_log": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
