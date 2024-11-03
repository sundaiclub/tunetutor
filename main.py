import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from suno_api import generate_tunes
from langchain_openai import ChatOpenAI

app = FastAPI()

llm = ChatOpenAI()


def generate_lyrics(query: str, version: int):
    prompt = Path(f"prompts/lyrics-{version}.txt").read_text()
    prompt += "\n\n" + query
    response = llm.invoke(prompt).content
    return response


def generate_style(query: str, version: int):
    prompt = Path(f"prompts/style-{version}.txt").read_text()
    prompt += "\n\n" + query
    response = llm.invoke(prompt).content
    return response


def generate_brainwash(query: str, version: int):
    lyrics = generate_lyrics(query, version)
    style = generate_style(query, version)
    print(f"Lyrics:\n\n{lyrics}")
    print(f"Style:\n\n{style}")
    urls = generate_tunes(lyrics, style)
    print(f"URLS:\n\n{urls}")
    return urls


html_content = """
<html>
    <body>
        <h1>Music Generation Form</h1>
        <form action="/form-results" method="post">
            <label for="query">Query:</label><br>
            <input type="text" id="query" name="query"><br>
            <label for="version">Version:</label><br>
            <input type="number" id="version" name="version"><br>
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
    urls = generate_brainwash(query, version)
    html_links = ""
    for url in urls:
        html_links += f"<a href='{url}' target='_blank'>Listen {url}</a><br>"
    return HTMLResponse(content=html_links, status_code=200)


@app.post("/api/generate")
async def generate_music_api(query: str, version: int):
    urls = generate_brainwash(query, version)
    return {"urls": urls}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
