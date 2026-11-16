import os
import time
import ssl
import json
import urllib.request
import urllib.parse
from pathlib import Path

HISTORICAL_ASSETS_DIR = Path("assets/historical_assets")
HISTORICAL_ASSETS_DIR.mkdir(parents=True, exist_ok=True)

TARGETS = [
    {
        "id": "wannsee_villa",
        "filename": "wannsee_villa.jpg",
        "search": "Wannsee Conference Villa",
        "title": "House of the Wannsee Conference (Villa Marlier, Berlin)"
    },
    {
        "id": "wannsee_protocol",
        "filename": "wannsee_protocol.jpg",
        "search": "Wannsee Protokoll",
        "title": "Wannsee Protocol (Besprechungsprotokoll 1942)"
    },
    {
        "id": "deportation_railway",
        "filename": "deportation_railway.jpg",
        "search": "Auschwitz Birkenau railway gate",
        "title": "Auschwitz-Birkenau Railway Gate & Tracks"
    },
    {
        "id": "auschwitz_blueprint",
        "filename": "auschwitz_blueprint.jpg",
        "search": "Auschwitz Bauplan Krematorium",
        "title": "Architectural Blueprints of Auschwitz-Birkenau Crematorium"
    },
    {
        "id": "nuremberg_courtroom",
        "filename": "nuremberg_courtroom.jpg",
        "search": "Nuremberg trials courtroom",
        "title": "Nuremberg International Military Tribunal (1945)"
    },
    {
        "id": "holocaust_memorial",
        "filename": "holocaust_memorial.jpg",
        "search": "Memorial to the Murdered Jews of Europe Berlin",
        "title": "Memorial to the Murdered Jews of Europe, Berlin"
    }
]

def search_and_download():
    ctx = ssl._create_unverified_context()
    headers = {"User-Agent": "AntigravityHistoryBot/2.0 (contact: user@local.bot)"}
    
    downloaded = []
    for target in TARGETS:
        dest_path = HISTORICAL_ASSETS_DIR / target["filename"]
        print(f"[*] Searching Commons for '{target['search']}'...")
        encoded_query = urllib.parse.quote(target["search"])
        api_url = (
            f"https://commons.wikimedia.org/w/api.php?action=query"
            f"&generator=search&gsrnamespace=6&gsrsearch={encoded_query}"
            f"&prop=imageinfo&iiprop=url|size|mime&format=json&gsrlimit=3"
        )
        try:
            req = urllib.request.Request(api_url, headers=headers)
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                data = json.loads(resp.read().decode())
                pages = data.get("query", {}).get("pages", {})
                
                chosen_url = None
                chosen_title = None
                for page_id, page in pages.items():
                    info_list = page.get("imageinfo", [])
                    if info_list:
                        info = info_list[0]
                        mime = info.get("mime", "")
                        if "image" in mime:
                            chosen_url = info.get("url")
                            chosen_title = page.get("title")
                            break
                            
                if not chosen_url:
                    print(f"    [!] No suitable image found for {target['search']}")
                    continue
                    
                print(f"    Found: {chosen_title}")
                print(f"    Downloading from: {chosen_url[:80]}...")
                dl_req = urllib.request.Request(chosen_url, headers=headers)
                with urllib.request.urlopen(dl_req, timeout=25, context=ctx) as dl_resp:
                    img_data = dl_resp.read()
                    with open(dest_path, "wb") as f:
                        f.write(img_data)
                    print(f"    [+] Saved {target['filename']} ({len(img_data) // 1024} KB)")
                    downloaded.append({
                        **target,
                        "commons_title": chosen_title,
                        "commons_url": chosen_url,
                        "size_bytes": len(img_data),
                        "local_path": str(dest_path)
                    })
        except Exception as e:
            print(f"    [!] Error during search/download: {e}")
        time.sleep(1.0)
        
    with open("assets/sources_manifest_holocaust.json", "w", encoding="utf-8") as f:
        json.dump(downloaded, f, indent=2)
    print(f"\n[+] Total downloaded: {len(downloaded)} assets.")

if __name__ == "__main__":
    search_and_download()
