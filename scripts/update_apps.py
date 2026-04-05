import json
import os

apps_path = 'c:/Projects/ZeroClick/data/apps.json'

with open(apps_path, 'r') as f:
    apps = json.load(f)

# Category mapping
category_updates = {
    "Web Browsers": "Browsers",
    "Media": "Media & Design",
    "Messaging": "Communication",
    "Gaming": "Gaming",
    "Utilities": "Utilities",
    "Development": "Development"
}

# Special re-categorizations
special_repro = {
    "dbeaver": "Databases",
    "heidisql": "Databases",
    "sqlitebrowser": "Databases",
    "steam": "Gaming",
    "wireshark": "Utilities",
    "systeminformer": "Utilities",
}

for app in apps:
    if app['category'] in category_updates:
        app['category'] = category_updates[app['category']]
    
    if app['id'] in special_repro:
        app['category'] = special_repro[app['id']]

# New apps
new_apps = [
    {
        "id": "mongodb",
        "name": "MongoDB Community Server",
        "download_url": "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-8.0.0-signed.msi",
        "silent_args": "/quiet /qn /norestart SHOULD_INSTALL_COMPASS=\"0\"",
        "file_type": ".msi",
        "category": "Databases",
        "icon_url": "https://www.google.com/s2/favicons?domain=mongodb.com&sz=64"
    },
    {
        "id": "mongodb-compass",
        "name": "MongoDB Compass",
        "download_url": "https://downloads.mongodb.com/compass/mongodb-compass-1.42.1-win32-x64.exe",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Databases",
        "icon_url": "https://www.google.com/s2/favicons?domain=mongodb.com&sz=64"
    },
    {
        "id": "antigravity",
        "name": "Antigravity",
        "download_url": "https://antigravity.im/download/win",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=antigravity.im&sz=64"
    },
    {
        "id": "cursor",
        "name": "Cursor",
        "download_url": "https://downloader.cursor.sh/windows/nsis/x64",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=cursor.sh&sz=64"
    },
    {
        "id": "ollama",
        "name": "Ollama",
        "download_url": "https://ollama.com/download/OllamaSetup.exe",
        "silent_args": "/silent",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=ollama.com&sz=64"
    },
    {
        "id": "docker-desktop",
        "name": "Docker Desktop",
        "download_url": "https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe",
        "silent_args": "install --quiet",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=docker.com&sz=64"
    },
    {
        "id": "powertoys",
        "name": "Microsoft PowerToys",
        "download_url": "https://github.com/microsoft/PowerToys/releases/latest/download/PowerToysSetup-0.80.1-x64.exe",
        "silent_args": "/quiet /norestart",
        "file_type": ".exe",
        "category": "Utilities",
        "icon_url": "https://www.google.com/s2/favicons?domain=microsoft.com&sz=64"
    },
    {
        "id": "rustup",
        "name": "Rustup (Rust Toolchain)",
        "download_url": "https://static.rust-lang.org/rustup/dist/x86_64-pc-windows-msvc/rustup-init.exe",
        "silent_args": "-y",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=rust-lang.org&sz=64"
    },
    {
        "id": "neovim",
        "name": "Neovim",
        "download_url": "https://github.com/neovim/neovim/releases/latest/download/nvim-win64.msi",
        "silent_args": "/quiet /qn /norestart",
        "file_type": ".msi",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=neovim.io&sz=64"
    },
    {
        "id": "tableplus",
        "name": "TablePlus",
        "download_url": "https://tableplus.com/release/windows/tableplus_latest.exe",
        "silent_args": "/VERYSILENT",
        "file_type": ".exe",
        "category": "Databases",
        "icon_url": "https://www.google.com/s2/favicons?domain=tableplus.com&sz=64"
    },
    {
        "id": "insomnia",
        "name": "Insomnia",
        "download_url": "https://updates.insomnia.rest/downloads/windows/latest?app=com.insomnia.app&source=website",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=insomnia.rest&sz=64"
    },
    {
        "id": "pycharm-community",
        "name": "PyCharm Community Edition",
        "download_url": "https://download.jetbrains.com/python/pycharm-community-2024.1.exe",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=jetbrains.com&sz=64"
    },
    {
        "id": "intellij-community",
        "name": "IntelliJ IDEA Community Edition",
        "download_url": "https://download.jetbrains.com/idea/ideaIC-2024.1.exe",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=jetbrains.com&sz=64"
    },
    {
        "id": "android-studio",
        "name": "Android Studio",
        "download_url": "https://redirector.gvt1.com/edgedl/android/studio/install/2024.1.1.11/android-studio-2024.1.1.11-windows.exe",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=google.com&sz=64"
    },
    {
        "id": "winscp",
        "name": "WinSCP",
        "download_url": "https://cdn.winscp.net/files/WinSCP-6.3.3-Setup.exe",
        "silent_args": "/VERYSILENT /NORESTART",
        "file_type": ".exe",
        "category": "Utilities",
        "icon_url": "https://www.google.com/s2/favicons?domain=winscp.net&sz=64"
    },
    {
        "id": "filezilla",
        "name": "FileZilla",
        "download_url": "https://download.filezilla-project.org/client/FileZilla_3.67.0_win64-setup.exe",
        "silent_args": "/S",
        "file_type": ".exe",
        "category": "Utilities",
        "icon_url": "https://www.google.com/s2/favicons?domain=filezilla-project.org&sz=64"
    },
    {
        "id": "screentogif",
        "name": "ScreenToGif",
        "download_url": "https://github.com/NickeManarin/ScreenToGif/releases/download/2.41/ScreenToGif.2.41.Setup.msi",
        "silent_args": "/quiet /qn /norestart",
        "file_type": ".msi",
        "category": "Media & Design",
        "icon_url": "https://www.google.com/s2/favicons?domain=screentogif.com&sz=64"
    },
    {
        "id": "windows-terminal",
        "name": "Windows Terminal",
        "download_url": "https://github.com/microsoft/terminal/releases/download/v1.20.11271.0/Microsoft.WindowsTerminal_1.20.11271.0_x64.zip",
        "silent_args": "",
        "file_type": ".zip",
        "category": "Utilities",
        "icon_url": "https://www.google.com/s2/favicons?domain=microsoft.com&sz=64"
    },
    {
        "id": "pwsh",
        "name": "PowerShell 7",
        "download_url": "https://github.com/PowerShell/PowerShell/releases/download/v7.4.2/PowerShell-7.4.2-win-x64.msi",
        "silent_args": "/quiet /qn /norestart",
        "file_type": ".msi",
        "category": "Utilities",
        "icon_url": "https://www.google.com/s2/favicons?domain=microsoft.com&sz=64"
    },
    {
        "id": "gh-cli",
        "name": "GitHub CLI",
        "download_url": "https://github.com/cli/cli/releases/download/v2.50.0/gh_2.50.0_windows_amd64.msi",
        "silent_args": "/quiet /qn /norestart",
        "file_type": ".msi",
        "category": "Development",
        "icon_url": "https://www.google.com/s2/favicons?domain=github.com&sz=64"
    }
]

# Add new apps if not already present
existing_ids = {app['id'] for app in apps}
for new_app in new_apps:
    if new_app['id'] not in existing_ids:
        apps.append(new_app)

with open(apps_path, 'w') as f:
    json.dump(apps, f, indent=2)

print(f"Updated {len(apps)} apps successfully.")
