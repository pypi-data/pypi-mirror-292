from cooputils.config import internal_get_loaded_config
import requests

CHUNK_SIZE = 1024  # Size of chunks to read/write at a time


def download_text_to_speech(text: str, download_path: str):
    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{internal_get_loaded_config().ELEVEN_LABS_VOICE_ID}/stream"

    headers = {
      "xi-api-key": internal_get_loaded_config().ELEVEN_LABS_API_KEY,
      "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.35,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        },
        # "seed": 123,
        # "previous_text": "<string>",
        # "next_text": "<string>",
    }

    print("Downloading audio stream...")
    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    # Check if the request was successful
    if response.ok:
        # Open the output file in write-binary mode
        with open(download_path, "wb") as f:
            # Read the response in chunks and write to the file
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        # Inform the user of success
        print("Audio stream saved successfully.")
    else:
        # Print the error message if the request was not successful
        print(response.text)

