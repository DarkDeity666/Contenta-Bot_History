import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

from config import YOUTUBE_CLIENT_SECRET_FILE, BASE_DIR, OAUTH_REDIRECT_PORT
from database import get_connection

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = BASE_DIR / "youtube_token.json"

def get_authenticated_service(interactive: bool = True):
    """Authenticates using OAuth 2.0 on custom isolated port 54892."""
    creds = None
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
        except Exception:
            creds = None
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                if not interactive:
                    return None
        else:
            if not interactive:
                return None
            if not os.path.exists(YOUTUBE_CLIENT_SECRET_FILE):
                print(f"[!] YouTube client secret file not found at: {YOUTUBE_CLIENT_SECRET_FILE}")
                print("[!] To enable real uploads, place your OAuth client_secret.json from Google Cloud Console into the project folder.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(
                YOUTUBE_CLIENT_SECRET_FILE, 
                SCOPES
            )
            # Custom unassigned port 54892 prevents any conflict with local web development
            creds = flow.run_local_server(
                port=OAUTH_REDIRECT_PORT, 
                success_message="Antigravity History Bot authorized successfully! You may close this tab."
            )
            
        if creds and creds.valid:
            with open(TOKEN_FILE, "w", encoding="utf-8") as token:
                token.write(creds.to_json())
            
    return build("youtube", "v3", credentials=creds) if creds and creds.valid else None

def upload_short_to_youtube(
    video_path: str, 
    title: str, 
    description: str, 
    tags: Optional[list] = None, 
    schedule_delay_hours: int = 0,
    privacy_status: str = "public"
) -> Optional[str]:
    """Uploads a video to YouTube with SEO metadata and scheduling."""
    youtube = get_authenticated_service()
    if not youtube:
        print("[*] SIMULATION MODE: Video ready for upload. (Place client_secret.json to activate live uploads).")
        return f"SIMULATED_ID_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    # YouTube SEO & Hashtags for high discovery
    if "#Shorts" not in title:
        title = f"{title[:50]} #Shorts"
        
    if tags is None:
        tags = ["History", "Shorts", "HistoricalFacts", "BizarreHistory", "UntoldHistory", "Documentary"]

    full_description = f"{description}\n\n" \
                       "🔔 Subscribe for daily obscure history facts!\n\n" \
                       "#History #Shorts #HistoricalFacts #DidYouKnow #AncientHistory #UntoldStories"

    body: Dict[str, Any] = {
        "snippet": {
            "title": title,
            "description": full_description,
            "tags": tags,
            "categoryId": "27"  # 27 = Education
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    # If scheduling is enabled, space out videos
    if schedule_delay_hours > 0:
        publish_time = datetime.utcnow() + timedelta(hours=schedule_delay_hours)
        body["status"]["privacyStatus"] = "private"
        body["status"]["publishAt"] = publish_time.isoformat() + "Z"
        print(f"[*] Scheduling video upload for {publish_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)
    
    response = None
    print(f"[*] Uploading '{title}' to YouTube...")
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"    Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    print(f"[+] Video uploaded successfully! YouTube URL: https://youtube.com/shorts/{video_id}")
    return video_id

def get_channel_details() -> Optional[Dict[str, Any]]:
    """Retrieves authenticated channel information if credentials are valid."""
    try:
        youtube = get_authenticated_service(interactive=False)
        if not youtube:
            return None
        response = youtube.channels().list(part="snippet,statistics", mine=True).execute()
        items = response.get("items", [])
        if items:
            ch = items[0]
            return {
                "id": ch.get("id"),
                "title": ch["snippet"].get("title", "YouTube Channel"),
                "customUrl": ch["snippet"].get("customUrl", ""),
                "thumbnail": ch["snippet"]["thumbnails"]["default"]["url"],
                "subscribers": ch["statistics"].get("subscriberCount", "0"),
                "videoCount": ch["statistics"].get("videoCount", "0")
            }
    except Exception as e:
        print(f"[!] Channel info fetch error: {e}")
    return None

if __name__ == "__main__":
    result = upload_short_to_youtube(
        video_path=str(BASE_DIR / "output" / "history_short_1.mp4"),
        title="The Strange Truth About The Corpse Synod",
        description="In 897 AD, Pope Stephen VI had the decaying body of his predecessor exhumed and placed on trial."
    )
    print("Upload result:", result)
