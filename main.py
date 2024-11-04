import os
import random
import requests
import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from pathlib import Path
from suno_api import generate_tunes, get_audio_information
from langchain_openai import ChatOpenAI
from yt_dlp import YoutubeDL

app = FastAPI()

llm = ChatOpenAI(model="gpt-4o")


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


html_content = """
<html>
    <body>
        <h1>Music Generation Form</h1>
        <form action="/form-results" method="post">
            <label for="query">Query:</label><br>
            <textarea cols=50 rows=3 id="query" name="query"></textarea><br><br>
            <label for="version">Version:</label>
            <select id="version" name="version">
                <option value="1">1 (Kris)</option>
                <option value="2">2 (Chloe)</option>
            </select><br><br>
            <input type="submit" value="Generate Music">
        </form>
    </body>
</html>
"""


@app.get("/")
async def get_form():
    return HTMLResponse(content=html_content, status_code=200)


@app.post("/form-results")
async def generate_music_form(request: Request):
    form_data = await request.form()
    query = form_data.get("query")
    version = form_data.get("version")
    lyrics, style, audios = generate_brainwash(query, version)
    html = "<h1>Music Generation Results:</h1>"
    for audio in audios:
        url = audio["url"]
        idd = audio["id"]
        html += f"<a href='{url}' target='_blank'>Listen</a>, <a href='/videofy/{idd}/NO' target='_blank'>Videofy</a>, ID: {idd}<br>"
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


VIDEO_URLS = """
iFiPxTrcoWw
wv8_ePzdMv8
qK1VjY_cU9w
13_4cPyWiIo
dBE0pZtK3ao
GA8vYmmvqEk
oPz7Uh_6ey4
r5utBFtLtWk
3j5PUUQz5cw
Pap_Ln-Fz2A
0ikEJppc9qQ
FHkeRqGnNQk
A2RQGBQvHfI
IWy5lAkt6CY
CCfNnjiN8xI
iUEccNy3m04
l0aysU5iE5k
wrSXoFBozu4
ckKNrq56XIw
-IegPHSc2VA
o9b2oynTQXo
X_79-x_nLzs
1e6Rn6JEICc
StgZ5ct4Jx4
QZQPRIg245A
vC04Xj7NWBc
Pp7fmvfyaOI
YB10EbfzZts
mvNSGMcTN1s
pSgWt_CFtHM
i5w6Y74ZgYk
FXzWKqMPHI0
prmMgmdM-xc
xKRNDalWE-E
rsEP9N9c5CQ
bb07ui130-8
7cIPxrLYw8M
--owd7CIjYs
axAYvo8gOIA
B2GM98bKhVg
E1CgDCh5KC0
BbM2MJ6aeZE
rYPeM4m-tJc
oSzKvHzjrSA
YpjTpjFuhZM
wXN08vl6TWI
AGnZ8nMnbv4
lzEEhDRRafM
Ctdg-sOW8po
6GPXGBg7UGo
4ASNL5RwghA
lVtPEAeM-UM
cOUcu-xSKHM""".strip().splitlines()


@app.get("/videofy/{suno_id}/{yt_id}")
async def videofy(suno_id: str, yt_id: str = None):
    if yt_id == "NO":
        yt_id = random.choice(VIDEO_URLS)
    os.makedirs("files", exist_ok=True)
    print(suno_id, yt_id)
    audio_url = None
    for _ in range(60):
        data = get_audio_information(suno_id)
        if data[0]["status"] in ["streaming", "complete"]:
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            audio_url = data[0]["audio_url"]
            break
        # sleep 5s
        time.sleep(5)

    response = requests.get(audio_url)
    audio_filename = f"files/suno-{suno_id}.mp3"
    if response.status_code == 200:
        with open(audio_filename, "wb") as file:
            file.write(response.content)

    video_filename = f"files/{yt_id}.mp4"
    ydl_opts = {
        "format": "bestvideo",
        "outtmpl": video_filename,
    }

    with YoutubeDL(ydl_opts) as ydl:
        urls = f"https://www.youtube.com/watch?v={yt_id}"
        ydl.download(urls)

    output_filename = f"files/merged-{suno_id}.mp4"
    download_filename = f"tune-tutor-{suno_id}.mp4"
    merge_command = f'ffmpeg -y -i "{video_filename}" -stream_loop -1 -i "{audio_filename}" -map 0:v -map 1:a -c:v copy -shortest {output_filename}'
    print(merge_command)
    os.system(merge_command)

    return FileResponse(
        output_filename, media_type="video/mp4", filename=download_filename
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
