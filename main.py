from fastapi import FastAPI
from pathlib import Path
from suno_api import generate_tunes
from langchain_openai import ChatOpenAI

app = FastAPI()

llm = ChatOpenAI()


def generate_lyrics(query: str):
    prompt = Path("prompts/lyrics-1.txt").read_text()
    llm.invoke(prompt).content
    return query


def generate_style(query: str):
    prompt = Path("prompts/style-1.txt").read_text()
    llm.invoke(prompt).content
    return query


@app.post("/api/generate")
async def generate_music(query: str):
    lyrics = generate_lyrics(query)
    style = generate_style(query)
    urls = generate_tunes(lyrics, style)
    return {"urls": urls}
