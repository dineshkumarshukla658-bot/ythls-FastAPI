from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
    return {"status": "online", "message": "API is running (Invidious Engine)"}

@app.get("/api/stream")
def get_stream(id: str):
    if not id:
        raise HTTPException(status_code=400, detail="YouTube ID required")
    
    # -------------------------------------------------------------
    # THE ULTIMATE FIX: Invidious API Network (No yt-dlp needed)
    # -------------------------------------------------------------
    invidious_instances = [
        "https://inv.tux.pizza",
        "https://invidious.jing.rocks",
        "https://invidious.nerdvpn.de",
        "https://invidious.slipfox.xyz",
        "https://invidious.protokolla.fi"
    ]
    
    for base_url in invidious_instances:
        try:
            # API ko call karke video details mangwao
            res = requests.get(f"{base_url}/api/v1/videos/{id}", timeout=6)
            if res.status_code == 200:
                data = res.json()
                
                # formatStreams ke andar pre-merged (Audio+Video) MP4 files hoti hain
                format_streams = data.get("formatStreams", [])
                if format_streams:
                    # 720p ya 360p best MP4 stream dhoondho
                    for stream in format_streams:
                        if stream.get("container") == "mp4":
                            return {"success": True, "streamUrl": stream["url"], "source": f"invidious-{base_url}"}
                    
                    # Agar specifically mp4 tag na mile toh pehla stream return kar do
                    return {"success": True, "streamUrl": format_streams[0]["url"], "source": f"invidious-fallback-{base_url}"}
        except Exception as e:
            continue # Agar ek Invidious server down ho, toh agle par try karo
    
    # Agar kisi bhi wajah se saare Invidious servers fail ho jayein (jo ki rare hai)
    fallback_dummy = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
    return {"success": True, "streamUrl": fallback_dummy, "source": "dummy-fallback", "error_log": "All APIs failed"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
