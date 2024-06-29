from sqlalchemy.orm import Session
from app import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username:str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session , user:schemas.UserCreate):
    fake_hashed_password =user.password + "notreallyhashed"
    db_user = models.User(username = user.username, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_message(db:Session, message: schemas.MessageCreate, user_id: int):
    db_message = models.Message(**message.dict(), owner_id = user_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_message (db: Session, skip: int =0, limit: int = 10):
    return db.query(models.Message).offset(skip).limit(limit).all()