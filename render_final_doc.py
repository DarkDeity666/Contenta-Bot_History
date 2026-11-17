import os
import sys
import ctypes
from video_engine import render_history_short

# Set process priority to BELOW_NORMAL to keep user's PC 100% responsive for coding/browsing
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x00004000)
    print("[*] Set process priority to BELOW_NORMAL_PRIORITY_CLASS via Windows API for lag-free execution.")
except Exception as e:
    print(f"[*] Priority notice: {e}")

if __name__ == "__main__":
    script_id = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    print(f"[*] Launching Full 2.5D Archival Documentary Short #{script_id} render...")
    output_path = render_history_short(script_id, mode="documentary")
    print(f"[SUCCESS] Final video exported to: {output_path}")
