import os, random
from pprint import pprint
import uvicorn, json
import schemas
from uuid import uuid4
from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import HTMLResponse
from a2a.utils import new_agent_text_message
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.getenv("PORT", 4000))

app = FastAPI()

RAW_AGENT_CARD_DATA = {
  "name": "PingPongAgent",
  "description": "An agent that responds 'pong' to 'ping'.",
  "url": "",
  "documentationUrl": "",
  "provider": {
      "organization": "Telex Org.",
      "url": "https://telex.im"
    },
  "version": "1.0.0",
  "capabilities": {
    "streaming": False,
    "pushNotifications": False
  },
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
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
    external_base = request.headers.get("x-external-base-url", "")
    current_base_url = str(request.base_url).rstrip("/") + external_base

    response_agent_card = RAW_AGENT_CARD_DATA.copy()
    response_agent_card["url"] = current_base_url
    response_agent_card["provider"]["url"] = current_base_url
    response_agent_card["provider"]["documentationUrl"] = f"{current_base_url}/docs"

    return response_agent_card


async def handle_task_send(message:str, request_id):
  if message.lower() == "ping":
    text = "pong"

  else:
    text = "I only understand 'ping'"

  parts = schemas.TextPart(type="text", text=text)

  message = schemas.Message(role="agent", parts=[parts])

  response = schemas.SendResponse(
      id=request_id,
      result=message
  )

  return response



@app.post("/")
async def handle_task(request: Request):
  try:
    body = await request.json()
    request_id = body.get("id")

    message = body["params"]["message"]["parts"][0].get("text", None)

    if not message:
      raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Message cannot be empty."
      )
    
    response = await handle_task_send(message=message, request_id=request_id)

  except json.JSONDecodeError as e:
    error = schemas.JSONParseError(
      data = str(e)
    )

    request = await request.json()
    response = schemas.JSONRPCResponse(
       id=request.get("id"),
       error=error
    )

  except Exception as e:
    error = schemas.JSONRPCError(
      code = -32600,
      message = str(e)
    )

    request = await request.json()
    response = schemas.JSONRPCResponse(
       id=request.get("id"),
       error=error
    )

  response = response.model_dump(exclude_none=True)
  pprint(response)
  return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=PORT, reload=True)
