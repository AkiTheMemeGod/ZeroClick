import asyncio
import httpx

async def test_url(client, name, url):
    try:
        async with client.stream("GET", url, follow_redirects=True, timeout=10.0) as response:
            if response.status_code == 200:
                print(f"[OK] {name}: {url}")
                return True
            else:
                print(f"[FAIL {response.status_code}] {name}: {url}")
                return False
    except Exception as e:
        print(f"[ERROR] {name}: {e}")
        return False

async def main():
    urls = {
        "7-Zip (24.09 x64)": "https://www.7-zip.org/a/7z2409-x64.exe",
        "Wireshark (4.4.2)": "https://2.tcdn.wireshark.org/win64/Wireshark-win64-4.4.2.exe",
        "LibreOffice (24.8.4)": "https://download.documentfoundation.org/libreoffice/stable/24.8.4/win/x86_64/LibreOffice_24.8.4_Win_x86-64.msi",
        "Audacity (3.7.1)": "https://github.com/audacity/audacity/releases/download/Audacity-3.7.1/audacity-win-3.7.1-x64.exe",
        "HeidiSQL (12.8)": "https://www.heidisql.com/downloads/HeidiSQL_12.8_64_Setup.exe",
        "System Informer (Nightly)": "https://github.com/winsiderss/systeminformer/releases/download/v3.0.7977/systeminformer-3.0.7977-setup.exe",
        "Telegram (5.11.1)": "https://updates.tdesktop.com/tsetup/tsetup.5.11.1.exe",
        "Strawberry Perl (5.40.0.1)": "https://github.com/StrawberryPerl/Perl-Dist-Strawberry/releases/download/SP_5.40.0.1_64bit_UCRT/strawberry-perl-5.40.0.1-64bit.msi"
    }

    async with httpx.AsyncClient(verify=False) as client:
        tasks = [test_url(client, name, url) for name, url in urls.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
