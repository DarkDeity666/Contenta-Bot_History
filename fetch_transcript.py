import urllib.request
import re
import json
import xml.etree.ElementTree as ET

url = 'https://www.youtube.com/watch?v=OtbLL6OBNE4'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
req = urllib.request.Request(url, headers=headers)
with urllib.request.urlopen(req, timeout=10) as resp:
    html = resp.read().decode('utf-8', errors='ignore')

player_match = re.search(r'var ytInitialPlayerResponse\s*=\s*({.+?});</script>', html)
if player_match:
    data = json.loads(player_match.group(1))
    captions = data.get('captions', {}).get('playerCaptionsTracklistRenderer', {}).get('captionTracks', [])
    print(f'Found {len(captions)} caption tracks.')
    for c in captions:
        print('Lang:', c.get('languageCode'), 'Name:', c.get('name', {}).get('simpleText'))
        track_url = c.get('baseUrl')
        if track_url:
            req2 = urllib.request.Request(track_url, headers=headers)
            with urllib.request.urlopen(req2, timeout=10) as resp2:
                xml_data = resp2.read().decode('utf-8', errors='ignore')
            # Parse XML transcript
            root = ET.fromstring(xml_data)
            lines = []
            for text_elem in root.findall('text'):
                t_start = text_elem.attrib.get('start')
                text = text_elem.text or ''
                lines.append(f"[{float(t_start):.1f}s] {text}")
            transcript_text = "\n".join(lines)
            with open("tutorial_transcript.txt", "w", encoding="utf-8") as f_out:
                f_out.write(transcript_text)
            print(f"[+] Saved transcript ({len(lines)} lines) to tutorial_transcript.txt")
            break
else:
    print('No ytInitialPlayerResponse found.')
