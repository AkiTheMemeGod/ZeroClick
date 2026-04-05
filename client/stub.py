import os
import sys
import json
import asyncio
import httpx
import subprocess
import tempfile
import shutil
import threading
import time
import math
from pathlib import Path
from typing import List, Dict, Any
import customtkinter as ctk
from PIL import Image

# Unique marker used to find the JSON payload appended to the EXE
MARKER = b"###ZEROCLICK_PAYLOAD###"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class AppleSpinner(ctk.CTkCanvas):
    """Modern macOS-style activity indicator."""
    def __init__(self, master, size=32, color="#a371f7", bg_hex="#1a1a1a", **kwargs):
        super().__init__(master, width=size, height=size, bg=bg_hex, highlightthickness=0, **kwargs)
        self.size = size
        self.color = color
        self.angle = 0
        self.running = False
        
    def start(self):
        self.running = True; self._animate()
        
    def stop(self):
        self.running = False; self.delete("all")

    def _animate(self):
        if not self.running: return
        self.delete("all")
        for i in range(8):
            angle = (self.angle + i * 45) % 360
            rad = angle * (math.pi / 180)
            inner_r = self.size/4
            outer_r = self.size/2 - 2
            self.create_line(
                self.size/2 + inner_r * math.cos(rad), 
                self.size/2 + inner_r * math.sin(rad),
                self.size/2 + outer_r * math.cos(rad),
                self.size/2 + outer_r * math.sin(rad),
                fill=self.color, width=3, capstyle="round"
            )
        self.angle = (self.angle + 10) % 360
        self.after(40, self._animate)

class MacOSSplashScreen(ctk.CTkToplevel):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.configure(fg_color="#1a1a1a")
        w, h = 400, 320
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")
        logo_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            img = ctk.CTkImage(Image.open(logo_path), size=(120, 120))
            ctk.CTkLabel(self, image=img, text="").pack(pady=(60, 20))
        ctk.CTkLabel(self, text="ZEROCLICK", font=("Inter", 18, "bold"), text_color="#ffffff").pack()
        self.progress = ctk.CTkProgressBar(self, mode="indeterminate", height=4, width=200, progress_color="#a371f7", fg_color="#333333")
        self.progress.pack(pady=40); self.progress.start()
        self.status = ctk.CTkLabel(self, text="Preparing workspace...", font=("Inter", 11), text_color="#777777")
        self.status.pack()

class MacOSInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.bg_deep, self.sidebar_bg, self.glass_fg = "#1a1a1a", "#252525", "#2a2a2a"
        self.accent, self.text_main, self.text_sub = "#a371f7", "#ffffff", "#a0a0a0"
        self.title("ZeroClick Installer")
        self.geometry("780x520")
        self.resizable(False, False)
        self.configure(fg_color=self.bg_deep)
        ctk.set_appearance_mode("dark")
        
        # New: More reliable cache location in user's profile to avoid Temp/AV restrictions
        self.cache_dir = Path.home() / ".zeroclick" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.apps = []
        self.steps = ["Introduction", "Installation", "Summary"]
        self.current_step_idx = 0
        self.withdraw(); self._show_splash()

    def _show_splash(self):
        splash = MacOSSplashScreen()
        def finalize():
            self._init_layout(); self._load_data(); splash.destroy(); self.deiconify()
        self.after(2000, finalize)

    def _init_layout(self):
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=self.sidebar_bg, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        logo_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            img = ctk.CTkImage(Image.open(logo_path), size=(60, 60))
            ctk.CTkLabel(self.sidebar, image=img, text="").pack(pady=(40, 30))
        self.step_labels = []
        for i, step in enumerate(self.steps):
            lbl = ctk.CTkLabel(self.sidebar, text=step, font=("Inter", 13, "bold" if i==0 else "normal"),
                               text_color=self.text_main if i==0 else self.text_sub, anchor="w")
            lbl.pack(fill="x", padx=30, pady=8); self.step_labels.append(lbl)
        self.content_frame = ctk.CTkFrame(self, fg_color=self.glass_fg, corner_radius=20, border_color="#3a3a3a", border_width=1)
        self.content_frame.pack(side="right", expand=True, fill="both", padx=30, pady=30)
        self.view_container = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.view_container.pack(expand=True, fill="both", padx=40, pady=40)
        self._show_intro()
        self.controls = ctk.CTkFrame(self.content_frame, fg_color="transparent", height=60)
        self.controls.pack(side="bottom", fill="x", padx=40, pady=(0, 20))
        self.next_btn = ctk.CTkButton(self.controls, text="Continue", fg_color=self.accent, hover_color="#8e5fe0", width=110, command=self._on_continue)
        self.next_btn.pack(side="right")

    def log(self, text: str):
        # We'll use this for hidden diagnostics if needed
        print(f"[{time.strftime('%H:%M:%S')}] {text}")

    def _show_intro(self):
        for w in self.view_container.winfo_children(): w.destroy()
        ctk.CTkLabel(self.view_container, text="Install ZeroClick", font=("Inter", 26, "bold")).pack(anchor="w")
        ctk.CTkLabel(self.view_container, text="Refine your workspace. ZeroClick provides silent, professional software management. Ready to optimize your system.",
                     font=("Inter", 14), text_color=self.text_sub, wraplength=450, justify="left").pack(anchor="w", pady=(20, 0))
        details = ctk.CTkFrame(self.view_container, fg_color="#333333", corner_radius=10)
        details.pack(fill="x", pady=40, ipady=10); self.info_lbl = ctk.CTkLabel(details, text="Reading manifest...", font=("Inter", 12)); self.info_lbl.pack(pady=10)

    def _show_installation(self):
        self._update_sidebar(1)
        for w in self.view_container.winfo_children(): w.destroy()
        ctk.CTkLabel(self.view_container, text="Installation in Progress", font=("Inter", 22, "bold")).pack(anchor="w")
        self.app_name_lbl = ctk.CTkLabel(self.view_container, text="Initializing...", font=("Inter", 14), text_color=self.accent)
        self.app_name_lbl.pack(anchor="w", pady=(5, 20))
        card = ctk.CTkFrame(self.view_container, fg_color="#222222", corner_radius=15, border_color="#444444", border_width=1)
        card.pack(fill="x", pady=10, ipady=20)
        self.spinner = AppleSpinner(card, size=36, color=self.accent, bg_hex="#222222"); self.spinner.pack(pady=(20, 10)); self.spinner.start()
        self.progress_bar = ctk.CTkProgressBar(card, height=6, progress_color=self.accent, fg_color="#1a1a1a"); self.progress_bar.pack(fill="x", padx=40, pady=(20, 5)); self.progress_bar.set(0)
        self.status_lbl = ctk.CTkLabel(card, text="DOWNLOADING", font=("Inter", 10, "bold"), text_color=self.text_sub); self.status_lbl.pack()
        self.next_btn.configure(state="disabled", text="Installing...")

    def _show_summary(self, failed_apps=None):
        self._update_sidebar(2)
        for w in self.view_container.winfo_children(): w.destroy()
        title = "Installation Complete" if not failed_apps else "Verification Required"
        color = "#2ecc71" if not failed_apps else "#f1c40f"
        ctk.CTkLabel(self.view_container, text=title, font=("Inter", 26, "bold"), text_color=color).pack(pady=(40, 10))
        desc = "System refined and ready for use." if not failed_apps else f"Note: {len(failed_apps)} items required manual intervention (Permission issue or AV block)."
        ctk.CTkLabel(self.view_container, text=desc, font=("Inter", 14), text_color=self.text_sub, justify="center").pack()
        logo_path = resource_path(os.path.join("assets", "logo.png"))
        if os.path.exists(logo_path):
            img = ctk.CTkImage(Image.open(logo_path), size=(100, 100))
            ctk.CTkLabel(self.view_container, image=img, text="").pack(pady=40)
        self.next_btn.configure(state="normal", text="Close", command=self.destroy)

    def _update_sidebar(self, idx):
        for i, lbl in enumerate(self.step_labels):
            lbl.configure(font=("Inter", 13, "bold" if i==idx else "normal"), text_color=self.text_main if i==idx else self.text_sub)

    def _load_data(self):
        if not self._load_payload(): return
        if hasattr(self, 'info_lbl'): self.info_lbl.configure(text=f"Ready to install {len(self.apps)} applications.")

    def _load_payload(self) -> bool:
        try:
            if not getattr(sys, 'frozen', False):
                payload_path = Path(__file__).parent / "payload.json"
                if payload_path.exists(): self.apps = json.loads(payload_path.read_text()); return True
            with open(sys.executable, "rb") as f:
                content = f.read()
                if MARKER in content: _, p = content.split(MARKER, 1); self.apps = json.loads(p.decode('utf-8')); return True
        except: pass
        return False

    def _on_continue(self):
        if self.current_step_idx == 0: self.current_step_idx = 1; self._show_installation(); threading.Thread(target=self._run_install_thread, daemon=True).start()

    def _run_install_thread(self): asyncio.run(self._install_sequence())

    async def _install_sequence(self):
        total, failed = len(self.apps), []
        async with httpx.AsyncClient(timeout=120.0) as client:
            for i, app in enumerate(self.apps):
                self.after(0, lambda n=app['name']: self.app_name_lbl.configure(text=f"Downloading: {n}"))
                dest = self.cache_dir / f"{app['id']}{app['file_type']}"
                try:
                    async with client.stream("GET", app['download_url'], follow_redirects=True) as res:
                        if res.status_code == 200:
                            dl_total, downloaded = int(res.headers.get("Content-Length", 1)), 0
                            with open(dest, "wb") as f:
                                async for chunk in res.aiter_bytes():
                                    f.write(chunk); downloaded += len(chunk)
                                    p = ((i / total) + ((downloaded / dl_total) * (1 / total)))
                                    self.after(0, lambda val=p: self.progress_bar.set(val))
                    
                    # Verify integrity
                    if not dest.exists() or dest.stat().st_size == 0: raise Exception("Incomplete download")
                    
                    self.after(0, lambda n=app['name']: self.app_name_lbl.configure(text=f"Installing: {n}"))
                    self.after(0, lambda: self.status_lbl.configure(text="EXECUTING"))
                    
                    # More robust execution using subprocess to bypass Shell permission quirks
                    is_msi = app['file_type'].lower() == ".msi"
                    if is_msi:
                        cmd = ["msiexec.exe", "/i", str(dest)] + app["silent_args"].split()
                    else:
                        cmd = [str(dest)] + app["silent_args"].split()
                    
                    proc = await asyncio.create_subprocess_exec(*cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
                    _, stderr = await proc.communicate()
                    if proc.returncode != 0 and proc.returncode not in [3010]:
                        self.log(f"Execution warning for {app['name']}: {stderr.decode()}")
                except Exception as e:
                    self.log(f"Failed {app['name']}: {e}")
                    failed.append(app['name'])
                    
                p = (i + 1) / total; self.after(0, lambda val=p: self.progress_bar.set(val))
        self.after(0, lambda: self._show_summary(failed))

if __name__ == "__main__":
    app = MacOSInstaller(); app.mainloop()
