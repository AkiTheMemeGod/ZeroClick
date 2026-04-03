import httpx
import asyncio

async def test_url(name, url):
    print(f"Testing {name}: {url}")
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.head(url)
            print(f"  Status: {response.status_code}")
            if response.status_code in [200, 302]:
                print(f"  SUCCESS: {name} URL is reachable.")
            else:
                print(f"  FAILURE: {name} URL returned {response.status_code}")
    except Exception as e:
        print(f"  ERROR: {name} lookup failed: {e}")

async def main():
    await test_url("PuTTY", "https://the.earth.li/~sgtatham/putty/latest/w64/putty-64bit-0.83-installer.msi")
    await test_url("OBS Studio", "https://github.com/obsproject/obs-studio/releases/download/30.1.2/OBS-Studio-30.1.2-Full-Installer-x64.exe")

if __name__ == "__main__":
    asyncio.run(main())
