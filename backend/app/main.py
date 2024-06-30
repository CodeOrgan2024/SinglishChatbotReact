import spacy
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import openai
import os
from typing import List, Tuple


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Set OpenAI API key
openai.api_key = os.getenv("sk-proj-orvvkVdIhDxmr4as8b9bT3BlbkFJ4UVTuhythsI3Bsm1EQ7V")

class ChatRequest(BaseModel):
    message: str

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

def process_message(message: str) -> Tuple[dict, str]:
    """
    Process the user's message using NLP techniques.
    Returns a dictionary of extracted entities and a summary of the message.
    """
    doc = nlp(message)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    summary = " ".join([token.text for token in doc if not token.is_stop and not token.is_punct])
    return {"entities": entities}, summary

def generate_response(message: str) -> str:
    """
    Generate a response using the OpenAI API, based on the processed message.
    """
    _, summary = process_message(message)
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": summary}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message['content'].strip()

def classify_intent(doc):
    """
    Classify the intent of the user's message using a trained model.
    """
    # Implement your intent classification logic here
    return "ask_definition"

@app.post("/chatbot/")
async def chatbot_response(request: ChatRequest):
    try:
        entities, _ = process_message(request.message)
        reply = generate_response(request.message)
        return {"entities": entities, "response": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Message text was: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
