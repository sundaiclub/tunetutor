import requests
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


def download_audio(url, filename="audio_file.mp3"):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Downloaded audio file to {filename}")
        return filename
    else:
        raise Exception("Failed to download the audio file")


# URL of the audio file
url = "https://audiopipe.suno.ai/?item_id=d8e35699-df92-4b0c-967b-92752c0993dd"

audio_file = download_audio(url)


def timestamp_audio(audio_file_path):
    try:
        client = OpenAI()  # will use .env file key OPENAI_API_KEY automatically
        with open(audio_file_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["word"],
            )
            word_timestamps = [
                {"word": word.word, "start": word.start, "end": word.end}
                for word in transcription.words
            ]
            return word_timestamps
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None


audio_file_path = "audio_file.mp3"
timestamps = timestamp_audio(audio_file_path)
if timestamps:
    for ts in timestamps:
        print(f"Word: {ts['word']}, Start: {ts['start']:.2f}, End: {ts['end']:.2f}")
