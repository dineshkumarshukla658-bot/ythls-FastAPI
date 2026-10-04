from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yt_dlp
import requests
import os

app = FastAPI(title="YTHLS Trailer Stream Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "online", "message": "YTHLS FastAPI is running with Multi-Server Fallback"}

@app.get("/api/stream")
def get_stream(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="YouTube ID required")
    
    # -------------------------------------------------------------
    # METHOD 1: Multi-Piped API Fallback (Bypasses YouTube Blocks)
    # -------------------------------------------------------------
    piped_instances = [
        "https://pipedapi.smnz.de",
        "https://pipedapi.in.projectsegfau.lt",
        "https://pipedapi.privacy.com.de"
    ]
    
    for base_url in piped_instances:
        try:
            res = requests.get(f"{base_url}/streams/{id}", timeout=5)
            if res.status_code == 200:
                data = res.json()
                video_streams = data.get("videoStreams", [])
                for stream in video_streams:
                    # Sirf wo format chahiye jisme Audio aur Video pehle se mix ho
                    if not stream.get("videoOnly") and stream.get("mimeType") == "video/mp4":
                        return {"success": True, "streamUrl": stream["url"], "source": f"piped-{base_url}"}
        except:
            continue # Agar ek Piped fail ho toh doosre par jao

    # -------------------------------------------------------------
    # METHOD 2: Strict yt-dlp Fallback
    # -------------------------------------------------------------
    # 18 = 360p MP4 (Video+Audio), 22 = 720p MP4 (Video+Audio), b = Best Pre-merged
    ydl_opts = {
        'format': '18/22/b', 
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={id}", download=False)
            stream_url = info.get('url')
            if stream_url:
                return {"success": True, "streamUrl": stream_url, "source": "yt-dlp"}
    except Exception as e:
        fallback_dummy = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
        return {"success": True, "streamUrl": fallback_dummy, "source": "dummy-fallback", "error_log": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
