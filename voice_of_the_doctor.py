#Step1a: Setup Text to Speech–TTS–model with gTTS

import os
from gtts import gTTS

def text_to_speech_with_gtts_old(input_text, output_filepath):
    language="en"

    audioobj= gTTS(
        text=input_text,
        lang=language,
        slow=False
    )
    audioobj.save(output_filepath)


input_text="Hi this is Ai with Ashik khan"
text_to_speech_with_gtts_old(input_text=input_text, output_filepath="gtts_testing.mp3")




#Step2: Use Model for Text output to Voice
# tts_and_playback.py
import os
import platform
import subprocess
import shutil
from gtts import gTTS

def save_tts(input_text: str, output_filepath: str, lang: str = "en") -> None:
    """Generate and save TTS audio using gTTS."""
    tts = gTTS(text=input_text, lang=lang, slow=False)
    tts.save(output_filepath)
    print(f" Saved TTS to: {os.path.abspath(output_filepath)}")

def play_audio(output_filepath: str, timeout_seconds: int = 30) -> None:
    """Try several reliable ways to play audio across platforms."""
    if not os.path.exists(output_filepath):
        raise FileNotFoundError(f"Audio file not found: {output_filepath}")

    system = platform.system()
    # 1) Prefer ffplay (part of ffmpeg) if present — quick and reliable
    ffplay_path = shutil.which("ffplay")
    if ffplay_path:
        print(" Playing with ffplay...")
        # -nodisp: no video window, -autoexit: exit when done
        subprocess.run([ffplay_path, "-nodisp", "-autoexit", "-hide_banner", output_filepath],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=timeout_seconds)
        return

    # 2) Windows PowerShell synchronous playback (works reasonably well)
    if system == "Windows":
        print(" Playing with PowerShell Media.SoundPlayer...")
        # Use PlaySync to block until done
        powershell_cmd = [
            "powershell",
            "-NoProfile",
            "-Command",
            f'(New-Object Media.SoundPlayer "{output_filepath}").PlaySync();'
        ]
        try:
            subprocess.run(powershell_cmd, check=True, timeout=timeout_seconds)
            return
        except subprocess.CalledProcessError as e:
            print("PowerShell playback failed:", e)
        except subprocess.TimeoutExpired:
            print("PowerShell playback timed out.")

    # 3) Try playsound library if installed (cross-platform, simple)
    try:
        from playsound import playsound  # type: ignore
        print(" Playing with playsound...")
        playsound(output_filepath)
        return
    except Exception as e:
        # playsound not installed or failed
        print("playsound not available or failed:", e)

    # 4) macOS: afplay
    if system == "Darwin":
        afplay_path = shutil.which("afplay") or "/usr/bin/afplay"
        if afplay_path and os.path.exists(afplay_path):
            print(" Playing with afplay...")
            subprocess.run([afplay_path, output_filepath], check=False, timeout=timeout_seconds)
            return

    # 5) Linux: try aplay or mpg123 or xdg-open as fallback
    if system == "Linux":
        for cmd_name in ("aplay", "mpg123", "mpv", "xdg-open"):
            cmd_path = shutil.which(cmd_name)
            if cmd_path:
                print(f" Playing with {cmd_name}...")
                # xdg-open will open default player (non-blocking); others block
                if cmd_name == "xdg-open":
                    subprocess.Popen([cmd_path, output_filepath])
                else:
                    subprocess.run([cmd_path, output_filepath], check=False, timeout=timeout_seconds)
                return

    # 6) Last resort: open file with OS default (non-blocking)
    try:
        print(" Opening with default application (last resort)...")
        if system == "Windows":
            os.startfile(output_filepath)  # type: ignore
        elif system == "Darwin":
            subprocess.Popen(["open", output_filepath])
        else:
            subprocess.Popen(["xdg-open", output_filepath])
    except Exception as e:
        raise RuntimeError(f"All playback methods failed: {e}")

if __name__ == "__main__":
    # Example usage
    output_path = r"Ai chatbot\gtts_testing_autoplay.mp3"
    text = "Hi, this is AI with Ashik Khan. Autoplay testing."

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        save_tts(text, output_path)
        play_audio(output_path)
    except Exception as exc:
        print("Error:", exc)
        print("If playback failed, check that ffplay or playsound is installed, or try opening the file manually.")
