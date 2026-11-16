import os
import ctypes
from video_engine import render_history_short

# Set process priority to BELOW_NORMAL to keep user's PC 100% responsive for coding/browsing
try:
    # 0x00004000 = BELOW_NORMAL_PRIORITY_CLASS
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    print("[*] Set process priority to BELOW_NORMAL_PRIORITY_CLASS via Windows API for lag-free execution.")
except Exception as e:
    print(f"[*] Priority notice: {e}")

if __name__ == "__main__":
    print("[*] Launching Full 2.5D Archival Documentary Short #5 render...")
    output_path = render_history_short(5, mode="documentary")
    print(f"[SUCCESS] Final video exported to: {output_path}")
