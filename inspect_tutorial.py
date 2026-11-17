import urllib.request
import re
import json

url = 'https://www.youtube.com/watch?v=OtbLL6OBNE4'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        
    title = re.search(r'<title>(.*?)</title>', html)
    print('TITLE:', title.group(1) if title else 'None')
    
    # Try finding initial player response or ytInitialPlayerResponse
    player_match = re.search(r'var ytInitialPlayerResponse\s*=\s*({.+?});</script>', html)
    if player_match:
        try:
            data = json.loads(player_match.group(1))
            video_details = data.get('videoDetails', {})
            print('VIDEO TITLE:', video_details.get('title'))
            print('AUTHOR:', video_details.get('author'))
            print('SHORT DESCRIPTION:', video_details.get('shortDescription')[:600])
        except Exception as e:
            print('JSON parse error:', e)
    else:
        meta_desc = re.search(r'<meta name="description" content="(.*?)">', html)
        print('META DESC:', meta_desc.group(1) if meta_desc else 'None')
except Exception as e:
    print('Error:', e)
