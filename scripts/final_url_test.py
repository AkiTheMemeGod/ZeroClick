import asyncio
import httpx

async def test_url(client, name, url):
    try:
        async with client.stream("GET", url, follow_redirects=True, timeout=15.0) as response:
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
        "7-Zip": "https://www.7-zip.org/a/7z2409-x64.exe",
        "Wireshark": "https://2.na.dl.wireshark.org/win64/Wireshark-4.6.4-x64.exe",
        "LibreOffice": "https://download.documentfoundation.org/libreoffice/stable/26.2.2/win/x86_64/LibreOffice_26.2.2_Win_x86-64.msi",
        "Audacity": "https://github.com/audacity/audacity/releases/download/Audacity-3.7.7/audacity-win-3.7.7-64bit.exe",
        "EA App": "https://origin-a.akamaihd.net/EA-Desktop-Client-Download/installer-releases/EAappInstaller.exe",
        "HeidiSQL": "https://github.com/HeidiSQL/HeidiSQL/releases/download/v12.16/HeidiSQL_12.16.0.7229_Setup.exe",
        "System Informer": "https://github.com/winsiderss/systeminformer/releases/download/v3.2.25011.2103/systeminformer-3.2.25011-release-setup.exe",
        "Telegram": "https://telegram.org/dl/desktop/win64",
        "MusicBee": "https://www.getmusicbee.com/download/latest/MusicBeeSetup.zip",
        "Strawberry Perl": "https://github.com/StrawberryPerl/Perl-Dist-Strawberry/releases/download/SP_54201_64bit/strawberry-perl-5.42.0.1-64bit.msi",
        ".NET SDK 8": "https://builds.dotnet.microsoft.com/dotnet/Sdk/8.0.419/dotnet-sdk-8.0.419-win-x64.exe",
        "Git": "https://github.com/git-for-windows/git/releases/download/v2.48.1.windows.1/Git-2.48.1-64-bit.exe"
    }

    async with httpx.AsyncClient(verify=False) as client:
        tasks = [test_url(client, name, url) for name, url in urls.items()]
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
