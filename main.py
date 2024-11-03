import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from pathlib import Path
from suno_api import generate_tunes
from langchain_openai import ChatOpenAI

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
    urls = generate_tunes(lyrics, style)
    print(f"URLS:\n\n{urls}")
    return lyrics, style, urls


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
    lyrics, style, urls = generate_brainwash(query, version)
    html = "<h1>Music Generation Results:</h1>"
    for url in urls:
        html += f"<a href='{url}' target='_blank'>Listen {url}</a><br>"
    html += f"<h1>Lyrics:</h1><pre>{lyrics}</pre>"
    html += f"<h1>Style:</h1><pre>{style}</pre>"
    html += f"<h1>User Query:</h1><pre>{query}</pre>"
    html += "<br><br><a href='/'>← Go Back</a>"
    return HTMLResponse(content=html, status_code=200)


@app.post("/api/generate")
async def generate_music_api(query: str, version: int):
    lyrics, style, urls = generate_brainwash(query, version)
    return {"lyrics": lyrics, "style": style, "urls": urls}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
