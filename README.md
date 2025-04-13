# AIStep 🚶‍♂️🗺️ – AI-Powered Walking Route Generator

AIStep is a smart Telegram bot that helps users generate custom walking routes based on their preferences using **AI** and **voice input**. Simply tell the bot what kind of places you'd like to visit — parks, museums, coffee shops — and it will build a personalized walking route using Google Maps APIs and GPT.

> 🧠 Built entirely by one developer as a solo project and pitched to 2GIS for future integration.

---

## 🛠 Tech Stack

- **Python**
- **Aiogram** – for building the Telegram bot
- **OpenAI GPT** – to process natural language requests
- **SpeechRecognition** & **pydub** – for converting voice to text
- **Google Maps Platform APIs**:
  - Places API (to find locations)
  - Directions API (to calculate routes)
  - Static Maps API (to visualize the route)

---

## ✨ Features

- 🎙️ **Voice Input**: Speak your preferences — the bot understands and processes them.
- 🧭 **Custom Route Generation**: Get walking routes based on your interests and location.
- 🧠 **AI-Powered Planning**: GPT converts natural language into smart API queries.
- 🗺️ **Map Rendering**: The route is visualized with pins and path overlays.
- 📍 **Details Included**: For each place, see its name, rating, and address.
- ⚡ **Fast & Async**: Built with asynchronous Python for a responsive experience.

---

## 📸 Example Usage

1. Send a **voice message** like:  
   > “I want to walk through some quiet parks and stop by a nice café.”

2. The bot replies with:
   - A **custom-generated map**
   - A list of places with ratings and details
   - Total walking time & distance

---

## 📦 Installation & Running Locally

1. Clone the repo:
   ```bash
   git clone https://github.com/Kyimatik/AIStep.git
   cd aistep
Install dependencies:

pip install -r requirements.txt
Add your API keys in .env:
TELEGRAM_TOKEN=your_bot_token
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_maps_key
Run the bot:
python main.py

🧪 Status
✅ Working prototype
🔜 Potential for future features: multi-stop optimization, route preferences (distance, time), public transport integration.



Emirlan Ysmanov 
📧 y.emirlan08@gmail.com

🧠 Fun Fact
This project was created during a weekend hackathon and proposed as a feature to 2GIS, a major mapping company. It combines AI, maps, and voice tech to make urban exploration effortless.
