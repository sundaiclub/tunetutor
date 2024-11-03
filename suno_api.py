import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()

base_url = os.environ.get("SUNO_API_URL")


def custom_generate_audio(payload):
    url = f"{base_url}/api/custom_generate"
    response = requests.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    return response.json()


def extend_audio(payload):
    url = f"{base_url}/api/extend_audio"
    response = requests.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    return response.json()


def generate_audio_by_prompt(payload):
    url = f"{base_url}/api/generate"
    response = requests.post(
        url, json=payload, headers={"Content-Type": "application/json"}
    )
    return response.json()


def get_audio_information(audio_ids):
    url = f"{base_url}/api/get?ids={audio_ids}"
    response = requests.get(url)
    return response.json()


def get_quota_information():
    url = f"{base_url}/api/get_limit"
    response = requests.get(url)
    return response.json()


def get_clip(clip_id):
    url = f"{base_url}/api/clip?id={clip_id}"
    response = requests.get(url)
    return response.json()


def generate_whole_song(clip_id):
    payload = {"clip_id": clip_id}
    url = f"{base_url}/api/concat"
    response = requests.post(url, json=payload)
    return response.json()


def generate_tunes(lyrics, style):
    data = custom_generate_audio(
        {
            "prompt": lyrics,
            "tags": style,
            "make_instrumental": False,
            "wait_audio": False,
        }
    )

    ids = f"{data[0]['id']},{data[1]['id']}"
    print(f"ids: {ids}")

    for _ in range(60):
        data = get_audio_information(ids)
        if data[0]["status"] == "streaming":
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            print(f"{data[1]['id']} ==> {data[1]['audio_url']}")
            return data[0]["audio_url"], data[1]["audio_url"]
        # sleep 5s
        time.sleep(5)


if __name__ == "__main__":
    style = "A jazzy, lounge-style tune with a slow swing and smooth feel, evoking classic cocktail hour vibes."
    lyrics = """
[Verse 1]
Start with gin, an ounce or two,
Fresh and bright, a classic brew.
Add lemon juice, an ounce to pour,
Citrusy notes, we’re wanting more.

Cointreau next, just add a splash,
Orange liqueur—it’s gonna last!
Then Lillet Blanc, smooth and light,
Balance the flavors, get it right.

[Chorus]
Corpse Reviver, one of a kind,
Sip it slow, you’ll unwind.
Gin and citrus, bold and sweet,
In this drink, flavors meet.

[Verse 2]
Now the absinthe, just a drop,
Too much, and it’s over the top.
Shake with ice until it’s chill,
Smooth and bright, it fits the bill.

Pour in a coupe, so cold and clear,
Raise your glass and bring it near.
One sip wakes you, starts the night,
Corpse Reviver—just right.

[Chorus]
Corpse Reviver, one of a kind,
Sip it slow, you’ll unwind.
Gin and citrus, bold and sweet,
In this drink, flavors meet."""
    data = custom_generate_audio(
        {
            "prompt": lyrics,
            "tags": style,
            "make_instrumental": False,
            "wait_audio": False,
        }
    )

    ids = f"{data[0]['id']},{data[1]['id']}"
    print(f"ids: {ids}")

    for _ in range(60):
        data = get_audio_information(ids)
        if data[0]["status"] == "streaming":
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            print(f"{data[1]['id']} ==> {data[1]['audio_url']}")
            for elem in data:
                url = elem["audio_url"]
                idd = elem["id"]
                response = requests.get(url)
                with open(f"suno-{idd}.wav", "wb") as f:
                    f.write(response.content)
            break
        # sleep 5s
        time.sleep(5)
