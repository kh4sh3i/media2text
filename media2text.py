import os
import sys
import logging
import warnings
import requests
import ssl
from pathlib import Path
from dotenv import load_dotenv
import whisper
from moviepy import VideoFileClip

# ---------------------- Configuration ----------------------
warnings.filterwarnings("ignore", message="FP16 is not supported on CPU")
load_dotenv()

VIDEO_EXTS = {".mp4", ".mkv", ".mov", ".avi", ".flv"}
AUDIO_EXTS = {".wav", ".mp3", ".m4a", ".aac", ".ogg"}
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    logging.error("❌ OpenRouter API key not found. Add OPENROUTER_API_KEY to .env")
    sys.exit(1)

# Output files
RAW_TRANSCRIPT_FILE = "transcript_raw.txt"
TUNED_TRANSCRIPT_FILE = "transcript_tuned.txt"
# -----------------------------------------------------------

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )

def is_supported_file(file_path: str, extensions: set) -> bool:
    return Path(file_path).suffix.lower() in extensions

def extract_audio(video_path: str, output_audio: str = "temp_audio.wav") -> str:
    logging.info(f"🎬 Extracting audio from: {video_path}")
    try:
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(output_audio, codec='pcm_s16le')
        return output_audio
    except Exception as e:
        logging.error(f"❌ Audio extraction failed: {e}")
        sys.exit(1)

def detect_language(audio_path: str) -> str:
    logging.info("🌐 Detecting language...")
    try:
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, task="detect_language", fp16=False)
        language = result.get("language", "en")
        logging.info(f"Detected language: {language}")
        return language
    except Exception as e:
        logging.error(f"❌ Language detection failed: {e}")
        sys.exit(1)

def transcribe_audio(audio_path: str, language_code: str) -> str:
    model_size = "medium" if language_code == "fa" else "base"
    logging.info(f"🧠 Transcribing with '{model_size}' model...")
    try:
        model = whisper.load_model(model_size)
        result = model.transcribe(audio_path, language=language_code, fp16=False)
        return result["text"]
    except Exception as e:
        logging.error(f"❌ Transcription failed: {e}")
        sys.exit(1)

def tune_text_with_openrouter(text: str, language: str) -> str:
    """Corrects text while preserving the original language with SSL fixes"""
    logging.info(f"✨ Tuning {language} text via OpenRouter...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Audio Corrector",
    }
    
    PERSIAN_MODELS = [
        "meta-llama/llama-3-70b-instruct",  # Best overall
        "anthropic/claude-3-opus",          # Excellent for languages
        "google/gemini-pro",                # Strong multilingual
        "mistralai/mixtral-8x7b-instruct",  # Good free alternative
        "openai/gpt-4.1-mini",
        "tngtech/deepseek-r1t2-chimera:free"
    ]

    instructions = {
        "fa": "فقط متن فارسی زیر را از نظر:\n"
                           "1. دستور زبان و ساختار جملات\n"
                           "2. روان‌سازی و طبیعی‌سازی متن\n"
                           "3. اصلاح اشتباهات املایی و نگارشی\n\n"
                           "مهم: تحت هیچ شرایطی:\n"
                           "- متن را ترجمه نکن\n"
                           "- اصطلاحات تخصصی را تغییر نده\n"
                           "- محتوای اصلی را عوض نکن",
        "en": "Improve this English text's grammar and clarity without translation",
        "default": "Improve grammar and clarity while preserving the original language"
    }.get(language, "default")


    payload = {
        "model": PERSIAN_MODELS[5],  # Using best available model
        "messages": [
            {"role": "system", "content": instructions},
            {"role": "user", "content": text},
        ],
        "temperature": 0.3,
    }

    try:
        # First attempt with default SSL
        response = requests.post(
            OPENROUTER_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    
    except requests.exceptions.SSLError:
        logging.warning("⚠️ SSL error detected. Retrying with SSL verification disabled...")
        try:
            # Second attempt without SSL verification
            response = requests.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload,
                verify=False,
                timeout=30
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        
        except Exception as e:
            logging.error(f"❌ OpenRouter failed after SSL retry: {e}")
            return text
    
    except Exception as e:
        logging.error(f"❌ OpenRouter error: {e}")
        return text

def save_text(text: str, filename: str) -> None:
    try:
        Path(filename).write_text(text, encoding="utf-8")
        logging.info(f"💾 Saved: {filename}")
    except Exception as e:
        logging.error(f"❌ Failed to save {filename}: {e}")
        sys.exit(1)

def main(input_path: str) -> None:
    setup_logging()

    if not Path(input_path).exists():
        logging.error(f"❌ File not found: {input_path}")
        return

    temp_audio = None
    if is_supported_file(input_path, VIDEO_EXTS):
        temp_audio = extract_audio(input_path)
        audio_path = temp_audio
    elif is_supported_file(input_path, AUDIO_EXTS):
        audio_path = input_path
    else:
        logging.error(f"⚠️ Unsupported file type: {input_path}")
        return

    # Process audio
    language_code = detect_language(audio_path)
    raw_text = transcribe_audio(audio_path, language_code)
    save_text(raw_text, RAW_TRANSCRIPT_FILE)

    # Improve text
    tuned_text = tune_text_with_openrouter(raw_text, language_code)
    save_text(tuned_text, TUNED_TRANSCRIPT_FILE)

    # Cleanup
    if temp_audio and Path(temp_audio).exists():
        Path(temp_audio).unlink()
        logging.info(f"🧹 Deleted temp file: {temp_audio}")

    logging.info("✅ Processing complete!")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python media2text.py <video_or_audio_file>")
        sys.exit(1)
    main(sys.argv[1])