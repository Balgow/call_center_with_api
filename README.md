# Voice Assistant with Yandex Speech-to-Text and GPT-4

This is a voice assistant that uses Yandex's Speech-to-Text API for speech recognition and OpenAI's GPT-4 for generating responses.

## Features

- Real-time speech recognition using Yandex Speech-to-Text API
- GPT-4 powered responses
- Streaming audio processing
- Clean and modular architecture

## Prerequisites

- Python 3.8+
- Yandex Cloud account with Speech-to-Text API access
- OpenAI API key
- Microphone access

## Setup

1. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your API keys:
```
YANDEX_API_KEY=your_yandex_api_key
```

## Usage

1. Run the main script:
```bash
python -m src.main
```

2. Press Enter to start recording
3. Speak into your microphone
4. The system will:
   - Convert your speech to text using Yandex Speech-to-Text
   - Process the text using GPT-4o-mini
   - Display both the recognized text and GPT's response
5. Press Ctrl+C to exit


## Error Handling

The system includes comprehensive error handling for:
- Audio recording issues
- API connection problems
- Invalid API keys
- Network interruptions
