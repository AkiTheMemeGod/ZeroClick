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
        "Brave": "https://github.com/brave/brave-browser/releases/latest/download/BraveBrowserSetup.exe",
        "Git": "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/Git-2.44.0-64-bit.exe",
        "7-Zip": "https://www.7-zip.org/a/7z2401-x64.msi",
        "Wireshark": "https://1.na.dl.wireshark.org/win64/Wireshark-win64-4.2.3.exe",
        "LibreOffice": "https://download.documentfoundation.org/libreoffice/stable/7.6.5/win/x86_64/LibreOffice_7.6.5_Win_x86-64.msi",
        "Audacity": "https://github.com/audacity/audacity/releases/download/Audacity-3.4.2/audacity-win-3.4.2-x64.exe",
        "EA App": "https://eaassets-a.akamaihd.net/eaapp/v1/installer/EAappInstaller.exe",
        "HeidiSQL": "https://www.heidisql.com/downloads/HeidiSQL_12.6_64_Setup.exe",
        "System Informer": "https://github.com/winsiderss/systeminformer/releases/download/v3.0.7303/systeminformer-3.0.7303-setup.exe",
        "Telegram": "https://updates.tdesktop.com/tsetup/tsetup.4.15.2.exe",
        "MusicBee": "https://getmusicbee.com/download/latest/MusicBeeSetup.exe",
        "Strawberry Perl": "https://github.com/StrawberryPerl/Perl-Dist-Strawberry/releases/download/SP_5.38.2.2_64bit_UCRT/strawberry-perl-5.38.2.2-64bit.msi",
        ".NET SDK 8": "https://download.visualstudio.microsoft.com/download/pr/45089e02-45e0-40e9-b5f7-c9993358079d/d90e292d3f0347895f320b9e83ec5507/dotnet-sdk-8.0.202-win-x64.exe"
    }

    async with httpx.AsyncClient(verify=False) as client:
        tasks = [test_url(client, name, url) for name, url in urls.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
