import asyncio
from aiohttp.test_utils import TestServer, TestClient
import server

async def run_tests():
    app = server.create_app()
    client = TestClient(TestServer(app))
    await client.start_server()
    
    # Test 1: GET /
    r1 = await client.get('/')
    assert r1.status == 200, f"Expected 200, got {r1.status}"
    print("[PASS] GET / -> 200 OK")
    
    # Test 2: GET /api/topics/search?count=3
    r2 = await client.get('/api/topics/search?count=3')
    assert r2.status == 200
    d2 = await r2.json()
    assert len(d2.get('topics', [])) == 3
    print(f"[PASS] GET /api/topics/search -> 200 OK ({len(d2['topics'])} topics returned)")
    
    # Test 3: POST /api/scripts/generate
    r3 = await client.post('/api/scripts/generate', json={'topic_ids': ['corpse_synod']})
    assert r3.status == 200
    d3 = await r3.json()
    assert len(d3.get('scripts', [])) >= 1
    print(f"[PASS] POST /api/scripts/generate -> 200 OK (generated: {d3['scripts'][0]['title'][:30]}...)")
    
    # Test 4: GET /api/videos
    r4 = await client.get('/api/videos')
    assert r4.status == 200
    d4 = await r4.json()
    print(f"[PASS] GET /api/videos -> 200 OK ({len(d4.get('videos', []))} videos found in vault)")

    # Test 5: GET /api/youtube/status
    r5 = await client.get('/api/youtube/status')
    assert r5.status == 200
    d5 = await r5.json()
    print(f"[PASS] GET /api/youtube/status -> 200 OK (has_secret={d5['has_secret']}, authenticated={d5['authenticated']})")

    await client.close()
    print("[SUCCESS] All API endpoints validated successfully!")

if __name__ == '__main__':
    asyncio.run(run_tests())
