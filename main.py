import os
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests

app = FastAPI()

api_key = os.environ.get("OPENAI_API_KEY")
prompts = {}

class PromptData(BaseModel):
    prompt: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Bark API!"}

@app.post("/prompts/{prompt_id}")
def create_prompt(prompt_id: str, prompt_data: PromptData):
    prompt = prompt_data.prompt
    if prompt:
        prompts[prompt_id] = prompt
        return {"prompt_id": prompt_id, "prompt": prompt}
    else:
        raise HTTPException(status_code=400, detail="Prompt is required.")

@app.get("/process/{prompt_id}")
def process_prompt(prompt_id: str):
    prompt = prompts.get(prompt_id)
    if prompt:
        response = requests.post(
            "https://api.openai.com/v1/engines/davinci-codex/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "prompt": prompt,
                "max_tokens": 100,
            }
        )
        response.raise_for_status()
        result = response.json()["choices"][0]["text"]
        return {"prompt_id": prompt_id, "result": result}
    else:
        raise HTTPException(status_code=404, detail="Prompt not found.")

