import os
import sys
import time
import ctypes
from datetime import datetime
from pathlib import Path

from config import BASE_DIR, OUTPUT_DIR
from database import init_db, get_connection
from scraper import harvest_and_store_topics
from script_generator import process_next_script
from audio_engine import process_audio_for_script
from video_engine import render_history_short
from youtube_uploader import upload_short_to_youtube

def set_background_priority():
    """
    Sets Windows process priority to BELOW_NORMAL.
    Ensures the bot never causes lag in VS Code, browsers, or dev servers.
    """
    try:
        BELOW_NORMAL_PRIORITY_CLASS = 0x00004000
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        ctypes.windll.kernel32.SetPriorityClass(handle, BELOW_NORMAL_PRIORITY_CLASS)
        print("[*] Windows Process Priority set to BELOW_NORMAL (User apps prioritized).")
    except Exception as e:
        print(f"[!] Could not adjust process priority: {e}")

def run_production_batch(batch_size: int = 10, spacing_hours: int = 4):
    """
    Runs the complete production pipeline to create and schedule a batch of videos.
    Designed to run seamlessly during your 3-hour computer session.
    """
    start_time = datetime.now()
    print("=" * 65)
    print("  ANTIGRAVITY HISTORY BOT - 10M VIEWS AUTOMATION ENGINE  ")
    print(f"  Session Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Target: {batch_size} Videos (RTX 3060 NVENC Accelerated)")
    print("=" * 65)

    # 1. System Setup & Resource Tuning
    set_background_priority()
    init_db()

    # 2. Infinite Topic Miner
    print("\n>>> STAGE 1: Harvesting Fresh Historical Anomalies...")
    new_topics = harvest_and_store_topics()

    # 3. Batch Production Loop
    completed = 0
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM topics WHERE status = 'pending' LIMIT ?", (batch_size,))
    pending_topics = cursor.fetchall()
    conn.close()

    print(f"\n>>> STAGE 2: Producing Batch ({len(pending_topics)} topics ready)...")

    for idx, row in enumerate(pending_topics, start=1):
        topic_id = row["id"]
        print("-" * 55)
        print(f"[*] Processing Video #{idx}/{len(pending_topics)} (Topic #{topic_id})...")

        try:
            # Step A: Script & Fact-Check
            script_id = process_next_script()
            if not script_id:
                continue

            # Step B: Voiceover & Whisper Sync
            audio_info = process_audio_for_script(script_id)

            # Step C: RTX 3060 NVENC 2D Animated Stickman Render
            video_path = render_history_short(script_id)

            # Fetch script details for YouTube metadata
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT title, full_narration FROM scripts WHERE id = ?", (script_id,))
            s_row = cursor.fetchone()
            conn.close()

            title = s_row["title"]
            description = s_row["full_narration"]

            # Step D: Scheduled YouTube Upload (Spaced out for algorithm momentum)
            schedule_delay = idx * spacing_hours
            upload_id = upload_short_to_youtube(
                video_path=video_path,
                title=title,
                description=description,
                schedule_delay_hours=schedule_delay
            )

            completed += 1
            print(f"[✓] Video #{idx} COMPLETE: Scheduled for +{schedule_delay}h | ID: {upload_id}")

            # Brief pause to keep GPU cool
            time.sleep(2)

        except Exception as e:
            print(f"[X] Error processing topic #{topic_id}: {e}")

    elapsed = datetime.now() - start_time
    print("=" * 65)
    print(f"  BATCH COMPLETE! {completed}/{batch_size} Videos Generated & Scheduled.")
    print(f"  Total Session Time: {str(elapsed).split('.')[0]}")
    print(f"  Videos stored in: {OUTPUT_DIR}")
    print("=" * 65)

if __name__ == "__main__":
    # Run 2 videos for quick verification (or change to 10 for full batch)
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    run_production_batch(batch_size=target, spacing_hours=4)
