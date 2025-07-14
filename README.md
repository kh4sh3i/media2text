<h1 align="center">
  <a><img src="/img/logo.png" alt="" width="200px"></a>
  <br>
  <img src="https://img.shields.io/badge/PRs-welcome-blue">
  <img src="https://img.shields.io/github/last-commit/kh4sh3i/media2text">
  <img src="https://img.shields.io/github/commit-activity/m/kh4sh3i/media2text">
  <a href="https://twitter.com/intent/follow?screen_name=kh4sh3i_"><img src="https://img.shields.io/twitter/follow/kh4sh3i_?style=flat&logo=twitter"></a>
  <a href="https://github.com/kh4sh3i"><img src="https://img.shields.io/github/stars/kh4sh3i?style=flat&logo=github"></a>
</h1>

# 🎙️ media2text (AI Audio & Video Transcriber)

Convert audio and video files into accurate text transcripts using AI (Whisper, DeepSeek, or OpenRouter models).  
Supports multiple formats and can be self-hosted with minimal setup.

## 🚀 Features

- 🔊 Supports audio files: `.mp3`, `.wav`, `.m4a`, `.ogg`
- 🎥 Supports video files: `.mp4`, `.mkv`, `.mov` (extracts audio automatically)
- 🧠 Powered by AI models:
  - OpenAI Whisper
  - DeepSeek (via OpenRouter)
- 🔧 Self-hosted: run locally on your own machine
- 🗂 Outputs clean, timestamped text files

## 🛠 Installation

```bash
git clone https://github.com/kh4sh3i/media2text.git
cd media2text
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create your `.env` file (based on `.env.example`) and add your API keys if needed.

## 🧪 Usage

```bash
python media2text.py "path/to/media"
```

## 🧠 Supported Models

| Model     | API Support | Offline | Notes                        |
|-----------|-------------|---------|------------------------------|
| Whisper   | ✅ Yes       | ✅ Yes  | Best balance of accuracy/speed |
| DeepSeek  | ✅ Yes       | ❌ No   | Requires API key via OpenRouter |

## 📄 License

MIT License. Use freely, credit appreciated.
