"""
Contenta History Bot Studio - Web Backend Server
Fast, async aiohttp server providing complete REST APIs for topic scraping,
6-beat script generation, video vault streaming, and YouTube Data API v3 publishing.
"""

import os
import json
import asyncio
from pathlib import Path
from aiohttp import web
from typing import Dict, Any, List, Optional

from config import BASE_DIR, OUTPUT_DIR, YOUTUBE_CLIENT_SECRET_FILE, STUDIO_PORT
import youtube_uploader
import story_director

WEB_DIR = BASE_DIR / "web"
SCRIPTS_CACHE_FILE = OUTPUT_DIR / "scripts_vault.json"

# In-memory scripts cache fallback
cached_scripts: List[Dict[str, Any]] = []

def load_cached_scripts():
    global cached_scripts
    if SCRIPTS_CACHE_FILE.exists():
        try:
            with open(SCRIPTS_CACHE_FILE, "r", encoding="utf-8") as f:
                cached_scripts = json.load(f)
        except Exception:
            cached_scripts = []
    if not cached_scripts:
        cached_scripts = [story_director.synthesize_viral_script("The man who bought an entire bank for $1", style="tall_tale_3d")]

def save_cached_scripts():
    with open(SCRIPTS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cached_scripts, f, indent=2)

load_cached_scripts()

# Active OAuth flows map for preserving PKCE verifiers
active_oauth_flows: Dict[str, Any] = {}

def get_redirect_uri(request) -> str:
    host = request.host
    return f"http://{host}/"

async def process_oauth_code(code: str, redirect_uri: str) -> bool:
    global active_oauth_flows
    flow = active_oauth_flows.get(redirect_uri)
    if flow:
        try:
            flow.fetch_token(code=code)
            creds = flow.credentials
            if creds and creds.valid:
                with open(youtube_uploader.TOKEN_FILE, "w", encoding="utf-8") as token:
                    token.write(creds.to_json())
                print("[+] YouTube token saved successfully from active flow!")
                return True
        except Exception as e:
            print(f"[!] Active flow token fetch failed: {e}")

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        lambda: youtube_uploader.exchange_code_for_token(code, redirect_uri=redirect_uri)
    )

# ---------------------------------------------------------------------------
# Route Handlers
# ---------------------------------------------------------------------------

async def handle_index(request):
    code = request.query.get("code")
    if code:
        redirect_uri = get_redirect_uri(request)
        ok = await process_oauth_code(code, redirect_uri)
        if ok:
            raise web.HTTPFound("/?auth=success#tab-upload")
        else:
            raise web.HTTPFound("/?auth=error#tab-upload")

    resp = web.FileResponse(WEB_DIR / "index.html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp

async def handle_oauth_callback(request):
    code = request.query.get("code")
    if code:
        redirect_uri = f"http://{request.host}/oauth2callback"
        ok = await process_oauth_code(code, redirect_uri)
        if ok:
            raise web.HTTPFound("/?auth=success#tab-upload")
        else:
            raise web.HTTPFound("/?auth=error#tab-upload")
    raise web.HTTPFound("/?auth=error#tab-upload")

async def handle_styles(request):
    resp = web.FileResponse(WEB_DIR / "styles.css")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp

async def handle_app_js(request):
    resp = web.FileResponse(WEB_DIR / "app.js")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp

async def handle_media(request):
    filename = request.match_info.get("filename")
    filepath = OUTPUT_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        raise web.HTTPNotFound(text="Media file not found")
    return web.FileResponse(filepath)

async def api_get_scripts(request):
    return web.json_response({"scripts": cached_scripts})

async def api_create_custom_script(request):
    try:
        data = await request.json()
        topic = data.get("topic", "").strip()
        style = data.get("style", "tall_tale_3d")
        duration = data.get("duration", "viral_35s")
        seamless_loop = data.get("seamless_loop", True)
        hook_type = data.get("hook_type", "paradox")
        
        if not topic:
            return web.json_response({"success": False, "error": "Please provide a story topic or loophole!"})
            
        loop = asyncio.get_event_loop()
        script = await loop.run_in_executor(
            None,
            lambda: story_director.synthesize_viral_script(
                topic=topic,
                style=style,
                duration=duration,
                seamless_loop=seamless_loop,
                hook_type=hook_type
            )
        )
        
        # Check if already present, or insert at front
        existing_idx = next((i for i, s in enumerate(cached_scripts) if s.get("id") == script["id"]), None)
        if existing_idx is not None:
            cached_scripts[existing_idx] = script
        else:
            cached_scripts.insert(0, script)
            
        save_cached_scripts()
        return web.json_response({"success": True, "script": script})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

def find_matching_script(filename: str) -> Optional[Dict[str, Any]]:
    fn = filename.lower()
    for s in cached_scripts:
        sid = s.get("id", "").lower()
        stitle = s.get("title", "").lower()
        if sid and sid in fn:
            return s
        words = [w.lower() for w in stitle.split() if len(w) > 4]
        if any(w in fn for w in words):
            return s
    if "triboulet" in fn:
        return next((s for s in cached_scripts if "triboulet" in s.get("id", "").lower()), None)
    # Check if numbered like history_short_6.mp4 or short_2.mp4
    import re
    m = re.search(r'_(\d+)(?:\.|$)', fn)
    if m:
        idx = int(m.group(1)) - 1
        if 0 <= idx < len(cached_scripts):
            return cached_scripts[idx]
    return None

# --- Video Vault APIs ---
async def api_get_videos(request):
    videos = []
    if OUTPUT_DIR.exists():
        for file in OUTPUT_DIR.glob("*.mp4"):
            name = file.name
            if name.startswith("raw_"):
                continue
            stat = file.stat()
            size_mb = round(stat.st_size / (1024 * 1024), 2)
            
            clean_title = name.replace(".mp4", "").replace("_", " ").title()
            matched_script = find_matching_script(name)
            
            if matched_script:
                story_title = matched_script.get("title", clean_title)
                raw_title = matched_script.get("suggested_title") or story_title
                if not raw_title.endswith("#Shorts"):
                    if len(raw_title) > 85:
                        raw_title = raw_title[:82].rsplit(' ', 1)[0] + "..."
                    suggested_title = f"{raw_title} #Shorts"
                else:
                    suggested_title = raw_title

                suggested_desc = matched_script.get("suggested_desc") or (
                    f"{matched_script.get('hook', '')}\n\n"
                    f"{matched_script.get('escalation', '')}\n\n"
                    f"📚 Historical Citations: {matched_script.get('citations', 'Verified Archives')}\n\n"
                    f"🔔 Subscribe for daily historical animations!\n\n"
                    f"#History #Shorts #HistoricalFacts #DidYouKnow #UntoldHistory #Documentary"
                )
            else:
                story_title = clean_title
                suggested_title = f"{clean_title} #Shorts"
                suggested_desc = f"The incredible true historical record of {clean_title}.\n\n#History #Shorts #Animation"
                
            videos.append({
                "filename": name,
                "title": story_title,
                "url": f"/media/{name}",
                "size_mb": size_mb,
                "duration_str": "0:38",
                "suggested_title": suggested_title,
                "suggested_desc": suggested_desc
            })
            
    # Sort with master / latest first
    videos.sort(key=lambda v: (0 if "master" in v["filename"].lower() else 1, v["filename"]))
    return web.json_response({"videos": videos})

# --- YouTube OAuth APIs ---
async def api_youtube_status(request):
    secret_path = Path(YOUTUBE_CLIENT_SECRET_FILE)
    token_path = BASE_DIR / "youtube_token.json"
    
    has_secret = secret_path.exists()
    has_token = token_path.exists()
    
    channel_info = None
    is_authenticated = False
    if has_token:
        try:
            from google.oauth2.credentials import Credentials
            creds = Credentials.from_authorized_user_file(str(token_path))
            if creds and (creds.valid or creds.refresh_token):
                is_authenticated = True
                channel_info = {
                    "title": "Time Riddles (@timeriddlesyt)",
                    "subscribers": "0",
                    "videoCount": "0"
                }
        except Exception:
            pass

        # Optionally enrich with full channel stats if network/scopes allow
        loop = asyncio.get_event_loop()
        try:
            detailed = await asyncio.wait_for(
                loop.run_in_executor(None, youtube_uploader.get_channel_details),
                timeout=2.0
            )
            if detailed:
                channel_info = detailed
        except Exception:
            pass
        
    return web.json_response({
        "has_secret": has_secret,
        "authenticated": is_authenticated,
        "channel": channel_info
    })

async def api_youtube_save_secret(request):
    try:
        secret_data = await request.json()
        secret_path = Path(YOUTUBE_CLIENT_SECRET_FILE)
        with open(secret_path, "w", encoding="utf-8") as f:
            json.dump(secret_data, f, indent=2)
        return web.json_response({"success": True})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=400)

async def api_youtube_auth(request):
    secret_path = Path(YOUTUBE_CLIENT_SECRET_FILE)
    if not secret_path.exists():
        return web.json_response({
            "success": False, 
            "error": "client_secret.json not found."
        })
        
    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
        redirect_uri = get_redirect_uri(request)
        flow = InstalledAppFlow.from_client_secrets_file(
            YOUTUBE_CLIENT_SECRET_FILE,
            youtube_uploader.SCOPES,
            redirect_uri=redirect_uri
        )
        auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
        active_oauth_flows[redirect_uri] = flow
        return web.json_response({
            "success": True, 
            "auth_url": auth_url,
            "redirect_uri": redirect_uri,
            "message": "Google authentication link generated."
        })
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

async def api_youtube_exchange_code(request):
    data = await request.json()
    code = data.get("code", "").strip()
    if not code:
        return web.json_response({"success": False, "error": "No code provided"}, status=400)
    loop = asyncio.get_event_loop()
    ok = await loop.run_in_executor(None, lambda: youtube_uploader.exchange_code_for_token(code))
    if ok:
        channel_info = await loop.run_in_executor(None, youtube_uploader.get_channel_details)
        return web.json_response({"success": True, "channel": channel_info})
    else:
        return web.json_response({"success": False, "error": "Code exchange failed"}, status=400)

async def api_upload_execute(request):
    try:
        data = await request.json()
        video_filename = data.get("video_filename", "")
        title = data.get("title", "")
        description = data.get("description", "")
        tags = data.get("tags", [])
        privacy = data.get("privacy", "public")
        delay_hours = data.get("schedule_delay_hours", 0)

        video_path = OUTPUT_DIR / video_filename
        if not video_filename or not video_path.exists():
            return web.json_response({"success": False, "error": f"Video file not found: {video_filename}"}, status=404)

        loop = asyncio.get_event_loop()
        res_dict = await loop.run_in_executor(
            None,
            lambda: youtube_uploader.upload_short_to_youtube(
                video_path=str(video_path),
                title=title,
                description=description,
                tags=tags,
                schedule_delay_hours=delay_hours,
                privacy_status=privacy
            )
        )
        if res_dict.get("success"):
            vid = res_dict.get("video_id")
            return web.json_response({
                "success": True,
                "video_id": vid,
                "video_url": res_dict.get("url") or f"https://youtube.com/shorts/{vid}"
            })
        else:
            return web.json_response({
                "success": False,
                "error": res_dict.get("error", "Upload failed")
            }, status=400)
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)}, status=500)

async def api_upload_batch(request):
    try:
        data = await request.json()
    except Exception as e:
        return web.json_response({"success": False, "error": f"Invalid JSON payload: {e}", "results": []}, status=400)

    items = data.get("items", [])
    results = []
    loop = asyncio.get_event_loop()
    
    for item in items:
        video_filename = item.get("video_filename", "")
        title = item.get("title", "")
        description = item.get("description", "")
        tags = item.get("tags", [])
        privacy = item.get("privacy", "public")
        delay_hours = item.get("schedule_delay_hours", 0)

        video_path = OUTPUT_DIR / video_filename
        if not video_filename or not video_path.exists():
            results.append({
                "video_filename": video_filename,
                "success": False,
                "error": f"Video file not found: {video_filename}"
            })
            continue

        try:
            res_dict = await loop.run_in_executor(
                None,
                lambda v_path=str(video_path), t=title, d=description, tg=tags, h=delay_hours, p=privacy: (
                    youtube_uploader.upload_short_to_youtube(
                        video_path=v_path,
                        title=t,
                        description=d,
                        tags=tg,
                        schedule_delay_hours=h,
                        privacy_status=p
                    )
                )
            )
            if res_dict.get("success"):
                vid = res_dict.get("video_id")
                results.append({
                    "video_filename": video_filename,
                    "success": True,
                    "video_id": vid,
                    "video_url": res_dict.get("url") or f"https://youtube.com/shorts/{vid}"
                })
            else:
                results.append({
                    "video_filename": video_filename,
                    "success": False,
                    "error": res_dict.get("error", "Failed during upload")
                })
        except Exception as e:
            results.append({
                "video_filename": video_filename,
                "success": False,
                "error": str(e)
            })
            
    return web.json_response({"success": True, "results": results})

async def api_render_generate(request):
    try:
        data = await request.json()
        script_id = data.get("script_id")
        
        # Find matching script
        script = next((s for s in cached_scripts if s.get("id") == script_id), None)
        if not script:
            # Fallback to the first available script if none matches id
            if cached_scripts:
                script = cached_scripts[0]
            else:
                return web.json_response({"success": False, "error": f"Script not found: {script_id}"})
                
        loop = asyncio.get_event_loop()
        out_file = await loop.run_in_executor(
            None,
            lambda: story_director.render_script_video(script)
        )
        
        if out_file and os.path.exists(out_file):
            fn = os.path.basename(out_file)
            return web.json_response({
                "success": True, 
                "video_file": fn,
                "video_url": f"/media/{fn}",
                "message": f"Render completed: {fn}"
            })
        else:
            return web.json_response({"success": False, "error": "Video rendering failed during FFmpeg composite."})
    except Exception as e:
        return web.json_response({"success": False, "error": str(e)})

# ---------------------------------------------------------------------------
# App Initialization
# ---------------------------------------------------------------------------
def create_app():
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/oauth2callback", handle_oauth_callback)
    app.router.add_get("/styles.css", handle_styles)
    app.router.add_get("/app.js", handle_app_js)
    app.router.add_get("/media/{filename}", handle_media)

    # API Routes
    app.router.add_post("/api/scripts/create-custom", api_create_custom_script)
    app.router.add_get("/api/scripts", api_get_scripts)
    app.router.add_get("/api/videos", api_get_videos)
    app.router.add_get("/api/youtube/status", api_youtube_status)
    app.router.add_post("/api/youtube/save-secret", api_youtube_save_secret)
    app.router.add_post("/api/youtube/auth", api_youtube_auth)
    app.router.add_get("/api/youtube/auth", api_youtube_auth)
    app.router.add_post("/api/youtube/exchange_code", api_youtube_exchange_code)
    app.router.add_post("/api/upload/execute", api_upload_execute)
    app.router.add_post("/api/upload/batch", api_upload_batch)
    app.router.add_post("/api/videos/generate", api_render_generate)

    return app

if __name__ == "__main__":
    import sys
    port = STUDIO_PORT
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    print(f"[*] Starting Contenta History Bot Studio on http://localhost:{port}")
    app = create_app()
    web.run_app(app, host="127.0.0.1", port=port)
