from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import json
import mimetypes
import random
import smtplib
import requests
import time
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path
from suno_api import generate_tunes, get_audio_information
from langchain_openai import ChatOpenAI
from yt_dlp import YoutubeDL
from openai import OpenAI

load_dotenv()

app = FastAPI()

llm = ChatOpenAI(model="gpt-4o")

STATIC_DIR = "/tutu_files"
# STATIC_DIR = "static"  # uncomment to run locally

os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR))


# GCP can't serve large static files from buckets, so we stream them, TODO improve streaming or resolve GCP issue
@app.get("/static2/{file_path:path}")
async def stream_file(file_path: str):
    """Stream a file as a response with appropriate content type."""
    path = f"{STATIC_DIR}/{file_path}"
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")

    def iterfile():
        with open(path, mode="rb") as file:
            while chunk := file.read(8192):  # 8KB chunks
                yield chunk

    # Get MIME type based on file extension
    content_type, _ = mimetypes.guess_type(file_path)
    if not content_type:
        content_type = "application/octet-stream"

    # Get file size for Content-Length header
    file_size = os.path.getsize(path)

    headers = {"Content-Length": str(file_size), "Accept-Ranges": "bytes"}

    return StreamingResponse(iterfile(), media_type=content_type, headers=headers)


def send_email(to_email: str, subject: str, body_html: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.send_message(message)


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


@app.post("/api/generate-video", response_class=JSONResponse)
async def generate_video_api(request: Request, input: dict):
    youtube_id = input.get("youtube_id")
    email = input.get("email")

    # First generate the music by reusing generate_music_api
    music_response = await generate_music_api(request, input)
    # audio1_suno_id = json.loads(music_response.body)["ids"][0]
    audio2_suno_id = json.loads(music_response.body)["ids"][1]

    # Then create videos for each generated audio
    video_response = await videofy(request, audio2_suno_id, youtube_id, email)
    return video_response


def get_audio_url(suno_id: str) -> str:
    for _ in range(60):
        data = get_audio_information(suno_id)
        if data[0]["status"] in ["streaming", "complete"]:
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            return data[0]["audio_url"]
        # sleep 5s
        time.sleep(5)
    return None


def subtitle_audio(audio_file_path):
    client = OpenAI()
    with open(audio_file_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            response_format="srt",
            # timestamp_granularities=["word"],  # Timestamp granularities are only supported with response_format=verbose_json'
        )
        print(transcription)
        return transcription


def get_audio_duration(audio_file_path: str) -> float:
    duration_command = f'ffmpeg -i "{audio_file_path}" 2>&1 | grep "Duration"'
    duration_output = os.popen(duration_command).read()
    if duration_output:
        time_str = duration_output.split("Duration: ")[1].split(",")[0]
        h, m, s = time_str.split(":")
        return float(h) * 3600 + float(m) * 60 + float(s)
    return 0


def repeat_subtitles(subtitles: str, audio_duration: float, times: int) -> str:
    repeated_subtitles = ""
    for i in range(times):
        # For each line in subtitles, shift timestamps by i * audio_duration
        shifted = ""
        for line in subtitles.split("\n"):
            if " --> " in line:  # This is a timestamp line
                start, end = line.split(" --> ")

                # Convert timestamp to seconds, add offset, convert back
                def timestamp_to_seconds(ts):
                    h, m, s = ts.split(":")
                    s, ms = s.split(",")
                    return float(h) * 3600 + float(m) * 60 + float(s) + float(ms) / 1000

                def seconds_to_timestamp(secs):
                    h = int(secs // 3600)
                    m = int((secs % 3600) // 60)
                    s = secs % 60
                    return f"{h:02d}:{m:02d}:{s:06.3f}".replace(".", ",")

                start_sec = timestamp_to_seconds(start) + (i * audio_duration)
                end_sec = timestamp_to_seconds(end) + (i * audio_duration)

                line = f"{seconds_to_timestamp(start_sec)} --> {seconds_to_timestamp(end_sec)}"
            shifted += line + "\n"
        repeated_subtitles += shifted
    return repeated_subtitles


@app.get("/api/video")
async def videofy(
    request: Request, suno_id: str, youtube_id: str = None, email: str = None
):
    print(suno_id, youtube_id)
    os.makedirs(f"{STATIC_DIR}/suno", exist_ok=True)
    os.makedirs(f"{STATIC_DIR}/youtube", exist_ok=True)
    os.makedirs(f"{STATIC_DIR}/output", exist_ok=True)
    os.makedirs(f"{STATIC_DIR}/output-hardsub", exist_ok=True)
    os.makedirs(f"{STATIC_DIR}/subtitles", exist_ok=True)

    audio_filename = f"{STATIC_DIR}/suno/suno-{suno_id}.mp3"
    if not os.path.exists(audio_filename):
        audio_url = get_audio_url(suno_id)
        response = requests.get(audio_url, stream=True)
        response.raise_for_status()
        if response.status_code == 200:
            with open(audio_filename, "wb") as file:
                file.write(response.content)

    subtitle_filename = f"{STATIC_DIR}/subtitles/suno-{suno_id}-10x.srt"
    if not os.path.exists(subtitle_filename):
        with open(subtitle_filename, "w") as file:
            subtitles = subtitle_audio(audio_filename)
            audio_duration = get_audio_duration(audio_filename)
            print(f"Audio duration: {audio_duration} seconds")
            repeated_subtitles = repeat_subtitles(subtitles, audio_duration, 50)
            file.write(repeated_subtitles)
    has_subtitles = (
        os.path.exists(subtitle_filename) and os.path.getsize(subtitle_filename) > 0
    )

    if not youtube_id:
        youtube_ids = open("youtube_ids.txt").read().strip().splitlines()
        youtube_id = random.choice(youtube_ids)

    video_filename = f"{STATIC_DIR}/youtube/youtube-{youtube_id}.mp4"
    if not os.path.exists(video_filename):
        ydl_opts = {
            "format": "bestvideo[ext=mp4]",
            "outtmpl": video_filename,
        }

        with YoutubeDL(ydl_opts) as ydl:
            urls = f"https://www.youtube.com/watch?v={youtube_id}"
            ydl.download(urls)

    download_filename = f"tutu-{suno_id}-{youtube_id}.mp4"
    output_filename = f"{STATIC_DIR}/output/{download_filename}"
    merge_command = f'ffmpeg -y -i "{video_filename}" -stream_loop -1 -i "{audio_filename}" -map 0:v -map 1:a -c:v copy -t $(ffprobe -i "{audio_filename}" -show_entries format=duration -v quiet -of csv="p=0") {output_filename}'
    print(merge_command)
    os.system(merge_command)
    output_filename_hardsub = f"{STATIC_DIR}/output-hardsub/{download_filename}"

    if has_subtitles and not os.path.exists(output_filename_hardsub):
        # TODO: combine it with merge command maybe
        # see https://superuser.com/a/869473 & https://stackoverflow.com/a/25880038 :
        # -vf "subtitles=subs.srt:force_style='Fontsize=24,PrimaryColour=&H0000ff&,OutlineColour=&H80000000'"
        subtitle_command = f"""ffmpeg -y -hwaccel auto -i "{output_filename}" -vf "subtitles={subtitle_filename}:force_style='Fontsize=14,OutlineColour=&H80000000,BorderStyle=3,Outline=1,Shadow=0,MarginV=20'" -c:v libx264 -preset fast -crf 23 -threads 8 -c:a copy {output_filename_hardsub}"""
        print(subtitle_command)
        os.system(subtitle_command)

    result_filename = output_filename_hardsub if has_subtitles else output_filename
    result_filename = result_filename.replace(STATIC_DIR, "static2")

    hostname = request.headers.get("host", "localhost:8000")
    scheme = request.headers.get("x-forwarded-proto", "http")
    url = f"{scheme}://{hostname}/{result_filename}"
    if email:
        send_email(
            email,
            "Your TUTU video is generated!",
            f"<a href='{url}'>Check your video out!</a>",
        )
    # FIXME: GCP can't serve large static files from buckets, max 32 MB :(
    # use `Transfer-Encoding: chunked`, or `http2`, or something else...
    return JSONResponse(content={"url": url})


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
