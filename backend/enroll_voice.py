import sys
import time
from pathlib import Path

import dashscope
from dashscope.audio.tts_v2 import VoiceEnrollmentService

from app.config import settings

dashscope.api_key = settings.dashscope_api_key
dashscope.base_http_api_url = "https://dashscope-intl.aliyuncs.com/api/v1"

VOICE_DIR = Path("voice")
VOICE_ID_FILE = VOICE_DIR / "voice_id.txt"


def main() -> None:
    if len(sys.argv) < 2:
        print('Usage: python enroll_voice.py "https://public-url/reference_voice.wav"')
        sys.exit(1)
    url = sys.argv[1]

    service = VoiceEnrollmentService()
    print("Submitting your voice for cloning...")
    voice_id = service.create_voice(
        target_model=settings.clone_model,
        prefix=settings.clone_prefix,
        url=url,
        language_hints=["en"],
    )
    print(f"Voice submitted. ID: {voice_id}")
    print(f"Request ID: {service.get_last_request_id()}")

    print("Waiting for it to be approved (this can take a minute)...")
    for _ in range(30):
        time.sleep(5)
        voices = service.list_voices(prefix=settings.clone_prefix, page_index=0, page_size=10)
        match = next((v for v in voices if v.get("voice_id") == voice_id), None)
        status = match.get("status") if match else "UNKNOWN"
        print(f"  status: {status}")
        if status == "OK":
            VOICE_DIR.mkdir(exist_ok=True)
            VOICE_ID_FILE.write_text(voice_id, encoding="utf-8")
            print("\nDone. Your cloned voice is ready.")
            print(f"Saved voice_id to {VOICE_ID_FILE}")
            return
        if status in ("UNDEPLOYED", "FAILED"):
            print(f"\nRejected (status {status}). The reference may be too noisy, or the URL "
                  f"unreachable. Confirm the URL plays in a browser, then retry.")
            sys.exit(1)

    print("\nStill pending. Re-run later to check, or try a cleaner reference.")


if __name__ == "__main__":
    main()
