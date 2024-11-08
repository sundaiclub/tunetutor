import os
import random
import requests
import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
)
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from suno_api import generate_tunes, get_audio_information
from langchain_openai import ChatOpenAI
from yt_dlp import YoutubeDL

app = FastAPI()

llm = ChatOpenAI(model="gpt-4o")

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


def generate_lyrics(query: str, version: int):
    prompt = Path(f"prompts/lyrics-{version}.txt").read_text()
    prompt += "\n\n" + query
    response = llm.invoke(prompt).content
    return response


def generate_style(query: str, version: int):
    prompt = Path(f"prompts/style-{version}.txt").read_text()
    if version == 2:
        return prompt  # fixed, no AI
    prompt += "\n\n" + query
    response = llm.invoke(prompt).content
    return response


def generate_brainwash(query: str, version: int):
    version = int(version)
    lyrics = generate_lyrics(query, version)
    style = generate_style(query, version)
    print(f"Lyrics:\n\n{lyrics}")
    print(f"Style:\n\n{style}")
    audios = generate_tunes(lyrics, style, query)
    print(f"AUDIOS:\n\n{audios}")
    return lyrics, style, audios


@app.get("/")
async def index_form():
    html_content = open("index.html").read()
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/form-results")
async def index_form_results(request: Request):
    form_data = await request.form()
    query = form_data.get("query")
    version = form_data.get("version")
    lyrics, style, audios = generate_brainwash(query, version)
    html = "<h1>Music Generation Results:</h1>"
    html += "<ol>"
    for audio in audios:
        audio_url = audio["url"]
        suno_id = audio["id"]
        html += f"<li>Listen: <audio src='{audio_url}' style='vertical-align: middle;' controls></audio><br>Watch: <a href='/api/video?suno_id={suno_id}' target='_blank'>API</a><br>Suno ID: {suno_id}<br>"
    html += f"<h1>Lyrics:</h1><pre>{lyrics}</pre>"
    html += f"<h1>Style:</h1><pre>{style}</pre>"
    html += f"<h1>User Query:</h1><pre>{query}</pre>"
    html += "<br><br><a href='/'>← Go Back</a>"
    return HTMLResponse(content=html, status_code=200)


@app.post("/api/generate", response_class=JSONResponse)
async def generate_music_api(request: Request, input: dict):
    query = input.get("query")
    version = input.get("version")
    lyrics, style, audios = generate_brainwash(query, version)
    return JSONResponse(
        content={
            "lyrics": lyrics,
            "style": style,
            "urls": [audio["url"] for audio in audios],
            "ids": [audio["id"] for audio in audios],
        }
    )


def get_audio_url(suno_id: str) -> str:
    for _ in range(60):
        data = get_audio_information(suno_id)
        if data[0]["status"] in ["streaming", "complete"]:
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            return data[0]["audio_url"]
        # sleep 5s
        time.sleep(5)
    return None


@app.get("/api/video")
async def videofy(request: Request, suno_id: str, youtube_id: str = None):
    print(suno_id, youtube_id)
    os.makedirs("static/suno", exist_ok=True)
    os.makedirs("static/youtube", exist_ok=True)
    os.makedirs("static/output", exist_ok=True)

    audio_url = get_audio_url(suno_id)
    response = requests.get(audio_url)
    audio_filename = f"static/suno/suno-{suno_id}.mp3"
    if response.status_code == 200:
        with open(audio_filename, "wb") as file:
            file.write(response.content)

    if not youtube_id:
        youtube_ids = open("youtube_ids.txt").read().strip().splitlines()
        youtube_id = random.choice(youtube_ids)
    video_filename = f"static/youtube/youtube-{youtube_id}.mp4"
    ydl_opts = {
        "format": "bestvideo",
        "outtmpl": video_filename,
    }

    with YoutubeDL(ydl_opts) as ydl:
        urls = f"https://www.youtube.com/watch?v={youtube_id}"
        ydl.download(urls)

    download_filename = f"tutu-{suno_id}-{youtube_id}.mp4"
    output_filename = f"static/output/{download_filename}"
    merge_command = f'ffmpeg -y -i "{video_filename}" -stream_loop -1 -i "{audio_filename}" -map 0:v -map 1:a -c:v copy -shortest {output_filename}'
    print(merge_command)
    os.system(merge_command)

    hostname = request.headers.get("host", "localhost:8000")
    scheme = request.headers.get("x-forwarded-proto", "http")
    return JSONResponse(content={"url": f"{scheme}://{hostname}/{output_filename}"})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
