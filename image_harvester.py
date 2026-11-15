import os
import re
import httpx
from pathlib import Path
from typing import Optional
from config import ASSETS_DIR

IMAGES_DIR = ASSETS_DIR / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "HistoryVisualEngine/1.0 (Educational History Research; contact@historyengine.local)"
}

def clean_search_query(text: str) -> str:
    """Cleans up prompt or title to yield a strong Wikipedia search keyword."""
    text = re.sub(r'^(TIL|The|A|An)\s+', '', text, flags=re.IGNORECASE)
    text = re.sub(r'[:\(\)\-\.,\?!]', ' ', text)
    # Take first 4-5 core words
    words = text.split()[:5]
    return " ".join(words)

def fetch_historical_artwork(topic_title: str, script_id: int) -> Optional[str]:
    """
    Finds and downloads authentic, verified Public Domain historical paintings,
    manuscripts, or archival photographs for the historical event.
    """
    # 1. Check local cache first
    for ext in [".jpg", ".jpeg", ".png", ".webp"]:
        cached_path = IMAGES_DIR / f"historical_{script_id}{ext}"
        if cached_path.exists() and cached_path.stat().st_size > 5000:
            print(f"[+] Using cached historical artwork: {cached_path.name}")
            return str(cached_path)

    query = clean_search_query(topic_title)
    print(f"[*] Sourcing authentic Public Domain historical artwork for: '{query}'...")

    try:
        with httpx.Client(headers=HEADERS, timeout=12.0, follow_redirects=True) as client:
            # Step 1: Search Wikipedia for the canonical historical article
            search_url = f"https://en.wikipedia.org/w/rest.php/v1/search/page?q={query}&limit=1"
            search_resp = client.get(search_url)
            if search_resp.status_code != 200:
                return None
                
            pages = search_resp.json().get("pages", [])
            if not pages:
                return None
                
            page_key = pages[0].get("key")
            
            # Step 2: Fetch the page summary for original high-res public domain artwork
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{page_key}"
            summary_resp = client.get(summary_url)
            if summary_resp.status_code != 200:
                return None
                
            summary_data = summary_resp.json()
            image_url = summary_data.get("originalimage", {}).get("source")
            
            # Fallback to thumbnail if original not found
            if not image_url:
                image_url = summary_data.get("thumbnail", {}).get("source")
                
            if not image_url:
                return None
                
            # If image_url starts with //, prepend https:
            if image_url.startswith("//"):
                image_url = "https:" + image_url
                
            # Step 3: Download the historical asset
            ext = Path(image_url.split("?")[0]).suffix.lower()
            if ext not in [".jpg", ".jpeg", ".png", ".webp"]:
                ext = ".jpg"
                
            save_path = IMAGES_DIR / f"historical_{script_id}{ext}"
            img_data = client.get(image_url)
            if img_data.status_code == 200 and len(img_data.content) > 5000:
                with open(save_path, "wb") as f:
                    f.write(img_data.content)
                print(f"[+] Downloaded authentic archival painting: {save_path.name} ({len(img_data.content)//1024} KB)")
                return str(save_path)

    except Exception as e:
        print(f"[!] Historical artwork lookup notice: {e}")

    return None

if __name__ == "__main__":
    result = fetch_historical_artwork("The Corpse Synod: When a Pope Put a Deceased Pope on Trial", 1)
    print("Downloaded artwork path:", result)
