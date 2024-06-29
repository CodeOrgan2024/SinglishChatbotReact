from fastapi import Depends, FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app import models, schemas, crud, Database

app = FastAPI()

def get_db():
    db = Database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    return crud.create_user(db=db, user=user)

@app.post("/messages/", response_model=schemas.Message)
def create_message(message: schemas.MessageCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_message(db=db, message=message, user_id=user_id)

@app.get("/messages/", response_model=list[schemas.Message])
def read_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    messages = crud.get_message(db, skip=skip, limit=limit)
    return messages

class Query(BaseModel):
    message: str

@app.post("/chatbot/")
async def get_response(query: Query):
    response = process_message(query.message)
    return {"response": response}

def process_message(message: str) -> str:
    # This function will integrate with Llama2 via LangChain
    return "This is a placeholder response."

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
