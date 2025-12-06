# 🎙️ AI-Powered Voice Assistant

A Python-based intelligent voice assistant that can respond to your spoken commands, perform tasks like sending emails, checking weather/news, playing music, taking notes, doing calculations, and even interacting with AI via a Language Model API.

---

## 🧠 Overview

This AI-Powered Voice Assistant listens to your voice, processes the command using keyword-based logic (and optionally with an LLM), and performs the task using specialized modules.

- 🎤 Converts voice to text using `speech_recognition`
- 🗣️ Speaks responses using `pyttsx3`
- 🔍 Integrates utilities like email, weather, notes, music, reminders, and PDFs
- 💬 (Optional) Connects to an external AI API like Gemini/OpenAI for enhanced responses

---

## 📁 Project Structure


---

## 🚀 Features

| Feature         | Description |
|----------------|-------------|
| 🎧 Voice Control | Talk to the assistant via your microphone |
| 🧠 AI Integration | Use `gemini_api.py` to plug in an AI language model |
| 🔗 Web Browsing | Open websites, search queries |
| 📨 Email Sender | Compose and send emails with voice |
| 📅 Reminder Set | Get local notifications |
| 🎵 Music Player | Play MP3s stored locally |
| 📖 News Reader | Fetch latest news headlines |
| 📄 PDF Reader | Read content from PDF files |
| 📝 Note Keeper | Create & read quick notes |
| 📍 Weather Info | Get current weather by city |
| ➗ Calculator | Perform basic math |

---
> **Note:** If any module error appears while running, install it using:
> ```
> pip install <module_name>
> ```

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/MrShalby/AI-Powered-Voice-Assistant.git
cd AI-Powered-Voice-Assistant



