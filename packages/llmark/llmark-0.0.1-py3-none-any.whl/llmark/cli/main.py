import os

from cyclopts import App
from openai import OpenAI

from llmark.context import fetch_context

app = App()


@app.command
def make(filename: str):
    context = fetch_context(filename)
    prompt = format_context(context)

    for chunk in complete(prompt):
        content = chunk.choices[0].delta.content
        if content:
            print(content, end="")


def format_context(contxt: list[tuple[str, str]]):
    return "\n".join([f"Filename: {f}\n {c}" for f, c in contxt])


def complete(prompt: str):
    client = get_client()
    completion = client.chat.completions.create(
        model=os.getenv("MODEL", "meta-llama/llama-3.1-8b-instruct:free"),
        messages=[
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=True,
    )
    return completion


def get_client():
    base_url = os.getenv("BASE_URL", "https://openrouter.ai/api/v1")
    api_key = os.getenv("API_KEY")
    return OpenAI(base_url=base_url, api_key=api_key)


def run_app():
    app()
