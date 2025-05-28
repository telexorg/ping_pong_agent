from pprint import pprint
import uvicorn, json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from a2a.utils import new_agent_text_message

app = FastAPI()

RAW_AGENT_CARD_DATA = {
  "name": "PingPongAgent",
  "description": "An agent that responds 'pong' to 'ping'.",
  "url": "http://localhost:4000",
  "version": "1.0.0",
  "capabilities": {
    "streaming": False,
    "pushNotifications": False
  },
  "skills": [
    {
      "id": "ping",
      "name": "Ping-Pong",
      "description": "Responds with 'pong' when given 'ping'.",
      "inputModes": ["text"],
      "outputModes": ["text"],
      "examples": [
        {
          "input": { "parts": [{ "text": "ping", "contentType": "text/plain" }] },
          "output": { "parts": [{ "text": "pong", "contentType": "text/plain" }] }
        }
      ]
    }
  ]
}


@app.get("/", response_class=HTMLResponse)
def read_root():
    return '<p style="font-size:30px">Ping Pong Agent</p>'


@app.get("/.well-known/agent.json")
def agent_card(request: Request):
    current_base_url = str(request.base_url).rstrip("/")

    response_agent_card = RAW_AGENT_CARD_DATA.copy()
    response_agent_card["url"] = current_base_url

    return response_agent_card



@app.post("/task/send")
async def handle_task(request: Request):
    body = await request.json()

    task_id = body.get("id")
    message = body["params"]["message"]["parts"][0].get("text", None)

    if message and message.lower() == "ping":
        text = "pong"

    else:
        text = "I only understand 'ping'"

    message = new_agent_text_message(text=text, task_id=task_id)


    response = {
        "jsonrpc": "2.0",
        "id": task_id,
        "result": message.model_dump()
    }

    pprint(response)
    return response


if __name__ == "__main__":
    uvicorn.run("mainn:app", host="127.0.0.1", port=4000, reload=True)