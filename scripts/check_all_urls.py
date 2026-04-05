import json
import asyncio
import httpx
from pathlib import Path

async def check_url(semaphore, client, app):
    async with semaphore:
        url = app.get('download_url')
        name = app.get('name')
        if not url:
            return {"name": name, "status": "No URL", "url": url}
        
        try:
            # Some servers block HEAD, so we try GET with stream=True
            async with client.stream("GET", url, follow_redirects=True, timeout=15.0) as response:
                if response.status_code == 200:
                    return {"name": name, "status": "OK", "code": 200, "url": url}
                else:
                    return {"name": name, "status": "FAIL", "code": response.status_code, "url": url}
        except Exception as e:
            return {"name": name, "status": "ERROR", "message": str(e), "url": url}

async def main():
    json_path = Path("data/apps.json")
    if not json_path.exists():
        print("data/apps.json not found")
        return

    with open(json_path, "r", encoding="utf-8") as f:
        apps = json.load(f)

    print(f"Checking {len(apps)} applications...")
    
    semaphore = asyncio.Semaphore(5) # Limit to 5 concurrent requests
    async with httpx.AsyncClient(verify=False) as client:
        tasks = [check_url(semaphore, client, app) for app in apps]
        results = await asyncio.gather(*tasks)

    broken = [r for r in results if r['status'] != "OK"]
    
    print("\n--- BROKEN LINKS ---")
    for b in broken:
        print(f"[{b['status']} {b.get('code', '')}] {b['name']}: {b['url']}")
        if 'message' in b:
            print(f"   Error: {b['message']}")

    print(f"\nSummary: {len(broken)} broken links found out of {len(apps)} total.")

if __name__ == "__main__":
    asyncio.run(main())
