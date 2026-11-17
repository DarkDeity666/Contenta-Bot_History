"""
One-Time YouTube Channel Authorization Helper
Opens your browser so you can log into your Google / YouTube channel once.
Tokens are saved securely in youtube_token.json.
"""
import sys
from youtube_uploader import get_authenticated_service, get_channel_details

def main():
    print("=" * 60)
    print("   CONTENTA HISTORY BOT - YOUTUBE CHANNEL AUTHORIZATION")
    print("=" * 60)
    print("\n[*] Initializing OAuth flow using client_secret.json...")
    print("[*] A browser window will now open.")
    print("[*] Select your Google account that owns your YouTube channel and click 'Allow'.\n")

    try:
        service = get_authenticated_service(interactive=True)
        if service:
            channel = get_channel_details()
            print("\n" + "=" * 60)
            if channel:
                print(f"🎉 SUCCESS! Connected to channel: {channel['title']}")
                print(f"   Subscribers: {int(channel['subscribers']):,}")
                print(f"   Video count: {channel['videoCount']}")
            else:
                print("🎉 SUCCESS! Authorization token saved to youtube_token.json")
            print("=" * 60)
            print("\nYou can now upload videos directly from the Contenta Studio Dashboard!")
        else:
            print("\n[!] Authorization could not be completed.")
    except Exception as e:
        print(f"\n[!] Error during authorization: {e}")

if __name__ == "__main__":
    main()
