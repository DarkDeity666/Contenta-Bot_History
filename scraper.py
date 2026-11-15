import httpx
import re
from typing import List, Dict, Any
from database import save_topic, is_topic_duplicate

HEADERS = {
    "User-Agent": "HistoryEngineBot/1.0 (Educational History Shorts Discovery; contact@historyengine.local)"
}

# Evergreen high-virality historical seed templates if internet connection is offline
CURATED_HISTORICAL_ANOMALIES = [
    {
        "title": "The Corpse Synod: When a Pope Put a Deceased Pope on Trial",
        "source": "curated_archive",
        "content": "In 897 AD, Pope Stephen VI had the decaying body of his predecessor, Pope Formosus, exhumed, dressed in papal robes, and placed on a throne to stand trial for perjury and ecclesiastical crimes. An appointed deacon had to speak on behalf of the rotting corpse."
    },
    {
        "title": "The London Beer Flood of 1814",
        "source": "curated_archive",
        "content": "A 22-foot-tall wooden vat at the Meux and Company Brewery ruptured, unleashing a 15-foot tidal wave of over 323,000 gallons of fermenting porter through the slums of St. Giles, destroying two houses and claiming eight lives."
    },
    {
        "title": "The 1904 Olympic Marathon: The Most Chaotic Race in Human History",
        "source": "curated_archive",
        "content": "The 1904 St. Louis marathon was a disaster: the winner hitchhiked in a car for 11 miles, another runner took rat poison and brandy as an energy cocktail, and a Cuban postman ran in dress pants and took a nap in an apple orchard mid-race."
    },
    {
        "title": "Ching Shih: The Prostitute Who Became History's Greatest Pirate Overlord",
        "source": "curated_archive",
        "content": "Ching Shih commanded over 1,800 ships and 80,000 pirates in the South China Sea. She defeated the Qing dynasty, British, and Portuguese navies, forced the Emperor to grant her full amnesty, and retired with all her plunder."
    },
    {
        "title": "The Dancing Plague of 1518",
        "source": "curated_archive",
        "content": "In Strasbourg, Frau Troffea stepped into the street and began dancing uncontrollably. Within a month, hundreds of citizens joined her, dancing continuously until many collapsed from exhaustion or heart attacks."
    },
    {
        "title": "The Boston Molasses Disaster of 1919",
        "source": "curated_archive",
        "content": "A giant storage tank collapsed in Boston, releasing a 25-foot wave of 2.3 million gallons of molasses moving at 35 miles per hour. The sticky wave demolished buildings, trapped horses, and claimed 21 lives."
    },
    {
        "title": "The War of the Bucket (1325)",
        "source": "curated_archive",
        "content": "Soldiers from Modena slipped into Bologna and stole an ordinary wooden bucket from the city well. The insult triggered the Battle of Zappolino involving over 30,000 soldiers. Modena won, and the bucket is still displayed in Modena's cathedral."
    },
    {
        "title": "How a Stray Dog Started a War in 1925 (War of the Stray Dog)",
        "source": "curated_archive",
        "content": "A Greek soldier chased his runaway dog across the border into Bulgaria and was shot by a Bulgarian sentry. The border dispute escalated into an invasion with heavy artillery until the League of Nations intervened."
    }
]

def clean_reddit_title(title: str) -> str:
    """Removes common Reddit prefixes like TIL, TIL that, [Serious], etc."""
    cleaned = re.sub(r'^(TIL\s*[:-]?|TIL\s*that\s*|Today\s*I\s*learned\s*that\s*)', '', title, flags=re.IGNORECASE)
    cleaned = re.sub(r'\[.*?\]', '', cleaned)
    return cleaned.strip()

def fetch_reddit_history_topics(limit: int = 15) -> List[Dict[str, str]]:
    """Mines top verified historical anomalies from r/TodayILearned and r/AskHistorians"""
    topics = []
    urls = [
        "https://www.reddit.com/r/TodayILearned/search.json?q=ancient+OR+emperor+OR+ww2+OR+medieval+OR+century&restrict_sr=1&sort=top&t=month&limit=25",
        "https://www.reddit.com/r/AskHistorians/top.json?t=month&limit=20"
    ]
    
    with httpx.Client(headers=HEADERS, timeout=10.0, follow_redirects=True) as client:
        for url in urls:
            try:
                response = client.get(url)
                if response.status_code == 200:
                    data = response.json()
                    children = data.get("data", {}).get("children", [])
                    for child in children:
                        post = child.get("data", {})
                        title = clean_reddit_title(post.get("title", ""))
                        selftext = post.get("selftext", "")
                        score = post.get("score", 0)
                        
                        # Only pick high engagement posts with strong narrative substance
                        if score > 300 and len(title) > 30:
                            topics.append({
                                "title": title,
                                "source": f"reddit_{post.get('subreddit', 'history')}",
                                "content": selftext if selftext else title
                            })
            except Exception as e:
                # If Reddit rate limits, gracefully proceed to next source
                pass
    return topics

def fetch_wikipedia_unusual_topics() -> List[Dict[str, str]]:
    """Mines Wikipedia's curated catalog of historical anomalies and strange events"""
    topics = []
    # Wikipedia API random query in history categories
    api_url = "https://en.wikipedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=Category:Curiosities_in_history&cmlimit=20"
    with httpx.Client(headers=HEADERS, timeout=10.0) as client:
        try:
            resp = client.get(api_url)
            if resp.status_code == 200:
                pages = resp.json().get("query", {}).get("categorymembers", [])
                for p in pages:
                    title = p.get("title", "")
                    if title and not title.startswith("Category:"):
                        topics.append({
                            "title": title,
                            "source": "wikipedia_curiosities",
                            "content": f"Historical anomaly documented on Wikipedia: {title}"
                        })
        except Exception:
            pass
    return topics

def harvest_and_store_topics() -> int:
    """Discovers, deduplicates, and saves fresh historical topics into SQLite"""
    print("[*] Mining fresh historical topics from multiple sources...")
    all_candidates: List[Dict[str, str]] = []
    
    # 1. Curated Goldmine
    all_candidates.extend(CURATED_HISTORICAL_ANOMALIES)
    
    # 2. Reddit Historical Channels
    reddit_topics = fetch_reddit_history_topics()
    all_candidates.extend(reddit_topics)
    
    # 3. Wikipedia Unusual Curiosities
    wiki_topics = fetch_wikipedia_unusual_topics()
    all_candidates.extend(wiki_topics)
    
    added_count = 0
    for item in all_candidates:
        title = item["title"]
        if not is_topic_duplicate(title):
            topic_id = save_topic(title, item["source"], item["content"])
            if topic_id:
                added_count += 1
                
    print(f"[+] Total candidate topics evaluated: {len(all_candidates)}")
    print(f"[+] Brand-new unique historical topics saved to database: {added_count}")
    return added_count

if __name__ == "__main__":
    from database import init_db
    init_db()
    count = harvest_and_store_topics()
