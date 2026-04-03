import psutil
import time
from typing import Dict

class NetworkMonitor:
    def __init__(self):
        self.last_time = time.time()
        self.last_io = psutil.net_io_counters()
    
    def get_speed(self) -> Dict[str, str]:
        current_time = time.time()
        current_io = psutil.net_io_counters()
        
        delta_time = current_time - self.last_time
        if delta_time < 0.1: # Prevent division by zero or jitter
            return {"download": "0 B/s", "upload": "0 B/s"}
        
        bytes_sent = current_io.bytes_sent - self.last_io.bytes_sent
        bytes_recv = current_io.bytes_recv - self.last_io.bytes_recv
        
        # Bits per second
        up_bps = (bytes_sent * 8) / delta_time
        down_bps = (bytes_recv * 8) / delta_time
        
        self.last_time = current_time
        self.last_io = current_io
        
        return {
            "upload": self._format_speed(up_bps),
            "download": self._format_speed(down_bps)
        }
    
    def _format_speed(self, bps: float) -> str:
        if bps < 1000:
            return f"{bps:.1f} bps"
        elif bps < 1000000:
            return f"{bps/1000:.1f} Kbps"
        else:
            return f"{bps/1000000:.1f} Mbps"

# Singleton instance
monitor = NetworkMonitor()
